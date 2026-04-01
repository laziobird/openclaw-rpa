---
name: openclaw-rpa
description: 录制浏览器网站与本机文件操作；回放不调大模型—省费用、更快、少幻觉。github.com/laziobird/openclaw-rpa · #rpa-list #rpa-run #运行 #自动化机器人 #RPA。Use when user says #自动化机器人, #RPA, #rpa, #rpa-list, 录制自动化, browser automation, or asks to automate browser/file tasks.
metadata: {"openclaw": {"emoji": "🤖", "os": ["darwin", "linux"]}}
---

> **本文件语言：** `zh-CN`（由 [config.json](config.json) 或缺失时的 [config.example.json](config.example.json) 中 `locale` 选择；英文全文见 [SKILL.en-US.md](SKILL.en-US.md)）

> **GitHub 源码仓库：** **[https://github.com/laziobird/openclaw-rpa](https://github.com/laziobird/openclaw-rpa)**（安装说明、`rpa/` 示例、问题与反馈）

# openclaw-rpa

**典型场景示例（录制一次、反复回放；须遵守各站服务条款与所在地法规）：** 电商 **登录与购物** 全流程自动化；**Yahoo 财经** 股票行情与新闻 **自动获取**；电影类网站 **一键汇总影评与评分** 等。

## 这个 skill 做什么

**openclaw-rpa** 是一条 **录制 → 生成 Playwright 脚本 → 反复回放** 的流水线：在真实浏览器里按你的指令一步步执行并截图确认，**`#结束录制`** 后把步骤编译成 **`rpa/` 下的普通 Python**。日常**直接跑脚本**，不必每次让模型现场点网页。生成物可再按需加本机文件处理（`pathlib` / `extract_text` 等），见 [playwright-templates.md](playwright-templates.md)。

**亮点**

1. **大幅节约算力与费用** — 若每次重复操作都让**大模型**代点浏览器，单次会话往往 **数美金到数十美金** 量级（token、工具、长上下文等）。录成 RPA 后，**重复执行不再调大模型**，成本接近 **仅跑本地脚本**，且 **速度远快于** 每步都等模型推理。
2. **第一次把流程跑通、确认无误，以后按同一套步骤执行** — 录制阶段你已 **验证** 任务能正确完成；回放时 **严格按已保存步骤执行**（可预期、可重复），不必每次再让 AI「临场发挥」。避免 **反复调用大模型** 带来的 **稳定性变差** 与 **幻觉、误操作** 风险。

**不适合** — 重型 ETL、数据库或大型运维；请用专门工具。

## 何时用（对照发什么）

| 你想… | 发什么 |
|--------|--------|
| **开始录制**新流程 | `#自动化机器人`、`#RPA`、`#rpa`，或提到 **Playwright automation** |
| **看已保存的任务** | `#rpa-list` |
| **执行已保存任务**（如新对话） | `#rpa-run:{任务名}` |
| **当前会话里执行** | `#运行:{任务名}` |
| **在 OpenClaw + 飞书等里定时/提醒** | 自然语言 + `#rpa-run:…`（以实际接入为准） |

## 快速上手

```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py run "任务名"
```

对话里可发 **`#rpa-list`** → **`#rpa-run:任务名`**，名称与 `registry.json` 一致即可。

### 运行已录制的任务（先看有哪些，再跑哪一个）

- **有哪些可以跑**：发 **`#rpa-list`**，列出 **当前已登记、可执行** 的任务名。不知道名字时**先发这一条**。
- **跑其中一个**：**`#rpa-run:任务名`**（**新开对话**）或 **`#运行:任务名`**（**当前会话**）。二者都是 **再次执行已生成脚本**，不是重新录制。

### 说明性例子（非穷举）

| 类型 | 含义 |
|------|------|
| **仅浏览器** | 如电商：**登录 → 选购 → 加购/结算**（参考仓库 `rpa/电商网站购物*.py`）；或 **Yahoo 财经** 行情/新闻；或电影站 **影评与评分** 汇总。 |
| **浏览器 + 文件** | 同上，必要时 **`extract_text`** 落盘。 |
| **脚本内文件** | 录完后只加整理下载目录、改名等——可与网页无关。 |

## 故障排查：`LLM request timed out`（与录制超时不同）

日志里若出现 `error=LLM request timed out`、`model=gemini-...`、`provider=google`：

| 含义 | 这是 **OpenClaw 对模型 API 的单次请求**（生成回复 + 工具规划）超过网关/客户端的 **LLM 超时**，不是 `record-step` 等待结果的 120s，也不是 Chromium 的导航超时。 |
| 常见诱因 | **单轮里想做的太多**：多步 `record-step`/长推理/把整页 snapshot 再抄进回复；上下文与输出过长；`gemini-3-pro-preview` 等模型推理 + 工具链较慢。 |
| Skill 侧 | **必须**遵守下方「防超时规则」：`plan-set` 拆解后 **每用户轮只推进一小步**（≤2 次 `record-step`），回复尽量短，勿在对话里重复粘贴完整 snapshot JSON。 |
| 环境侧 | 在 OpenClaw / Gateway 配置中 **调高 LLM 请求超时**（若产品提供该选项）；网络到 Google API 不稳定时也会拉长耗时。 |

---

## 触发检测

每次收到用户消息时，**按下表顺序**检查（**先命中先执行**，后续不再判断；勿跳过顺序，否则 `#rpa-list` 会因含 `#rpa` 而误判为 ONBOARDING）：

| 顺序 | 条件 | 进入状态 |
|:----:|------|---------|
| 1 | 消息为 **RUN**（见下表） | RUN |
| 2 | 消息**去掉首尾空白**后**等于** `#rpa-list`（**不区分大小写**，如 `#RPA-LIST`） | LIST |
| 3 | 消息含 `#自动化机器人` 或 `#RPA` / `#rpa`（不区分大小写） | ONBOARDING |

**RUN 触发（命中顺序 1 即进入 RUN）：**

| 形式 | 说明 |
|------|------|
| `#rpa-run:{任务名}` | **在新对话里执行**（不依赖当前会话上下文）：消息**去掉首尾空白**后以 `#rpa-run:` 开头（**不区分大小写**，如 `#RPA-RUN:`）。**第一个英文冒号 `:` 之后**到**行尾**为 `{任务名}`（须与 `#rpa-list` 中某一项一致，首尾去空白）。 |
| `#运行:{任务名}` | **在当前会话里执行**：消息**去掉首尾空白**后以 `#运行:` 开头。**第一个英文冒号 `:` 之后**到**行尾**为任务名（同上，须为已登记任务）。 |

命中即拦截，不要直接执行原始任务。

---

## 状态机

```
IDLE ──触发词──► ONBOARDING ──任务名──► RECORDING ──#结束录制──► GENERATING ──► IDLE
                                           │#放弃
                                           └──────────────────────────────► IDLE
IDLE ──"#rpa-run:{任务名}" / "#运行:{任务名}"──► RUN ──► IDLE
IDLE ──"#rpa-list"──► LIST ──► IDLE
```

---

## ONBOARDING 状态

**逐字输出以下引导语，不要省略：**

```
🤖 OpenClaw RPA 实验室已就绪

在 AI 协助下，把你在常见网站上的操作、以及需要的本机文件步骤，录制成可反复执行的 RPA 脚本。
之后日常直接跑脚本即可，不必每次让模型现场点网页——省算力，步骤按录制执行，少受幻觉影响。

工作方式:
1. 告诉我任务名称
2. 下达指令 → 我在浏览器里真实执行，截图给你确认
3. 说"#结束录制" → 我把录制步骤编译成 RPA 脚本

常用指令:
• 输入"#结束录制" → 生成可独立运行的 Playwright 脚本
• 输入"#放弃"     → 关闭浏览器，清空本次录制
• 多步任务拆成计划后，要进入下一步时可只发:**#继续**、**1** 或 **next**（与「#好」「#下一步」「ok」一样有效）

请告诉我，你要录制的第一个任务名称是什么？
```

---

## RECORDING 状态（Recorder 模式 — 有界面真实录制）

### 进入录制（用户提供任务名后）

执行：
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-start "{任务名}"
```

等命令输出 `✅ Recorder 已就绪` 后，回复：
```
✅ 已进入录制模式: 「{任务名}」
🖥️  Chrome 窗口已打开，请注视屏幕——接下来每一步操作都将在这个浏览器中真实执行。
截图将自动保存，你可以随时核对。
请下达指令，为你拆解任务
```

---

### ⚡ 防超时规则：多步指令必须拆解，每轮只执行一步

**判断标准：** 用户指令中包含 2 个以上可独立完成的原子操作（导航、搜索、点击、提取等）时，触发拆解流程。

#### 拆解流程

**第一轮（收到多步指令时）：**

1. 将指令分解为原子子任务列表（每个子任务对应 ≤2 次 record-step 调用）
2. 调用 `plan-set` 持久化计划：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-set '["子任务1描述", "子任务2描述", "子任务3描述"]'
   ```
3. 执行 **第 1 步**（仅此一步，不继续）
4. 固定结尾：
   ```
   📍 进度: 1/{N} 步已完成
   ✅ [步骤描述]
   📸 截图: {path}
   请确认截图，然后说「#继续」或「1」或「next」执行第 2/{N} 步（见下方快捷确认词）。
   ```

> **快捷确认词（均视为「继续执行下一步」）：** `#继续`、`1`、`next`、`#好`、`#下一步`、`ok`（`next` 不区分大小写）。用户只打 **`1`** 或 **`next`** 即可，无需完整句子。

**后续轮（收到上述快捷确认词之一时）：**

1. 查看当前计划进度：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-status
   ```
2. 执行当前步对应的操作（snapshot + action，≤2 次 record-step）
3. 推进计划：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py plan-next
   ```
4. 若还有下一步 → 输出进度，等待用户确认；若全部完成 → 输出：
   ```
   🎉 所有 {N} 步已全部完成！
   可以说「#结束录制」生成 RPA 脚本，或继续描述更多操作。
   ```

> **为什么这么设计：** 每次 LLM 请求只运行 2-3 个工具调用；单步 `record-step` 等待录制器回写结果最多 **120s**（与 `rpa_manager` 轮询一致），仍须拆解多步以免总耗时长触发 "LLM request timed out"。

---

### 单步录制协议（每条用户指令执行以下流程）

#### 第一步：获取当前页面元素（免费，不记入脚本）
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{"action":"snapshot"}'
```
→ 返回页面中所有可交互元素及其 **真实 CSS 选择器**（如 `#search-input`、`input[name="q"]`、`[aria-label="搜索"]`）。

#### 第二步：根据 snapshot 确定目标元素的 CSS 选择器
- **必须使用 snapshot 中返回的真实 `sel` 字段**，禁止凭空猜测。
- 若 snapshot 未返回有效选择器，说明目标元素可能在页面下方未渲染，先 `scroll` 再重新 snapshot。

#### 第三步：执行操作（以下任选）

| action | target | value | 说明 |
|--------|--------|-------|------|
| `goto` | URL 字符串 | — | 导航到页面，wait_until=domcontentloaded + 1.5s SPA 等待 |
| `snapshot` | — | — | 获取当前 DOM 元素 + 内容区块（不记入脚本） |
| `fill` | CSS 选择器 | 填写文本 | **仅用于 `<input>` / `<textarea>`**；**不要**对原生 `<select>` 用 fill |
| `select_option` | `<select>` 的 CSS | **option 的 value** 或见下 | 原生下拉框：`locator.select_option(...)`。可选 `"select_by": "label"` 时 `value` 填可见文字；`"index"` 时填数字下标 |
| `press` | 键名（如 `Enter`） | — | 按键并等待页面稳定 |
| `click` | CSS 选择器 | — | 点击并等待页面稳定 |
| `scroll` | — | 像素数 | 向下滚动 N 像素 |
| `scroll_to` | CSS 选择器 | — | **滚动到指定元素，触发懒加载**，再 wait + snapshot |
| `extract_text` | CSS 选择器 | 输出文件名 | 提取多元素文本 → 写到 ~/Desktop/文件名 |
| `wait` | — | 毫秒数 | 等待 |

> `extract_text` 支持额外的 `"limit": N` 字段，只取前 N 条。

> **字段名（写入文件时显示）：** 可选 `"field"` 或 `"field_name"`（如 `"片名"`、`"rating"`、`plot`）。输出排版为 `【字段：{名称}】` + 分隔线 + 正文；未填时沿用 `context`。

> **同一 `value` 文件名多次 `extract_text`：** 生成脚本会**自动**处理：该文件名**第一次** `write_text`，**后续**同文件名**追加**；每段均带 `【字段：…】` 标识。

**原生 `<select>` 示例（Sauce Demo `inventory.html` 排序）：** 用 `snapshot` 看 `<select>` 的 `sel`，`option` 的 value。价格从高到低为 `hilo`，不要用 `fill` / 箭头键硬猜：

```json
{"action":"select_option","target":"[data-test=\"product-sort-container\"]","value":"hilo","context":"按价格从高到低排序"}
```

---

### ⚠️ 懒加载内容必须先滚动（适用于所有 SPA）

React / Vue / Next.js 等现代 SPA **不会一次性渲染整页内容**，页面下方的区块（新闻列表、统计面板、评论区等）只有滚动到附近才会触发渲染。

**通用流程：提取页面某个区块的内容**
```
1. goto  目标页面 URL

2. snapshot  ← 了解初始 DOM 结构

3. scroll  value=1000~2000      ← 向下滚动，触发目标区块的懒加载
   （如果不知道区块在哪，可多次 scroll 直到 snapshot 里出现目标元素）

4. wait  value=1000~2000        ← 等待懒加载内容渲染

5. snapshot                     ← 重新扫描；查看 🗂️ 区块列表，找含目标标题的容器

6. extract_text  target="{从 snapshot 区块中获取的选择器} h3"
                 value="output.txt"  limit=5
```

> 每个 SPA 的懒加载时机不同，如果 snapshot 仍未出现目标元素，继续 scroll 800px 后再试。

### 🔍 读取 snapshot 结果的方法

`snapshot` 返回两部分信息：

**1. `📋 页面可交互元素`** — 每行格式：
```
CSS选择器  [placeholder=...]  「文本预览」
```
- 直接把 `sel` 用作下一步的 `target`
- 若元素本身无 id/aria/testid，会**自动向上查找最近父容器**补全，如 `[data-testid="news-panel"] h3`

**2. `🗂️ 页面内容区块`** — 每行格式：
```
[data-testid="区块名"]  ← 含标题「区块标题」
```
- 提取特定区块内容时，先用区块 selector 限定范围，再加子元素类型：
  ```
  target = "[data-testid=\"目标区块\"] h3 a"  ← 只抓该区块，不误抓其他版块内容
  ```
- 如果区块没有 data-testid，可用 `section:has(h2:text("区块标题")) li` 这类 Playwright 文本过滤语法

### 💡 常见场景提示

| 场景 | 推荐做法 |
|------|---------|
| 页面内容区块（新闻/列表/评论等） | scroll 下去 → wait → snapshot → 从 🗂️ 区块找选择器 |
| snapshot 找不到目标元素 | 元素未渲染，继续 scroll 800px 后重试 |
| 提取重复结构内容（列表/卡片） | 用 `extract_text` + `limit` 只取前 N 条 |
| 需要点击展开更多内容 | click "更多" 按钮 → wait → snapshot → extract_text |

示例（导航到任意页面）：
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "goto",
  "target": "https://example.com",
  "context": "打开目标页面"
}'
```

示例（填写搜索框，selector 来自 snapshot）：
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "fill",
  "target": "#search-input",
  "value": "关键词",
  "context": "在搜索框输入关键词（selector 来自 snapshot）"
}'
```

