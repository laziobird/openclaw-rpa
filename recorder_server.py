#!/usr/bin/env python3
"""
RPA Recorder Server
===================
Long-running headed Playwright process started by `rpa_manager record-start`.

IPC protocol (file-based):
  rpa_manager writes  → SESSION_DIR/cmd.json   {"action":..., "seq": N, ...}
  recorder_server writes → SESSION_DIR/result_N.json  {"success":..., "snapshot":[], ...}

Each executed action:
  - Runs in the headed (visible) Chromium window
  - Takes a screenshot
  - Returns DOM snapshot so the LLM can pick real CSS selectors
  - Appends generated Python code to code_blocks list

On shutdown:
  - Compiles code_blocks into a full standalone Playwright script
  - Saves to SESSION_DIR/script_log.py
  - Writes SESSION_DIR/done marker
"""

import asyncio
import inspect
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR   = Path(__file__).parent
SESSION_DIR = SKILL_DIR / "recorder_session"

POLL_INTERVAL = 0.15  # seconds

# 同一次录制会话内，同一输出文件名多次 extract_text：首次 write_text，之后 open("a") 追加，避免生成脚本互相覆盖
_EXTRACT_OUTPUT_FILES: set[str] = set()


def _reset_extract_output_tracking() -> None:
    global _EXTRACT_OUTPUT_FILES
    _EXTRACT_OUTPUT_FILES = set()


_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# 与 _build_final_script 生成脚本中的 _EXTRACT_JS 一致。
# 裸标签选择器（如 h3、无 # . [ 空格）在存在 <main> / [role=main] 时只在该区域内匹配，
# 避免 Yahoo 等站顶栏 mega-menu 的 h3 先于正文被 slice(0,n) 取走。
_EXTRACT_JS_MIN = (
    '([s,n])=>{const r=document.querySelector("main")||document.querySelector(\'[role="main"]\');'
    'const bare=/^[a-zA-Z][a-zA-Z0-9-]*$/.test(s)&&s.indexOf("#")<0&&s.indexOf(".")<0&&'
    's.indexOf("[")<0&&s.indexOf(" ")<0;'
    'const sc=bare&&r?r:document;return Array.from(sc.querySelectorAll(s)).slice(0,n)'
    '.map(e=>(e.textContent||"").replace(/\\s+/g," ").trim()).filter(Boolean)}'
)


# ── Code generation helpers ──────────────────────────────────────────────────

def _step_code(step_n: int, context: str, body: list[str]) -> str:
    """Wrap body lines in a try/except block inside async def run()."""
    ind = "            "  # 12 spaces — sits inside: async with → browser → try
    lines = [
        f"{ind}# ── 步骤 {step_n}：{context}",
        f"{ind}try:",
    ]
    for b in body:
        lines.append(f"{ind}    {b}")
    lines += [
        f"{ind}except Exception:",
        f'{ind}    await page.screenshot(path="step_{step_n}_error.png")',
        f"{ind}    raise",
    ]
    return "\n".join(lines)


def _format_extract_section(field_label: str, lines: list[str]) -> str:
    """Format extracted DOM text: show field name, separator line, then body."""
    name = (field_label or "").strip() or "extract"
    title = f"【字段：{name}】"
    if not lines:
        body = "(no text matched)\n"
    elif len(lines) == 1:
        body = lines[0].strip() + "\n"
    else:
        parts = [f"{i + 1}. {s.strip()}" for i, s in enumerate(lines)]
        body = "\n\n".join(parts) + "\n"
    sep = "─" * 32
    return f"{title}\n{sep}\n{body}\n"


# ── DOM snapshot ─────────────────────────────────────────────────────────────

