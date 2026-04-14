#!/usr/bin/env python3
"""
OpenClaw RPA Manager — 状态持久化 & 脚本生成 CLI
OpenClaw RPA Manager — Session persistence & script generation CLI

【登录会话管理 / Login Session Management（复杂登录 / SMS OTP / CAPTCHA / slider）】
  python3 rpa_manager.py login-start <url>   # 打开浏览器到登录页，用户手动完成登录 / Open browser to login page; user logs in manually
  python3 rpa_manager.py login-done          # 导出当前 Cookie 并关闭浏览器 / Export cookies & close browser
  python3 rpa_manager.py login-list          # 列出所有已保存的登录会话 / List all saved login sessions
  python3 rpa_manager.py help                # 显示完整指令列表与简单用法 / Show full command reference
  # Cookie 存储于 ~/.openclaw/rpa/sessions/{domain}/cookies.json（勿提交 git）
  # Cookies stored at ~/.openclaw/rpa/sessions/{domain}/cookies.json (never commit to git)
  # 录制/回放时任务描述含 #rpa-autologin <domain|url> 则自动注入
  # Add #rpa-autologin <domain|url> to task description to auto-inject cookies on record/replay

【Recorder 模式 / Recorder Mode — 推荐，有界面真实录制 / Recommended: headed real-browser recording】
  python3 rpa_manager.py record-start <task> [--profile A]   # 启动 headed Playwright / Start headed Playwright; --profile writes to task.json
  python3 rpa_manager.py deps-check <A-N>        # 按能力码检查依赖 / Check deps by capability code
  python3 rpa_manager.py deps-install <A-N>      # 安装缺失依赖 / Install missing deps
  python3 rpa_manager.py record-step '<json>'    # 执行单步操作 / Execute a single recorded step
  python3 rpa_manager.py record-status           # 查看 Recorder 状态 / Check recorder status
  python3 rpa_manager.py record-end              # 结束录制，生成脚本 / End recording, compile script
  python3 rpa_manager.py record-end --abort      # 放弃录制 / Abort recording
  # 每步指令与生成代码片段追加写入 recorder_session/playwright_commands.jsonl
  # Each step appended to recorder_session/playwright_commands.jsonl; copied to rpa/{slug}_playwright_commands.jsonl on end

【Legacy 模式 / Legacy Mode — 兼容保留 / kept for compatibility; requires manual screenshot proof】
  python3 rpa_manager.py init <task_name>
  python3 rpa_manager.py add --proof <file> '<json>'
  python3 rpa_manager.py generate

【通用命令 / General Commands】
  python3 rpa_manager.py run <task_name>   # 运行已保存的任务 / Run a saved task
  python3 rpa_manager.py list              # 列出所有任务 / List all tasks
  python3 rpa_manager.py status            # 查看当前状态 / Show current session status
  python3 rpa_manager.py reset             # 清空 Buffer / Clear buffer
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import envcheck

# ── 时间戳日志：所有 print() 自动加前缀 [HH:MM:SS] ──────────────────────────
# Timestamped logging: prepend [HH:MM:SS] to every print() call
import builtins as _builtins
_real_print = _builtins.print
def _timed_print(*args, **kwargs):  # type: ignore[override]
    _real_print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]", *args, **kwargs)
_builtins.print = _timed_print
# ─────────────────────────────────────────────────────────────────────────────

SKILL_DIR        = Path(__file__).parent
SESSION_FILE     = SKILL_DIR / "session.json"
REGISTRY_FILE    = SKILL_DIR / "registry.json"
RPA_DIR          = SKILL_DIR / "rpa"
PROOFS_DIR       = SKILL_DIR / "proofs"
SESSION_REC_DIR  = SKILL_DIR / "recorder_session"  # Recorder 模式专用目录 / dedicated dir for Recorder mode
# 录制时每一步 record-step 追加一行 JSON（含指令与生成的 Playwright 代码片段）
# Each record-step appends one JSON line (command + generated Playwright code snippet)
PLAYWRIGHT_CMD_LOG = SESSION_REC_DIR / "playwright_commands.jsonl"
# 登录会话存储目录（Cookie JSON，按域名分子目录；敏感数据，勿提交 git）
# Login session store: Cookie JSON per domain subdirectory. Sensitive — never commit to git.
SESSIONS_DIR     = Path.home() / ".openclaw" / "rpa" / "sessions"

# record-step 等待 recorder_server 写出 result_{seq}.json 的最长时间
# Max wait time for recorder_server to write result_{seq}.json after each record-step
RECORD_STEP_RESULT_WAIT_S   = 120
# extract_by_vision 需调用多模态 API + 截图，易超过 120s；轮询上限单独放宽
RECORD_STEP_RESULT_WAIT_VISION_S = 300
RECORD_STEP_POLL_INTERVAL_S = 0.2
RECORD_STEP_POLL_ITERATIONS = int(RECORD_STEP_RESULT_WAIT_S / RECORD_STEP_POLL_INTERVAL_S)  # 600

# 证明文件最小字节数（避免空文件 / 未真实截图）
# Minimum proof file size in bytes (guards against empty files / missing screenshots)
MIN_PROOF_BYTES = 64


# ── 登录会话 helpers / Login session helpers ─────────────────

def _fix_json_literal_newlines(raw: str) -> str:
    """修复 AI 用 Write 工具写 JSON 时，字符串值内含字面换行（不是 \\n）导致 JSON 非法的问题。

    策略：逐字符扫描，在 JSON 字符串值（双引号内）里遇到裸 CR/LF 就替换为 \\n/\\r，
    同时正确处理 \\\\ 转义序列，不碰 JSON 结构本身的换行。
    """
    out: list[str] = []
    in_str = False
    i = 0
    while i < len(raw):
        ch = raw[i]
        if in_str:
            if ch == "\\":
                # 转义序列：原样保留两个字符
                out.append(ch)
                i += 1
                if i < len(raw):
                    out.append(raw[i])
                    i += 1
                continue
            elif ch == '"':
                in_str = False
                out.append(ch)
            elif ch == "\n":
                out.append("\\n")
            elif ch == "\r":
                out.append("\\r")
            elif ch == "\t":
                out.append("\\t")
            else:
                out.append(ch)
        else:
            if ch == '"':
                in_str = True
                out.append(ch)
            else:
                out.append(ch)
        i += 1
    return "".join(out)


def _domain_from_url(url: str) -> str:
    """从 URL 提取 hostname，去掉 www. 前缀，用作会话目录名。
    Extract hostname from URL, strip www. prefix, used as session directory name."""
    from urllib.parse import urlparse
    host = urlparse(url).hostname or url
    if host.startswith("www."):
        host = host[4:]
    return host


def _cookies_path_for_domain(domain: str) -> Path:
    return SESSIONS_DIR / domain / "cookies.json"


def _cookies_meta_path_for_domain(domain: str) -> Path:
    return SESSIONS_DIR / domain / "cookies_meta.json"


# ── 状态管理 / Session state management ────────────────────────────────────

def load_session() -> dict:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    return {"task": None, "state": "IDLE", "buffer": []}


def save_session(session: dict):
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def load_registry() -> dict:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return {}


def save_registry(registry: dict):
    REGISTRY_FILE.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 命令实现 / Command implementations ──────────────────────────────────────

def _proof_dir_for_task(task_name: str) -> Path:
    slug = _slugify(task_name)
    return PROOFS_DIR / slug


def cmd_init(task_name: str) -> int:
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    pdir = _proof_dir_for_task(task_name)
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True, exist_ok=True)

    session = {
        "task": task_name,
        "state": "RECORDING",
        "buffer": [],
        "created_at": datetime.now().isoformat(),
    }
    save_session(session)
    print(f"✅ 录制会话已初始化 / Recording session initialised: 「{task_name}」")
    print("Action Buffer 已清空，proofs 目录已重置。/ Action buffer cleared, proofs directory reset.")
    print(f"证明目录 / Proof dir: {pdir}")
    print("下一步：每步必须先浏览器实操成功，再带 --proof 调用 add。/ Next: complete each step in the browser first, then call add --proof.")
    return 0


def _validate_proof_file(path: Path):
    if not path.exists():
        return False, f"证明路径不存在 / proof path not found: {path}"
    if not path.is_file():
        return False, f"证明路径不是普通文件 / proof path is not a regular file: {path}"
    try:
        sz = path.stat().st_size
    except OSError as e:
        return False, f"无法读取证明文件 / cannot read proof file: {e}"
    if sz < MIN_PROOF_BYTES:
        return False, f"证明文件过小 / proof file too small ({sz} < {MIN_PROOF_BYTES} bytes), rejected"
    return True, ""


def cmd_add(action_json: str, proof_path: str) -> int:
    session = load_session()
    if session["state"] != "RECORDING":
        print(f"❌ 当前状态为 {session['state']}，未处于录制中。请先执行 init <task_name> / Current state is {session['state']}, not recording. Run init <task_name> first.", file=sys.stderr)
        return 1

    src = Path(proof_path).expanduser().resolve()
    ok, err = _validate_proof_file(src)
    if not ok:
        print(f"❌ 拒绝记录 / Rejected: {err}", file=sys.stderr)
        return 1

    try:
        action = json.loads(action_json)
    except json.JSONDecodeError as e:
        print(f"❌ 无效 JSON / Invalid JSON: {e}", file=sys.stderr)
        return 1

    task_name = session.get("task") or "task"
    step_n = len(session["buffer"]) + 1
    dest_dir = _proof_dir_for_task(task_name)
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix if src.suffix else ".bin"
    dest = dest_dir / f"step_{step_n:02d}{suffix}"
    shutil.copy2(src, dest)

    action["step"] = step_n
    action.setdefault("timestamp", datetime.now().isoformat())
    action["proof"] = str(dest)
    action["proof_source"] = str(src)

    session["buffer"].append(action)
    save_session(session)
    print(f"✅ [步骤 / step {action['step']}] 已提交证明 / proof submitted → {dest}")
    print(f"   {action.get('context', 'recorded')}（共 / total {len(session['buffer'])} 步 / steps）")
    return 0


def cmd_status() -> int:
    session = load_session()
    print(f"状态 / State: {session['state']}")
    print(f"任务 / Task: {session.get('task') or '无 / none'}")
    buf = session.get("buffer", [])
    print(f"已录制步骤 / Recorded steps: {len(buf)}（每步须含有效 proof / each step must have a valid proof）")
    for a in buf:
        pf = a.get("proof", "")
        ok = "✅" if pf and Path(pf).is_file() else "❌"
        print(
            f"  [{a['step']}] {ok} {a.get('category','?')}:{a.get('action','?')} — {a.get('context','')}"
        )
        if pf:
            print(f"       proof: {pf}")
    return 0


def cmd_generate() -> int:
    session = load_session()
    buf = session.get("buffer", [])
    if not buf:
        print("❌ Action Buffer 为空，无法生成脚本。/ Action buffer is empty, cannot generate script.", file=sys.stderr)
        return 1

    # 强制：每步必须有可验证的 proof，否则拒绝生成
    for a in buf:
        pf = a.get("proof")
        if not pf:
            print(
                f"❌ 拒绝生成：步骤 {a.get('step')} 缺少 proof 字段。"
                "请用「浏览器实操成功 → 保存截图/结果文件 → add --proof」重新录制。"
                f" / Rejected: step {a.get('step')} is missing a proof field."
                " Re-record using: browser action → save screenshot/result → add --proof.",
                file=sys.stderr,
            )
            return 1
        p = Path(pf)
        ok, err = _validate_proof_file(p)
        if not ok:
            print(f"❌ 拒绝生成：步骤 {a.get('step')} 的证明无效：{err} / Rejected: proof for step {a.get('step')} is invalid: {err}", file=sys.stderr)
            return 1

    task_name = session.get("task") or "task"
    filename = _slugify(task_name)
    RPA_DIR.mkdir(exist_ok=True)
    output_path = RPA_DIR / f"{filename}.py"

    script = _build_playwright_script(task_name, buf)
    output_path.write_text(script, encoding="utf-8")

    registry = load_registry()
    registry[task_name] = f"{filename}.py"
    save_registry(registry)

    # 重置会话
    save_session({"task": None, "state": "IDLE", "buffer": []})

    print(f"✨ RPA 脚本生成成功！/ RPA script generated successfully!")
    print(f"📄 文件 / File: {output_path}")
    print(f"📋 共录制 {len(buf)} 个步骤 / {len(buf)} steps recorded")
    print(f"\n运行方式 / Run: python3 {output_path}")
    print(f'下次直接说"运行：{task_name}"即可重放。/ Next time say "run:{task_name}" to replay.')
    return 0


def cmd_run(task_name: str) -> int:
    registry = load_registry()
    if task_name not in registry:
        available = list(registry.keys())
        print(f"❌ 未找到任务「{task_name}」。/ Task not found: {task_name}", file=sys.stderr)
        if available:
            print(f"   可用任务 / Available tasks: {', '.join(available)}", file=sys.stderr)
        else:
            print("   暂无已录制任务，请先录制。/ No recorded tasks yet, record one first.", file=sys.stderr)
        return 1

    script_path = RPA_DIR / registry[task_name]
    if not script_path.exists():
        print(f"❌ 脚本文件不存在 / Script file not found: {script_path}", file=sys.stderr)
        return 1

    if envcheck.ensure_playwright_chromium(auto_install=True) != 0:
        return 1

    print(f"▶️  正在运行 / Running: 「{task_name}」…")
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode == 0:
        print(f"✅ 运行完毕 / Done: 「{task_name}」")
    else:
        print(f"❌ 运行失败 / Run failed (exit code {result.returncode})", file=sys.stderr)
    return result.returncode


def cmd_list() -> int:
    registry = load_registry()
    if not registry:
        print("暂无已录制的任务。/ No recorded tasks yet.")
        return 0
    print("已录制的 RPA 任务 / Recorded RPA tasks:")
    for task, filename in registry.items():
        exists = "✅" if (RPA_DIR / filename).exists() else "❌ 文件缺失"
        print(f"  {exists}  「{task}」→ rpa/{filename}")
    return 0


def cmd_reset() -> int:
    session = load_session()
    task = session.get("task")
    if task:
        pdir = _proof_dir_for_task(task)
        if pdir.exists():
            shutil.rmtree(pdir)
            print(f"🗑️  已删除证明目录 / Proof directory deleted: {pdir}")
    save_session({"task": None, "state": "IDLE", "buffer": []})
    print("🗑️  录制已放弃，Action Buffer 已清空。/ Recording aborted, action buffer cleared.")
    return 0


# ── 计划管理命令（多步指令拆解，防 LLM 超时）/ Plan management (multi-step decomposition, prevents LLM timeout) ──

PLAN_FILE = SESSION_REC_DIR / "plan.json"


def _load_plan() -> Optional[dict]:
    if PLAN_FILE.exists():
        try:
            return json.loads(PLAN_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def cmd_plan_set(steps_json: str) -> int:
    """Initialize a multi-step execution plan."""
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as e:
        print(f"❌ 无效 JSON / Invalid JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(steps, list) or not steps:
        print("❌ steps 必须是非空字符串数组，如 '[\"步骤1\", \"步骤2\"]' / steps must be a non-empty string array, e.g. '[\"step1\", \"step2\"]'", file=sys.stderr)
        return 1

    SESSION_REC_DIR.mkdir(parents=True, exist_ok=True)
    plan = {
        "steps": [str(s) for s in steps],
        "current": 1,
        "total": len(steps),
        "created_at": datetime.now().isoformat(),
    }
    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"📋 任务计划已创建 / Plan created ({len(steps)} steps):")
    for i, step in enumerate(steps, 1):
        marker = "▶️ " if i == 1 else "  "
        print(f"  {marker}{i}. {step}")
    print(f"\n当前执行 / Now executing: step 1/{len(steps)}")
    return 0


def cmd_plan_next() -> int:
    """Advance plan to next step."""
    plan = _load_plan()
    if plan is None:
        print("❌ 无活跃计划。请先执行 plan-set。/ No active plan. Run plan-set first.", file=sys.stderr)
        return 1

    current = plan["current"]
    total   = plan["total"]

    if current >= total:
        print(f"🎉 所有 {total} 步均已完成！/ All {total} steps completed!")
        print('请说「结束录制」生成 RPA 脚本。/ Say "end recording" to generate the RPA script.')
        return 0

    plan["current"] = current + 1
    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    next_desc = plan["steps"][plan["current"] - 1]
    print(f"📍 进度 / Progress: {plan['current']}/{total}")
    print(f"当前步骤 / Current step: {next_desc}")
    return 0


def cmd_plan_status() -> int:
    """Show current plan progress."""
    plan = _load_plan()
    if plan is None:
        print("ℹ️  无活跃计划。/ No active plan.")
        return 0

    current = plan["current"]
    total   = plan["total"]
    print(f"📋 任务计划进度 / Plan progress ({current}/{total} 步 / steps):")
    for i, step in enumerate(plan["steps"], 1):
        if i < current:
            marker = "✅"
        elif i == current:
            marker = "▶️ "
        else:
            marker = "⬜"
        print(f"  {marker} {i}. {step}")
    return 0


# ── Recorder 模式命令 / Recorder mode commands ──────────────────────────────

def _rec_current_seq() -> int:
    """Return current cmd seq from recorder cmd.json, or -1."""
    p = SESSION_REC_DIR / "cmd.json"
    if p.exists():
        try:
            return json.loads(p.read_text()).get("seq", -1)
        except Exception:
            pass
    return -1


def _append_playwright_cmd_log(entry: dict) -> None:
    """Append one JSON object per line (JSONL) for audit / debugging."""
    PLAYWRIGHT_CMD_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with open(PLAYWRIGHT_CMD_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def _rec_send_shutdown():
    """Write shutdown command to recorder IPC."""
    cmd_path = SESSION_REC_DIR / "cmd.json"
    seq = _rec_current_seq()
    cmd_path.write_text(json.dumps({"action": "shutdown", "seq": seq + 1}))
    time.sleep(1.0)


def cmd_login_start(url: str) -> int:
    """打开 headed 浏览器到指定登录页；用户手动完成登录后执行 login-done 导出 Cookie。
    Open a headed browser to the given login URL; run login-done after manual login to export cookies."""
    if envcheck.ensure_playwright_chromium(auto_install=True) != 0:
        return 1

    if SESSION_REC_DIR.exists():
        shutil.rmtree(SESSION_REC_DIR)
    SESSION_REC_DIR.mkdir(parents=True)

    domain = _domain_from_url(url)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    (SESSIONS_DIR / domain).mkdir(parents=True, exist_ok=True)
    cookies_path      = _cookies_path_for_domain(domain)
    cookies_meta_path = _cookies_meta_path_for_domain(domain)

    task_payload = {
        "task":                f"login_{domain}",
        "mode":                "login_capture",
        "login_url":           url,
        "domain":              domain,
        "cookies_output":      str(cookies_path),
        "cookies_meta_output": str(cookies_meta_path),
    }
    (SESSION_REC_DIR / "task.json").write_text(
        json.dumps(task_payload, ensure_ascii=False, indent=2)
    )

    server_script = SKILL_DIR / "recorder_server.py"
    if not server_script.exists():
        print(f"❌ recorder_server.py 不存在 / not found: {server_script}", file=sys.stderr)
        return 1

    log_path = SESSION_REC_DIR / "server.log"
    with open(log_path, "w") as log:
        proc = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=log,
            stderr=log,
            start_new_session=True,
        )

    print(f"⏳ 正在启动登录浏览器（PID: {proc.pid}）… / Starting login browser (PID: {proc.pid})…")

    ready_path = SESSION_REC_DIR / "ready"
    for _ in range(150):
        if ready_path.exists():
            break
        time.sleep(0.2)
    else:
        print("❌ 浏览器启动超时（30s）。/ Browser startup timed out (30s).", file=sys.stderr)
        print(f"   详细日志 / See log: {log_path}", file=sys.stderr)
        return 1

    print(f"✅ 浏览器已打开 / Browser opened → {url}")
    print(f"   请在浏览器窗口中完成登录（账号/密码/短信/滑块等所有验证）。/ Complete login in the browser window (password / OTP / slider / QR code, etc.).")
    print(f"   确认已登录后，执行 / When done, run: python3 rpa_manager.py login-done")
    return 0


def cmd_login_done() -> int:
    """通知浏览器导出当前 Cookie 并关闭，完成登录会话保存。
    Signal the login browser to export current cookies and shut down; finishes session save."""
    pid_path  = SESSION_REC_DIR / "server.pid"
    task_path = SESSION_REC_DIR / "task.json"

    if not pid_path.exists():
        print("❌ 没有运行中的登录浏览器，请先执行 login-start <url>。/ No running login browser — run login-start <url> first.", file=sys.stderr)
        return 1
    if not task_path.exists():
        print("❌ 找不到任务信息（task.json）。/ task.json not found.", file=sys.stderr)
        return 1

    task_data         = json.loads(task_path.read_text())
    domain            = task_data.get("domain", "unknown")
    cookies_output    = task_data.get("cookies_output", "")
    cookies_meta_out  = task_data.get("cookies_meta_output", "")

    seq = _rec_current_seq()
    (SESSION_REC_DIR / "cmd.json").write_text(
        json.dumps({"action": "login_done", "seq": seq + 1})
    )
    print("⏳ 正在导出 Cookie，请稍候…")

    done_path = SESSION_REC_DIR / "login_done"
    for _ in range(75):
        if done_path.exists():
            break
        time.sleep(0.2)
    else:
        print("❌ Cookie 导出超时（15s）。", file=sys.stderr)
        return 1

    if SESSION_REC_DIR.exists():
        shutil.rmtree(SESSION_REC_DIR)

    if cookies_output and Path(cookies_output).exists():
        meta: dict = {}
        if cookies_meta_out and Path(cookies_meta_out).exists():
            try:
                meta = json.loads(Path(cookies_meta_out).read_text())
            except Exception:
                pass
        total         = meta.get("total", "?")
        session_count = meta.get("session_cookies", 0)
        earliest      = meta.get("earliest_expires")
        print(f"✅ Cookie 已保存 → {cookies_output}")
        print(f"   域名：{domain}，共 {total} 条（其中 {session_count} 条为会话型）")
        if earliest:
            print(f"   ⏰ 参考过期时间（最早一条）：{earliest}（实际以服务端策略为准，可能更早）")
        else:
            print(f"   ⚠️  所有 Cookie 均为会话类型，无固定过期时间，以页面是否仍登录为准")
        print(f"\n   下次录制或回放自动注入：在任务描述中加入 #rpa-autologin {domain}")
    else:
        print("❌ Cookie 文件未生成，请确认浏览器中已完成登录。", file=sys.stderr)
        return 1

    return 0


def cmd_login_list() -> int:
    """列出所有已保存的登录会话及参考过期状态。
    List all saved login sessions with their reference expiry status."""
    from datetime import datetime as _dt

    if not SESSIONS_DIR.exists():
        print("📭 暂无已保存的登录会话。")
        print(f"   使用 python3 rpa_manager.py login-start <url> 来保存。")
        return 0

    domains = sorted(d for d in SESSIONS_DIR.iterdir()
                     if d.is_dir() and (d / "cookies.json").exists())
    if not domains:
        print("📭 暂无已保存的登录会话。")
        print(f"   使用 python3 rpa_manager.py login-start <url> 来保存。")
        return 0

    print(f"\n{'域名':<32} {'条数':>4} {'会话型':>4} {'保存时间':<22} 状态")
    print("─" * 92)
    for domain_dir in domains:
        meta: dict = {}
        meta_path = domain_dir / "cookies_meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except Exception:
                pass
        total         = meta.get("total", "?")
        session_count = meta.get("session_cookies", 0)
        saved_at      = meta.get("saved_at", "—")
        earliest      = meta.get("earliest_expires")

        if not earliest:
            status = "⚠️  无固定过期时间（会话型）"
        else:
            try:
                exp_dt    = _dt.fromisoformat(earliest)
                days_left = (exp_dt - _dt.now()).days
                if days_left < 0:
                    status = f"🔴 已过参考期（{earliest[:10]}）"
                elif days_left <= 7:
                    status = f"🟡 即将到期（{days_left}天，{earliest[:10]}）"
                else:
                    status = f"🟢 {days_left}天后参考过期（{earliest[:10]}）"
            except Exception:
                status = f"✅ 参考期：{earliest}"

        print(f"{domain_dir.name:<32} {str(total):>4} {str(session_count):>4} {saved_at:<22} {status}")

    print(f"\n共 {len(domains)} 条，保存于：{SESSIONS_DIR}")
    print("使用方式：录制或回放任务时，在任务描述中加入 #rpa-autologin <域名或完整URL>")
    return 0


def cmd_help() -> int:
    """打印完整指令参考表，供开发者快速查阅。
    Print the full command reference for developers."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          OpenClaw RPA Manager — 指令参考 / Command Reference               ║