示例（滚动触发懒加载后提取列表）：
```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-step '{
  "action": "extract_text",
  "target": "[data-testid=\"content-list\"] h3 a",
  "value": "output.txt",
  "limit": 5,
  "field": "标题",
  "context": "提取前 5 条内容标题（selector 来自 snapshot 区块）"
}'
```

#### 第四步：向用户汇报（固定格式）
```
✅ [步骤 N] {context}
📸 截图: {screenshot_path}（可在屏幕上直接看到浏览器变化）
🔗 当前 URL: {url}
请确认操作是否符合预期，然后回复「#继续」「1」或「next」进入下一步。
```

#### 第五步：若操作失败
- 向用户说明错误信息
- 可再次 snapshot 获取最新选择器后重试
- **不要记录失败步骤**（失败时无 code_block，不影响脚本）

---

### 状态转换检测（每条消息都检查）

- 收到 `#结束录制` → 进入 **GENERATING**
- 收到 `#放弃` → 执行：
  ```bash
  python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-end --abort
  ```
  → 回到 IDLE
- 收到 `#继续` / `1` / `next` / `#好` / `#下一步` / `ok` → 继续执行多步计划的**当前步骤**（见上方「防超时规则」与「快捷确认词」）

---

## GENERATING 状态

按序执行，**不要跳过任何步骤**：

