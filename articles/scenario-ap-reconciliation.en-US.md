# Scenario: AP Reconciliation (API pull + local Excel + Word table output)

> **Simplified flow:** the cloud API is **read-only — only pulls open payables**; the accountant reconciles against a **local invoice workbook** on their own machine; the final result is saved as a **Word (`.docx`) report** whose body contains a **table** (ready to print, sign, or email).  
> Recording tip: use **`#rpa-api`** or **`#automation robot`**; select capability **F** (Excel + Word, no browser) or **G** (if a browser is also needed); steps are **`api_call`** + **`excel_write`** + **`word_write`** (the `table` parameter generates the table directly — no manual post-edit required).

---

## Video demo

Full recording walkthrough (end-to-end: trigger → record API + Excel + Word → synthesize script → replay):



https://github.com/user-attachments/assets/c994d58a-9cbb-42e4-a01e-7d9899a39ebe



**What the recording covers (4 steps)**

| Step | Action | Notes |
|:----:|--------|-------|
| 1 | Trigger with `#rpa-api` | Select capability **F** (Excel + Word, no browser) |
| 2 | `api_call` — pull open payables | GET Mock endpoint; save result as `reconcile_raw.json` |
| 3 | `excel_write` × 2 + `python_snippet` | "System" sheet from API rows; "Invoices" sheet copied from `invoice_import_thisweek.xlsx`; local matching logic writes "Match Results" |
| 4 | `word_write` — generate report | Produces `ap_reconciliation_YYYYMMDD.docx` with a table; `#end` → script synthesized |

---

## 1. Business background

| Dimension | Details |
|-----------|---------|
| **Who** | Accounts-payable accountant |
| **System side** | Open payable lines from an ERP / expense system (pulled as JSON via **Mock API**, simulating a real endpoint) |
| **Invoice side** | Existing Desktop Excel file (e.g. `invoice_import_thisweek.xlsx`), maintained by the finance team |
| **What** | Pull system data → write to workbook → match locally against invoice file → **generate a Word report with a table** |

---

## 2. Workflow (four steps)

1. **`api_call`**: `GET` the open payables (see §3), save the JSON to disk or parse inline.
2. **`excel_write`** (one or more): write the **"System"** sheet from API rows; write the **"Invoices"** sheet by reading the local invoice file (or have the generated script use `openpyxl` to read `invoice_import_thisweek.xlsx` and write into the same workbook).
3. **Local matching**: compute `match_status` / `diff_reason` etc. in the **"Match Results"** sheet (or inline script logic) — **entirely local, no network call**.
4. **Word output**: produce `ap_reconciliation_YYYYMMDD.docx` containing at least one **table** (columns: line ID, PO ref, system amount, invoice no., invoice amount, match status, notes).

Optional: keep an intermediate `ap_draft_YYYYMMDD.xlsx` so the accountant can add manual notes; the Word document is the final deliverable.

---

## 3. Single API endpoint (cloud Mock)

- Path **`GET /ap/reconciliation/batches`** with `status` / `week` query parameters
- **`components.schemas`**: `PayableLine`, `ReconciliationBatch`, `BatchesResponse`
- **`200` response example**: identical to the JSON below (two lines sharing the same `po_ref`)

After upload, paste the platform-assigned **Base URL** into the `api_call` / `###` block.

---

### `GET https://0a34723da37946b7add0b4581c37ada2_oas.api.mockbin.io/ap/reconciliation/batches?status=open&week=15`

| Query param | Meaning |
|-------------|---------|
| `status` | Use `open` |
| `week` | e.g. `2026-W14` |

**Sample 200 response**

```json
{
  "batches": [
    {
      "batch_id": "batch_2026w14_01",
      "week": "2026-W14",
      "lines": [
        {
          "line_id": "L-10001",
          "vendor_id": "V-7788",
          "po_ref": "PO-2026-0091",
          "amount_system": 12500.5,
          "currency": "USD",
          "due_date": "2026-04-18"
        },
        {
          "line_id": "L-10002",
          "vendor_id": "V-7788",
          "po_ref": "PO-2026-0091",
          "amount_system": 3200.0,
          "currency": "USD",
          "due_date": "2026-04-20"
        }
      ]
    }
  ]
}
```