╚══════════════════════════════════════════════════════════════════════════════╝

【登录会话管理 / Login Session Management】
  适用场景：短信验证码、滑块、扫码、企业 SSO 等复杂登录场景。
  Use when: SMS OTP, CAPTCHA slider, QR-code login, enterprise SSO, etc.

  login-start <url>
      打开 headed 浏览器到登录页，用户手动完成登录。
      Open headed browser to login page; user logs in manually.
      示例 / Example:
        python3 rpa_manager.py login-start https://passport.ctrip.com/user/login

  login-done
      登录完成后执行，导出 Cookie 并关闭浏览器。
      Run after manual login: exports cookies and closes the browser.
      Cookie 保存至 / Saved to: ~/.openclaw/rpa/sessions/<domain>/cookies.json

  login-list
      列出所有已保存的登录会话及参考过期状态（🟢已保存 / 🟡即将到期 / 🔴已过期）。
      List all saved login sessions with reference expiry status.

  ➜ 录制/回放时注入 Cookie / Inject cookies during record or replay:
      在任务描述中加入 #rpa-autologin <域名或URL>
      Add #rpa-autologin <domain|url> to the task description.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Recorder 模式 / Recorder Mode（推荐 / Recommended）】
  基于真实浏览器一步步录制，record-end 后自动编译为可独立运行的 Python 脚本。
  Records in a real headed browser step-by-step; compiles to standalone Python on record-end.

  record-start <task> [--profile A-N] [--autologin <domain|url>]
      启动 Recorder 浏览器，进入录制模式；--autologin 自动注入已保存的登录 Cookie。
      Launch headed Playwright Recorder; --autologin injects saved cookies before recording starts.

  record-step '<json>'
      向 Recorder 发送一步操作（goto / click / fill / snapshot 等）。
      Send a single action step to the running Recorder.
      示例 / Example:
        python3 rpa_manager.py record-step '{"action":"snapshot"}'
        python3 rpa_manager.py record-step '{"action":"goto","url":"https://example.com"}'

  record-status
      查看当前 Recorder 运行状态与已录步骤数。
      Show running status and recorded step count.

  record-end [--abort]
      结束录制并编译生成 rpa/<task>.py；加 --abort 则放弃。
      End recording and compile script; --abort discards the session.

  deps-check <A-N>
      按能力码检查 Python / Playwright / openpyxl / python-docx 是否就绪。
      Check dependencies by capability code (A–N maps to feature sets).

  deps-install <A-N>
      安装缺失依赖（与 Playwright 同一 python3）。
      Install missing deps using the same python3 as Playwright.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【计划管理 / Plan Management（防 LLM 超时 / Prevents LLM timeout）】

  plan-set '<json-array>'
      设置多步执行计划，LLM 每轮只推进一步。
      Set a multi-step plan; LLM advances one step per turn.
      示例 / Example:
        python3 rpa_manager.py plan-set '["打开携程首页","搜索酒店","截图结果"]'

  plan-next      推进到下一步 / Advance to next step.
  plan-status    查看计划进度 / Show plan progress.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【通用命令 / General Commands】

  run <task_name>    运行已录制的任务脚本 / Run a saved task script.
  list               列出所有已保存的任务 / List all saved tasks.
  env-check          检查 Python / Playwright 环境 / Check Python + Playwright environment.
  help               显示本帮助 / Show this help.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【Legacy 模式 / Legacy Mode（兼容保留 / kept for compatibility）】
  init / add --proof <file> '<json>' / generate / status / reset

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【对话指令（发给 AI / Chat commands sent to the AI assistant）】
  #rpa / #自动化机器人 / #RPA     → 开始新录制任务 / Start a new recording task
  #rpa-login <url>              → 保存登录 Cookie（分步：login-start + 手动登录 + login-done）
  #rpa-login-done               → 通知导出 Cookie / Signal cookie export
  #rpa-autologin <domain|url>   → 录制/回放时注入已保存的 Cookie / Inject saved cookies
  #rpa-autologin-list           → 查看已保存的登录会话 / View saved login sessions
  #rpa-list                     → 查看已录制的任务 / List recorded tasks
  #rpa-run:<task>               → 回放指定任务 / Replay a specific task
  #rpa-help                     → 显示本指令帮助 / Show this command reference
