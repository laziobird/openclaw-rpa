# 案例：财务对账（API财务系统数据 + 本地财务 Excel + 输出 Word 对账表）

> **简化版**：云端 API **只负责「拉待对账数据」**；会计在**本机 Excel** 里完成与发票明细的核对；最终把**对账结果**存成一份 **Word（`.docx`）**，正文里用**表格**展示清单（便于打印、签字或邮件发出）。  
> 录制建议：`**#rpa-api**` 或 `**#rpa**`，能力码选 **F**（Excel + Word，无网页）或 **G**（若还要开网页）；步骤含 **`api_call`** + **`excel_write`** + **`word_write`**（`table` 参数直接生成表格，无需录完后手补）。

---

## 视频演示

完整录制演示（全流程：触发 → 录制 API + Excel + Word → 生成脚本 → 回放）：



https://github.com/user-attachments/assets/13cfda68-5a67-4efa-aa6d-c1ecc501a30e



**录屏内容说明（共 4 步）**

| 步骤 | 操作 | 说明 |
|:----:|------|------|
| 1 | `#rpa-api` 触发录制 | 选能力码 **F**（Excel + Word，无网页） |
| 2 | `api_call` 拉待对账数据 | GET Mock 接口，结果存 `reconcile_raw.json` |
| 3 | `excel_write` × 2 | 「系统侧」写接口行；「发票侧」从 `发票导入_本周.xlsx` 复制；`python_snippet` 做本地匹配写「匹配结果」 |
| 4 | `word_write` 输出报告 | 生成带表格的 `对账报告_YYYYMMDD.docx`；`#end` → 脚本合成 |

---

## 一、业务背景

| 维度 | 说明 |
|------|------|
| **谁** | 应付会计 |
| **系统侧** | ERP/费控里待对账行（通过 **Mock API** 拉 JSON，模拟真实接口） |
| **发票侧** | 桌面已有 Excel（如 `发票导入_本周.xlsx`），财务自己维护 |
| **做什么** | 拉系统数 → 写入工作簿 → 与发票表在本地对齐、打匹配结果 → **生成带表格的 Word 报告** |

---

## 二、流程（四步）

1. **`api_call`**：`GET` 待对账数据（见下节），把返回 JSON 落盘或直接在脚本里解析。  
2. **`excel_write`**（可多次）：例如工作表 **「系统侧」** 写接口行；**「发票侧」** 从本地只读复制/写入（若发票已是固定列，也可在生成脚本里用 `openpyxl` 读 `发票导入_本周.xlsx` 再写入同一工作簿）。  
3. **本地匹配**：在 **「匹配结果」** 表（或脚本内逻辑）按规则打 `match_status`、`diff_reason` 等——**全部在本地完成**。  
4. **输出 Word**：生成 `对账报告_YYYYMMDD.docx`，文档中至少包含一张 **表格**（列如：行号、订单引用、系统金额、发票号、发票金额、匹配状态、说明）。

可选：中间保留一份 `对账底稿_YYYYMMDD.xlsx` 便于会计改备注；最终对外材料以 Word 为准。

---

## 三、API 只此一条（云端 Mock）

- 路径 **`GET /ap/reconciliation/batches`**、`status` / `week` 查询参数  
- **`components.schemas`**：`PayableLine`、`ReconciliationBatch`、`BatchesResponse`  
- **`200` 响应示例**：与下文 JSON **完全一致**（两行同 `po_ref`）

上传后把平台分配的 **Base URL** 填进 RPA 的 `api_call` / `###` 块即可。

---

### `GET https://0a34723da37946b7add0b4581c37ada2_oas.api.mockbin.io/ap/reconciliation/batches?status=open&week=15`

| Query | 含义 |
|--------|------|
| `status` | 固定 `open` 即可 |
| `week` | 如 `2026-W14` |