**Mock tip**: both lines share the same `po_ref` — use this to test **duplicate-candidate / needs-review** labeling in local matching logic.

---

## 4. Task prompts (copy and paste directly into the chat)

**Step 1:**  #rpa-api
```
###
Pull this week's open AP payables
GET https://0a34723da37946b7add0b4581c37ada2_oas.api.mockbin.io/ap/reconciliation/batches?status=open&week=2026-W14
Response path: batches[].lines[], fields: line_id / vendor_id / po_ref / amount_system / currency / due_date
###
```

**Step 2:** Write the data returned by the API (`reconcile_raw.json`, fields `line_id / vendor_id / po_ref / amount_system / currency / due_date / batch_id`) to the Desktop workbook **`ap_draft_thisweek.xlsx`**, sheet **"System"**, freeze the first row, columns in the order listed above.

**Step 3:** Read invoice data from the **"Invoices"** sheet of the Desktop file **`invoice_import_thisweek.xlsx`**, write it into the **"Invoices"** sheet of **`ap_draft_thisweek.xlsx`**, preserving the original column order (invoice_no / vendor_tax_id / amount_invoice / tax_amount / po_ref / notes).

**Step 4:** Match locally on `po_ref` (system) = `po_ref` (invoices) using a **two-stage** algorithm:
1. **po_ref filter** — find all invoice rows whose `po_ref` equals the system line's `po_ref`.
2. **Amount-tolerance filter** — from those candidates, keep only rows where `|amount_invoice − amount_system| ≤ 1`.
3. **Decide status** based on how many candidates survive stage 2:
   - **0 survivors** → `unmatched` (no po_ref match, or all amounts exceed tolerance)
   - **exactly 1 survivor** → `matched` (diff = 0) or `partial` (0 < diff ≤ 1)
   - **2+ survivors** (amounts truly ambiguous within tolerance — two invoices sharing the same `po_ref` but with very different amounts, e.g. 12 500 vs 3 200, are **not** ambiguous; pick the one whose amount is closest to the system amount and within tolerance) → `pending`

Write results to the **"Match Results"** sheet of **`ap_draft_thisweek.xlsx`** (columns: line_id / po_ref / amount_system / invoice_no / amount_invoice / match_status / diff_notes). Also generate **`ap_reconciliation_YYYYMMDD.docx`** on the Desktop with the same columns in a table.

> The AI will automatically choose `excel_write` (dynamic `rows` parameter) for Steps 2–3, and `python_snippet` (matching logic validated at record time) for Step 4. Full `record-step` JSON examples and `python_snippet` design rationale: **[python-snippet-design.md](python-snippet-design.md)**.

---

## 5. OpenClaw RPA integration

> **Test data (Fixture):** A ready-made invoice file is included in the repository — copy it to your Desktop before recording:  
> `articles/fixtures/invoice_import_thisweek.xlsx` (sheet "Invoices", 3 sample rows: `INV-9001 / INV-9002 / INV-9003`)

| Capability | Usage |
|------------|-------|
| **`api_call`** | `GET` only (the URL in §3); use `save_response_to` to save `reconcile_raw.json` then parse in the script, or write query params directly into the generated code. |
| **`excel_write`** | Write **System / Invoices / Match Results** sheets; if invoices come from a separate file, add `openpyxl.load_workbook` after `record-end`. |
| **Word table** | The recorder's **`word_write`** handles paragraph headings; for **multi-column tables** it is better to use `docx.Document` + `doc.add_table(rows=…, cols=…)` in the final `rpa/*.py`, consistent with the "append / small patch" rule in **SKILL**. |
| **Replay** | `#rpa-run:task-name` |



https://github.com/user-attachments/assets/61b4fc7c-a05a-4fc9-b41f-f29dbd48675d



---

## Related links

- **OpenAPI 3.1 Mock source:** **[openapi-ap-reconciliation-mock.yaml](openapi-ap-reconciliation-mock.yaml)**
- **[SKILL.en-US.md](../SKILL.en-US.md)** · **[README.md](../README.md)**