""")
    return 0


def cmd_deps_check(capability: str) -> int:
    """Exit 0 if Python + Playwright/Chromium + profile office libs are OK."""
    return envcheck.print_deps_capability_report(capability)


def cmd_deps_install(capability: str) -> int:
    """pip install openpyxl/python-docx as needed; ensure Playwright Chromium."""
    return envcheck.ensure_capability_deps(capability, auto_chromium=True)


def cmd_record_start(
    task_name: str,
    profile: Optional[str] = None,
    autologin: Optional[str] = None,
) -> int:
    """Launch recorder server and wait for ready.
    For browser capabilities (A/D/E/G) a headed Chromium is opened; for file-only capabilities
    (B/C/F/N) no browser is started.
    autologin: domain or URL; if provided, looks up saved cookies and injects them into the recorder context."""
    _needs_browser = True
    if profile:
        _cap = envcheck.normalize_capability_letter(profile)
        if _cap and _cap in envcheck.CAPABILITY_PROFILES:
            _needs_browser = envcheck.CAPABILITY_PROFILES[_cap]["needs_browser"]

    if _needs_browser:
        if envcheck.ensure_playwright_chromium(auto_install=True) != 0:
            return 1

    # Resolve autologin domain → cookies file path
    # 解析 autologin 域名 → Cookie 文件路径（若用户传入的是 URL，提取 hostname）
    resolved_cookies_file = ""
    if autologin:
        domain = _domain_from_url(autologin) if autologin.startswith("http") else autologin.strip()
        cookies_file_path = _cookies_path_for_domain(domain)
        if cookies_file_path.exists():
            resolved_cookies_file = str(cookies_file_path)
            print(f"🍪 已找到 {domain} 的登录 Cookie，将在浏览器启动后自动注入。")
            print(f"   Cookie 文件：{resolved_cookies_file}")
        else:
            print(f"⚠️  未找到 {domain} 的登录会话文件：{cookies_file_path}", file=sys.stderr)
            print(f"   请先执行：python3 rpa_manager.py login-start <登录页URL>", file=sys.stderr)
            return 1

    # Clean up any stale session / 清理残留会话
    if SESSION_REC_DIR.exists():
        shutil.rmtree(SESSION_REC_DIR)
    SESSION_REC_DIR.mkdir(parents=True)

    # Write task info so recorder_server.py can read it
    # 将任务信息写入 task.json，recorder_server.py 启动时读取
    task_payload: dict = {"task": task_name}
    if profile:
        cap = envcheck.normalize_capability_letter(profile)
        if cap is None:
            print(
                f"❌ 无效能力码 {profile!r}（须为 A–G 或 N，与 ONBOARDING 一致）",
                file=sys.stderr,
            )
            return 1
        p = envcheck.CAPABILITY_PROFILES[cap]
        task_payload["capability"] = cap
        task_payload["needs_excel"] = p["needs_excel"]
        task_payload["needs_word"] = p["needs_word"]
        task_payload["needs_browser"] = p["needs_browser"]
    if resolved_cookies_file:
        # cookies_file 字段由 recorder_server.py 在 new_context 之后读取并注入
        # recorder_server.py reads this after new_context() to call add_cookies()
        task_payload["cookies_file"] = resolved_cookies_file
    (SESSION_REC_DIR / "task.json").write_text(
        json.dumps(task_payload, ensure_ascii=False, indent=2)
    )

    server_script = SKILL_DIR / "recorder_server.py"
    if not server_script.exists():
        print(f"❌ recorder_server.py 不存在：{server_script}", file=sys.stderr)
        return 1

    log_path = SESSION_REC_DIR / "server.log"
    with open(log_path, "w") as log:
        proc = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=log,
            stderr=log,
            start_new_session=True,
        )

    print(f"⏳ 正在启动 Recorder（PID: {proc.pid}），等待浏览器窗口就绪…")

    # Poll for ready signal (up to 30 s)
    ready_path = SESSION_REC_DIR / "ready"
    for _ in range(150):  # 150 × 0.2 s = 30 s
        if ready_path.exists():
            break
        time.sleep(0.2)
    else:
        print("❌ Recorder 启动超时（30s）。", file=sys.stderr)
        print(f"   详细日志：{log_path}", file=sys.stderr)
        return 1

    if _needs_browser:
        print(f"✅ Recorder 已就绪！浏览器窗口已打开，请注视屏幕。")
    else:
        print(f"✅ Recorder 已就绪！（无浏览器模式，仅支持 Excel / Word / API 等文件操作）")
    print(f"   任务：「{task_name}」")
    if resolved_cookies_file:
        print(f"   🍪 已注入登录 Cookie（{resolved_cookies_file}）")
    print(f"   截图保存至：{SESSION_REC_DIR / 'screenshots'}")
    _append_playwright_cmd_log(
        {
            "type": "session",
            "event": "start",
            "ts": datetime.now().isoformat(),
            "task": task_name,
            "log_path": str(PLAYWRIGHT_CMD_LOG),
        }
    )
    print(f"   📝 Playwright 指令日志（每步追加）：{PLAYWRIGHT_CMD_LOG}")
    print()
    if _needs_browser:
        print("下一步建议：先发一条 snapshot 了解页面元素，再执行 goto/fill/select_option/click 等操作。")
        print('示例：python3 rpa_manager.py record-step \'{"action":"snapshot"}\'')
    else:
        print("下一步建议：直接发送 excel_write / word_write / api_call / python_snippet 等文件操作步骤。")
        print('示例：python3 rpa_manager.py record-step \'{"action":"excel_write","path":"report.xlsx","sheet":"Sheet1","value":[["A","B"]]}\'')
    return 0


def cmd_record_step(step_json: Optional[str], from_file: Optional[str] = None) -> int:
    """Send one step command to the recorder server and print result."""
    if from_file:
        fp = Path(from_file).expanduser().resolve()
        if not fp.exists():
            print(f"❌ --from-file 路径不存在：{fp}", file=sys.stderr)
            return 1
        try:
            raw = fp.read_text(encoding="utf-8")
        except OSError as e:
            print(f"❌ 无法读取 --from-file：{e}", file=sys.stderr)
            return 1
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            fixed = _fix_json_literal_newlines(raw)
            try:
                data = json.loads(fixed)
                print("⚠️  --from-file JSON 已自动修复（code 字段含字面换行）", file=sys.stderr)
            except json.JSONDecodeError as e2:
                print(f"❌ --from-file 文件内容不是有效 JSON：{e2}", file=sys.stderr)
                return 1
    elif step_json:
        try:
            data = json.loads(step_json)
        except json.JSONDecodeError:
            fixed = _fix_json_literal_newlines(step_json)
            try:
                data = json.loads(fixed)
            except json.JSONDecodeError as e2:
                print(f"❌ 无效 JSON：{e2}", file=sys.stderr)
                return 1
    else:
        print("❌ 需提供 JSON 参数或 --from-file 文件路径。/ Provide JSON argument or --from-file path.", file=sys.stderr)
        return 1

    pid_path = SESSION_REC_DIR / "server.pid"
    if not pid_path.exists():
        print("❌ Recorder 未在运行。请先执行 record-start <task>。", file=sys.stderr)
        return 1

    cmd_path   = SESSION_REC_DIR / "cmd.json"
    new_seq    = _rec_current_seq() + 1
    data["seq"] = new_seq
    cmd_path.write_text(json.dumps(data, ensure_ascii=False))

    # Poll for result（视觉步骤单独延长等待，避免 VL API 慢导致 120s 误报超时）
    wait_s = (
        RECORD_STEP_RESULT_WAIT_VISION_S
        if data.get("action") == "extract_by_vision"
        else RECORD_STEP_RESULT_WAIT_S
    )
    max_polls = int(wait_s / RECORD_STEP_POLL_INTERVAL_S)
    result_path = SESSION_REC_DIR / f"result_{new_seq}.json"
    for _ in range(max_polls):
        if result_path.exists():
            break
        time.sleep(RECORD_STEP_POLL_INTERVAL_S)
    else:
        print(
            f"❌ 等待结果超时（{wait_s}s）。action={data.get('action')}",
            file=sys.stderr,
        )
        _append_playwright_cmd_log(
            {
                "type": "step",
                "ts": datetime.now().isoformat(),
                "seq": new_seq,
                "command": data,
                "success": False,
                "error": f"等待结果超时（{wait_s}s），未收到 result_{new_seq}.json",
                "code_block": None,
            }
        )
        return 1

    result = json.loads(result_path.read_text())
    action = data.get("action", "")

    if not result.get("success"):
        print(f"❌ 操作失败：{result.get('error', '未知错误')}")
        if result.get("screenshot"):
            print(f"   截图（供调试）：{result['screenshot']}")
        # Still print snapshot so LLM can retry with correct selector
    else:
        icon = "🔍" if action == "snapshot" else "✅"
        print(f"{icon} [{action}] 执行成功")

    if result.get("screenshot"):
        print(f"   📸 截图：{result['screenshot']}")
    if result.get("url"):
        print(f"   🔗 URL：{result['url']}")

    snap = result.get("snapshot", [])
    if snap:
        print(f"   📋 页面可交互元素（{len(snap)} 个，可用作下一步 target）：")
        for el in snap[:30]:
            sel_s  = el.get("sel") or f"[tag={el.get('tag')}，无选择器]"
            ph_s   = f" [placeholder={el['ph']}]" if el.get("ph") else ""
            txt_s  = f"  「{el['text'][:45]}」" if el.get("text") else ""
            print(f"     {sel_s}{ph_s}{txt_s}")

    sections = result.get("sections", [])
    if sections:
        print(f"   🗂️  页面内容区块（可用于范围限定选择器，如 [data-testid=X] h3）：")
        for sec in sections[:10]:
            h = f"  ← 含标题「{sec['heading']}」" if sec.get("heading") else ""
            print(f"     {sec['sel']}{h}")

    # dom_inspect: show child element structure
    inspect_children = result.get("_inspect_children", [])
    if inspect_children:
        print(f"\n   🔬 dom_inspect 子元素结构（共 {len(inspect_children)} 个）：")
        print(f"   {'tag':<10} {'选择器':<40} {'文本预览'}")
        print(f"   {'-'*8:<10} {'-'*38:<40} {'-'*20}")
        for c in inspect_children[:30]:
            sel_h = (
                f"#{c['id']}" if c.get("id")
                else f"[data-testid=\"{c['testid']}\"]" if c.get("testid")
                else f"[aria-label=\"{c['aria']}\"]" if c.get("aria")
                else f".{c['cls'].split()[0]}" if c.get("cls")
                else c.get("tag", "?")
            )
            print(f"   {c.get('tag','?'):<10} {sel_h:<40} 「{(c.get('text') or '')[:35]}」")
        print()
        print("   💡 提示：找到含新闻标题的 tag/sel，组合成 'a h3'、'li .clamp2' 等选择器")

    _append_playwright_cmd_log(
        {
            "type": "step",
            "ts": datetime.now().isoformat(),
            "seq": new_seq,
            "command": data,
            "success": result.get("success"),
            "error": result.get("error"),
            "code_block": result.get("code_block"),
            "url": result.get("url"),
            "screenshot": result.get("screenshot"),
        }
    )

    return 0 if result.get("success") else 1


def cmd_record_status() -> int:
    """Show recorder session status."""
    if not SESSION_REC_DIR.exists():
        print("ℹ️  无活跃 Recorder 会话。")
        return 0

    task_name = "未知"
    task_path = SESSION_REC_DIR / "task.json"
    if task_path.exists():
        try:
            task_name = json.loads(task_path.read_text()).get("task", "未知")
        except Exception:
            pass

    pid_path   = SESSION_REC_DIR / "server.pid"
    is_running = pid_path.exists()
    print(f"{'🟢 运行中' if is_running else '🔴 未运行'}  任务：「{task_name}」")

    log_path = SESSION_REC_DIR / "script_log.py"
    if log_path.exists():
        content     = log_path.read_text()
        step_count  = content.count("# ── 步骤")
        print(f"📋 已录制步骤：{step_count}")

    shots_dir = SESSION_REC_DIR / "screenshots"
    if shots_dir.exists():
        shots = list(shots_dir.glob("*.png"))
        print(f"📸 截图数量：{len(shots)}")
        if shots:
            latest = max(shots, key=lambda p: p.stat().st_mtime)
            print(f"   最新截图：{latest.name}")

    if PLAYWRIGHT_CMD_LOG.exists():
        with open(PLAYWRIGHT_CMD_LOG, encoding="utf-8") as lf:
            n = sum(1 for _ in lf)
        print(f"📝 Playwright 指令日志：{PLAYWRIGHT_CMD_LOG}（约 {n} 行）")

    return 0


def cmd_record_end(abort: bool = False) -> int:
    """Shutdown recorder server and compile RPA script (or abort)."""
    if abort:
        if (SESSION_REC_DIR / "server.pid").exists():
            _rec_send_shutdown()
        if SESSION_REC_DIR.exists():
            shutil.rmtree(SESSION_REC_DIR)
        print("🗑️  录制已放弃，Recorder 已关闭。")
        return 0

    pid_path  = SESSION_REC_DIR / "server.pid"
    done_path = SESSION_REC_DIR / "done"
    task_path = SESSION_REC_DIR / "task.json"

    if not pid_path.exists() and not done_path.exists():
        print("❌ Recorder 未在运行。请先执行 record-start <task>。", file=sys.stderr)
        return 1

    if not task_path.exists():
        print("❌ 找不到任务信息（task.json）。", file=sys.stderr)
        return 1

    task_name = json.loads(task_path.read_text()).get("task", "task")

    # Send shutdown if server still running
    if pid_path.exists():
        _rec_send_shutdown()

    # Wait for done marker (up to 15 s)
    for _ in range(75):
        if done_path.exists():
            break
        time.sleep(0.2)

    log_path = SESSION_REC_DIR / "script_log.py"
    if not log_path.exists():
        print("❌ Recorder 未生成脚本（script_log.py 不存在）。", file=sys.stderr)
        return 1

    script      = log_path.read_text(encoding="utf-8")
    step_count  = script.count("# ── 步骤")

    if step_count == 0:
        print("⚠️  警告：录制到 0 个步骤，生成空壳脚本。", file=sys.stderr)

    filename    = _slugify(task_name)
    RPA_DIR.mkdir(exist_ok=True)
    output_path = RPA_DIR / f"{filename}.py"
    output_path.write_text(script, encoding="utf-8")

    archive_log = RPA_DIR / f"{filename}_playwright_commands.jsonl"
    if PLAYWRIGHT_CMD_LOG.exists():
        _append_playwright_cmd_log(
            {
                "type": "session",
                "event": "end",
                "ts": datetime.now().isoformat(),
                "task": task_name,
                "steps_recorded": step_count,
                "script_path": str(output_path),
                "archived_log": str(archive_log),
            }
        )
        shutil.copy2(PLAYWRIGHT_CMD_LOG, archive_log)

    registry = load_registry()
    registry[task_name] = f"{filename}.py"
    save_registry(registry)

    # ── 若录制了 extract_by_vision 步骤，自动生成 vision_setup.md ──────────────
    vision_doc_path: "Path | None" = None
    vision_steps_file = SESSION_REC_DIR / "vision_steps.json"
    if vision_steps_file.exists():
        try:
            vs_data = json.loads(vision_steps_file.read_text(encoding="utf-8"))
            vision_doc_path = _generate_vision_setup_doc(
                task_name=vs_data.get("task", task_name),
                model_key=vs_data.get("model_key", "qwen"),
                model=vs_data.get("model", "qwen3-vl-plus"),
                steps=vs_data.get("steps", []),
                script_path=output_path,
            )
        except Exception as e:
            print(f"⚠️  生成 vision_setup.md 失败（非致命）：{e}", file=sys.stderr)

    print(f"✨ RPA 脚本生成成功！")
    print(f"📄 文件：{output_path}")
    print(f"📋 共录制 {step_count} 个步骤")
    if vision_doc_path:
        print(f"👁️  视觉识别文档：{vision_doc_path}")
    if archive_log.exists():
        print(f"📝 指令日志（副本）：{archive_log}")
    print(f"📸 截图目录：{SESSION_REC_DIR / 'screenshots'}")
    print(f"\n运行方式：python3 {output_path}")
    print(f'下次直接说"运行：{task_name}"即可重放。')
    return 0


def _generate_vision_setup_doc(
    task_name: str,
    model_key: str,
    model: str,
    steps: list[dict],
    script_path: "Path",
) -> "Path":
    """生成视觉识别使用说明文档，与 RPA 脚本放在同一目录。"""
    from datetime import datetime as _dt

    _VISION_META = {
        "qwen": {
            "label":   "Qwen3-VL-Plus（阿里云百炼）",
            "key_env": "DASHSCOPE_API_KEY",
            "key_url": "https://bailian.console.aliyun.com → API Key 管理",
            "price":   "约 ¥0.002/次截图",
        },
        "gemini": {
            "label":   "Gemini 3 Pro（Google AI Studio）",
            "key_env": "GOOGLE_AI_KEY",
            "key_url": "https://aistudio.google.com/app/apikey",
            "price":   "约 ¥0.01/次截图",
        },
    }
    meta = _VISION_META.get(model_key, _VISION_META["qwen"])

    step_rows = ""
    for s in steps:
        preview_str = "、".join(
            f'**{k}**：{v}' for k, v in s.get("preview", {}).items() if v
        ) or "（无内容）"
        step_rows += (
            f"| 步骤 {s['step']} | {', '.join(s.get('fields', []))} "
            f"| {s.get('file','')} | {preview_str} |\n"
        )

    vision_count = len(steps)
    config_line_hint = script_path.name

    doc = f"""\
