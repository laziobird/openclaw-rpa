---
name: openclaw-rpa
description: Record browser & local-file actions once; replay runs without the LLM—save $ vs AI browsing, faster, no hallucinations. github.com/laziobird/openclaw-rpa
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

**GitHub:** **[https://github.com/laziobird/openclaw-rpa](https://github.com/laziobird/openclaw-rpa)** — source, README, install, sample scripts under `rpa/`.

**Example flows** (ideas; record once, replay many times—**follow each site’s terms and local law**): **e‑commerce login & shopping**; **Yahoo Finance** stock quotes / news headlines; movie sites **reviews & ratings** in one automated run.

## What this skill does

**openclaw-rpa** turns repeatable **web** and optional **local file** work into a **Playwright Python** script by **recording** what actually happens in a real browser (plus file steps when needed). **Replay** runs that script directly—**not** the model clicking every time—so runs are **deterministic**, **cheaper**, and **less error-prone** than ad-hoc “automate this now” prompts.

**Why this matters**

1. **Saves compute and money** — Having a **large model** drive the browser on **every** run can cost **roughly single-digit to tens of US dollars** per heavy session (tokens, tools, long context). After you **record once**, repeat work **does not call the model**—replay is **much faster** and **near-zero** LLM cost for those steps.
2. **Verify once, run the same way every time** — During recording you **confirm** the flow works; later, replay **executes the saved steps** deterministically. You avoid asking the AI to “do it again” on every run, which **hurts consistency** and **raises hallucination risk**.

## When to use

| You want to… | Send |
|----------------|------|
| **Start recording** a new flow | `#automation robot`, `#RPA`, `#rpa`, or mention **Playwright automation** |
| **See saved tasks** you can run | `#rpa-list` |
| **Run a saved task** (e.g. new chat) | `#rpa-run:{task name}` |
| **Run in this chat** | `run:{task name}` (`zh-CN`: `#运行:{任务名}`) |

## Quick start (after install)

```text
#rpa-list
#rpa-run:your-task-name
```

Full protocol, state machine, and `record-step` JSON live in the locale file below.

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

- **SKILL.md** (this file): short router + **when to use** + **quick start** for listings like [ClawHub](https://clawhub.ai/).
- **SKILL.zh-CN.md** / **SKILL.en-US.md**: full **onboarding**, **recording**, **RUN/LIST**, and anti-timeout rules.

## Relative paths

When the loaded file references `playwright-templates.md`, `synthesis-prompt.md`, or `rpa_manager.py`, resolve paths **relative to this skill directory** (parent of `SKILL.md`).
