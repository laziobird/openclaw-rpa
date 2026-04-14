---
name: openclaw-rpa
language: en-US
description: Record browser & local-file actions once; replay runs without the LLM—save $ vs AI browsing, faster, no hallucinations. github.com/laziobird/openclaw-rpa
metadata: {"openclaw": {"emoji": "🤖", "os": ["darwin", "linux"]}}
---

> **This file:** `en-US` (selected by `locale` in [config.json](config.json) or [config.example.json](config.example.json) if `config.json` is missing; Chinese: [SKILL.zh-CN.md](SKILL.zh-CN.md))

> **GitHub:** **[https://github.com/laziobird/openclaw-rpa](https://github.com/laziobird/openclaw-rpa)** — install, `rpa/` samples, issues

# openclaw-rpa

**Example automations** (illustrative; **obey each site’s terms of use and applicable law**): **e‑commerce login & shopping**; **Scenario 1** (below) **quotes API + news page + local brief**; **Yahoo Finance** browser-only quotes / news; movie sites **reviews & ratings** in one scripted run; **AP reconciliation** (GET-only mock API, local Excel vs invoices, **Word table** report — no ERP submit) — **[EN](articles/scenario-ap-reconciliation.en-US.md)** · **[中文](articles/scenario-ap-reconciliation.md)**.

## What this skill does

**openclaw-rpa** is a **Recorder → Playwright script** pipeline: the agent drives a real browser, you confirm steps, and **`record-end`** compiles a **normal Python** file under `rpa/`. **Replay** runs that file with **`rpa_manager.py run`**—**no** LLM per click.

**Highlights**

1. **Saves compute and money** — Letting a **large model** operate the browser **every** time can cost **on the order of single-digit to tens of US dollars** per heavy session (tokens, tools, long context). After you **record once**, repeat runs **do not invoke the model**—cost is essentially **local script execution**, and runs are **much faster** than step-by-step LLM reasoning.
2. **Verify the flow once, then run the same steps every time** — During recording you **prove** the task works; replay **executes the saved steps** deterministically. You avoid asking the AI to improvise on each run, which **reduces inconsistency** and **hallucination-driven** mistakes.
3. **Vision recognition conquers SPAs** — For heavily dynamic Single-Page Applications like Airbnb or Ctrip, recording auto-triggers vision mode: the agent takes a screenshot and calls **[Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)** (Alibaba open-source vision model) to read data directly from the screen — **no fragile DOM selectors**. Ultra-low token cost; supports local deployment. Featured case: [Airbnb Competitor Price Tracker](articles/scenario-airbnb-compare.md).
4. **Structured task prompt + standard orchestration templates** — Use the `[var]` / `[step]` / `[constraint]` three-section prompt format; the Skill automatically decomposes multi-step goals into a sequential recording series and organizes each step with the built-in **Extract → Aggregate → Write** (three-layer) template, ensuring clear, replayable, deterministic results.

**Recommended LLM:** Minimax 2.7 · Google Gemini Pro 3.0 and above · Claude Sonnet 4.6

Output is **ordinary Python**; after **`record-end`** you may still patch helpers (`pathlib` / `shutil` / `open()`, or **`extract_text`** during recording)—browser-only, file-only, or both.

## When to use

| Goal | What to send |
|------|----------------|
| **Start recording** a new flow | `#automation robot`, `#RPA`, `#rpa`, or mention **Playwright automation** |
| **Record a flow with an HTTP API** | `#rpa-api` (describe the API or paste an API doc param block `###...###` in the message) |
| **List saved tasks** | `#rpa-list` |
| **Run a saved task** (e.g. new chat) | `#rpa-run:{task name}` |
| **Run in this chat** | `run:{task name}` |
| **Schedule / reminder** (OpenClaw + IM) | Natural language + `#rpa-run:…` — depends on your gateway |

## Quick start

```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list   # same as #rpa-list
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py run "your-task-name"
```

In chat, prefer **`#rpa-list`** → **`#rpa-run:your-task-name`** so names match `registry.json`.

### Running recorded scripts (reminder)

- **`#rpa-list`** — shows **registered** task names; use **first** if unsure.
- **`#rpa-run:{task}`** / **`run:{task}`** — **execute the saved script again**; they do **not** start a new recording.

## Scope (details)

**In the browser** — Clicks, typing, selects, scroll, wait, screenshots; multi-step flows are first-class. Extracting page text is **one** option.

**On disk (optional)** — While recording, **`extract_text`** can write text under the user’s home. After **`record-end`**, edit `rpa/*.py` per [playwright-templates.md](playwright-templates.md).

**Out of scope** — Large ETL, databases, or heavy OS automation.

### Examples (illustrative)

| Pattern | Example |
|---------|---------|
| **Browser only** | **E‑commerce:** login → browse → cart/checkout (`rpa/电商网站购物*.py` style). **Yahoo Finance:** quotes / headlines. **Movies:** aggregate **reviews & ratings**. |
| **Browser then files** | Same flow, plus **`extract_text`** when asked. |
| **Browser + Vision (SPA) + Word** | **Airbnb competitor pricing:** SPA pages use **`extract_by_vision`** (Qwen3-VL) to pull listing name / price / rating, written to a **Word report**. See **[tutorial](articles/scenario-airbnb-compare.md)**. |
| **Browser + HTTP API + files** | **Scenario 1:** **`api_call`** (e.g. [Alpha Vantage TIME_SERIES_DAILY](https://www.alphavantage.co/documentation/#daily)) saves JSON/text locally, then **`goto` + `extract_text`** for a brief. |
| **HTTP API + Excel + Word (browser optional)** | **AP reconciliation:** mock **GET** batches, local sheets, **no submit**; output **.docx** with tables — see **[EN](articles/scenario-ap-reconciliation.en-US.md)** · **[中文](articles/scenario-ap-reconciliation.md)**. |
| **Files only in script** | After **`record-end`**, add folder cleanup—**no URL** for that block. |

## Recommended sites for getting started

**Good fits — predictable structure, works well out of the box:**

| Category | Examples |
|----------|---------|
| **Finance / data** | Yahoo Finance (quotes, headlines), Google Finance, investing.com |
| **E-commerce** | Sauce Demo (`saucedemo.com`), AliExpress product pages, eBay search results |
| **News / media** | BBC News, Reuters, Hacker News, Reddit (listing pages) |
| **Reference** | Wikipedia, GitHub (public repo pages, issues list) |
| **Job boards** | LinkedIn Jobs (public search), Indeed results page |
| **Travel / weather** | weather.com, Google Flights results (read-only) |
| **Demo / test sites** | `the-internet.herokuapp.com`, `demoqa.com`, `automationpractice.pl` |

**Not recommended — likely to break or require manual workarounds:**

| Situation | Why |
|-----------|-----|
| **Highly dynamic SPAs** (heavy client-side routing, frequent DOM mutations) | Selectors shift between renders; snapshots may miss unrendered content |
| **CAPTCHA / bot-detection sites** (Google reCAPTCHA, hCaptcha, Cloudflare Turnstile) | Automation will be blocked; human intervention required |
| **Login-gated flows without saved sessions** | Credentials and 2FA must be handled manually before replay |
| **Infinite-scroll feeds with no stable IDs** | Progressive probing helps but results are inconsistent |

> **Tip:** when trying a new site, start with a simple `goto` + `snapshot` step to check whether the page structure is readable before building a full flow.

---

## Troubleshooting: `LLM request timed out` (not the record-step timeout)

If logs show `error=LLM request timed out`, `model=gemini-...`, `provider=google`:

| Meaning | A **single** OpenClaw → LLM API call (reply generation + tool planning) exceeded the gateway/client **LLM timeout**. This is **not** the `record-step` wait for a result (e.g. 120s) and **not** Chromium navigation timeout. |
| Common causes | **Too much in one turn**: multiple `record-step` calls / long reasoning / pasting the full page snapshot back into the reply; oversized context and output; slower models (e.g. `gemini-3-pro-preview`) plus the tool chain. |
| Skill-side | **Must** follow the anti-timeout rules below: after `plan-set`, advance **only a small slice per user turn** (≤2 `record-step` calls), keep replies short, and **do not** paste full snapshot JSON into the chat repeatedly. |
| Environment | **Raise the LLM request timeout** in OpenClaw/Gateway if the product exposes it; unstable network to the Google API also increases latency. |

---

## Trigger detection

On each user message, **check in this order** (**first match wins**; do not skip order or `#rpa-list` may be mistaken for ONBOARDING because it contains `#rpa`; `#rpa-api` must be checked before the generic `#rpa`):

| Order | Condition | State |
|:-----:|-----------|--------|
| 1 | Message is a **RUN** (see table below) | RUN |
| 2 | After trim, message **equals** `#rpa-list` (**case-insensitive**, e.g. `#RPA-LIST`) | LIST |
| 3 | Message contains **`#rpa-api`** (case-insensitive) | RPA-API |
| 4 | Message contains **#automation robot** OR **#RPA** OR **#rpa** (case-insensitive for `#RPA` / `#rpa`) | ONBOARDING |

Intercept and handle these; do not run the raw user task outside this skill.

**RUN triggers (order 1):**

| Form | Notes |
|------|--------|
| `#rpa-run:{task name}` | **Run in a new chat** (no reliance on this thread): after trim, message **starts with** `#rpa-run:` (**case-insensitive**, e.g. `#RPA-RUN:`). **After the first colon** to **end of line** is `{task name}` (**must match** a name from `#rpa-list`, trimmed). |
| `run:{task name}` | **Run in this chat:** `run:` then optional spaces, then task name to end of line (trimmed; same name rules). |

> **`zh-CN` locale:** use [SKILL.zh-CN.md](SKILL.zh-CN.md) (`#RPA` / `#rpa`, `#rpa-list`, `#rpa-run:`).

---

## State machine

```
IDLE ──trigger──► ONBOARDING (show signup rules)
                    │
                    └──one user message ("task name LETTER" or two-line)──► DEPS_CHECK
                                                                                      │
                    ┌───────────────────────────────────────────────────────────────┘
                    │  python3 rpa_manager.py deps-check <letter>
                    ├─failed + user sends CANCEL (fixed token)──────────────────────► IDLE (abort)
                    ├─failed + user sends AGREE──deps-install──deps-check again───────┐
                    └─passed ──────────────────────────────────────────────────────┤
                                                                                       ▼
                                                                                RECORDING
RECORDING ──#end──► GENERATING ──► IDLE
    │#abort
    └────────────────────────────────────► IDLE
IDLE ──"#rpa-api"──► RPA-API ──parsed──► (same task+capability rules)──► DEPS_CHECK ──► RECORDING …
IDLE ──"#rpa-run:{task}" / "run:{task}"──► RUN ──► IDLE
IDLE ──"#rpa-list"──► LIST ──► IDLE
```

> **Note:** For codes **B / C / F / N**, **`record-start` does NOT open Chrome** — no browser is launched. The agent issues `excel_write`, `word_write`, `api_call`, `merge_files`, `python_snippet` steps directly without any browser window.

---

## RPA-API state

Triggered by: message contains **`#rpa-api`** (case-insensitive).

### ⛔ Absolute prohibitions (agent MUST enforce)

> **Do NOT call the HTTP API yourself. Do NOT run Python / httpx / requests / curl. Do NOT return the API response to the user.**  
> The **sole purpose** of `#rpa-api` is to **record the API call into a replayable RPA script** — exactly like `#rpa` / `#automation robot` does for browser actions.  
> No matter how trivial the API call looks, it **must** go through `record-start` → `record-step api_call` → `record-end`.  
> **Fetching data "on behalf of the user" without recording is a violation.**

### Output the following verbatim — do not skip

```
🤖 OpenClaw RPA recorder ready (API + browser mode)

I'll record your API call and browser steps into a replayable RPA script.
Future runs just execute the script — no model needed to fetch data every time.

How it works:
1. I parse the API info you provided → key is written directly into the script (no export needed)
2. Browser / file steps run in a real Chrome window with screenshots for confirmation
3. Say `#end` → compile into a standalone Playwright Python script

Send one message: line 1 = task name, line 2 = capability letter **A–G** or **N** (see `#automation robot` / `#RPA` onboarding table).
```

### Parsing the `###...###` API declaration block

Wrap API info in `###` markers. Two accepted formats:

**Format A — natural language + API doc URL + key**
```
###
Task description (e.g.: fetch NVDA daily OHLCV, save to Desktop as nvda_time_series_daily.json)
API docs  https://www.alphavantage.co/documentation/#daily
API key   YOUR_API_KEY
###
```

**Format B — paste API doc parameter snippet + key**
```
###
API Parameters
❚ Required: function    → TIME_SERIES_DAILY
❚ Required: symbol      → IBM
❚ Required: apikey
Example: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo
apikey  YOUR_API_KEY
###
```

Both formats can be mixed. Lines **outside** the block are the subsequent **browser / file steps**.

### Agent steps (in order — none may be skipped or merged)

**Step 0 — Output the greeting and wait for “task name + capability”** (same format as **ONBOARDING**: `task name LETTER` on one line, or two-line compatible). If the user already included it in the same message as `#rpa-api`, go straight to **DEPS_CHECK**.

**Step 1 — Extract API info from the block**  
   - Identify: **base_url**, **required params** (function, symbol, …), **key field name** (apikey / token / key / …)  
   - If a doc URL is given, infer base_url + function from URL path + params; fill business params (symbol, etc.) from the user description  
   - Save filename from user description → **`save_response_to`**

**Step 2 — Embed the key into the script (when provided)**  
   - Name the env var from the API provider (examples: Alpha Vantage → `ALPHAVANTAGE_API_KEY`; OpenAI → `OPENAI_API_KEY`; custom → `MY_API_TOKEN`)  
   - In the `record-step` JSON:
     - Use **`__ENV:VAR_NAME__`** placeholder in `params` / `headers`  
     - **Also** put the real key in the step's **`"env"`** field:  
       ```json
       {
         "action": "api_call",
         ...,
         "params": {"apikey": "__ENV:ALPHAVANTAGE_API_KEY__", ...},
         "env": {"ALPHAVANTAGE_API_KEY": "user-supplied-real-key"}
       }
       ```
   - When `env` is present, the code generator writes the key **directly into the script** (e.g. `'apikey': 'UXZ3BOXOH817CQWS'`) — **no `export` required** for replay  
   - **Do NOT** output an `export VAR=…` instruction; instead confirm: "Key written directly into the script — no setup needed before replay."  
   - If the user **did not** supply a key, omit `env`, use placeholder only, and tell the user they'll need `export VAR_NAME=…` before running

**Step 3 — After “task name + capability” and DEPS_CHECK, start recording**  
   - Run `record-start "{task name}" --profile {LETTER}` (same capability rules as ONBOARDING; `deps-check` must pass first)  
   - After `✅ Recorder ready`, inject `api_call` as the **first step** (key in the `env` field):
     ```bash
     python3 rpa_manager.py record-step '{"action":"api_call","context":"...","base_url":"...","params":{...,"key_field":"__ENV:VAR_NAME__"},"env":{"VAR_NAME":"real_key"},"method":"GET","save_response_to":"..."}'
     ```
   - Confirm result to the user (screenshot / file written)

**Step 4 — Continue with steps outside the block**  
   Follow the RECORDING single-step protocol for browser steps, `merge_files`, etc., until the user sends `#end`.

> **No `###` block:** if the message is only `#rpa-api` with no block, output the greeting, ask for task name + capability (`task name LETTER` on one line, or two-line; same as ONBOARDING) → **DEPS_CHECK** → **RECORDING** — the user issues `api_call` steps manually.

## ONBOARDING

**Output the following verbatim (English):**

```
🤖 OpenClaw RPA is ready

With AI assistance, we can record your operations on common websites and any required local file steps, then compile them into an RPA script you can replay repeatedly.
After recording, daily runs execute the script directly — lower compute cost, deterministic steps, and less exposure to hallucinations.

── Name your recording task ──
Format:  Task name  Capability code
Example: reconciliation  F

Capability code (one trailing uppercase letter):
  A  Browser only
  B  Excel only (.xlsx via openpyxl; no Microsoft Excel app required)
  C  Word only (.docx via python-docx; no Microsoft Word app required)
  D  Browser + Excel
  E  Browser + Word
  F  Excel + Word (no web steps in the task)
  G  Browser + Excel + Word
  N  None of the above (e.g. API + merge text files only)

Excel / Word (plain language):
• Usually OK: multiple sheets, data, headers, column width, freeze top row, hidden columns; Word templates, paragraphs, simple tables.
• Not a good fit: macros, pivot refresh, heavy formula evaluation without Excel; Word track-changes, complex fields, legacy .doc.

If dependencies are missing, I will ask for confirmation before installing.

Recording flow (after entering recording mode):
1. You give an instruction → I execute it in a real browser (if the task includes web steps), then show screenshots for confirmation.
2. Say `#end` → compile into an RPA script.

Common commands:
• `#end` → generate a standalone RPA program
• `#abort` → close browser and discard this recording session
• For multi-step plans, to move forward you can send: **continue**, **1**, or **next** (same as "ok", "y", "go")
• Need HTTP API calls in the task? Start a **new chat** and send **`#rpa-api`** to enter the dedicated recording flow (`#rpa-api` is an IDLE trigger, not an in-recording step command)
• Help or all available commands: **`#rpa-help`**; list recorded tasks: **`#rpa-list`** (different purposes)

Please send: task name + capability letter (e.g. `reconciliation F`)
```

---

## DEPS_CHECK (after onboarding signup)

**Parse the user message**

1. **Single-line format** (preferred): after trimming, if the **last whitespace-separated token** is a single character `A`–`G` or `N` (case-insensitive → uppercase) → capability; **everything before it** trimmed → `{task name}`.  
2. **Two-line format** (compatible): split into lines, last non-empty line is single letter → capability; all previous lines joined → `{task name}`.  
3. If neither format yields a valid capability letter → do **not** `record-start`; show corrected example `Supplier reconciliation sheet F` and ask the user to resend.  
4. If the user already included the info in the **same trigger message**, skip re-asking.

**Check (same `python3` as Playwright)**

```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py deps-check {LETTER}
```

- **Exit 0** → start recording (below) with `--profile`.  
- **Non-zero** → explain what’s missing in plain language, then tell the user there are **exactly two** allowed replies — nothing else counts.

**Fixed options only** (verbatim; copy-paste recommended)

After **trimming leading/trailing whitespace**, the message must be **exactly** one of (ASCII **case-insensitive**):

| Reply | Meaning |
|-------|---------|
| `AGREE` | Run `deps-install {LETTER}` → `deps-check` again → `record-start` if OK |
| `CANCEL` | Abort signup, return to IDLE, do not install |

- If the user sends anything else (`ok`, `yes install`, `go ahead`, …) → **do not** run `deps-install`. Reply: **Send only `AGREE` or `CANCEL` on its own line (no extra words or punctuation).**  
- On **`AGREE`** (any casing) → run `deps-install` → `deps-check` → `record-start` or show stderr.  
- On **`CANCEL`** → IDLE.

Do **not** run `deps-install` unless the trimmed message equals **`AGREE`** ignoring ASCII case.

---

## RECORDING (Recorder mode — headed browser)

### Start recording (after DEPS_CHECK passes)

Run (**always pass `--profile`** matching the signup letter):

```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-start "{task name}" --profile {LETTER}
```

When the command prints `✅ Recorder ready`, reply one of the following based on the capability:

**If capability includes a browser (A / D / E / G):**
```
✅ Recording started: 「{task name}」
Capability saved in recorder_session/task.json (needs_excel / needs_word / needs_browser / capability).
🖥️  Chrome is now open.

⬇️  Please send your COMPLETE TASK DESCRIPTION. AI will parse it and execute step-by-step (confirming each step before continuing).
    Structured tags are strongly recommended for accurate dynamic code generation:

  [var]    Constants use 'value'; dynamic vars use ### description ### (AI generates the code)
  [do]     Execution steps ← required; AI records these one by one
  [rule]   Code-generation constraints (optional)

Example:
  [var]
  query_time = ### current system time, precise to the minute, format MM/DD HH:MM ###
  output_path = '~/Desktop/result.docx'
  urls:
    https://example.com/room/1
    https://example.com/room/2

  [do]
  1. Visit each URL in urls
  2. Extract name, rating, price, ${query_time}
  3. Write table and save to output_path

  [rule]
  - Both URLs share the same structure; reuse selectors with a loop

👉 You can also describe the task in plain natural language — AI will try to decompose it automatically.
```

**If capability has NO browser (B / C / F / N):**
```
✅ Recording started: 「{task name}」
Capability saved in recorder_session/task.json (needs_excel / needs_word / needs_browser / capability).
📂 No browser — file / API steps only (excel_write / word_write / api_call / python_snippet / merge_files).

⬇️  Please send your COMPLETE TASK DESCRIPTION. AI will parse it and execute step-by-step.
    Recommended tags:

  [var]    Constants use 'value'; dynamic vars use ### description ###
  [do]     Execution steps ← required
  [rule]   Constraints (optional)

👉 Plain natural language also works.
```

---

### Anti-timeout: multi-step instructions **must** be split — **one step per user turn**

> **This rule applies to all scenarios: free-text multi-step instructions AND structured tag tasks (`[do]`/`[步骤]`). The execution protocol is identical for both. No exceptions.**

**When to split:** The user’s message contains **two or more** independent atomic actions (navigate, search, click, extract, …).

#### Split workflow

**First turn (multi-step instruction):**

1. Decompose into atomic sub-tasks (each sub-task maps to ≤2 `record-step` calls). **During decomposition:** run **SPA / vision classification** on **every URL** you will visit (including links in `[var]`) against the **heavy SPA host list** (see §SPA detection below). If matched and the step extracts from the page, **state `extract_by_vision` in the sub-task text** — do not postpone that choice until execution. **Word append:** If the user asks to **append** to a Word file / `${output_path}` / “don’t overwrite the existing doc”, **state in that sub-task** that **`word_write` must use `mode: append`**; otherwise the agent often omits `mode` in JSON and the generator emits `_wmode='new'`, **overwriting** the whole file. **Excel append:** If the user asks to **append rows** to an existing `.xlsx`, **add rows at the end of an existing sheet**, or **keep existing sheet data**, **state that `excel_write` must use `replace_sheet: false`**; the default `true` **deletes and recreates** the same-named sheet, wiping old rows.
2. Persist the plan with `plan-set` (step numbers must be consecutive from 1 to N, no gaps):
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-set '["subtask 1", "subtask 2", "subtask 3"]'
   ```
3. Execute **step 1 only** (do not continue).
4. End with:
   ```
   📍 Progress: 1/{N} done
   ✅ [step description]
   📸 Screenshot: {path}
   Confirm the screenshot, then say **continue**, **1**, or **next** to run step 2/{N} (see shortcut confirmations below).
   ```

> **Shortcut confirmations** (all mean “continue to the next step”): `continue`, `1`, `next`, `ok`, `y`, `go` (`next` is case-insensitive). The user may send **`1`** or **`next`** alone — no full sentence required.

**Later turns (after one of the shortcuts):**

1. Check plan progress:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-status
   ```
2. Run the action for the current step (`snapshot` + action, ≤2 `record-step` calls).
3. Advance the plan:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-next
   ```
4. If there is a next step → print progress and wait for confirmation. If all steps are done → print:
   ```
   🎉 All {N} steps completed!
   Say `#end` to generate the RPA script, or describe more actions.
   ```

> **Why:** Each LLM request should only run **2–3** tool calls; a single `record-step` wait for the recorder can be up to **120s** (same as `rpa_manager` polling). Multi-step work must still be split so total time does not trigger `LLM request timed out`.

---

### Structured task description tags (task decomposition rules)

> Users may annotate their task description with explicit tags after entering recording mode.  
> **Tag recognition:** case-insensitive; Chinese and English are equivalent (`[变量]` = `[var]` = `[VAR]`); a tag occupies its own line, followed by the block's content.

| Tag (EN) | Tag (ZH) | Required | AI behaviour |
|---------|---------|---------|------------|
| `[var]` | `[变量]` | No | Declare constants and dynamic variables (see line-format rules below) |
| `[do]` | `[步骤]` | **Yes** | Parse step sequence → convert to atomic `record-step` operation plan (persist via `plan-set`) |
| `[rule]` | `[约束]` | No | Extract constraints → apply when choosing selector strategies, loop patterns, retry logic |

#### `[var]` line-format rules

Three formats, each with a distinct syntax:

| Line format | Type | AI behaviour |
|-------------|------|-------------|
| `key = 'value'` | **Constant** (single quotes) | Write into `CONFIG[key]`; used as-is |
| `key = ### description ###` | **Dynamic variable** (triple hash) | AI generates a runtime Python expression from the natural-language description; referenceable as `${key}` |
| `key:` + indented list | **Constant list** | Write into `CONFIG[key]` as a list |

**Dynamic variable rule:** Variables declared with `### description ###` **must** be assigned a runtime expression in `python_snippet`. Hardcoding values observed during recording is strictly forbidden.

**`${variable_name}` reference syntax:** Use `${variable_name}` anywhere in `[do]` or `[rule]` to reference a declared variable. When generating code, the AI substitutes it with the Python variable name (runtime value) — never a literal.

#### Task description parsing flow

1. **Detect `[do]`/`[步骤]`**:
   - **Found** → enter structured parsing; all tag blocks must be parsed in order.
   - **Not found** → treat as free-text task (existing logic unchanged).
2. **Parse `[var]`/`[变量]`**:
   - `key = 'value'` → constant → `CONFIG[key] = "value"`
   - `key = ### description ###` → AI generates runtime Python expression
   - `key:` + indented lines → constant list → `CONFIG[key] = [...]`
3. **Parse `[do]`/`[步骤]`** (required):
   - Expand each user step into atomic operation descriptions (≤2 `record-step` calls each)
   - **Combine with `[var]` and URLs inside steps:** finish **SPA classification in this parsing turn** (hostname vs host list); if extraction is needed and the host is heavy SPA, the atomic text must specify **vision extraction** — do not wait until mid-run to guess
   - **Word write mode:** If a step says **append**, **end of document**, **don’t overwrite**, or **append to `${output_path}`**, the matching `word_write` **`record-step` JSON must include top-level `"mode":"append"`** (same level as `path` / `table`). **Natural language alone does not enable append**; omitting `mode` defaults to `new` → generated code overwrites the file
   - **Excel write mode:** If a step says **append to xlsx**, **add rows at the bottom**, or **keep existing sheet data**, the matching `excel_write` **`record-step` JSON must include top-level `"replace_sheet": false`** (same level as `path` / `sheet` / `rows`). Omitting it or using `true` **recreates** the sheet → contradicts “append” semantics
   - **⚠️ Do NOT execute any `record-step` during the parsing phase — only build the plan**
   - Persist the plan via `plan-set` (step numbers must be consecutive from 1 to N, no gaps)
   - Enter the [Parse Confirm → Step-by-step Execute] protocol (see below)
4. **Parse `[rule]`/`[约束]`**:
   - Extract each constraint individually and apply it during action decomposition

#### Quick reference

**`[var]` examples:**

| Declaration | Type | Generated code |
|-------------|------|---------------|
| `output_path = '~/Desktop/result.docx'` | Constant | `CONFIG["output_path"] = "~/Desktop/result.docx"` |
| `query_time = ### current time, minute precision, format MM/DD HH:MM ###` | Dynamic | `query_time = datetime.datetime.now().strftime(...)` |
| `api_key = ### env var MY_API_KEY ###` | Dynamic | `api_key = os.environ.get("MY_API_KEY")` |
| `urls:` + indented URLs | Constant list | `CONFIG["urls"] = ["url1", "url2"]` |

**`${variable_name}` references:**

| Location | Example | AI generation behaviour |
|----------|---------|------------------------|
| Inside `[do]` | `Extract: name, rating, ${query_time}` | `query_time` assigned a runtime expression generated by AI |
| Inside `[rule]` | `${query_time} format must match the table header` | Written as a formatting constraint in generated code |

#### Full example

```
[var]
query_time = ### current system time, precise to the minute, format MM/DD HH:MM ###
output_path = '~/Desktop/Airbnb/hotelCompare.docx'
urls:
  https://www.example.com/room/123
  https://www.example.com/room/456

[do]
1. Visit each URL in urls one by one
2. Extract 5 fields per page: name, rating, price, ${query_time}
3. Organise into a table: name | rating | price | query_time
4. Append to the Word file at output_path (create if it does not exist)
   → final `word_write` **must** include `"mode":"append"` (otherwise default overwrites the file)

[rule]
- Both URLs share the same site structure; reuse selectors with a loop
```

> After parsing the structured description, **do not start recording immediately**. First output a confirmation summary (variables / static config / step count / constraints), and wait for user confirmation before entering the step-by-step recording flow.

#### ⛔ Serial Execution Protocol after Structured Task Parsing (mandatory)

> **This is a hard rule with highest priority. Violating it causes step confusion and data errors.**

**Phase 1 — Parse (zero `record-step` calls)**

After receiving a task description containing `[do]`/`[步骤]`, immediately output the following fixed summary and **stop**:

```
📋 Task Parse Summary
─────────────────────────────
🔢 [var] Dynamic variables: {N}
   • key1 = expression1  (omit if none)
📦 [var] Static config: {N} items
   • key: value  (omit if none)
📌 [do]  Execution plan ({N} steps):
   1. Atomic operation description 1  (≤2 record-step calls)
   2. Atomic operation description 2
   ...
⚙️  [rule] Constraints: {N}  (omit if none)
   • constraint 1
📝 Office output: append to Word / output_path → state **word_write uses mode=append**; append rows to xlsx / keep sheet data → state **excel_write uses replace_sheet=false** (avoids default sheet wipe)
─────────────────────────────
Confirm, then say "continue" or "1" to start recording step 1/{N}.
```

> **Never auto-continue after the summary. Stop and wait for user confirmation.**

**Phase 2 — Step-by-step execution (one step per conversation turn, strictly serial)**

Once the user confirms, follow the **exact same protocol as the Anti-timeout rule**:

1. Execute the **current step's** `record-step` calls (≤2), capture screenshot.
2. End with this fixed format:
   ```
   📍 Progress: {current}/{N} done
   ✅ {step description}
   📸 Screenshot: {path}
   Confirm the screenshot, then say "continue" or "1" to run step {next}/{N}.
   ```
3. **Stop. Do not execute the next step. Wait for user confirmation.**
4. On receiving a shortcut confirmation, call `plan-next`, execute the next step. Repeat until complete.
5. After all steps finish:
   ```
   🎉 All {N} steps recorded!
   Say "#end" to generate the RPA script.
   ```

> **Shortcut confirmations:** `continue`, `1`, `next`, `ok`, `y`, `go` (case-insensitive, equivalent).  
> Any **non-shortcut** message → treat as a new instruction; process it, then ask whether to resume the plan.

---

### Single-step recording protocol (for every user instruction)

> #### ⚠️ exec tool compatibility: `--from-file` rule
>
> OpenClaw's `exec` tool has a built-in **preflight security check** that refuses shell arguments containing complex JSON (multi-line code, braces, special characters), producing:
> `exec preflight: complex interpreter invocation detected`
>
> **Rule:** When the action is `python_snippet` / `excel_write` / `word_write` / `api_call` / `merge_files` / `extract_by_vision`,
> or whenever the JSON body spans more than one line, **always** write the JSON to a temp file first and pass it with `--from-file`:
> ```bash
> # 1. Use the Write tool to write the full JSON to /tmp/rpa_step.json
> # 2. Then run:
> python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step --from-file /tmp/rpa_step.json
> ```
> Simple single-line JSON (e.g. snapshot, goto) can still be passed inline:
> ```bash
> python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{"action":"snapshot"}'
> ```

> #### ⛔ Hard Constraint: Vision mode locked → `extract_text` permanently banned
>
> **Either of the following conditions triggers this constraint for the entire recording session — no exceptions, no temporary bypasses:**
> 1. The **decomposition / `plan-set` plan** already specifies `extract_by_vision` for this step
> 2. The current `page.url` hostname **matches the heavy SPA domain list** (§SPA Detection)
>
> **Once triggered, the following are strictly forbidden — regardless of what CSS classes appear in the snapshot, and regardless of price/title strings being visible on screen:**
>
> | ⛔ Forbidden action | Why |
> |---|---|
> | Sending `extract_text` (any CSS selector) | Recorder rejects immediately with an error; wastes a record-step round-trip |
> | Using `dom_inspect` to derive field CSS | Hashed classes change every build; the selector will be stale on the next run |
> | Scanning snapshot output to "find the price/title selector" | Meaningless on SPAs |
> | Sending a "test" `extract_text` to see if it works | Even if it succeeds, the generated script breaks when the class rotates |
>
> **Once triggered, only the following are allowed:**
>
> | ✅ Allowed action | Notes |
> |---|---|
> | `goto` / `wait` / `scroll` / `click` | Navigation and interaction |
> | `snapshot` | **Only** to confirm the page opened / for scroll positioning — **not** to find field CSS |
> | `extract_by_vision` | Screenshot → vision API → direct field extraction; the only legal extraction method |
>
> **Recorder hard gate (enforced at code level):** `extract_text` on any heavy-SPA host is rejected server-side (error returned, no script line written). Override only possible with `"force_extract_text": true` in the JSON (expert fallback, not recommended).  
> The full `snapshot → CSS → extract_text` recipe in this section **only applies to non-SPA sites** and is completely inapplicable to tasks locked to vision mode.

#### Step 1: Get current page elements (free, not written to script)
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{"action":"snapshot"}'
```
→ Returns all interactive elements and their **real CSS selectors** (e.g. `#search-input`, `input[name="q"]`, `[aria-label="Search"]`).

#### Step 2: Choose the target CSS from the snapshot
- **Exception (overrides this step):** The task already uses **`extract_by_vision`**, or the hostname **matches the heavy-SPA list** → **skip** CSS derivation for fields to extract; do not use `extract_text` for listing title/price, etc.
- **Must** use the real `sel` from the snapshot — **do not guess** (for sites where **`extract_text` is allowed**).
- **Default to progressive probing** (below): do not expect one `snapshot` to cover the whole page; if the target is missing, loop **scroll → wait → snapshot**, and use **`dom_inspect`** when needed.
- If there is no valid selector, the element may be below the fold — `scroll` first, then `snapshot` again.

#### Step 3: Perform an action (pick one)

| action | target | value | Notes |
|--------|--------|-------|--------|
| `goto` | URL string | — | Navigate: `wait_until=domcontentloaded` + 1.5s SPA settle |
| `snapshot` | — | — | Current DOM + content blocks (not logged to script) |
| `fill` | CSS | text | **Only** `<input>` / `<textarea>` — **not** native `<select>` |
| `select_option` | `<select>` CSS | **option value** (see below) | Native `<select>`: `locator.select_option(...)`. Optional `"select_by": "label"` → `value` is visible text; `"index"` → numeric index |
| `press` | Key name e.g. `Enter` | — | Key press, then wait for stability |
| `click` | CSS | — | Click, then wait for stability |
| `scroll` | — | pixels | Scroll down by N pixels |
| `scroll_to` | CSS | — | **Scroll element into view (lazy-load)**, then `wait` + `snapshot` |
| `dom_inspect` | Container CSS | — | **Debug:** list child structure under a container (**not logged** to script); use to infer list/title selectors |
| `extract_text` | CSS | output filename | Text from multiple elements → `~/Desktop/<filename>` (in-page `querySelectorAll`; `:has-text()` **does not** work). **Rejected on built-in heavy-SPA hosts** — use `extract_by_vision`; experts may set **`"force_extract_text": true`**. |
| `extract_by_vision` | — | output filename | **Vision LLM extraction:** screenshot → multimodal API → same kv file format as `extract_text`. Fields in JSON body: **`fields`**, **`model_key`** (`qwen` / `gemini`), **`api_key`**, optional **`crop_selector`**. **Must** use `--from-file` for the step JSON. |
| `api_call` | — | — | **HTTP** (independent of the page): either full **`url`**, or **`base_url` + `params`**. Optional **`method`** (default `GET`), **`headers`**, **`body`** (POST JSON), **`save_response_to`** (relative path under `~/Desktop`). **Secrets:** in `params` or `headers` string values, use **`__ENV:ENV_VAR_NAME__`** (e.g. `"apikey": "__ENV:ALPHAVANTAGE_API_KEY__"`). **If the step also has an `"env"` field** (e.g. `{"ALPHAVANTAGE_API_KEY":"real_key"}`), the key is **written directly into the generated script** — no `export` needed for replay; omitting `env` generates `os.environ.get("VAR", "")` and requires `export` before replay. |
| `merge_files` | — | — | **Merge Desktop files** (pure local, no browser): **`sources`** (list of filenames under `~/Desktop`), **`target`** (output filename), optional **`separator`** (default `"\n\n"`). Typical use: combine an `api_call` JSON with an `extract_text` news file into a single brief. |
| `excel_write` | — | — | **Write `.xlsx`** (openpyxl; **no Microsoft Excel required**). **⛔ Default `replace_sheet` omitted or `true`:** the same-named worksheet is **deleted and recreated** — all previous rows are lost. If the task requires **appending rows** to an existing workbook, **adding at the bottom of the sheet**, or **preserving existing sheet data**, the JSON **must** explicitly set **`"replace_sheet": false`** (top level, alongside `path` / `sheet` / `rows_from_json`) so new **`rows`** are **appended** after existing data; natural language alone does not flip this (same pitfall as Word `mode`). **`path`** or **`value`**: relative filename (recording writes under **~/Desktop**; generated script uses `CONFIG["output_dir"]`). **`sheet`**: worksheet name. **`headers`**: optional list of header strings. **Row data — pick one**: ① **`rows`**: static 2-D array of cell values; ② **`rows_from_json`**: `{"file":"x.json","outer_key":"batches","inner_key":"lines","fields":["f1","f2"],"parent_fields":["batch_id"]}` — dynamically flatten a nested JSON array from Desktop (`inner_key`/`parent_fields` optional); ③ **`rows_from_excel`**: `{"file":"发票导入_本周.xlsx","sheet":"发票侧","skip_header":true}` — copy data rows from another xlsx sheet. **`freeze_panes`**: optional e.g. `"A2"`. **`hidden_columns`**: optional list of **1-based** column indexes to hide (e.g. `[1]` hides column A). **`replace_sheet`**: `true` (default, delete same-named sheet then recreate) or `false` (**append `rows` after existing rows** when the sheet already exists). **If the user says "append rows", "add at the end of the table", or "keep existing data", always use `replace_sheet: false` — even if "create file" is also mentioned** (missing file still creates a new workbook). **Multi-source aggregation:** use a `python_snippet` to merge all intermediate data into a complete `rows` array first, then write with a **single** `excel_write`; do not call `excel_write` repeatedly to append one row at a time. |
| `word_write` | — | — | **Write `.docx`** (python-docx; **no Word app required**). **⛔ Default when `mode` is omitted = `"new"`:** generated script uses `_wmode='new'` and **overwrites the entire file**. If the task requires **append**, **end of file**, **don’t overwrite**, or **append to `${output_path}`**, the JSON **must** explicitly set **`"mode":"append"`** — otherwise behaviour contradicts the task. **`path`** or **`value`**: relative filename (paths starting with `~/` are expanded as absolute). **`paragraphs`**: list of strings (one paragraph each). **⛔ like `rows`, `paragraphs` is a static literal** — codegen serialises the array verbatim into the script; whatever you write at record time is frozen forever on replay. **Never put the current timestamp, extracted values, or any dynamic data inside `paragraphs`.** For a dynamic timestamp use the **`{{now:fmt}}`** placeholder (e.g. `"Query time: {{now:%Y-%m-%d %H:%M}}"`); codegen replaces it with a `datetime.datetime.now().strftime(...)` call at runtime. For other dynamic values use `python_snippet` to build and write the docx directly. **`table`**: optional — inserts a table after paragraphs (auto-applies "Table Grid" style); **row data — pick one**: ① **`rows`**: 2-D array, **for truly static/template data only** (never fill in values extracted from web pages); ② **`rows_from_json`**: `{"file":"rows.json"}` — read a JSON file from Desktop (content must be a 2-D array), ideal for dynamically scraped data; **⚠️ if `rows_from_json.file` starts with `~/`, write the full path (e.g. `"~/Desktop/Airbnb/rows.json"`); without `~/` it is relative to `~/Desktop/`**. **`mode`**: `new` (default, create or overwrite) or `append` (**auto-creates if file does not exist; appends to the end if it does**, without overwriting existing content). **If the user says "append", "add to the end", or "don't overwrite", always use `append` — even if "create" is also mentioned**. **Multi-source aggregation:** use `python_snippet` to assemble all extracted data into a complete rows array and save as JSON, then use `word_write` + `rows_from_json`; **never fill scraped values into the static `rows` array**. |
| `python_snippet` | — | — | **Inject Python code directly into the generated script.** **`code`**: multi-line string. Use for **file I/O, data parsing, datetime generation, openpyxl/docx writes** — operations that have no dedicated action. **The code is executed immediately at record time** to validate dependencies and logic. **⛔ NEVER access the DOM inside python_snippet** — the sandbox's `page` object raises an error by design; attempting to call `page.evaluate()` and then hardcoding the values you see on screen will make the generated script completely static (data never updates on replay). DOM extraction must use `extract_text` / `extract_by_vision` / `click` / `fill` actions. |
| `wait` | — | milliseconds | Wait |

> `extract_text` supports an optional **`"limit": N`** — only the first **N** matches.  
> Optional **`"extract_ready_timeout_ms": 30000`** (default matches generated `CONFIG["extract_ready_timeout_ms"]`): **SPA content-ready wait** before `querySelector` extraction (same helper as `extract_by_vision`), reducing empty reads during skeleton phases. **`snapshot`** / **`dom_inspect`** also wait before DOM capture during recording.
>
> **⛔ Never fill web-extracted values into `word_write.table.rows` or `excel_write.rows`** — these static arrays are serialized as literals at record time and never update on replay. Web-extracted data must flow through the three-layer Extract → Aggregate → Write pattern (see §Universal task decomposition pattern).

---

### SPA detection & vision extraction triggers (mandatory)

#### When to decide: **task decomposition** (mandatory)

- **Whether the site is treated as a heavy SPA and whether extraction defaults to vision** must be decided **before** you call `plan-set` and persist the plan — **not** when you finally reach the “extract” step.
- **Inputs available at decomposition time (no browser open yet):** URLs in the user text, links in `[var]` / `urls`, and any `goto` targets implied by `[do]` / `[步骤]`. Parse **hostname** for each URL and match the **heavy SPA host list** below.
- **Reflect it in the plan:** Sub-task strings should state this explicitly (e.g. “After opening the Airbnb listing, use **`extract_by_vision`** to read …”), or the plan summary shown to the user should say “heavy SPA → vision for all field reads”. Later `record-step` calls should **follow the plan** and use `extract_by_vision` on extract steps — avoid a wasteful `extract_text` first pass.
- **Fallback:** If you missed it at decomposition and only discover `extract_text` == 0 or hashed classes at run time, still follow the “runtime” rows below; apply the hostname check earlier on similar tasks next time.

**Switch to `extract_by_vision` in these cases — do not skip:**

| Signal | What to do |
|--------|------------|
| **Decomposition:** Any step’s URL hostname **matches the heavy SPA host list** and that step reads text/price from the page | **Default to vision:** write this into the plan; at execution, use **`extract_by_vision` directly** — **do not** try `extract_text` first (**recorder rejects `extract_text` on those hosts** unless `force_extract_text`) |
| **Runtime (fallback):** `extract_text` returns 0 matches, and a second attempt is still 0 | Start the vision-model dialog flow immediately |
| **Runtime (fallback):** `dom_inspect` shows mostly hashed class names (e.g. `.hpipapi`, `.u174bpcy`) | Use vision — CSS selectors are unreliable |

#### Can you tell a SPA from the URL immediately?

- **Random unknown sites:** You **cannot** prove SPA vs not from the URL alone; mark “unknown” at decomposition and fall back to runtime signals (`extract_text` failure, DOM).
- **Hosts in the table below:** **Yes — and you must classify them at decomposition.** For every user-supplied URL, parse **hostname** (`urllib.parse.urlparse`, lowercase) and match — **no browser, no `record-step`**. If a step’s URL was incomplete at decomposition, you may re-check **`page.url`** after `goto`, but that is **not** an excuse to defer the first decision until the extract step.

**Heavy SPA host list (matching rules)**

- Lowercase the hostname; **match if any**:
  - hostname **equals** an entry, or
  - hostname **ends with** `.<entry>` (subdomains, e.g. `www.airbnb.cn` matches `airbnb.cn`).
- **Table (extend over time; matched hosts are treated as SPA by default):**

| Root / example host (lowercase) | Notes |
|--------------------------------|--------|
| `airbnb.cn`, `airbnb.com`, any `*.airbnb.*` | Listings / travel |
| `booking.com` | |
| `hotels.com`, `agoda.com`, `expedia.com`, `expedia.*`, `trivago.com` | OTAs |
| `trip.com`, `ctrip.com`, `fliggy.com`, `hotels.ctrip.com`, etc. | Ctrip / Trip / Fliggy |
| `xiaohongshu.com`, `xhslink.com` | |
| `douyin.com`, `iesdouyin.com` | |
| `tiktok.com` | |
| `instagram.com`, `facebook.com` | |
| `linkedin.com` | |
| `twitter.com`, `x.com` | |
| `maps.google.com`; or `www.google.*` / `google.*` **with** `/maps` in the path | Google Maps |
| `openrice.com`, `yelp.com`, `shein.com`, `shopee.*`, etc. | Large content / commerce SPAs (examples) |

**When the host matches and the task includes extraction — say this in the opener:**

- State clearly: **“This hostname is on our heavy-SPA list; to avoid wasted retries, we’ll default to vision for reading fields from the page.”** Then continue with the existing A/B model dialog.

#### Reuse the open Playwright page inside the same recording session (mandatory)

- **Situation:** The user already started **`record-start`**, then used `goto` / clicks to reach the target SPA page, and you now switch to vision extraction.
- **Do this:** **Do not** `record-end` and `record-start` “from scratch”. **Do not** ask the user to reopen the browser or revisit the same URL for vision alone. Send the next **`record-step`** in the **still-running** session with **`action`: `extract_by_vision`**.
- **Why:** `recorder_server` screenshots the **existing session `page`** (optional `crop_selector`), then calls the vision API — **same browser context and cookies**, matching what was on screen in the previous step.
- **Exception:** Only if recording never started, the session already ended, or the task name must change should you `record-start` again and navigate to the target URL.

**After a trigger, use this dialog verbatim (do not omit):**

```
⚠️  Dynamic rendering detected — CSS selectors are not stable for extraction.

We recommend **vision mode**: a multimodal model reads a screenshot and extracts
fields without relying on CSS class names, so site redesigns hurt less.

Choose a vision model:
  A) Qwen3-VL-Plus (Alibaba Cloud Bailian multimodal — recommended)
  B) Gemini 3 Pro (Google AI Studio — high precision)

Reply A or B (Enter = A):
```

After the user picks (example for A):

```
✅ Selected: Qwen3-VL-Plus

Please paste your API key (from Bailian console):
  👉 https://bailian.console.aliyun.com → API Key management
  (You only need to provide it once; later recordings reuse it.)

Paste API key:
```

After receiving the key, **validate immediately** (`_validate_vision_key`). On success:

```
✅ API key is valid. Vision extraction will use these fields:
  • [list field names]

We will screenshot **the page already open in the recording browser** (no new browser). Say "#continue" or "1" to proceed.
```

**Vision model quick reference:**

| Code | model_key | model | base_url |
|------|-----------|-------|----------|
| A | `qwen` | `qwen3-vl-plus` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| B | `gemini` | `gemini-3-pro-preview` | `https://generativelanguage.googleapis.com/v1beta/openai/` |

---

### `extract_by_vision` action spec

**Shape:**

```json
{
  "action": "extract_by_vision",
  "fields": ["listing_title", "price", "room_name"],
  "value": "/tmp/rpa_step_vision.txt",
  "model_key": "qwen",
  "api_key": "sk-xxxxxxxx",
  "crop_selector": "#main-content"
}
```

**Parameters:**

| Field | Type | Meaning |
|-------|------|---------|
| `fields` | `string[]` | Field names to extract |
| `value` | `string` | Output kv file path (same format as `extract_text`) |
| `model_key` | `string` | `"qwen"` or `"gemini"` |
| `api_key` | `string` | Vision API key (from user; validated at record time) |
| `crop_selector` | `string` (optional) | CSS selector for a crop region; omit for full-page screenshot |
| `vision_ready_timeout_ms` | `number` (optional) | Max milliseconds to wait for real content before the vision screenshot (skeleton gone, large images decoded, or enough body text); default `45000`, raise for slow sites like Airbnb (`60000`). |

**Rules:**

0. **Reuse the live page** — same as above: `extract_by_vision` captures the **current `page`** only; no extra browser launch; after switching to vision on an SPA, issue the next `record-step` immediately.
1. **Recording must call the real API** — no mocks; the step succeeds only when fields are extracted. **Before the screenshot**, the recorder waits for SPA content to be ready (`networkidle` best-effort + polling for decoded images / enough body text) so skeleton screens are not sent to the vision model; increase `vision_ready_timeout_ms` if a site is still slow.
2. **Keys are cached locally** — `~/.openclaw/rpa/vision_keys.json` for reuse across sessions.
3. **Output matches `extract_text`** — kv text files for downstream `python_snippet` via `_parse_field`.
4. **After `record-end`** — `{script_stem}_vision_setup.md` is generated (model, fields, rough cost notes).

---

#### Action responsibility boundaries (universal principle)

**Decision rule: does this operation require a live browser page?**
- **Yes** → use a browser action (`extract_text`, `extract_by_vision`, `click`, `fill`, `goto`, `scroll`)
- **No** → use a file/compute action (`python_snippet`, `excel_write`, `word_write`)

| Operation type | Must use | Forbidden |
|----------------|----------|-----------|
| Extract text from the DOM (stable / static markup) | `extract_text` (one step per field) | ~~python_snippet~~ |
| Extract text from the DOM (heavy SPA / dynamic / hashed classes) | `extract_by_vision` | ~~extract_text~~ |
| Click / fill / navigate / scroll | `click` / `fill` / `goto` / `scroll` | ~~python_snippet~~ |
| Call an external HTTP API | `api_call` | ~~python_snippet~~ |
| Read files / parse / format / write output | `python_snippet` | — |
| Write Excel (static rows) | `excel_write` | — |
| Write Word (static rows) | `word_write` | — |

#### python_snippet responsibility model

```
Upstream (browser actions)       python_snippet          Downstream
──────────────────────────  →  ──────────────────────  →  ──────────
extract_text / extract_by_vision → .txt   read files      .docx
api_call      → .json            parse / aggregate        .xlsx
                                 datetime.now()           .json/.txt
                                 transform / format
```

**python_snippet can only:**
- Read files produced by earlier steps (`Path.read_text()` / `json.load()` / `load_workbook()`)
- Perform pure computation (regex, aggregation, formatting, `datetime.datetime.now()`, etc.)
- Write output files (`Document.save()` / `wb.save()` / `Path.write_text()`)

**python_snippet absolute prohibitions:**
```python
# ❌ DOM access — page raises an error in the validation sandbox
page.evaluate(...)
page.locator(...)

# ❌ Hardcoding values observed at record time — script will never refresh on replay
field_value = "value copied from screen during recording"
```

> **Why hardcoding is dangerous:** `python_snippet` is validated once at record time and its  
> code string is embedded verbatim in the generated script. Hardcoded values never change  
> on replay, regardless of what the page currently shows.

---

#### Core recording principle: Generate code → Run and verify → Save verified code

> **This is the fundamental guarantee of the entire recording mechanism.** Every line saved into the `.py` file must be code that "executed in a real environment and produced correct results dynamically" — not code that "happened to output correct results because it contained hardcoded values."

```
Every recorded step follows three phases:

  Phase 1 — Generate code
    AI generates Playwright / Python code for the intended action
    extract_text  → code that reads from the live DOM
    python_snippet → code that reads .txt files → parses → writes document

  Phase 2 — Run and verify
    extract_text  → executes in real browser; confirms .txt file is non-empty
    python_snippet → executes in sandbox; confirms real data was read from
                     files and document was generated successfully

  Phase 3 — Save verified code
    Verification passed → code written to recording log ✅
    Verification failed → rewrite code, re-verify; skipping is not allowed
```

**python_snippet verification criteria (all three must pass):**

| Condition | Description |
|-----------|-------------|
| ① Passes the structural gate | When this session has `extract_text` steps, the code **must** call `_parse_field()` referencing a registered extract file; otherwise the server rejects immediately |
| ② Sandbox execution produces correct output | Word / Excel generated successfully, content sourced from `_parse_field` dynamic reads |
| ③ Pure-compute snippets | Snippets with no upstream `extract_text` (e.g. datetime only) are not constrained by the gate |

> **How the gate works:** Each `extract_text` registers `filename → field names` in the server's internal table — **no extracted values are returned to the AI** (only field names + count summary). On `python_snippet` submission the server checks: ① code contains `_parse_field`; ② the filename in `_parse_field` appears in the registry. Both must pass, otherwise the step is rejected with a concrete hint.

> **How to resolve a gate error:** Follow the hint — rewrite field reads as `_parse_field(CONFIG["output_dir"] / "filename", "field_name")` and resubmit.

---

#### extract_text temp file format: fixed `key: value`

`extract_text` writes a strict **kv format** temp file (UTF-8, bilingual field names and values supported):

```
# Example: hotel1.txt (three extract_text calls appended to one file)
民宿名字: 新今宮1号/Osaka Namba 1min
评分: 4.91
price: ¥368/晚

# Multi-value fields (selector matches multiple elements) use .N suffix
tag.0: Entire rental
tag.1: Boutique apartment
```

**`_parse_field` — standard reader (auto-injected into generated scripts, no import needed):**

```python
# index=0 (default): first value; index=-1: last; index=None: return list
name  = _parse_field(CONFIG["output_dir"] / "hotel1.txt", "民宿名字")
score = _parse_field(CONFIG["output_dir"] / "hotel1.txt", "评分")
price = _parse_field(CONFIG["output_dir"] / "hotel1.txt", "price")
tags  = _parse_field(CONFIG["output_dir"] / "hotel1.txt", "tag", index=None)  # → list
```

> `_parse_field` raises `RuntimeError` when a field is missing — it **never** returns `None`.
> Fail loudly. Never silently produce stale data.

---

#### Universal task decomposition pattern: Extract → Aggregate → Write (three layers)

Applies to any "scrape web data → write local document/table" task — works identically whether you use `extract_text` or `extract_by_vision`:

```
[Extract layer]   For each data source (URL / page section):
                    goto → scroll (wait for lazy render)
                    extract_text OR extract_by_vision → page_{N}.txt (auto-appends kv format)

[Aggregate layer] After all extractions, one python_snippet:
                    ⚠ Steps are variable-isolated: cannot reference variables from other steps
                    _parse_field(CONFIG["output_dir"] / "page_{N}.txt", "field name") to read
                    Compute dynamic values (timestamps, calculations) here — never hardcode
                    To pass data to word_write / excel_write → write an intermediate JSON file first

[Write layer]     word_write / excel_write:
                    word_write: append semantics → "mode":"append" (default new overwrites file)
                    excel_write: append to existing sheet → "replace_sheet": false (default true wipes sheet)
                    rows_from_json: {"file": "rows.json"}   ← reads JSON, fully dynamic
                    rows: [["fixed value"]]                 ← static template data only
```

> **Step variable isolation is the core constraint:** each `python_snippet` runs in an isolated scope — variables set in step A are completely invisible in step B. **The only way to pass data between steps is write a file → read a file.**

> `word_write` / `excel_write` `rows` static arrays **are serialized as literals at record time and never update on replay.** Any web-extracted data must use `rows_from_json` or a `python_snippet` that writes the document directly.

**Standard two-step pattern for dynamic Word / Excel rows (shared aggregate JSON):**

```python
# Step N: python_snippet — aggregate extraction files → save JSON
import json, datetime
ts = datetime.datetime.now().strftime("%m/%d %H:%M")
rows = []
for n in range(1, total + 1):            # total = number of data sources
    f = CONFIG["output_dir"] / f"page_{n}.txt"
    rows.append([
        _parse_field(f, "field1"),
        _parse_field(f, "field2"),
        ts,                              # dynamic timestamp, refreshed every run
        CONFIG.get("custom_var", ""),
    ])
(CONFIG["output_dir"] / "rows.json").write_text(
    json.dumps(rows, ensure_ascii=False), encoding="utf-8"
)
```

```jsonc
// Step N+1a: word_write reads JSON; append to existing docx needs mode
{"action":"word_write","path":"output.docx","mode":"append",
 "table":{"headers":["field1","field2","time","custom"],
          "rows_from_json":{"file":"rows.json"}}}
// Step N+1b: excel_write reads JSON; append to existing sheet needs replace_sheet
{"action":"excel_write","path":"data.xlsx","sheet":"Sheet1",
 "rows_from_json":{"file":"rows.json"},
 "replace_sheet": false}
```

**Field reading rule inside python_snippet:**

```python
# ✅ Correct: use _parse_field — raises RuntimeError if field missing
name  = _parse_field(CONFIG["output_dir"] / "page_1.txt", "name")
score = _parse_field(CONFIG["output_dir"] / "page_1.txt", "rating")
ts    = datetime.datetime.now().strftime("%m/%d %H:%M")   # dynamic variable

# ❌ Forbidden: hardcoding a literal value observed during recording
name = 'Some Specific Product Name ...'   # ← this line must never appear in generated code
```

> **Silent fallback is the most dangerous failure mode**: the script executes without error, the output file looks populated, but every run returns the same stale data from recording time. `_parse_field` raises `RuntimeError` on missing fields — **crash loudly rather than silently write wrong data.**

| Checklist | Pass criteria | Fix |
|-----------|--------------|-----|
| Does every target field have an extraction step? | Each field has a corresponding `extract_text` / `extract_by_vision` step | **Add missing extraction steps** |
| Are all output files written to disk? | Each `page_{N}.txt` exists and is non-empty | Check upstream extraction step results |
| Any hardcoded page data in python_snippet? | All dynamic data read via `_parse_field` | Replace literals with `_parse_field` calls |
| Does word_write.paragraphs contain dynamic data? | Timestamps → use `{{now:fmt}}` placeholder; other dynamic values → use `python_snippet` to write docx | Literal strings baked in at record time → replay always shows stale data |
| Does word_write.rows contain web data? | If yes, must switch to `rows_from_json` | Add an aggregate python_snippet step |
| Does the task require **appending** to an existing Word file? | `word_write` JSON includes **`"mode":"append"`** (top level, alongside `path`) | Omitting it yields `_wmode='new'` and **overwrites** the docx |
| Does the task require **appending rows** to an existing Excel sheet? | `excel_write` JSON includes **`"replace_sheet": false`** (top level) | Default `true` **recreates** the sheet and **wipes** prior rows |

> **Field label (shown in the file):** optional **`"field"`** or **`"field_name"`** (e.g. `"title"`, `"rating"`, `plot`). Output is formatted as **`【字段：{name}】`** + a separator line + body; if omitted, **`context`** is used as the label.

> **Multiple `extract_text` steps with the same `value` filename:** the generated script **writes** on first use, then **appends**; each block is labeled **`【字段：…】`**.

**Native `<select>` example (Sauce Demo `inventory.html` sort):** use `snapshot` to read the `<select>` `sel` and each `option` value. Price high → low is `hilo` — do **not** use `fill` or arrow keys to guess:

```json
{"action":"select_option","target":"[data-test=\"product-sort-container\"]","value":"hilo","context":"Sort by price high to low"}
```

### Scenario 1: quotes + news page + local brief (browser + API + file)

**Goal:** One workflow with **REST quote data**, a **browser news list**, and a **local brief** (`extract_text` and/or `api_call` **`save_response_to`**).

**User prompt checklist (when the flow includes `api_call`):** Ask the human (or infer from the API docs) for **base URL**, **required query/body fields**, **header names** if auth is header-based, and **which env var name** will hold each secret (e.g. `ALPHAVANTAGE_API_KEY`). **Key embedding strategy:** if the user supplied the real key → put it in the step's `"env"` field; the code generator writes it **directly into the script** (no `export` needed). If no key provided → use `__ENV:VAR__` placeholder only and tell the user to `export` before replay.

**Suggested order (adjust per site):**

1. **`api_call`** — fetch daily OHLCV (or any documented endpoint); save JSON for replay/offline use. Include `"env"` if key is available — key is embedded in script.
2. **`goto`** — open a finance news page (e.g. Yahoo Finance symbol page).
3. **Progressive probing** — `scroll` / `wait` / `snapshot` (and `dom_inspect` if needed) until a stable news selector exists.
4. **`extract_text`** — **scoped** selector + `limit`; reuse the same **`value`** filename to **append** sections with **`【字段：…】`**.

**`api_call` example A — key written directly into script (user supplied key in `###` block):**

```json
{
  "action": "api_call",
  "context": "Alpha Vantage daily OHLCV",
  "base_url": "https://www.alphavantage.co/query",
  "params": {
    "function": "TIME_SERIES_DAILY",
    "symbol": "IBM",
    "outputsize": "compact",
    "datatype": "json",
    "apikey": "__ENV:ALPHAVANTAGE_API_KEY__"
  },
  "env": {"ALPHAVANTAGE_API_KEY": "user-supplied-real-key"},
  "method": "GET",
  "save_response_to": "ibm_time_series_daily.json"
}
```

Generated script contains `'apikey': 'user-supplied-real-key'` — runs directly, no `export` needed.

**`api_call` example B — key via env var (no key provided):**

```json
{
  "action": "api_call",
  "context": "Alpha Vantage daily OHLCV",
  "base_url": "https://www.alphavantage.co/query",
  "params": {
    "function": "TIME_SERIES_DAILY",
    "symbol": "IBM",
    "outputsize": "compact",
    "datatype": "json",
    "apikey": "__ENV:ALPHAVANTAGE_API_KEY__"
  },
  "method": "GET",
  "save_response_to": "ibm_time_series_daily.json"
}
```

Generated script contains `'apikey': os.environ.get("ALPHAVANTAGE_API_KEY", "")` — requires `export ALPHAVANTAGE_API_KEY=…` before replay.

---

### Progressive probing (default; replaces “one snapshot is enough”)

**Use for:** SPAs, long pages, sites where the nav fills the first snapshot lines, and lists below the fold. **Core idea:** multiple rounds of **scroll → wait → snapshot (and `dom_inspect` if needed)**, then **`extract_text` with a scoped selector** — **never** use bare global `h3` / `a` for “headline list” style tasks.

**Why one snapshot is not “the whole page”:** the 📋 list is a **sample** (about 100 visible interactive nodes, ~20 section blocks) to cap tokens; **unrendered or unsampled regions** need **scroll + snapshot again** or **`dom_inspect`**.

**Standard flow (before extracting a block / list / titles):**

1. **`goto`** URL (SPA settle is built in).
2. Optional **`wait`** 500–2000 ms depending on the site.
3. **`scroll`** `value=800~1200` (or 1000–2000), **repeat 1–2 times** for below-the-fold and lazy load.
4. **`wait`** `value=600~2000` after scrolls.
5. **`snapshot`** — check 📋 / 🗂️ for the **target region** (list rows, block headings, containers with `data-testid`, etc.).
6. **If missing** — **`scroll`** again (~800px) and repeat 4–5; **if a parent looks right but children are unclear** — run **`dom_inspect`** on that container and derive `target` from children (`a`, `h3`, testids).
7. **`extract_text`:** `target` **must include a container prefix**, e.g. `"[data-testid=\"…\"] h3 a"`, `main h3`, `#nimbus-app …` (from snapshot / `dom_inspect`) — **do not** use a global `"h3"` alone for news-style headlines. Use **`limit`** for first N.

**Short recipe:**
```
goto → (scroll + wait) × 1–2 → snapshot → if no target, more scroll or dom_inspect → extract_text (scoped + limit)
```

> Lazy-load timing varies; if the target still does not appear, scroll ~800px, **`snapshot` again**, retry.

### Reading the `snapshot` output

`snapshot` returns two parts:

**1. `📋 Interactive elements`** — each line:
```
CSS selector  [placeholder=...]  「text preview」
```
- Use `sel` directly as the next `target`.
- If the element has no id/aria/testid, **the nearest parent** may be prepended, e.g. `[data-testid="news-panel"] h3`.

**2. `🗂️ Content blocks`** — each line:
```
[data-testid="block-id"]  ← heading 「Block title」
```
- To scope extraction, combine the block selector with a child selector:
  ```
  target = "[data-testid=\"target-block\"] h3 a"   ← only that block, not other sections
  ```
- Without `data-testid`, you can use Playwright text filters, e.g. `section:has(h2:text("Section title")) li`.

### Selector strength rules (extract_text target must follow)

**Bare tags (`h3`, `a`, `li`, …) are never unique** — they appear in navs, sidebars, footers, and modals. A selector must **combine multiple signals** to pin the real target.

**Ranked by strength. When building `target`, use at least one strategy above “bare tag”:**

| Priority | Strategy | Generic pattern | When to use |
|:--------:|----------|----------------|-------------|
| 1 | **`main` / `[role="main"]` + child** | `main h3`, `main article h3`, `[role="main"] li a` | Almost every modern site has `<main>`; simplest universal scope |
| 2 | **Snapshot block id / data-testid + child** | `#content h3`, `[data-testid="…"] li` | When snapshot 🗂️ shows a clear container |
| 3 | **Attribute filter** | `a[href*="/news/"]`, `li[class*="item"]` | Link paths with keywords, or list items with recognizable class fragments |
| 4 | **Semantic tag nesting** | `article h2`, `section ul > li`, `[role="list"] a` | No id / testid — rely on HTML5 semantic tags |
| 5 | **Text anchor (Playwright `:has`)** | `section:has(h2:text("…")) li` | Snapshot has a visible section heading but the container has no id |
| 6 | **Exclude noise** | `h3:not(nav h3):not(header h3)` | Fallback when none of the above work |
| **Banned** | **Bare tag** | ~~`h3`~~, ~~`a`~~, ~~`li`~~ | **Never** use alone; even the engine’s `main` fallback may still hit nav areas |

**Workflow (universal):**
1. Run **snapshot**; find the container holding target content in the 🗂️ block list (check heading / sel).
2. Container has `id` / `data-testid` → use **strategy 2**.
3. Container has no identifiers → check for `<main>` → use **strategy 1**.
4. Still unclear → run **`dom_inspect`** on the candidate container; derive **strategy 3–5** from children’s tag / class / href.
5. Compose, then `extract_text`.

**Recorder fallback:** If `target` is still a bare tag (letters only, no `#` `.` `[`, or space), the engine scopes to `<main>` / `[role="main"]` when present — but this is a **last resort**, not a substitute for the composite selectors above.

### Common scenarios

| Scenario | Suggested approach |
|----------|-------------------|
| Content blocks (news/list/comments) | scroll → wait → snapshot → pick selector from 🗂️ |
| Target not in snapshot | Not rendered or not sampled — scroll ~800px → snapshot again; or **`dom_inspect`** a likely parent |
| Repeating list/card rows | `extract_text` + `limit` for first N |
| “Load more” / expand | click → wait → snapshot → `extract_text` |

Example (navigate):
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "goto",
  "target": "https://example.com",
  "context": "Open target page"
}'
```

Example (fill search box; selector from snapshot):
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "fill",
  "target": "#search-input",
  "value": "keyword",
  "context": "Type keyword in search (selector from snapshot)"
}'
```

Example (extract list after scroll / lazy-load):
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "extract_text",
  "target": "[data-testid=\"content-list\"] h3 a",
  "value": "output.txt",
  "limit": 5,
  "field": "titles",
  "context": "First 5 titles (selector from snapshot block)"
}'
```

#### Step 4: Report to the user (fixed format)
```
✅ [Step N] {context}
📸 Screenshot: {screenshot_path} (browser state is visible on screen)
🔗 Current URL: {url}
Confirm this step, then reply **continue**, **1**, or **next** for the following step.
```

#### Step 5: On failure
- Explain the error to the user.
- Optionally `snapshot` again for fresh selectors and retry.
- **Do not record failed steps** (no `code_block` on failure — script stays clean).

---

### State transitions (check every message)

- **`#end`** → **GENERATING**
- **`#abort`** → run:
  ```bash
  python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-end --abort
  ```
  → back to **IDLE**
- **`continue`** / **`1`** / **`next`** / **`ok`** / **`y`** / **`go`** → continue the **current** multi-step plan step (see anti-timeout rules and shortcut confirmations above)

---

## GENERATING

Execute in order — **do not skip steps**:

1. Reply: "⏳ Saving and compiling recording…"

2. Run:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-end
   ```
   → Close browser → compile real steps into a full Playwright script → save `rpa/{filename}.py` → update registry

3. ⚠️ **Output the template below verbatim. Do NOT rephrase, do NOT add offers like "Want me to run it for you?", do NOT improvise.**

   On success, print:
   ```
   ✨ RPA script generated! (from real recording; selectors verified in browser)

   📄 File: ~/.openclaw/workspace/skills/openclaw-rpa/rpa/{filename}.py
   📋 Recorded steps: {N}
   📸 Screenshots: ~/.openclaw/workspace/skills/openclaw-rpa/recorder_session/screenshots/

   Known limitations:
   • [If login was involved, remind user to log in before replay]
   • [Other caveats inferred from the recording; **do NOT** mention API keys or `export` commands — the generated script already checks for missing env vars at startup and prints instructions]

   To run this RPA later: if unsure what’s registered, send **`#rpa-list`** first to see **which recorded tasks are available**; then **`#rpa-run:{task name}`** (new chat) or **`run:{task name}`** (same chat).
   ```

4. **Do not LLM-rewrite the generated script** (agents must obey)
   - After successful `record-end`, `rpa/{filename}.py` is assembled by `recorder_server` `_build_final_script()` from real `code_block` segments — same source as `recorder_session/script_log.py`.
   - **Do not** generate a full replacement Playwright script from the task description alone; that drops recorder-validated selectors and `evaluate` semantics and often reintroduces `get_by_*` / `networkidle` patterns that diverge from the pipeline.
   - For behavior changes: **prefer** `record-start` and re-record the bad steps, then `record-end`; for tiny edits, patch **`rpa/*.py` locally** only, staying consistent with [playwright-templates.md](playwright-templates.md) (`CONFIG`, `_EXTRACT_JS`, `_wait_for_content`, `page.locator` + `page.evaluate`).

5. **Excel / Word — finalized layout**
   - **Primary path:** Use **`record-step`** **`excel_write`** / **`word_write`** during recording. After `record-end`, `recorder_server._build_final_script()` emits **one** `rpa/{filename}.py` with Office code **inside** `async def run()` (same `try` as Playwright / `api_call` / `merge_files`) and adds **top-level** `openpyxl` / `docx` imports when needed. **No** separate `rpa/*_office.py`.
   - **Fallback only:** If `task.json` flags Excel/Word but the recording has no `excel_write`/`word_write` steps, and the user gave explicit structure in chat, the agent may **append** supplemental code **only at the end** of that `.py` file — **never** replace recorder output.
   - **If details are missing:** do not invent business data; list required CONFIG / headers in the success message.

---

## RUN

Trigger: user message matches the **RUN** table above (`#rpa-run:` or `run:`); parsed `{task name}` is passed to `rpa_manager.py run` (**must match a registered name**; if unclear, user should **`#rpa-list`** first).

Meaning: **run an already-recorded script again** (repeat the same steps)—**not** start a new recording.

1. Reply: "▶️ Running 「{task name}」…"
2. Run:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py run "{task name}"
   ```
3. Capture stdout and summarize when done:
   ```
   ✅ Finished: 「{task name}」
   [stdout summary]
   ```
4. On error "task not found", list tasks:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list
   ```

---

## LIST

Trigger: **order 2** above — the whole message is only `#rpa-list` (case-insensitive).

Meaning: answer **“which recorded RPA scripts can I use right now?”** — same output as `rpa_manager.py list` / `registry.json`.

1. Reply: "📋 Listing recorded RPA tasks you can run…"
2. Run:
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list
   ```
3. Show **stdout** (light formatting OK); close with a short note that the names listed are **what’s available to run now**, and to execute one use **`#rpa-run:{task name}`** (new chat) or **`run:{task name}`** (this chat).

---

## Generated code quality (Recorder mode)

Because recording uses real CSS from a headed browser:

1. **Selectors are real** — every `target` comes from snapshot DOM, not guessed.
2. **Errors** — each step uses `try/except`, screenshot on failure, then re-raise.
3. **Paths** — outputs use `CONFIG["output_dir"]`.
4. **Portability** — generated `.py` runs standalone without OpenClaw.

---

## Recorder command log (audit: Playwright mapping per step)

- **During recording:** each `record-step` appends **one JSON line** (JSONL) to `recorder_session/playwright_commands.jsonl`.
- **Each line:** `command` (same JSON sent to the recorder: `action` / `target` / `value` / `seq`, …), `success`, `error`, `code_block` (Python fragment for the final RPA), `url`, `screenshot`.
- **Session bounds:** first line `type: session, event: start`; before successful `record-end`, append `event: end`, and copy the full log to `rpa/{task_slug}_playwright_commands.jsonl` for cross-check with `rpa/{task_slug}.py`.
- **`record-end --abort`:** deletes the whole `recorder_session` including the log.

---

## Example dialogue

```
User: #RPA
Agent: (ONBOARDING) … sign-up prompt…

User: Daily news scrape A
Agent: (deps-check A → record-start … --profile A) ✅ Chrome open…

User: Open example-news.com, search "AI", save the top 5 titles from the results to Desktop titles.txt
Agent:
  (multi-step: 3 sub-tasks → split)
  (plan-set '["Open site", "Search AI", "Save top 5 titles"]')
  (step 1 only: record-step goto) → screenshot
  📍 Progress: 1/3 done ✅ Open site
  📸 Screenshot: step_01_....png
  Reply continue / 1 / next for step 2/3: Search AI

User: 1
Agent:
  (plan-status → step 2)
  (record-step snapshot → find search input in 📋, e.g. input[name="q"])
  (record-step fill … AI)
  (record-step press Enter)
  (plan-next)
  📍 Progress: 2/3 done ✅ Search AI
  📸 Screenshot: step_03_....png
  Reply continue / 1 / next for step 3/3: Save top 5 titles

User: next
Agent:
  (plan-status → step 3)
  (record-step scroll value=1200 → lazy-load results)
  (record-step wait value=1200)
  (record-step snapshot → find results container in 🗂️ e.g. [data-testid="results"])
  (record-step extract_text [data-testid="results"] h3 a titles.txt limit=5)
  (plan-next → all done)
  🎉 All 3 steps done! titles.txt written to Desktop.
  Say `#end` to generate the RPA script.

User: #end
Agent: ✨ Generated: rpa/daily_news_scrape.py (5 steps, real recording, selectors verified)

User: #rpa-run:Daily news scrape
Agent: ▶️ Running… ✅ Finished.

User: run:Daily news scrape
Agent: ▶️ Running… ✅ Finished.

User: #rpa-list
Agent: 📋 Listing… (shows `rpa_manager.py list` output)
```

---

## Other resources

- Synthesis guidance: [synthesis-prompt.md](synthesis-prompt.md) (Recorder assembly vs legacy LLM synthesis; both must align with [playwright-templates.md](playwright-templates.md) / `recorder_server._build_final_script` — do not use old `get_by_role` + `networkidle` minimal skeletons as the main path)
- Playwright templates: [playwright-templates.md](playwright-templates.md) (same atoms as `recorder_server.py` `_build_final_script` / `_do_action`: `CONFIG`, `_EXTRACT_JS`, `_wait_for_content`, `page.locator` + `page.evaluate`)
- `rpa_manager.py` commands:

  **Plan (anti-timeout):**  
  `plan-set '<json>'` | `plan-next` | `plan-status`

  **Recorder (recommended):**  
  `record-start <task> [--profile A-N]` | `deps-check <A-N>` | `deps-install <A-N>` | `record-step '<json>'` | `record-status` | `record-end [--abort]`

  **General:**  
  `run <task>` | `list` (in chat, **`#rpa-list`** triggers LIST)

  **Legacy:**  
  `init <task>` | `add --proof <file> '<json>'` | `generate` | `status` | `reset`