1. 回复："⏳ 正在保存并编译录制步骤，请稍候…"

2. 执行：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py record-end
   ```
   → 关闭浏览器 → 将录制的真实操作步骤编译为完整 Playwright 脚本 → 保存到 `rpa/{filename}.py` → 更新 registry

3. 输出成功提示：
   ```
   ✨ RPA 脚本生成成功！（基于真实录制，选择器均经过浏览器验证）
   
   📄 文件: ~/.openclaw/workspace/skills/openclaw-rpa/rpa/{filename}.py
   📋 共录制 {N} 个步骤
   📸 截图目录: ~/.openclaw/workspace/skills/openclaw-rpa/recorder_session/screenshots/
   
   已知限制:
   • [如涉及登录，提醒用户手动登录后再运行]
   • [其他从录制内容识别出的注意事项]
   
   以后执行这个 RPA：不确定有哪些任务时先发 **`#rpa-list`** 查看 **当前可用的已录制任务**；再发 **`#rpa-run:{任务名}`**（新开对话）或 **`#运行:{任务名}`**（仍在本对话）。
   ```

4. **禁止用 LLM 全文重写已生成脚本**（Agent 必须遵守）  
   - `record-end` 成功后，`rpa/{filename}.py` 已由 `recorder_server` 的 `_build_final_script()` 从真实录制的 `code_block` **逐段拼装**，与 `recorder_session/script_log.py` 同源。  
   - **不要**根据「任务描述」再生成一份完整 Playwright 脚本去覆盖或替代上述文件；那会丢掉录制器保证的选择器与 `evaluate` 语义，且易重新引入 `get_by_*` / `networkidle` 等与流水线不一致的写法。  
   - 若用户要改行为：**优先**用 `record-start` 重录有问题的步骤后再次 `record-end`；仅当改动极小时，可在现有 `rpa/*.py` 上**局部**修改，且须与 [playwright-templates.md](playwright-templates.md) 中骨架、`_EXTRACT_JS`、`_wait_for_content` 风格一致。

---

## RUN 状态

触发：用户消息满足上表 **`#rpa-run:`** 或 **`#运行:`** 规则；解析出的 `{任务名}` 传入 `rpa_manager.py run`（**须与已登记任务名一致**；不确定时让用户先 **`#rpa-list`**）。

含义：**执行一条已录制好的 RPA 脚本**（再次跑同一套步骤），不是开始新录制。

1. 回复："▶️ 正在运行「{任务名}」…"
2. 执行：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py run "{任务名}"
   ```
3. 捕获输出，完成后汇报结果摘要：
   ```
   ✅ 运行完毕: 「{任务名}」
   [stdout 摘要]
   ```
4. 若返回错误 "未找到任务"，列出当前可用任务：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list
   ```

---

## LIST 状态

触发：见上表 **顺序 2**（整条消息仅为 `#rpa-list`，不区分大小写）。

含义：回答用户 **「当前有哪些已录制、可以使用的 RPA」** —— 与 `rpa_manager.py list` / `registry.json` 一致。

1. 回复："📋 正在列出当前可用的已录制 RPA 任务…"
2. 执行：
   ```bash
   python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa_manager.py list
   ```
3. 将 **stdout** 展示给用户（可适度排版）；末尾用一两句话说明：上面列出的就是 **现在能直接运行的任务名**；要跑其中某一个，发 **`#rpa-run:任务名`**（新对话）或 **`#运行:任务名`**（当前对话）。

---

## 生成代码质量（Recorder 模式自动保证）

由于录制时直接使用真实 CSS 选择器 + headed 浏览器验证，生成脚本天然满足：

1. **选择器真实**：所有 target 均来自 snapshot 返回的 DOM，不会猜选择器
2. **异常捕获**：每步用 `try/except`，失败时自动截图再 raise
3. **路径参数化**：输出路径通过 `CONFIG["output_dir"]` 配置
4. **可移植性**：生成的 `.py` 可脱离 OpenClaw 独立运行

---

## Recorder 指令日志（审计每一步 Playwright 对应代码）

- **录制过程中**：每执行一次 `record-step`，`rpa_manager` 向 `recorder_session/playwright_commands.jsonl` **追加一行 JSON**（JSONL）。
- **每行内容**：`command`（与发给录制器的 JSON 一致，含 `action` / `target` / `value` / `seq` 等）、`success`、`error`、`code_block`（该步写入最终 RPA 的 Python 片段）、`url`、`screenshot`。
- **会话边界**：首行为 `type: session, event: start`；`record-end` 成功前再追加 `event: end`，并把完整日志复制到 `rpa/{任务slug}_playwright_commands.jsonl`，便于与 `rpa/{任务slug}.py` 对照验收。
- **`record-end --abort`**：会删除整个 `recorder_session`，日志一并丢弃。

---

## 示例交互

```
用户：#自动化机器人
系统：🤖 OpenClaw RPA 实验室已就绪 ... 请告诉我任务名称？

用户：每日资讯采集
系统：（执行 record-start）✅ Chrome 窗口已打开...

用户：打开 example-news.com，搜索"AI"，把结果页前 5 条标题存到桌面 titles.txt
系统：
  （多步指令检测：3 个子任务，触发拆解）
  （执行 plan-set '["打开目标网站", "搜索关键词 AI", "提取前5条标题存文件"]'）
  （执行第 1 步：record-step goto）→ 截图
  📍 进度: 1/3 步已完成 ✅ 打开目标网站
  📸 截图: step_01_...png
  请回复「#继续」「1」或「next」执行第 2/3 步: 搜索关键词 AI

用户：1
系统：
  （plan-status → 第 2 步）
  （record-step snapshot → 在 📋 中找到搜索框选择器，如 input[name="q"]）
  （record-step fill input[name="q"] AI）
  （record-step press Enter）
  （plan-next）
  📍 进度: 2/3 步已完成 ✅ 搜索关键词 AI
  📸 截图: step_03_...png
  请回复「#继续」「1」或「next」执行第 3/3 步: 提取前5条标题

用户：next
系统：
  （plan-status → 第 3 步）
  （record-step scroll value=1200 → 滚动触发结果列表懒加载）
  （record-step wait value=1200）
  （record-step snapshot → 在 🗂️ 区块中找到含"results"的容器 [data-testid="results"]）
  （record-step extract_text [data-testid="results"] h3 a titles.txt limit=5）
  （plan-next → 全部完成）
  🎉 所有 3 步已全部完成！titles.txt 已写入桌面。
  可以说「#结束录制」生成 RPA 脚本。

用户：#结束录制
系统：✨ 生成成功！rpa/mei_ri_zi_xun_cai_ji.py（5 步，真实录制，选择器均经浏览器验证）

用户：#rpa-run:每日资讯采集
系统：▶️ 正在运行... ✅ 运行完毕。

用户：#运行:每日资讯采集
系统：▶️ 正在运行... ✅ 运行完毕。

用户：#rpa-list
系统：📋 正在列出…（输出 `rpa_manager.py list` 的注册任务列表）
```
---

## 其他资源

- 代码生成指导原则：[synthesis-prompt.md](synthesis-prompt.md)（区分 Recorder 直接拼装与 Legacy LLM 合成；二者均须对齐 `playwright-templates.md` / `recorder_server._build_final_script`，禁止用旧版 `get_by_role` + `networkidle` 极简骨架作为主路径）
- Playwright 代码模板库：[playwright-templates.md](playwright-templates.md)（骨架与原子步骤与 `recorder_server.py` 中 `_build_final_script` / `_do_action` 生成物一致：`CONFIG`、`_EXTRACT_JS`、`_wait_for_content`、`page.locator` + `page.evaluate`）
- RPA 管理工具命令一览：

  **计划管理（防超时）：**
  `rpa_manager.py plan-set '<json>'` | `plan-next` | `plan-status`

  **Recorder 模式（推荐）：**
  `rpa_manager.py record-start <task>` | `record-step '<json>'` | `record-status` | `record-end [--abort]`

  **通用：**
  `rpa_manager.py run <task>` | `list`（对话中也可发 **`#rpa-list`** 触发 LIST 状态）

  **Legacy：**
  `rpa_manager.py init <task>` | `add --proof <file> '<json>'` | `generate` | `status` | `reset`
