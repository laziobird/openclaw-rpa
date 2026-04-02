# Playwright RPA 代码模板库

本文件与 **`recorder_server.py`** 中 `_build_final_script()` 及 `_do_action()` 生成的脚本**逐段对齐**：以 `page.locator(CSS)` 做交互，以 `page.evaluate` + `_EXTRACT_JS` 做批量文本提取。

**重要：** `{占位符}` 仅示意；URL、CSS 选择器、文件名须来自**当前录制**或用户指定，禁止照抄示例。

---

## 标准脚本骨架（与 `_build_final_script` 一致）

以下为录制结束后写入 `script_log.py` 的完整结构；手写或补全脚本时应保持同一套常量与启动参数，避免与录制器行为分叉。

```python
# pip install playwright && playwright install chromium
# 任务：{任务名}
# 录制时间：{timestamp}
# 由 OpenClaw RPA Recorder（headed 真实录制）生成 — 可脱离 OpenClaw 独立运行

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

CONFIG = {
    "output_dir":    Path.home() / "Desktop",
    "headless":      False,
    "timeout":       60_000,
    "slow_mo":       300,
    # 导航后等待 SPA 内容渲染的额外时间（重型 SPA 可能需要 1–2 秒）
    "spa_settle_ms": 1_500,
    # extract_text 等待目标元素出现的超时（毫秒）
    "content_wait":  15_000,
}

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

_EXTRACT_JS = (
    "([s,n])=>{return Array.from(document.querySelectorAll(s))"
    ".slice(0,n).map(e=>(e.textContent||'')"
    ".replace(/\\s+/g,' ').trim()).filter(Boolean)}"
)


async def _wait_for_content(page, selector: str) -> None:
    """等待 selector 对应的元素出现在 DOM 中（容错：超时也继续）。"""
    try:
        await page.wait_for_selector(selector, timeout=CONFIG["content_wait"])
    except Exception:
        pass


async def _scroll_window(page, dy: int) -> None:
    """窗口滚动：导航后若再用 evaluate(scrollBy)，易因执行上下文销毁报错；用 mouse.wheel 并在滚动前等待页面稳定。"""
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
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = await context.new_page()
        page.set_default_timeout(CONFIG["timeout"])

        try:
            # ── 录制步骤展开于此（每步为 try/except 块，见下节）──
            pass

        except PlaywrightTimeout as e:
            await page.screenshot(path="error_timeout.png")
            raise RuntimeError(f"超时：{e}") from e
        except Exception:
            await page.screenshot(path="error_unexpected.png")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
```

---

## 原子步骤片段（与 `_do_action` 生成的 `code_block` 一致）

每步由 `_step_code` 包装为 `try` / `except` + 失败截图 `step_{N}_error.png`（与录制器一致）。下表为**体内语句**，省略外层 try。

### `goto`

```python
await page.goto("{START_URL}", wait_until="domcontentloaded")
await page.wait_for_timeout(CONFIG["spa_settle_ms"])
```

### `fill`（生成脚本仅一行 `locator`；录制进程里会先 `wait_for(visible)`）

```python
await page.locator("{CSS_SELECTOR}").first.fill("{TEXT}")
```

### `select_option`（原生 `<select>`，**勿用 fill**）

`target` 为 `<select>` 的 CSS；`value` 为 `<option value="...">`。可选 `"select_by": "label"`（按可见文字）或 `"index"`（数字）。

```python
await page.locator("{SELECT_CSS}").first.select_option("{OPTION_VALUE}")
await page.wait_for_load_state("domcontentloaded")
await page.wait_for_timeout(800)
```

### `click`

```python
await page.locator("{CSS_SELECTOR}").first.click()
await page.wait_for_load_state("domcontentloaded")
await page.wait_for_timeout(800)
```

### `press`（`target` 为键名，如 `Enter`）

```python
await page.keyboard.press("{KEY}")
await page.wait_for_load_state("domcontentloaded")
await page.wait_for_timeout(800)
```

### `extract_text`（**locator + evaluate**，与录制器同源）

`limit` 为 0 或未传时，生成脚本里用 `_lim = 9999`。

**同一输出文件名多次出现：** 第一次对该文件生成 `write_text`，同一文件名再次 `extract_text` 时 **`open(..., "a")` 追加**。

**排版：** `_format_extract_section(field_label, lines)`：首行 **`【字段：{field_label}】`**（`field` / `field_name` JSON 优先，否则 `context`）、分隔线，多条匹配时 **编号 + 段间空行**。

首次写入示例：

```python
_sel = "{CSS_SELECTOR}"
_lim = 9999
await _wait_for_content(page, _sel)
_texts = await page.evaluate(_EXTRACT_JS, [_sel, _lim])
_out = CONFIG["output_dir"] / "{OUTPUT_FILENAME}"
_field = "{SECTION_LABEL}"
_block = _format_extract_section(_field, _texts)
_out.write_text(_block, encoding="utf-8")
```

同文件再次提取时追加：

```python
_field = "{SECTION_LABEL}"
_block = _format_extract_section(_field, _texts)
with _out.open("a", encoding="utf-8") as _f:
    _f.write(_block)
```

说明：提取的是 `querySelectorAll(_sel)` 匹配节点的 **`textContent`**（整段文本），与 `inner_text()` 可能略有差异；SPA 重绘时用 evaluate 一次性取数，避免 locator 竞态。

### `wait`

```python
await page.wait_for_timeout({MS})
```

### `scroll`（窗口滚动）

使用 `_scroll_window`（`mouse.wheel` + 滚动前 `wait_for_load_state`），避免导航后 `evaluate(scrollBy)` 触发「Execution context was destroyed」。

```python
await _scroll_window(page, {PX})
await page.wait_for_timeout(600)
```

### `scroll_to`（元素滚入视区，触发懒加载）

与录制器生成的单行 JS 一致：

```python
await page.evaluate("(s)=>{const e=document.querySelector(s);if(e)e.scrollIntoView({block:'center'})}", "{CSS_SELECTOR}")
await page.wait_for_timeout(1200)
```

---

## 不写入生成脚本的步骤

| action        | 说明 |
|---------------|------|
| `snapshot`    | 只返回 DOM 快照给 Agent，不产生 `code_block` |
| `dom_inspect` | 调试用子节点结构，不产生 `code_block` |

---

## Registry 更新片段（GENERATING 阶段使用）

```python
import json
from pathlib import Path

registry_path = Path("./rpa/registry.json")
registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
registry["{任务名}"] = "{filename}.py"
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
```

---

## 选择器策略（与录制流水线一致）

1. **录制产出的脚本**：以 **CSS 字符串** 为主，通过 `page.locator(...).first` 与 `document.querySelectorAll`（`_EXTRACT_JS`）使用；来源为 `_snapshot()` 的 `sel` 字段或用户经 `dom_inspect` 修正后的选择器。
2. **手写补充**：若某站无障碍信息完整，可临时使用 `get_by_role` / `get_by_placeholder` 等；**合并进本仓库生成物时**，建议仍改回与录制器相同的 `locator` + `evaluate` 风格，便于与 `recorder_server.py` 再生成时 diff 一致。
3. **提取多条**：优先一条 `extract_text` + 合适 CSS，而不是多次 `inner_text()`，与 `_EXTRACT_JS` 行为对齐。
