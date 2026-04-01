---
name: openclaw-rpa
language: en-US
description: Record browser & local-file actions once; replay runs without the LLM—save $ vs AI browsing, faster, no hallucinations. github.com/laziobird/openclaw-rpa
metadata: {"openclaw": {"emoji": "🤖", "os": ["darwin", "linux"]}}
---

> **This file:** `en-US` (selected by `locale` in [config.json](config.json) or [config.example.json](config.example.json) if `config.json` is missing; Chinese: [SKILL.zh-CN.md](SKILL.zh-CN.md))

> **GitHub:** **[https://github.com/laziobird/openclaw-rpa](https://github.com/laziobird/openclaw-rpa)** — install, `rpa/` samples, issues

# openclaw-rpa

**Example automations** (illustrative; **obey each site’s terms of use and applicable law**): **e‑commerce login & shopping**; **Yahoo Finance** stock quotes / news; movie sites **reviews & ratings** in one scripted run.

## What this skill does

**openclaw-rpa** is a **Recorder → Playwright script** pipeline: the agent drives a real browser, you confirm steps, and **`record-end`** compiles a **normal Python** file under `rpa/`. **Replay** runs that file with **`rpa_manager.py run`**—**no** LLM per click.

**Highlights**

1. **Saves compute and money** — Letting a **large model** operate the browser **every** time can cost **on the order of single-digit to tens of US dollars** per heavy session (tokens, tools, long context). After you **record once**, repeat runs **do not invoke the model**—cost is essentially **local script execution**, and runs are **much faster** than step-by-step LLM reasoning.
2. **Verify the flow once, then run the same steps every time** — During recording you **prove** the task works; replay **executes the saved steps** deterministically. You avoid asking the AI to improvise on each run, which **reduces inconsistency** and **hallucination-driven** mistakes.

Output is **ordinary Python**; after **`record-end`** you may still patch helpers (`pathlib` / `shutil` / `open()`, or **`extract_text`** during recording)—browser-only, file-only, or both.

## When to use

| Goal | What to send |
|------|----------------|
| **Start recording** a new flow | `#automation robot`, `#RPA`, `#rpa`, or mention **Playwright automation** |
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
| **Files only in script** | After **`record-end`**, add folder cleanup—**no URL** for that block. |

## Troubleshooting: `LLM request timed out` (not the record-step timeout)

If logs show `error=LLM request timed out`, `model=gemini-...`, `provider=google`:

| Meaning | A **single** OpenClaw → LLM API call (reply generation + tool planning) exceeded the gateway/client **LLM timeout**. This is **not** the `record-step` wait for a result (e.g. 120s) and **not** Chromium navigation timeout. |
| Common causes | **Too much in one turn**: multiple `record-step` calls / long reasoning / pasting the full page snapshot back into the reply; oversized context and output; slower models (e.g. `gemini-3-pro-preview`) plus the tool chain. |
| Skill-side | **Must** follow the anti-timeout rules below: after `plan-set`, advance **only a small slice per user turn** (≤2 `record-step` calls), keep replies short, and **do not** paste full snapshot JSON into the chat repeatedly. |
| Environment | **Raise the LLM request timeout** in OpenClaw/Gateway if the product exposes it; unstable network to the Google API also increases latency. |

---

## Trigger detection

On each user message, **check in this order** (**first match wins**; do not skip order or `#rpa-list` may be mistaken for ONBOARDING because it contains `#rpa`):

| Order | Condition | State |
|:-----:|-----------|--------|
| 1 | Message is a **RUN** (see table below) | RUN |
| 2 | After trim, message **equals** `#rpa-list` (**case-insensitive**, e.g. `#RPA-LIST`) | LIST |
| 3 | Message contains **#automation robot** OR **#RPA** OR **#rpa** (case-insensitive for `#RPA` / `#rpa`) | ONBOARDING |

Intercept and handle these; do not run the raw user task outside this skill.

**RUN triggers (order 1):**

| Form | Notes |
|------|--------|
| `#rpa-run:{task name}` | **Run in a new chat** (no reliance on this thread): after trim, message **starts with** `#rpa-run:` (**case-insensitive**, e.g. `#RPA-RUN:`). **After the first colon** to **end of line** is `{task name}` (**must match** a name from `#rpa-list`, trimmed). |
| `run:{task name}` | **Run in this chat:** `run:` then optional spaces, then task name to end of line (trimmed; same name rules). |

> **`zh-CN` locale:** use [SKILL.zh-CN.md](SKILL.zh-CN.md) (`#自动化机器人`, `#RPA` / `#rpa`, `#rpa-list`, `#rpa-run:`, `#运行:`).

---

## State machine

```
IDLE ──trigger──► ONBOARDING ──task name──► RECORDING ──end recording──► GENERATING ──► IDLE
                                        │abort
                                        └──────────────────────────────► IDLE
IDLE ──"#rpa-run:{task}" / "run:{task}"──► RUN ──► IDLE
IDLE ──"#rpa-list"──► LIST ──► IDLE
```

---

## ONBOARDING

**Output the following verbatim (English):**

```
🤖 OpenClaw RPA lab ready

With AI help, we’ll record what you do in a real browser (and local file steps if you need them) and compile it into an RPA script you can run again and again.
Later runs use that script directly—no need for the model to drive every click—saving compute and keeping steps consistent (vs. LLM hallucinations on fragile actions).

How it works:
1. Give me a task name
2. Give instructions → I run the real steps in the browser and show screenshots
3. Say "end recording" → I compile the recorded steps into an RPA script

Common commands:
• "end recording" → generate the Playwright Python script
• "abort" → close the browser and discard this session
• For multi-step plans, to go on you may send: **continue**, **1**, or **next** (same as "ok", "y", "go")

What is the first task name you want to record?
```

---

## RECORDING (Recorder mode — headed browser)

### Start recording (after user gives task name)

Run:
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-start "{task name}"
```

When the command prints `✅ Recorder ready`, reply:
```
✅ Recording started: 「{task name}」
🖥️  Chrome is open — watch the window; each step runs for real.
Screenshots are saved automatically.
Send your first instruction (I can split multi-step work).
```

---

### Anti-timeout: multi-step instructions **must** be split — **one step per user turn**

**When to split:** The user’s message contains **two or more** independent atomic actions (navigate, search, click, extract, …).

#### Split workflow

**First turn (multi-step instruction):**

1. Decompose into atomic sub-tasks (each sub-task maps to ≤2 `record-step` calls).
2. Persist the plan with `plan-set`:
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
   Say "end recording" to generate the RPA script, or describe more actions.
   ```

> **Why:** Each LLM request should only run **2–3** tool calls; a single `record-step` wait for the recorder can be up to **120s** (same as `rpa_manager` polling). Multi-step work must still be split so total time does not trigger `LLM request timed out`.

---

### Single-step recording protocol (for every user instruction)

#### Step 1: Get current page elements (free, not written to script)
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{"action":"snapshot"}'
```
→ Returns all interactive elements and their **real CSS selectors** (e.g. `#search-input`, `input[name="q"]`, `[aria-label="Search"]`).

#### Step 2: Choose the target CSS from the snapshot
- **Must** use the real `sel` from the snapshot — **do not guess**.
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
| `extract_text` | CSS | output filename | Text from multiple elements → `~/Desktop/<filename>` |
| `wait` | — | milliseconds | Wait |

> `extract_text` supports an optional **`"limit": N`** — only the first **N** matches.

> **Field label (shown in the file):** optional **`"field"`** or **`"field_name"`** (e.g. `"title"`, `"rating"`, `plot`). Output is formatted as **`【字段：{name}】`** + a separator line + body; if omitted, **`context`** is used as the label.

> **Multiple `extract_text` steps with the same `value` filename:** the generated script **writes** on first use, then **appends**; each block is labeled **`【字段：…】`**.

**Native `<select>` example (Sauce Demo `inventory.html` sort):** use `snapshot` to read the `<select>` `sel` and each `option` value. Price high → low is `hilo` — do **not** use `fill` or arrow keys to guess:

```json
{"action":"select_option","target":"[data-test=\"product-sort-container\"]","value":"hilo","context":"Sort by price high to low"}
```

---

### Lazy-loaded content must be scrolled first (all SPAs)

React / Vue / Next.js SPAs **do not** render the full page at once. Blocks below the fold (news lists, stats, comments, …) render only when scrolled near.

**Generic flow: extract content from a page region**
```
1. goto   target URL

2. snapshot   ← understand initial DOM

3. scroll   value=1000~2000   ← scroll to trigger lazy-load for the target region
   (repeat scroll until the target appears in snapshot if needed)

4. wait     value=1000~2000   ← wait for lazy content

5. snapshot                   ← rescan; use the 🗂️ block list to find the container title

6. extract_text   target="{selector from snapshot block} h3"
                  value="output.txt"  limit=5
```

> Lazy-load timing varies per SPA; if the target still does not appear, scroll ~800px and try again.

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

### Common scenarios

| Scenario | Suggested approach |
|----------|-------------------|
| Content blocks (news/list/comments) | scroll → wait → snapshot → pick selector from 🗂️ |
| Target not in snapshot | Not rendered yet — scroll ~800px and retry |
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

- **`end recording`** → **GENERATING**
- **`abort`** → run:
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

3. On success, print:
   ```
   ✨ RPA script generated! (from real recording; selectors verified in browser)

   📄 File: ~/.openclaw/workspace/skills/openclaw-rpa/rpa/{filename}.py
   📋 Recorded steps: {N}
   📸 Screenshots: ~/.openclaw/workspace/skills/openclaw-rpa/recorder_session/screenshots/

   Known limitations:
   • [If login was involved, remind user to log in before replay]
   • [Other caveats inferred from the recording]

   To run this RPA later: if unsure what’s registered, send **`#rpa-list`** first to see **which recorded tasks are available**; then **`#rpa-run:{task name}`** (new chat) or **`run:{task name}`** (same chat).
   ```

4. **Do not LLM-rewrite the generated script** (agents must obey)
   - After successful `record-end`, `rpa/{filename}.py` is assembled by `recorder_server` `_build_final_script()` from real `code_block` segments — same source as `recorder_session/script_log.py`.
   - **Do not** generate a full replacement Playwright script from the task description alone; that drops recorder-validated selectors and `evaluate` semantics and often reintroduces `get_by_*` / `networkidle` patterns that diverge from the pipeline.
   - For behavior changes: **prefer** `record-start` and re-record the bad steps, then `record-end`; for tiny edits, patch **`rpa/*.py` locally** only, staying consistent with [playwright-templates.md](playwright-templates.md) (`CONFIG`, `_EXTRACT_JS`, `_wait_for_content`, `page.locator` + `page.evaluate`).

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
Agent: (ONBOARDING) … What is the task name?

User: Daily news scrape
Agent: (record-start) ✅ Chrome open…

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
  Say "end recording" to generate the RPA script.

User: end recording
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
  `record-start <task>` | `record-step '<json>'` | `record-status` | `record-end [--abort]`

  **General:**  
  `run <task>` | `list` (in chat, **`#rpa-list`** triggers LIST)

  **Legacy:**  
  `init <task>` | `add --proof <file> '<json>'` | `generate` | `status` | `reset`