async def _snapshot(page) -> list[dict]:
    """Return interactive elements with usable CSS selectors for LLM decision.

    Selector priority:
      1. Own  #id / [data-testid] / [aria-label] / tag[name]
      2. Ancestor walk (max 4 levels) — produces  [data-testid="X"] tag
      3. :nth-of-type fallback inside nearest sectioning parent
    Also returns a separate 'sections' list showing content containers
    so the LLM can scope selectors to specific page areas.
    """
    try:
        return await page.evaluate("""() => {
            // ── helpers ──────────────────────────────────────────────────────
            function ownSel(el) {
                if (el.id) return '#' + el.id;
                const tid  = el.getAttribute('data-testid');
                if (tid)  return `[data-testid="${tid}"]`;
                const aria = el.getAttribute('aria-label');
                if (aria) return `[aria-label="${aria}"]`;
                const name = el.getAttribute('name');
                if (name) return `${el.tagName.toLowerCase()}[name="${name}"]`;
                return null;
            }

            function ancestorSel(el) {
                // Walk up max 4 levels; return composite like [data-testid="X"] a h3
                // IMPORTANT: intermediate tags are included to preserve real DOM nesting
                // order, so LLM cannot confuse "a h3" with "h3 a".
                let cur = el.parentElement;
                const midTags = [];   // intermediate tag names (nearest → farthest)
                for (let d = 0; d < 4 && cur; d++, cur = cur.parentElement) {
                    const s = ownSel(cur);
                    if (s) {
                        // midTags are collected nearest-first; reverse so they read
                        // parent→child in CSS order: ancestor > mid1 > mid2 > el
                        const mid = midTags.slice().reverse().join(' ');
                        return mid ? `${s} ${mid} ${el.tagName.toLowerCase()}`
                                   : `${s} ${el.tagName.toLowerCase()}`;
                    }
                    midTags.push(cur.tagName.toLowerCase());
                }
                return null;
            }

            function nthSel(el) {
                // Fallback: find position among siblings of same tag inside nearest section
                const parent = el.parentElement;
                if (!parent) return null;
                const siblings = Array.from(parent.children)
                    .filter(c => c.tagName === el.tagName);
                const idx = siblings.indexOf(el) + 1;
                const ps = ownSel(parent);
                if (ps) return `${ps} > ${el.tagName.toLowerCase()}:nth-of-type(${idx})`;
                return null;
            }

            // ── collect interactive + heading elements ────────────────────
            const TAGS = [
                'input', 'button', 'select', 'textarea', 'a[href]',
                '[role="button"]', '[role="link"]', '[role="searchbox"]',
                '[role="tab"]', 'h1', 'h2', 'h3', 'li'
            ].join(',');

            const visible = Array.from(document.querySelectorAll(TAGS))
                .filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                })
                .slice(0, 100);

            const items = visible.map(el => {
                const tag  = el.tagName.toLowerCase();
                const ph   = el.getAttribute('placeholder') || null;
                const text = (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 70);
                const sel  = ownSel(el) || ancestorSel(el) || nthSel(el);
                return { tag, sel: sel || null, ph, text: text || null };
            }).filter(e => e.sel || e.text);

            // ── collect content sections (for scoped extraction) ──────────
            const SECTION_TAGS = [
                'section', 'article', '[data-testid]', '[id]'
            ].join(',');
            const sections = Array.from(document.querySelectorAll(SECTION_TAGS))
                .filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 100 && r.height > 50;
                })
                .slice(0, 20)
                .map(el => {
                    const s   = ownSel(el);
                    const h   = el.querySelector('h1,h2,h3');
                    const heading = h ? (h.textContent||'').replace(/\\s+/g,' ').trim().slice(0,50) : null;
                    return s ? { sel: s, heading } : null;
                })
                .filter(Boolean)
                .filter((v, i, a) => a.findIndex(x => x.sel === v.sel) === i);

            return { items, sections };
        }""")
    except Exception:
        return {"items": [], "sections": []}


# ── Action executor ──────────────────────────────────────────────────────────

