# openclaw-rpa

English | **[中文](README.zh-CN.md)**

## Demo video

### Sauce (Online Shopping WebSite) Demo (browser recording)

**Sauce Demo** ([saucedemo.com](https://www.saucedemo.com)): **sign in → sort by price → add two most expensive → sign out**.  
Shows the full flow from trigger through recording to a generated script.

https://github.com/user-attachments/assets/965fbecc-a0fc-4795-9f63-a5ef126f97f8

**Recording (`saucedemo-readme.mp4`) — steps in the video**

1. Send **`#rpa`** / **`#RPA`** / **`#automation robot`** — see [**SKILL.md**](SKILL.md) and [**SKILL.en-US.md** — Trigger detection](SKILL.en-US.md#trigger-detection).
2. Task name examples: match an existing script like **`onlineShoppingV1`** (see **`registry.json`**).

**Task prompt (Sauce segment)**

1. Open `www.saucedemo.com`, sign in **`standard_user`** / **`secret_sauce`**.  
2. Sort **price high → low**.  
3. Add the **two most expensive** items to the cart.  
4. **Log out**.

### OpenClaw + Feishu/Lark: `#rpa-list`, `#rpa-run`, and scheduled run

Screen recording of a typical chat with **OpenClaw-bot** on Feishu/Lark:

- **`#rpa-list`** — list registered RPA tasks you can run;
- **`#rpa-run:onlineShoppingV1`** — run a saved script from a new chat;
- A line like **「One minute later run `#rpa-run:onlineShoppingV1`」** — schedule or remind to run later via OpenClaw + IM (exact behavior depends on your setup; execution still goes through **`rpa_manager.py run`**).


https://github.com/user-attachments/assets/08ccbdc6-508b-457a-87d6-49ac77e9a89e



Full protocol: [**SKILL.en-US.md**](SKILL.en-US.md) (ONBOARDING, RECORDING). **See what recorded RPAs exist:** **`#rpa-list`**. **Run one:** `#rpa-run:{task}` (new chat) or `run:{task}` / `python3 rpa_manager.py run <name>` (same chat).

---

> With **AI assistance**, record **typical website** and **local file** workflows into a **repeatable Playwright Python** script. **Replay without the LLM on every run**—saves compute and keeps steps deterministic (vs. ad-hoc model calls).

| | |
|:---|:---|
| **Needs** | Python **3.8+**, network for `pip` / Playwright browsers |
| **License** | [Apache 2.0](LICENSE.md) |

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

After install, **start a new OpenClaw chat** (or reload skills) so the agent reads **`SKILL.md`**. Triggers and keywords: **`SKILL.md`** (e.g. `#RPA`, `#automation robot`).

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
| `电商网站购物v10.py` (and related) | Sauce Demo flow (same as the [demo video](#demo-video) at the top) |

More notes: **`examples/README.md`**.

---

<p align="center">
  <sub>Apache License 2.0 · Copyright © 2026 openclaw-rpa contributors</sub>
</p>