# 视觉识别配置说明 — {task_name}

> 本文档由 OpenClaw RPA 录制结束时自动生成 · {_dt.now().strftime('%Y-%m-%d %H:%M')}

## 使用的视觉模型

| 项目 | 内容 |
|---|---|
| **模型名称** | {meta['label']} |
| **Model ID** | `{model}` |
| **API Key 环境变量** | `{meta['key_env']}` |
| **获取地址** | {meta['key_url']} |

## API Key 管理

脚本的 `CONFIG["vision_api_key"]` 已在录制时自动写入，**直接运行无需额外配置**。

若 API Key 失效，有两种更新方式：

**方式 A：更新脚本（推荐）**
```python
# 编辑 {config_line_hint}，找到 CONFIG 字典并修改：
"vision_api_key":  "你的新 Key",
```

**方式 B：重新录制**
```
说「运行：{task_name}」重录，录制时重新粘贴新 Key 即可。
```

## 录制时的视觉提取效果

| 步骤 | 提取字段 | 输出文件 | 录制时识别结果 |
|---|---|---|---|
{step_rows}
> ✅ 以上为录制时**真实调用** {meta['label']} API 的提取结果。

## 费用估算

| 项目 | 数量 | 单价 | 小计 |
|---|---|---|---|
| 视觉 API 调用 | 每次运行 {vision_count} 次 | {meta['price']} | 约 ¥{0.002 * vision_count:.3f}–¥{0.01 * vision_count:.3f} |
| 每月 30 次运行 | {vision_count * 30} 次 | — | 约 ¥{0.002 * vision_count * 30:.2f}–¥{0.01 * vision_count * 30:.2f} |