**200 响应示例**

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
          "currency": "CNY",
          "due_date": "2026-04-18"
        },
        {
          "line_id": "L-10002",
          "vendor_id": "V-7788",
          "po_ref": "PO-2026-0091",
          "amount_system": 3200.0,
          "currency": "CNY",
          "due_date": "2026-04-20"
        }
      ]
    }
  ]
}
```

**Mock 小技巧**：两条共用同一 `po_ref`，可用来在本地匹配逻辑里标 **重复候选 / 需人工看一眼**。

---

## 四、任务提示词（复制后直接粘进对话）


**步骤 1：**  #rpa-api
###
拉取本周应付待对账数据
GET https://0a34723da37946b7add0b4581c37ada2_oas.api.mockbin.io/ap/reconciliation/batches?status=open&week=2026-W14
响应路径：batches[].lines[]，字段：line_id / vendor_id / po_ref / amount_system / currency / due_date
###

**步骤 2：** 把刚才接口返回的数据（`reconcile_raw.json`，字段 `line_id / vendor_id / po_ref / amount_system / currency / due_date / batch_id`）写入 桌面 **`对账底稿_本周.xlsx`** 的工作表 **「系统侧」**，冻结首行，列按上面顺序

**步骤 3：** 从桌面 **`发票导入_本周.xlsx`** 的工作表 **`发票侧`** 读取发票数据，写入 桌面 **`对账底稿_本周.xlsx`** 的工作表 **「发票侧」**，保持原列顺序（发票号码 / 销方税号 / 发票金额 / 税额 / 订单引用 / 备注）

**步骤 4：** 按 `po_ref`（系统侧）= `订单引用`（发票侧）做本地强匹配，采用**两阶段算法**：
1. **PO 过滤** — 找出所有 `订单引用` 与系统行 `po_ref` 相同的发票行。
2. **金额容差过滤** — 在上述候选中，保留 `|发票金额 − 系统金额| ≤ 1` 的行。
3. **根据第 2 阶段剩余候选数定状态**：
   - **0 个** → `unmatched`（无 PO 匹配，或所有候选金额差均超容差）
   - **恰好 1 个** → `matched`（差额 = 0）或 `partial`（0 < 差额 ≤ 1）
   - **≥ 2 个**（容差内金额真正歧义，无法区分）→ `pending`（多张发票 PO 相同但金额差异很大不算歧义，只取差额最小且 ≤ 1 的那张）

结果写入 **`对账底稿_本周.xlsx`** 的工作表 **「匹配结果」**（列：系统行ID / 订单引用 / 系统金额 / 发票号码 / 发票金额 / 匹配状态 / 差异说明），同时在桌面生成 **`对账报告_YYYYMMDD.docx`** Word 报告，正文含相同列的表格

> AI 会自动为步骤 2/3 选择 `excel_write`（动态行参数），为步骤 4 选择 `python_snippet`（匹配计算代码录制时立即验证执行）。完整 `record-step` JSON 示例及 `python_snippet` 设计原理见 **[python-snippet-design.md](python-snippet-design.md)**。

---

## 五、与 OpenClaw RPA 的衔接

> **测试数据（Fixture）：** 发票侧样例文件已预置在仓库，直接放到桌面即可使用：  
> `articles/fixtures/发票导入_本周.xlsx`（工作表「发票侧」，含 3 行测试数据，含 `INV-9001/9002/9003`）

| 能力 | 用法 |
|------|------|
| **`api_call`** | 仅 **GET** 上节 URL；`save_response_to` 可先存 `reconcile_raw.json` 再在脚本里解析，或直接把查询参数写进生成代码。 |
| **`excel_write`** | 写 **系统侧 / 发票侧 / 匹配结果** 各 sheet；发票若从另一文件读，多在 `record-end` 后补 `openpyxl.load_workbook`。 |
| **Word 表格** | 录制器 **`word_write`** 适合段落标题；**多列表格**建议在最终 `rpa/*.py` 中使用 `docx.Document` + `doc.add_table(rows=…, cols=…)` 填单元格，与 **SKILL** 中「末尾追加 / 小补全」规则一致。 |
| **回放** | `#rpa-run:任务名` |



https://github.com/user-attachments/assets/61057986-edb6-47ef-81e1-72122f33f081



---

## 相关链接

- **OpenAPI 3.1 Mock 源文件：** **[openapi-ap-reconciliation-mock.yaml](openapi-ap-reconciliation-mock.yaml)**  
- **[SKILL.zh-CN.md](../SKILL.zh-CN.md)** · **[README.zh-CN.md](../README.zh-CN.md)**
