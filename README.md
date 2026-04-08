# openclaw-rpa

English | **[中文](README.zh-CN.md)**

> **AI-driven RPA that records once and replays forever — no model needed at run time.**

**openclaw-rpa** is an **LLM-based RPA Agent framework**. You describe a task in plain language; the AI executes it step by step in a **real browser, on your computer, or via API services** — with screenshot proof at every step — then compiles everything into a **standalone Python script**. Replay requires no LLM, no cloud dependency; just let OpenClaw select and run the automation task automatically.

## What you can automate

| Category | Examples |
|----------|---------|
| **Browser** | Login, navigate, click, fill forms, extract text, sort / filter tables |
| **HTTP API** | Call any REST endpoint (`GET` / `POST`), save JSON, embed API keys directly in the script |
| **Excel (`.xlsx`)** | Create / update workbooks, multiple sheets, headers, freeze panes, dynamic rows from JSON or another file |
| **Word (`.docx`)** | Generate reports with paragraphs and tables — no Microsoft Office required |
| **Auto-login** | Save cookies once with `#rpa-login`, inject them on every future recording and replay — skip OTP / CAPTCHA flows |
| **Mixed flows** | Any combination of the above in a single recorded task |

## How it works

```
You (plain language)
      │
      ▼
  #RPA / #rpa-api          ← trigger
      │
      ▼
 AI drives real Chrome     ← record-step (screenshot proof every step)
      │
      ▼
 "end recording"           ← synthesize
      │
      ▼
 rpa/<task>.py             ← standalone Playwright Python script
      │
      ▼
 python3 rpa/<task>.py     ← replay — no model, no AI, runs anywhere
```

**Why not just let the AI click the browser every time (Computer Use)?**

| Pain point | What goes wrong |
|------------|----------------|
| 🌀 **Hallucinations** | The model sometimes clicks the wrong button, targets the wrong element, or invents an action that doesn't exist — every "improvised" run carries risk |
| 💸 **Cost** | Every repeat run calls the LLM — tokens + tool calls + long context add up fast; a single session can easily run several dollars |
| 🐢 **Speed** | Waiting for model inference before each step is orders of magnitude slower than running a local script directly |

**What openclaw-rpa does instead:** use AI to record and verify once, then replay with a local script — **no model call, no token burn, no hallucination risk, runs in seconds**.

## Quick start

```bash
# Install
git clone https://github.com/laziobird/openclaw-rpa.git
cd openclaw-rpa && ./scripts/install.sh

# In an OpenClaw chat — pick your trigger:
#RPA                   # browser-only flow
#rpa-api               # flow that includes an HTTP API call
#rpa-login <url>       # save a login session (cookies)
#rpa-list              # list all recorded tasks
#rpa-run:<task name>   # replay a recorded task
```

Full protocol and capability codes (A–G): **[SKILL.en-US.md](SKILL.en-US.md)**.

---

## Case videos

### 1. Sauce (Online Shopping WebSite) Demo (browser recording)

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

<a id="yahoo-finance-nvda-demo"></a>

### 2. Yahoo Finance (NVDA news) — browser recording