## 常见问题

**Q：截图内容不对，提取字段为空**  
A：在录制时加 `"crop_selector": "main"` 将截图范围限定在页面主体区域。

**Q：想换成 Gemini 3 Pro**  
A：重新录制，在视觉模型选择时输入 `B`，粘贴 Google AI Studio Key 即可。

**Q：API Key 不想写进脚本文件**  
A：将 Key 设为环境变量 `{meta['key_env']}`，脚本启动时会自动读取（需手动修改脚本读取逻辑）。
"""

    doc_path = script_path.parent / f"{script_path.stem}_vision_setup.md"
    doc_path.write_text(doc, encoding="utf-8")
    return doc_path


# ── Playwright 脚本生成 / Playwright script generation ──────────────────────

def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    text = re.sub(r"^_+|_+$", "", text)
    return text or "task"


def _is_css_selector(s: str) -> bool:
    """Return True if the string looks like a CSS selector rather than a human label."""
    return bool(s) and (
        s.startswith(("#", ".", "[", "input", "button", "a", "select", "textarea"))
        or "=" in s or ">" in s or ":" in s
    )


def _build_step(action: dict) -> str:
    step = action["step"]
    category = action.get("category", "Web")
    act = action.get("action", "")
    target = action.get("target", "")
    value = action.get("value", "")
    context = action.get("context", f"步骤 {step}")

    indent = "            "
    lines = [f"{indent}# 步骤 {step}：{context}", f"{indent}try:"]

    body = []
    if category == "Web":
        if act == "navigate":
            # domcontentloaded fires after HTML is parsed — reliable for heavy SPAs.
            # "load" waits for all subresources (images/ads) and often times out.
            body += [
                f'await page.goto({repr(target)}, wait_until="domcontentloaded")',
            ]
        elif act == "click":
            if _is_css_selector(target):
                body += [f'await page.locator({repr(target)}).first.click()']
            else:
                body += [f'await page.get_by_text({repr(target)}).first.click()']
        elif act == "fill":
            # If target looks like a CSS selector, use locator(); otherwise try
            # multiple semantic strategies so the script survives site redesigns.
            if _is_css_selector(target):
                body += [
                    f'await page.locator({repr(target)}).first.fill({repr(value)})',
                    'await page.keyboard.press("Enter")',
                    'await page.wait_for_load_state("domcontentloaded")',
                ]
            else:
                # Fallback: human label / placeholder text — try known Yahoo + generic
                # search selectors in order (never use input[name=placeholder_text]).
                body += [
                    f'_fill_value = {repr(value)}',
                    '_fill_done = False',
                    f'_labels = {repr(target)}',
                    'for _sel in (',
                    '    "#ybar-sbq",',
                    '    \'input[name="p"]\',',
                    '    \'input[aria-label*="Search"]\',',
                    '    \'input[type="search"]\',',
                    '):',
                    '    try:',
                    '        _loc = page.locator(_sel).first',
                    '        await _loc.wait_for(state="visible", timeout=8_000)',
                    '        await _loc.fill(_fill_value)',
                    '        _fill_done = True',
                    '        break',
                    '    except Exception:',
                    '        continue',
                    'if not _fill_done:',
                    '    try:',
                    '        await page.get_by_placeholder(_labels).first.fill(_fill_value)',
                    '        _fill_done = True',
                    '    except Exception:',
                    '        pass',
                    'if not _fill_done:',
                    '    try:',
                    '        await page.get_by_label(_labels).first.fill(_fill_value)',
                    '        _fill_done = True',
                    '    except Exception:',
                    '        pass',
                    'if not _fill_done:',
                    '    raise RuntimeError('
                    '"无法定位搜索框：请重新录制并在 target 中填写真实 CSS 选择器（如 input#ybar-sbq）")',
                    'await page.keyboard.press("Enter")',
                    'await page.wait_for_load_state("domcontentloaded")',
                ]
        elif act == "select_option":
            body += [
                f'await page.locator({repr(target)}).first.select_option({repr(value)})',
                'await page.wait_for_load_state("domcontentloaded")',
                'await page.wait_for_timeout(800)',
            ]
        elif act == "select":
            body += [f'await page.get_by_label({repr(target)}).select_option({repr(value)})']
        elif act == "screenshot":
            body += [
                f'await page.screenshot(path="step_{step}_capture.png", full_page=True)',
                f'print("截图已保存：step_{step}_capture.png")',
            ]
        else:
            body += [f'# TODO: 实现 {act} 操作，目标：{target}', 'pass']

    elif category == "File":
        if act == "write":
            fname = Path(target).name if target else "output.txt"
            body += [
                f'out = CONFIG["output_dir"] / {repr(fname)}',
                f'out.write_text({repr(value)}, encoding="utf-8")',
                f'print(f"已写入：{{out}}")',
            ]
        elif act == "read":
            body += [
                f'content = Path({repr(target)}).read_text(encoding="utf-8")',
                f'print(f"已读取：{{len(content)}} 字符")',
            ]
        else:
            body += [f'# TODO: 实现文件 {act} 操作', 'pass']

    else:
        body += [f'# TODO: 实现 {category}/{act}', 'pass']

    for b in body:
        lines.append(f"{indent}    {b}")

    lines += [
        f"{indent}except Exception:",
        f'{indent}    await page.screenshot(path="step_{step}_error.png")',
        f"{indent}    raise",
    ]
    return "\n".join(lines)


def _build_playwright_script(task_name: str, buffer: list) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    steps = "\n\n".join(_build_step(a) for a in buffer)

    return f'''# pip install playwright && playwright install chromium
# 任务：{task_name}
# 生成时间：{ts}
# 由 OpenClaw RPA 引擎自动生成 — 可脱离 OpenClaw 独立运行

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ── 配置区（修改此处即可适配不同环境）──────────────────────
CONFIG = {{
    "output_dir": Path.home() / "Desktop",  # 文件输出目录
    "headless": False,                       # True = 无头模式
    "timeout": 60_000,                       # 超时毫秒
    "slow_mo": 300,                          # 操作间隔 ms，模拟人类速度
}}

# ── 反爬虫：伪造真实浏览器特征 ────────────────────────────
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


# ── 主流程 ────────────────────────────────────────────────
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
            raise RuntimeError(f"操作超时，截图已保存: {{e}}") from e
        except Exception:
            await page.screenshot(path="error_unexpected.png")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run())
'''


# ── 入口 / Entry point ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw RPA Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── 帮助 / Help ──
    sub.add_parser("help", help="显示完整指令参考（中英双语） / Show full bilingual command reference")

    # ── 登录会话管理 / Login session management ──
    p_ls = sub.add_parser("login-start", help="打开浏览器到指定登录页，用户手动登录后执行 login-done")
    p_ls.add_argument("url", help="目标登录页 URL，如 https://passport.ctrip.com/user/login")

    sub.add_parser("login-done", help="导出当前浏览器 Cookie 并关闭（须先执行 login-start）")
    sub.add_parser("login-list", help="列出所有已保存的登录会话及参考过期状态")

    # ── Recorder 模式 ──
    p_rs = sub.add_parser("record-start",  help="启动 headed Playwright Recorder（有界面真实录制）")
    p_rs.add_argument("task_name", help="任务名称")
    p_rs.add_argument(
        "--profile",
        metavar="A-N",
        default=None,
        help="能力码（A–G 或 N），写入 recorder_session/task.json，供 Office 增补与文档化",
    )
    p_rs.add_argument(
        "--autologin",
        metavar="DOMAIN_OR_URL",
        default=None,
        help="自动注入已保存的登录 Cookie（域名或URL，须先执行 login-start + login-done）/ Auto-inject saved login cookies by domain or URL",
    )

    p_dc = sub.add_parser(
        "deps-check",
        help="按能力码检查依赖（须与运行 rpa_manager / Playwright 为同一 python3）",
    )
    p_dc.add_argument("capability", help="单字母：A–G 或 N（见 SKILL 中 ONBOARDING）")

    p_di = sub.add_parser(
        "deps-install",
        help="按能力码安装缺失依赖（openpyxl/python-docx + Playwright Chromium）",
    )
    p_di.add_argument("capability", help="单字母：A–G 或 N")

    p_rp = sub.add_parser("record-step",   help="向 Recorder 发送单步操作（含 select_option）")
    p_rp.add_argument(
        "step_json",
        nargs="?",
        default=None,
        help='操作 JSON 字符串，如 \'{"action":"snapshot"}\'（与 --from-file 二选一）',
    )
    p_rp.add_argument(
        "--from-file",
        metavar="PATH",
        default=None,
        dest="from_file",
        help="从文件读取操作 JSON（适用于 exec 工具不允许复杂 shell 参数的环境）",
    )

    sub.add_parser("record-status", help="查看 Recorder 运行状态与已录步骤")

    p_re = sub.add_parser("record-end",    help="结束录制，生成并保存 RPA 脚本")
    p_re.add_argument("--abort", action="store_true", help="放弃录制，清理会话")

    # ── 计划管理（多步指令防超时）──
    p_ps = sub.add_parser("plan-set",    help="设置多步执行计划（防 LLM 超时）")
    p_ps.add_argument("steps_json", help='步骤 JSON 数组，如 \'["步骤1描述", "步骤2描述"]\'')

    sub.add_parser("plan-next",   help="推进计划到下一步")
    sub.add_parser("plan-status", help="查看计划当前进度")

    # ── Legacy 模式 ──
    p_init = sub.add_parser("init",     help="[legacy] 初始化录制会话")
    p_init.add_argument("task_name", help="任务名称")

    p_add = sub.add_parser("add",       help="[legacy] 追加 Action 到 Buffer（须带 --proof）")
    p_add.add_argument("--proof", required=True, metavar="PATH",
                       help="本步实操成功后的证明文件（截图 PNG/JPG 或输出文件），须 ≥64 字节")
    p_add.add_argument("action_json", help='Action JSON，如 \'{"category":"Web","action":"navigate",...}\'')

    sub.add_parser("status",   help="[legacy] 查看当前录制状态与 Buffer")
    sub.add_parser("generate", help="[legacy] 从 Buffer 生成 Playwright 脚本")

    # ── 通用命令 ──
    p_run = sub.add_parser("run",  help="运行已保存的任务")
    p_run.add_argument("task_name", help="任务名称")

    sub.add_parser("list",  help="列出所有已录制任务")
    sub.add_parser("reset", help="[legacy] 清空 Buffer 并放弃录制")

    sub.add_parser(
        "env-check",
        help="检查 Python / playwright 包 / Chromium 是否可用（录制与运行前自检）",
    )

    args = parser.parse_args()
    dispatch = {
        # 帮助 / Help
        "help":          cmd_help,
        # 登录会话管理 / Login session management
        "login-start":   lambda: cmd_login_start(args.url),
        "login-done":    cmd_login_done,
        "login-list":    cmd_login_list,
        # Recorder 模式
        "record-start":  lambda: cmd_record_start(
            args.task_name,
            getattr(args, "profile", None),
            getattr(args, "autologin", None),
        ),
        "deps-check":    lambda: cmd_deps_check(args.capability),
        "deps-install":  lambda: cmd_deps_install(args.capability),
        "record-step":   lambda: cmd_record_step(
            getattr(args, "step_json", None),
            getattr(args, "from_file", None),
        ),
        "record-status": cmd_record_status,
        "record-end":    lambda: cmd_record_end(getattr(args, "abort", False)),
        # 计划管理
        "plan-set":      lambda: cmd_plan_set(args.steps_json),
        "plan-next":     cmd_plan_next,
        "plan-status":   cmd_plan_status,
        # Legacy 模式
        "init":          lambda: cmd_init(args.task_name),
        "add":           lambda: cmd_add(args.action_json, args.proof),
        "status":        cmd_status,
        "generate":      cmd_generate,
        # 通用
        "run":           lambda: cmd_run(args.task_name),
        "list":          cmd_list,
        "reset":         cmd_reset,
        "env-check":     lambda: envcheck.print_report(),
    }

    if args.command in dispatch:
        sys.exit(dispatch[args.command]())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
