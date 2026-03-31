# openclaw-rpa

English | **[中文](README.zh-CN.md)**

> With **AI assistance**, record **typical website** and **local file** workflows into a **repeatable Playwright Python** script. **Replay without the LLM on every run**—saves compute and keeps steps deterministic (vs. ad-hoc model calls).

| | |
|:---|:---|
| **Needs** | Python **3.8+**, network for `pip` / Playwright browsers |
| **License** | [Apache 2.0](LICENSE) |

---

## Quick install (OpenClaw)

Put the skill here: **`~/.openclaw/workspace/skills/openclaw-rpa`**

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa
cd ~/.openclaw/workspace/skills/openclaw-rpa

chmod +x scripts/install.sh && ./scripts/install.sh
python3 scripts/bootstrap_config.py
python3 scripts/set_locale.py zh-CN    # or: en-US

python3 rpa_manager.py env-check
```

**SSH clone:** `git@github.com:laziobird/openclaw-rpa.git`

After install, **start a new OpenClaw chat** (or reload skills) so the agent reads **`SKILL.md`**. Triggers and keywords: **`SKILL.md`** (e.g. `#RPA`, “automation robot”).

---

## Demo video

**Scenario:** Sauce Demo ([saucedemo.com](https://www.saucedemo.com)) e-commerce flow, same as recorded **`output.mp4`**.

| | |
|:---|:---|
| **Video** | [View on GitHub](https://github.com/laziobird/openclaw-rpa/blob/main/output.mp4) · [Raw download](https://github.com/laziobird/openclaw-rpa/raw/main/output.mp4) · [`output.mp4`](output.mp4) in repo |

**How this demo starts (matches the video)**

1. Send a trigger, e.g. **`#rpa`** / **`#RPA`**, or a message containing **`RPA`** / **“automation robot”** — see [**SKILL.md**](SKILL.md) and [**SKILL.en-US.md** — Trigger detection](SKILL.en-US.md#trigger-detection).
2. When prompted for a **task name**, use e.g. **`电商网站购物`** or align with an existing script like **`电商网站购物V10`** (see table below and **`registry.json`**).

**Task prompt used in this recording**

1. Open `www.saucedemo.com`, sign in with **`standard_user`** / **`secret_sauce`**.  
2. Sort products **price high → low**.  
3. Add the **two most expensive** items to the cart.  
4. **Log out**.

**Full protocol** — `record-start`, `record-step`, `plan-set`, “end recording” / `record-end`: follow [**SKILL.en-US.md**](SKILL.en-US.md) (ONBOARDING, RECORDING).  
Replay: `run:{task}` or `python3 rpa_manager.py run <name>` per **`registry.json`**.

---

## Advanced

<details>
<summary><b>Manual install · gateway Python · paths · publishing</b></summary>

### Manual install (no `install.sh`)

```bash
cd /path/to/openclaw-rpa
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
python -m playwright install chromium
```

### Which `python` does OpenClaw use?

`rpa_manager.py` uses **`sys.executable`**. That interpreter must have **Playwright**. If the gateway uses **system** `python3`, install deps there **or** point tools at:

`~/.openclaw/workspace/skills/openclaw-rpa/.venv/bin/python`

### Locale & `config.json`

- **`SKILL.md`** → `metadata.openclaw.localeConfig` → **`config.json`**
- If `config.json` is missing, the router can use **`config.example.json`** for `locale`
- Details: **`LOCALE.md`**

### Paths in `SKILL.en-US.md` / `SKILL.zh-CN.md`

Examples may use `~/.openclaw/workspace/skills/openclaw-rpa/`. Change the prefix if your workspace differs.

### Publish the skill

**[ClawHub — publish a skill](https://clawhub.ai/publish-skill)** (link this GitHub repo).

### Environment check

```bash
python3 envcheck.py
# or
python3 rpa_manager.py env-check
```

`record-start` / `run` can auto-install Chromium if missing.

</details>

---

## CLI quick start

```bash
python3 rpa_manager.py env-check
python3 rpa_manager.py list
python3 rpa_manager.py run wikipedia
```

Recorder: `record-start` → `record-step` → `record-end` (see `rpa_manager.py` docstring).

---

## Sample scripts (`rpa/`)

| Script | Notes |
|--------|--------|
| `wikipedia.py` / `wiki.py` | Wikipedia (English) |
| `豆瓣电影.py` | Chinese UI demo (follow site rules) |
| `电商网站购物v10.py` (and related) | Sauce Demo flow (same family as the [demo video](#demo-video)) |

More notes: **`examples/README.md`**.

---

<p align="center">
  <sub>Apache License 2.0 · Copyright © 2026 openclaw-rpa contributors</sub>
</p>
