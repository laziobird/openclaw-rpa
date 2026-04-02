# pip install playwright && playwright install chromium
# 任务：获取豆瓣电影数据
# 录制时间：2026-04-02 11:02:00
# 由 OpenClaw RPA Recorder（headed 真实录制）生成 — 可脱离 OpenClaw 独立运行

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

CONFIG = {
    "output_dir":    Path.home() / "Desktop",
    "headless":      False,
    "timeout":       60_000,
    "slow_mo":       300,
    # 导航后等待 SPA 内容渲染的额外时间（重型 SPA 如 Yahoo Finance 需要 1-2 秒）
    "spa_settle_ms": 1_500,
    # extract_text 等待目标元素出现的超时（毫秒）
    "content_wait":  15_000,
}

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

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


_EXTRACT_JS = '([s,n])=>{const r=document.querySelector("main")||document.querySelector(\'[role="main"]\');const bare=/^[a-zA-Z][a-zA-Z0-9-]*$/.test(s)&&s.indexOf("#")<0&&s.indexOf(".")<0&&s.indexOf("[")<0&&s.indexOf(" ")<0;const sc=bare&&r?r:document;return Array.from(sc.querySelectorAll(s)).slice(0,n).map(e=>(e.textContent||"").replace(/\\s+/g," ").trim()).filter(Boolean)}'


async def _wait_for_content(page, selector: str) -> None:
    """等待 selector 对应的元素出现在 DOM 中（容错：超时也继续）。"""
    try:
        await page.wait_for_selector(selector, timeout=CONFIG["content_wait"])
    except Exception:
        pass  # 元素未出现也继续，evaluate 会返回空列表


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
            # ── 步骤 1：打开豆瓣电影首页
            try:
                await page.goto('https://movie.douban.com', wait_until="domcontentloaded")
                await page.wait_for_timeout(CONFIG["spa_settle_ms"])
            except Exception:
                await page.screenshot(path="step_1_error.png")
                raise

            # ── 步骤 2：在搜索框输入「霸王别姬」
            try:
                await page.locator('#inp-query').first.fill('霸王别姬')
            except Exception:
                await page.screenshot(path="step_2_error.png")
                raise

            # ── 步骤 3：按 Enter 发起搜索
            try:
                await page.keyboard.press('Enter')
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(800)
            except Exception:
                await page.screenshot(path="step_3_error.png")
                raise

            # ── 步骤 4：等待搜索结果加载
            try:
                await page.wait_for_timeout(1500)
            except Exception:
                await page.screenshot(path="step_4_error.png")
                raise

            # ── 步骤 6：点击第一条搜索结果「霸王别姬」
            try:
                await page.locator('a.title-text').first.click()
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(800)
            except Exception:
                await page.screenshot(path="step_6_error.png")
                raise

            # ── 步骤 7：等待详情页加载
            try:
                await page.wait_for_timeout(2000)
            except Exception:
                await page.screenshot(path="step_7_error.png")
                raise

            # ── 步骤 8：提取片名
            try:
                _sel = 'h1'
                _lim = 9999
                await _wait_for_content(page, _sel)
                _texts = await page.evaluate(_EXTRACT_JS, [_sel, _lim])
                _out = CONFIG["output_dir"] / 'movie.txt'
                _field = '片名'
                _block = _format_extract_section(_field, _texts)
                _out.write_text(_block, encoding="utf-8")
                print(f"已提取 {len(_texts)} 条，写入 {_out}（本文件首次写入）")
            except Exception:
                await page.screenshot(path="step_8_error.png")
                raise

            # ── 步骤 9：提取评分
            try:
                _sel = '#interest_sectl .rating_self strong'
                _lim = 9999
                await _wait_for_content(page, _sel)
                _texts = await page.evaluate(_EXTRACT_JS, [_sel, _lim])
                _out = CONFIG["output_dir"] / 'movie.txt'
                _field = '评分'
                _block = _format_extract_section(_field, _texts)
                with _out.open("a", encoding="utf-8") as _f:
                    _f.write(_block)
                print(f"已提取 {len(_texts)} 条，追加写入 {_out}")
            except Exception:
                await page.screenshot(path="step_9_error.png")
                raise

            # ── 步骤 10：滚动到剧情简介区域
            try:
                await _scroll_window(page, 1000)
                await page.wait_for_timeout(600)
            except Exception:
                await page.screenshot(path="step_10_error.png")
                raise

            # ── 步骤 11：滚动到剧情简介区域
            try:
                await page.evaluate("(s)=>{const e=document.querySelector(s);if(e)e.scrollIntoView({block:'center'})}", '#link-report-intra')
                await page.wait_for_timeout(1200)
            except Exception:
                await page.screenshot(path="step_11_error.png")
                raise

            # ── 步骤 12：提取剧情简介
            try:
                _sel = '#link-report-intra span:first-child'
                _lim = 9999
                await _wait_for_content(page, _sel)
                _texts = await page.evaluate(_EXTRACT_JS, [_sel, _lim])
                _out = CONFIG["output_dir"] / 'movie.txt'
                _field = '剧情简介'
                _block = _format_extract_section(_field, _texts)
                with _out.open("a", encoding="utf-8") as _f:
                    _f.write(_block)
                print(f"已提取 {len(_texts)} 条，追加写入 {_out}")
            except Exception:
                await page.screenshot(path="step_12_error.png")
                raise

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
