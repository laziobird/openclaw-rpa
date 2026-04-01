---
name: openclaw-rpa
description: >
  OpenClaw RPA: AI-assisted recording of browser and local-file actions into a Playwright Python script. Replay without the LLM each run—saves compute and keeps steps deterministic (vs. hallucinated ad-hoc automation). Triggers: "#automation robot", "#RPA", "#rpa", "#rpa-list", "Playwright automation"; list recorded tasks: "#rpa-list"; run a saved script: "#rpa-run:{task}" or "run:{task}".
  中文触发：「#自动化机器人」「#RPA」「#rpa」「#rpa-list」；查看可用任务「#rpa-list」，执行已录制脚本：「#rpa-run:任务名」或「#运行:任务名」。
  Locale: read config.json (or config.example.json if config.json is missing) → SKILL.zh-CN.md or SKILL.en-US.md.
metadata:
  openclaw:
    emoji: "🤖"
    os: ["darwin", "linux"]
    localeConfig: "config.json"
    instructionFiles:
      zh-CN: "SKILL.zh-CN.md"
      en-US: "SKILL.en-US.md"
---

# openclaw-rpa — **Locale router (read this first)**

## Mandatory: load the correct instruction file

1. **Read** `config.json` in this skill directory. If it does not exist, read **`config.example.json`** (same shape; default `locale` is **`en-US`**).
2. Read the `"locale"` field. Allowed values: **`zh-CN`** and **`en-US`** (repository default in **`config.example.json`**: **`en-US`**).
3. **Immediately use the Read tool** to load the **full** skill body:
   - `zh-CN` → **`SKILL.zh-CN.md`**
   - `en-US` → **`SKILL.en-US.md`**

4. **Follow only that file** for state machine, triggers, `record-step` JSON, onboarding text, and user-facing replies.

5. **Reply to the user in the active locale’s language:**
   - `zh-CN` → Simplified Chinese for agent messages (user may still type English).
   - `en-US` → English for agent messages (user may still type Chinese).

## Changing language

- Copy `config.example.json` → `config.json` if needed (`python3 scripts/bootstrap_config.py`), then edit `"locale"`, **or**
- Run: `python3 scripts/set_locale.py en-US` / `python3 scripts/set_locale.py zh-CN` (creates `config.json` from the example when missing).

After a locale change, the agent should **re-read** the matching `SKILL.*.md` in a new turn or session. See **README.md** in this directory for the full workflow.

## ClawHub / discovery

- This file is intentionally short; **discoverability** keywords appear in YAML `description` (bilingual).
- Full behaviour lives in **`SKILL.zh-CN.md`** and **`SKILL.en-US.md`**.

## Relative paths

When the loaded file references `playwright-templates.md`, `synthesis-prompt.md`, or `rpa_manager.py`, resolve paths **relative to this skill directory** (parent of `SKILL.md`).
