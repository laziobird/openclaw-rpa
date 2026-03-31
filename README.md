# openclaw-rpa

English | **[中文](README.zh-CN.md)**

With **AI assistance**, record how you work on **typical websites** plus any **local file** steps you need, and compile that into a **repeatable RPA script** (Python / Playwright). **Everyday runs execute the script directly**—you don’t need the model to drive each click each time, which **saves compute** and keeps behavior **deterministic** (fewer surprises than ad-hoc LLM automation).

**Covers:** real browser interactions; optional read/write/rename/organize files in the same script, browser-only or file-only blocks.

**Example:** schedule the same checkout/form script daily, or add a block that only cleans `Downloads`—repeat runs **without** paying for full LLM-driven control each time.

## OpenClaw setup

Use this repo as an **OpenClaw skill**: the agent loads **`SKILL.md`** (router) and the locale file **`SKILL.zh-CN.md`** / **`SKILL.en-US.md`** from this directory, and runs **`rpa_manager.py`** for recording.

### 1. Put the skill under the workspace `skills` folder

| | Default path |
|---|--------------|
| OpenClaw workspace root | `~/.openclaw/workspace` |
| This skill (directory name) | `~/.openclaw/workspace/skills/openclaw-rpa` |

If the folder does not exist yet, clone this repository:

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa
```

SSH: `git clone git@github.com:laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa`

### 2. Python, Playwright, and Chromium

From the skill directory:

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
chmod +x scripts/install.sh
./scripts/install.sh
```

This creates **`.venv`** and installs **`requirements.txt`** + **`playwright install chromium`**.

### 3. Skill configuration (`config.json`)

OpenClaw reads **`metadata.openclaw.localeConfig`** in **`SKILL.md`**, which points to **`config.json`**. Create it from the example (default locale **`en-US`**):

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
python3 scripts/bootstrap_config.py
python3 scripts/set_locale.py zh-CN    # or: en-US
```

See **`LOCALE.md`**. If **`config.json`** is missing, **`SKILL.md`** tells the agent to fall back to **`config.example.json`** for the `locale` field. After changing locale, start a **new session** or have the agent **re-read** **`SKILL.md`** / **`SKILL.*.md`**.

### 4. Which Python runs `rpa_manager.py`?

Recording uses **`sys.executable`**. The interpreter that starts **`rpa_manager.py`** must have **Playwright** installed. If your OpenClaw gateway runs tools with **system** `python3`, either install deps into that interpreter **or** configure the gateway to use:

`~/.openclaw/workspace/skills/openclaw-rpa/.venv/bin/python`

when invoking **`rpa_manager.py`** and generated scripts under **`rpa/`**.

### 5. Reload the agent

After first install or any change to **`SKILL*.md`** / **`config.json`**, open a **new chat** or reload skills so the agent picks up the latest instructions.

### 6. Triggers and discovery

Triggers and keywords are defined in **`SKILL.md`** (YAML `description` and router). Typical examples: `#RPA`, `#rpa`, “automation robot”, etc. To publish the skill for others, use **[ClawHub](https://clawhub.ai/publish-skill)** with this GitHub repo.

### 7. Verify

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
source .venv/bin/activate   # optional
python3 rpa_manager.py env-check
```

### 8. Paths inside `SKILL.en-US.md` / `SKILL.zh-CN.md`

Those files may show commands under **`~/.openclaw/workspace/skills/openclaw-rpa/`**. If your workspace lives elsewhere, replace that prefix with your real skill path (or symlink).

---

## Requirements

- **Python 3.8+** (3.10+ recommended)
- **pip** and network access for `pip install` and Playwright browser downloads

## Install (recommended)

If you already ran **`./scripts/install.sh`** in [OpenClaw setup](#openclaw-setup), skip this block.

From the skill directory:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

This creates a **`.venv`**, installs Python dependencies from `requirements.txt`, and runs **`playwright install chromium`**.

Then activate the venv whenever you work with this skill:

```bash
source .venv/bin/activate
```

### Manual install

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
python -m playwright install chromium
```

### Check environment

```bash
python3 envcheck.py
# or
python3 rpa_manager.py env-check
```

`record-start` and `run` also verify Python + Playwright and **auto-install Chromium** when possible (same behavior as before).

Locale / **`config.json`** is covered in [OpenClaw setup §3](#openclaw-setup).

## Quick start (CLI)

```bash
python3 rpa_manager.py env-check
python3 rpa_manager.py list
python3 rpa_manager.py run wikipedia
```

Recorder flow: `record-start` → `record-step` → `record-end` (see `rpa_manager.py` docstring).

## Sample scripts

Pre-generated scripts and command logs live under **`rpa/`**. Good starting points:

| Script | Notes |
|--------|--------|
| `rpa/wikipedia.py` | Stable public site (English) |
| `rpa/wiki.py` | Same flow, alternate naming |
| `rpa/豆瓣电影.py` | Chinese demo (site policies apply) |
| `rpa/电商网站购物v10.py` | E-commerce style demo (example only) |

**examples/README.md** lists curated recommendations and cautions.

## License

[Apache License 2.0](LICENSE) — Copyright © 2026 openclaw-rpa contributors.