**Yahoo Finance** ([finance.yahoo.com](https://finance.yahoo.com)): **search a symbol → open the quote page → switch to the News tab → capture the top headlines to a text file on the Desktop**. This case shows the same end-to-end path as the Sauce demo—trigger, record, synthesize a Playwright script—for a finance/news workflow.

https://github.com/user-attachments/assets/8da98e97-415c-4a60-b412-9a30ea87551a

**Recording — steps in the video**

1. Send **`#rpa`** / **`#RPA`** / **`#automation robot`** — see [**SKILL.md**](SKILL.md) and [**SKILL.en-US.md** — Trigger detection](SKILL.en-US.md#trigger-detection).
2. Task name example: align with a registered script such as **`YahooNew`** (see **`registry.json`** → `yahoonew.py`).

**Task prompt (Yahoo Finance segment)**

1. Open `https://finance.yahoo.com/`, search for **NVDA**, and go to the quote page (e.g. `https://finance.yahoo.com/quote/NVDA/`).
2. In the row of tabs under the stock price (same row as **Summary**), click **News** for this symbol—the tab next to **Summary**. Wait until the news list has loaded.
3. Save the **top 5** news headlines (**title text only**) to **`YahooNews.txt`** on the **Desktop**.

<a id="api-quotes-news-brief"></a>

### 3. Quotes API + news page + local brief (browser + API + file)

**Yahoo Finance (browser) + market data (HTTP API):** **save daily price data for a stock to the Desktop → open the symbol page → switch to News → save headline titles to a text file**. This flow adds a **data API** step on top of normal browsing. **How to wire URLs, keys, and `record-step` JSON** is in **[API notes](#api_call_notes)** below ([full `api_call` section](#api_call)).

**Recording — steps in the video**

1. Send **`#rpa-api`** — dedicated trigger for flows with HTTP API calls (see [**SKILL.en-US.md** — Trigger detection](SKILL.en-US.md#trigger-detection)).
2. Task name example: align with **`registry.json`** or create a new name such as **`NVDABrief`**.

**Task prompt (quotes + news + local brief)**

```
#rpa-api
###
Fetch NVDA daily OHLCV and save to the Desktop as nvda_time_series_daily.json
API docs  https://www.alphavantage.co/documentation/#daily
API key   UXZ3BOXOH817CQWS
###
Open Sina Finance https://finance.sina.com.cn/, search for NVDA, wait for the new page,
click "Company News" in the left menu, wait for the new page, save the top 5 news headlines to nvda_news.txt on the Desktop.
Merge nvda_time_series_daily.json and nvda_news.txt into a single brief file called nvda.txt.
```

Or paste the API doc parameter block directly:

```
#rpa-api
###
API Parameters
❚ Required: function → TIME_SERIES_DAILY
❚ Required: symbol   → NVDA
❚ Required: apikey
Example: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo
apikey  UXZ3BOXOH817CQWS
###
Open Sina Finance https://finance.sina.com.cn/, search for NVDA, click "Company News" on the left, save the top 5 headlines to nvda_news.txt on the Desktop.
Merge nvda_time_series_daily.json and nvda_news.txt into nvda.txt.
```

### 4. OpenClaw + Feishu/Lark: `#rpa-list`, `#rpa-run`, and scheduled run

Screen recording of a typical chat with **OpenClaw-bot** on Feishu/Lark:

- **`#rpa-list`** — list registered RPA tasks you can run;
- **`#rpa-run:onlineShoppingV1`** — run a saved script from a new chat;
- A line like **「One minute later run `#rpa-run:onlineShoppingV1`」** — schedule or remind to run later via OpenClaw + IM (exact behavior depends on your setup; execution still goes through **`rpa_manager.py run`**).


https://github.com/user-attachments/assets/08ccbdc6-508b-457a-87d6-49ac77e9a89e

### 5. Auto-login (Cookie reuse) — record post-login pages without re-entering credentials

**Scenario:** Sites like e-commerce platforms that require SMS OTP, CAPTCHA sliders, or QR-code login. Log in once manually, save the session, and every subsequent recording or replay **injects the cookies automatically** — skipping the login flow entirely.

**Case: Sauce Demo — sort products by price high → low**

| Step | What happens |
|------|-------------|
| `#rpa-login https://www.saucedemo.com/` | Browser opens the login page; you log in normally |
| `#rpa-login-done` | Cookies exported and saved to `~/.openclaw/rpa/sessions/saucedemo.com/cookies.json` |
| Task prompt contains `#rpa-autologin saucedemo.com` | Recorder injects cookies before the first page load |
| Record only: open `/inventory.html` → sort `hilo` | Browser is already logged in — no re-login step needed |
| Generated `CONFIG` carries `cookies_path` | Replay works the same way, no manual intervention |

**👉 Full tutorial:** [articles/autologin-tutorial.en-US.md](articles/autologin-tutorial.en-US.md)

**Command quick reference:**

```
#rpa-login <login-page-URL>       Open browser; you log in manually (password / OTP / slider)
#rpa-login-done                   Export cookies and close browser
#rpa-autologin <domain-or-URL>    Inject saved cookies on record or replay
#rpa-autologin-list               List all saved login sessions
```

---

### 6. AP reconciliation — GET API + local Excel + Word tables

**Finance / AP:** mock **GET** pulls open payables lines; **no ERP submit/close**; match against a local invoice workbook; save a **Word (`.docx`)** report with **tables**.

- **Full write-up (EN):** **[articles/scenario-ap-reconciliation.en-US.md](articles/scenario-ap-reconciliation.en-US.md)**  
- **Full write-up (中文):** **[articles/scenario-ap-reconciliation.md](articles/scenario-ap-reconciliation.md)**  
- **Recording:** `#rpa-api` or `#RPA`; capability **F** (Excel + Word) or **G** if a browser is needed; `api_call` + `excel_write`; add `docx` **tables** in a small post-`record-end` patch if needed (see article).

Full protocol: [**SKILL.en-US.md**](SKILL.en-US.md) (ONBOARDING, RECORDING). **See what recorded RPAs exist:** **`#rpa-list`**. **Run one:** `#rpa-run:{task}` (new chat) or `run:{task}` / `python3 rpa_manager.py run <name>` (same chat).

---

> With **AI assistance**, record **typical website** and **local file** workflows into a **repeatable Playwright Python** script. **Replay without the LLM on every run**—saves compute and keeps steps deterministic (vs. ad-hoc model calls).

| | |
|:---|:---|
| **Needs** | Python **3.8+**, network for `pip` / Playwright browsers |
| **Recommended LLM** | Minimax 2.7 · Google Gemini Pro 3.0 and above · Claude Sonnet 4.6 |
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

If your flow uses **Excel / Word** (capability **B–G** in **SKILL.en-US.md** / **SKILL.zh-CN.md**), use the same `python3` for e.g. `python3 rpa_manager.py deps-check D`; the skill guides `deps-install` in chat when something is missing.

**SSH clone:** `git@github.com:laziobird/openclaw-rpa.git`

After install, **start a new OpenClaw chat** (or reload skills) so the agent reads **`SKILL.md`**. Triggers and keywords: **`SKILL.md`** (e.g. `#RPA`, `#automation robot`).

### What “full” `requirements.txt` means

**Full stack** = every Python package listed in `requirements.txt` **plus** Chromium from `playwright install chromium`, all in the **same** environment as `rpa_manager.py` (e.g. `.venv` from `./scripts/install.sh`).

| Dependency | Role |
|------------|------|
| **playwright** | Headed Recorder + generated browser automation |
| **httpx** | `api_call` in recording and replay |
| **openpyxl** | `excel_write` for `.xlsx` (no Microsoft Excel required) |
| **python-docx** | `word_write` for `.docx` (`import docx`; no Microsoft Word required) |
| **Chromium** | Installed by `playwright install chromium`, not via `pip` |

See comment block at the top of `requirements.txt` for the same breakdown.

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
| `获取豆瓣电影数据.py` | Chinese UI demo (follow site rules) |
| `onlineshoppingv1.py` (and related) | Sauce Demo flow (same as the [demo video](#demo-video) at the top) |
| `yahoonew.py` (`YahooNew` in **`registry.json`**) | Yahoo Finance quote → **News** tab → top 5 headlines to Desktop (see [Yahoo Finance demo](#yahoo-finance-nvda-demo)) |

More notes: **`examples/README.md`**.

---

<a id="api_call"></a>

## API recording (`api_call`)

The recorder supports **`api_call`** steps: **GET/POST** (or other methods) via **httpx**, with the response optionally saved under the Desktop. Full field list and progressive-probing tips: **[SKILL.en-US.md — `api_call`](SKILL.en-US.md#single-step-recording-protocol-for-every-user-instruction)** and **Scenario 1**.

### API notes

<a id="api_call_notes"></a>

For **agents / developers** (shell, JSON, `record-step`—not the plain-language user prompt in **[§3](#api-quotes-news-brief)**).

1. **What `api_call` does**  
   Adds a step that issues an **HTTP request** to a URL (independent of the current browser page) and optionally writes the response to a Desktop file (**`save_response_to`**).

2. **Key embedding strategy**  
   In the `record-step` JSON, use **`__ENV:ENV_VAR_NAME__`** in `params` or `headers` **and** include the actual key in the step's **`"env"` field**:

   ```json
   {
     "action": "api_call",
     ...,
     "params": {"apikey": "__ENV:ALPHAVANTAGE_API_KEY__", ...},
     "env": {"ALPHAVANTAGE_API_KEY": "your-real-key"}
   }
   ```

   The code generator detects the `env` field and **writes the key directly into the script** (e.g. `'apikey': 'your-real-key'`) — no `export` needed for replay; the script runs as-is.  
   If `env` is omitted, the generated code uses `os.environ.get("VAR", "")` and requires `export VAR=…` before running.

3. **This README's [§3](#api-quotes-news-brief) example (Alpha Vantage daily)**  
   Docs: [TIME_SERIES_DAILY](https://www.alphavantage.co/documentation/#daily). Typical `record-step`: **`base_url`** + **`params`** (`function`, `symbol` = IBM, `outputsize` = compact, …), `apikey` = `"__ENV:ALPHAVANTAGE_API_KEY__"`, `env` with real key, **`save_response_to`** = output filename.

**Summary:** Use **`__ENV:NAME__`** + **`"env"` field** together → key written into script, no `export` needed.

### Example: quotes + news page + local brief

**Plain-language task prompt:** **[§3](#api-quotes-news-brief)**. **Wiring:** **[API notes](#api_call_notes)**. One task can **(1)** save quote JSON, **(2)** open a news page, **(3)** **`extract_text`** into the same brief filename (append rules in **[Scenario 1](SKILL.en-US.md#scenario-1-quotes--news-page--local-brief-browser--api--file)**).

---

## Roadmap (planned)

The following capabilities are **not shipped yet**; they describe where the project is headed.

| Area | Description |
|:-----|:------------|
| **Deeper API tooling** | Richer **HTTP** helpers (e.g. auth presets, response shaping) on top of today’s **`api_call`** **record → synthesize → replay** path. |
| **✅ Auto-login / session reuse** (shipped) | `#rpa-login` for one manual login → cookies saved automatically → `#rpa-autologin` injects them on every subsequent recording and replay, no re-login needed. See **[articles/autologin-tutorial.en-US.md](articles/autologin-tutorial.en-US.md)**. |

**Caveats**

- **Compliance:** Follow each site’s terms of service and policies. This repo does not endorse evading safeguards or scraping where it isn’t allowed.
- **High-friction sites (e.g. LinkedIn):** Even with auto sign-in or session reuse, you may still hit **2FA, device checks, CAPTCHAs, and risk blocks** that require **human steps**. The goal is fewer redundant login flows **when your environment can keep a stable session**—not a promise of **fully unattended** operation on every platform.

---

<p align="center">
  <sub>Apache License 2.0 · Copyright © 2026 openclaw-rpa contributors</sub>
</p>