async def _do_action(page, data: dict, step_n: int, shots_dir: Path) -> dict:
    action  = data.get("action", "")
    target  = data.get("target", "")
    value   = data.get("value", "")
    context = data.get("context") or f"步骤 {step_n}"

    code_block        = None
    error             = None
    inspect_children  = None  # dom_inspect: passed through to result JSON for rpa_manager

    try:
        if action == "goto":
            await page.goto(target, wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)   # SPA initial render
            code_block = _step_code(step_n, context, [
                f'await page.goto({repr(target)}, wait_until="domcontentloaded")',
                'await page.wait_for_timeout(CONFIG["spa_settle_ms"])',
            ])

        elif action == "fill":
            loc = page.locator(target).first
            await loc.wait_for(state="visible", timeout=20_000)
            await loc.fill(value)
            code_block = _step_code(step_n, context, [
                f'await page.locator({repr(target)}).first.fill({repr(value)})',
            ])

        elif action == "press":
            key = target or "Enter"
            await page.keyboard.press(key)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(800)   # let SPA finish routing
            code_block = _step_code(step_n, context, [
                f'await page.keyboard.press({repr(key)})',
                'await page.wait_for_load_state("domcontentloaded")',
                'await page.wait_for_timeout(800)',
            ])

        elif action == "click":
            loc = page.locator(target).first
            await loc.wait_for(state="visible", timeout=20_000)
            await loc.click()
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(800)   # let SPA finish routing
            code_block = _step_code(step_n, context, [
                f'await page.locator({repr(target)}).first.click()',
                'await page.wait_for_load_state("domcontentloaded")',
                'await page.wait_for_timeout(800)',
            ])

        elif action == "select_option":
            # Native <select>: target = CSS, value = option value / label / index (see select_by)
            # Playwright fill() does NOT set <select>; use select_option (e.g. Sauce Demo hilo = price high→low)
            loc = page.locator(target).first
            await loc.wait_for(state="visible", timeout=20_000)
            how = (data.get("select_by") or "value").lower().strip()
            if how == "label":
                await loc.select_option(label=value)
                sel_line = f'await page.locator({repr(target)}).first.select_option(label={repr(value)})'
            elif how == "index":
                idx = int(value)
                await loc.select_option(index=idx)
                sel_line = f'await page.locator({repr(target)}).first.select_option(index={idx})'
            else:
                await loc.select_option(value)
                sel_line = f'await page.locator({repr(target)}).first.select_option({repr(value)})'
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(800)
            code_block = _step_code(step_n, context, [
                sel_line,
                'await page.wait_for_load_state("domcontentloaded")',
                'await page.wait_for_timeout(800)',
            ])

        elif action == "extract_text":
            filename = value or "output.txt"
            limit    = int(data.get("limit", 0)) or 0

            # Wait for page to settle (SPA re-renders can cause locator.all() race)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=5_000)
            except Exception:
                pass

            # Single atomic JS call — immune to mid-flight page re-renders
            limit_n = limit or 9999
            texts = await page.evaluate(_EXTRACT_JS_MIN, [target, limit_n])

            # field / field_name = short label for output; else fall back to context
            field_label = (
                (data.get("field") or data.get("field_name") or context or f"步骤 {step_n}")
                .strip()
                or "extract"
            )
            first_for_name = filename not in _EXTRACT_OUTPUT_FILES
            _EXTRACT_OUTPUT_FILES.add(filename)

            out = Path.home() / "Desktop" / filename
            blob = _format_extract_section(field_label, texts)
            if first_for_name:
                out.write_text(blob, encoding="utf-8")
            else:
                with out.open("a", encoding="utf-8") as f:
                    f.write(blob)
            if texts:
                print(f"[recorder] extracted {len(texts)} items → {out}", flush=True)
            else:
                print(f"[recorder] ⚠️  WARNING: 0 items matched selector {repr(target)}", flush=True)
                print(f"[recorder]    The selector may be wrong or content not yet rendered.", flush=True)
                print(f"[recorder]    Try: dom_inspect on a parent container to see real DOM structure.", flush=True)
                error = f"⚠️ 提取到 0 条内容。选择器 {repr(target)} 可能不匹配当前页面的真实 DOM 结构。\n建议：先用 dom_inspect 检查父容器的真实子元素结构，再修正选择器。"

            # Generated script: same filename → first step write_text, later steps append
            lim_code = str(limit) if limit else "9999"
            field_lit = repr(
                (data.get("field") or data.get("field_name") or context or f"步骤 {step_n}").strip()
                or "extract"
            )
            common_lines = [
                f'_sel = {repr(target)}',
                f'_lim = {lim_code}',
                'await _wait_for_content(page, _sel)',
                '_texts = await page.evaluate(_EXTRACT_JS, [_sel, _lim])',
                f'_out = CONFIG["output_dir"] / {repr(filename)}',
                f'_field = {field_lit}',
                '_block = _format_extract_section(_field, _texts)',
            ]
            if first_for_name:
                body_lines = common_lines + [
                    '_out.write_text(_block, encoding="utf-8")',
                    'print(f"已提取 {len(_texts)} 条，写入 {_out}（本文件首次写入）")',
                ]
            else:
                body_lines = common_lines + [
                    'with _out.open("a", encoding="utf-8") as _f:',
                    '    _f.write(_block)',
                    'print(f"已提取 {len(_texts)} 条，追加写入 {_out}")',
                ]
            code_block = _step_code(step_n, context, body_lines)

        elif action == "wait":
            ms = int(value) if value else 2000
            await page.wait_for_timeout(ms)
            code_block = _step_code(step_n, context, [
                f'await page.wait_for_timeout({ms})',
            ])

        elif action == "scroll":
            px = int(value) if value else 500
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10_000)
            except Exception:
                pass
            vp = page.viewport_size
            if vp:
                await page.mouse.move(vp["width"] // 2, vp["height"] // 2)
            else:
                await page.mouse.move(720, 450)
            await page.mouse.wheel(0, float(px))
            await page.wait_for_timeout(600)   # wait for lazy-load trigger
            code_block = _step_code(step_n, context, [
                f"await _scroll_window(page, {px})",
                "await page.wait_for_timeout(600)",
            ])

        elif action == "scroll_to":
            # Scroll a specific element into view — triggers lazy-load for that section
            await page.evaluate(
                """(sel) => {
                    const el = document.querySelector(sel);
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }""",
                target,
            )
            await page.wait_for_timeout(1200)  # wait for lazy content to render
            # Use single-quoted JS string in generated code to avoid escape hell
            js_str = "(s)=>{const e=document.querySelector(s);if(e)e.scrollIntoView({block:'center'})}"
            code_block = _step_code(step_n, context, [
                f'await page.evaluate({repr(js_str)}, {repr(target)})',
                'await page.wait_for_timeout(1200)',
            ])

        elif action == "snapshot":
            pass  # read-only DOM inspection — NOT logged to script

        elif action == "dom_inspect":
            # Diagnostic: return child structure of a container element.
            # NOT logged to the script — only used to discover real selectors.
            result = await page.evaluate("""(sel) => {
                const el = document.querySelector(sel);
                if (!el) return { found: false, message: 'Element not found: ' + sel };
                const children = Array.from(el.querySelectorAll('*'))
                    .slice(0, 50)
                    .map(c => ({
                        tag:    c.tagName.toLowerCase(),
                        id:     c.id || null,
                        testid: c.getAttribute('data-testid') || null,
                        cls:    Array.from(c.classList).slice(0, 2).join(' ') || null,
                        aria:   c.getAttribute('aria-label') || null,
                        text:   (c.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 60),
                    }));
                return { found: true, outerTag: el.tagName.toLowerCase(), children };
            }""", target)
            # Attach inspect result directly to action result (not to code_block)
            if isinstance(result, dict) and result.get("found"):
                children = result.get("children", [])
                # Print structured summary for the LLM to read
                lines = [f"[dom_inspect] 容器 {repr(target)} 共 {len(children)} 个子元素："]
                for c in children[:30]:
                    sel_hint = (
                        f"#{c['id']}" if c['id']
                        else f"[data-testid=\"{c['testid']}\"]" if c['testid']
                        else f"[aria-label=\"{c['aria']}\"]" if c['aria']
                        else f".{c['cls'].split()[0]}" if c['cls']
                        else c['tag']
                    )
                    print(f"  {sel_hint}  「{c['text'][:50]}」", flush=True)
                # Return children in result for rpa_manager to display
                code_block = None  # not logged
                inspect_children = children
            else:
                error = result.get("message", "dom_inspect failed") if isinstance(result, dict) else "dom_inspect failed"

        else:
            error = f"未知 action: {action!r}"

    except Exception as exc:
        error = str(exc)

    # Screenshot after every action (proof + visual feedback for user)
    ts         = datetime.now().strftime("%H%M%S")
    label      = "snapshot" if action == "snapshot" else f"step_{step_n:02d}"
    shot_path  = shots_dir / f"{label}_{ts}.png"
    try:
        await page.screenshot(path=str(shot_path), full_page=False)
    except Exception:
        shot_path = None

    # Always return current DOM snapshot so LLM can choose next selector
    raw_snap = await _snapshot(page)
    # _snapshot now returns {"items": [...], "sections": [...]}
    if isinstance(raw_snap, dict):
        snap     = raw_snap.get("items", [])
        sections = raw_snap.get("sections", [])
    else:
        snap     = raw_snap  # backward compat if something went wrong
        sections = []

    out = {
        "success":    error is None,
        "error":      error,
        "code_block": code_block,
        "screenshot": str(shot_path) if shot_path else None,
        "url":        page.url,
        "snapshot":   snap,
        "sections":   sections,
    }
    if inspect_children is not None:
        out["_inspect_children"] = inspect_children
    return out


# ── Script builder ───────────────────────────────────────────────────────────

def _build_final_script(task_name: str, code_blocks: list[str]) -> str:
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    steps = "\n\n".join(code_blocks) if code_blocks else "            pass  # 无录制步骤"
    fmt_src = inspect.getsource(_format_extract_section)
    extract_js_repr = repr(_EXTRACT_JS_MIN)
    return f"""\
# pip install playwright && playwright install chromium
# 任务：{task_name}
# 录制时间：{ts}
# 由 OpenClaw RPA Recorder（headed 真实录制）生成 — 可脱离 OpenClaw 独立运行

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

CONFIG = {{
    "output_dir":    Path.home() / "Desktop",
    "headless":      False,
    "timeout":       60_000,
    "slow_mo":       300,
    # 导航后等待 SPA 内容渲染的额外时间（重型 SPA 如 Yahoo Finance 需要 1-2 秒）
    "spa_settle_ms": 1_500,
    # extract_text 等待目标元素出现的超时（毫秒）
    "content_wait":  15_000,
}}

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

{fmt_src}

_EXTRACT_JS = {extract_js_repr}


async def _wait_for_content(page, selector: str) -> None:
    \"\"\"等待 selector 对应的元素出现在 DOM 中（容错：超时也继续）。\"\"\"
    try:
        await page.wait_for_selector(selector, timeout=CONFIG["content_wait"])
    except Exception:
        pass  # 元素未出现也继续，evaluate 会返回空列表


async def _scroll_window(page, dy: int) -> None:
    \"\"\"窗口滚动：导航后若再用 evaluate(scrollBy)，易因执行上下文销毁报错；用 mouse.wheel 并在滚动前等待页面稳定。\"\"\"
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=10_000)
    except Exception:
        pass
    vp = page.viewport_size
    if vp:
        await page.mouse.move(vp["width"] // 2, vp["height"] // 2)
    else:
        await page.mouse.move(720, 450)
    await page.mouse.wheel(0, float(dy))


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=CONFIG["headless"],
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            slow_mo=CONFIG["slow_mo"],
        )
        context = await browser.new_context(
            user_agent=_UA,
            viewport={{"width": 1440, "height": 900}},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={{"Accept-Language": "en-US,en;q=0.9"}},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}})"
        )
        page = await context.new_page()
        page.set_default_timeout(CONFIG["timeout"])

        try:
{steps}

        except PlaywrightTimeout as e:
            await page.screenshot(path="error_timeout.png")
            raise RuntimeError(f"超时：{{e}}") from e
        except Exception:
            await page.screenshot(path="error_unexpected.png")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
"""


# ── Server main loop ─────────────────────────────────────────────────────────

async def server_main():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    pid_path = SESSION_DIR / "server.pid"
    pid_path.write_text(str(os.getpid()))

    _reset_extract_output_tracking()

    task_data = json.loads((SESSION_DIR / "task.json").read_text())
    task_name = task_data["task"]
    shots_dir = SESSION_DIR / "screenshots"
    shots_dir.mkdir(exist_ok=True)

    code_blocks: list[str] = []
    step_n = 0

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            slow_mo=200,
        )
        ctx = await browser.new_context(
            user_agent=_UA,
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        await ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
        )
        page = await ctx.new_page()
        page.set_default_timeout(60_000)

        # Signal ready to rpa_manager (it polls for this file)
        (SESSION_DIR / "ready").write_text("1")
        print(f"[recorder] ready — task: {task_name}", flush=True)

        last_seq = -1
        cmd_path = SESSION_DIR / "cmd.json"

        while True:
            if cmd_path.exists():
                try:
                    data = json.loads(cmd_path.read_text())
                    seq  = data.get("seq", 0)
                    if seq > last_seq:
                        last_seq = seq
                        action   = data.get("action", "")

                        if action == "shutdown":
                            break

                        if action != "snapshot":
                            step_n += 1

                        result = await _do_action(page, data, step_n, shots_dir)

                        if result.get("code_block"):
                            code_blocks.append(result["code_block"])

                        (SESSION_DIR / f"result_{seq}.json").write_text(
                            json.dumps(result, ensure_ascii=False, indent=2)
                        )
                except Exception as exc:
                    try:
                        (SESSION_DIR / f"result_{last_seq}.json").write_text(
                            json.dumps(
                                {"success": False, "error": str(exc),
                                 "code_block": None, "snapshot": []},
                                ensure_ascii=False,
                            )
                        )
                    except Exception:
                        pass

            await asyncio.sleep(POLL_INTERVAL)

        await browser.close()

    # Compile and save final script
    script = _build_final_script(task_name, code_blocks)
    (SESSION_DIR / "script_log.py").write_text(script, encoding="utf-8")
    (SESSION_DIR / "done").write_text("1")
    pid_path.unlink(missing_ok=True)
    print(f"[recorder] done — {len(code_blocks)} steps — script saved.", flush=True)


if __name__ == "__main__":
    asyncio.run(server_main())
