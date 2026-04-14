# 🚀 OpenClaw-RPA 

**[English](README.md)** | 中文

### **AI Agent 的“RPA 编译器”**
**一次记录 → 永久重放为确定性 Python 脚本。彻底终结重复任务中的“大模型税”。**

[![许可证: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/powered%20by-Playwright-green)](https://playwright.dev/)

---

## 💡 为什么选择 OpenClaw-RPA？

目前的 AI 网页、Computer Use Agent 虽然强大，但在生产环境中存在**本质缺陷**：
* **“大模型税” (LLM Tax)：** 为什么要为了 Agent 点击一个它已经点过 100 次的“下载”按钮而重复支付 Token 费用？
* **高延迟：** 等待大模型对固定的 UI 界面进行“推理”极其缓慢。
* **不可控性：** 大模型每次运行结果都可能会产生幻觉，从而破坏稳定的工作流。

**OpenClaw-RPA 弥补了这一鸿沟。** 利用大模型的智能来**发现并记录**一次工作流，然后将其编译为**独立的、高速运行的 Playwright 脚本**。此后运行，**Token 消耗永远为零**。

---

## ✨ 核心特性

* **⚡ 零 Token 重放：** 将 Agent 的推理过程编译为纯 Python 代码。在日常重复任务中节省 100% 的推理成本。比如：在实时浏览器窗口中立即回放你录制的操作行为。
* **🔑 会话保持与免登录 (#rpa-login)：** 手动解决一次 2FA、二维码或短信验证。工具会自动将 Cookie 注入到未来的所有无头（Headless）运行中。**永久绕过登录墙。**
* **🌐 HTTP API 记录：** 在同一个可重放脚本中，将 REST `GET/POST` 请求与浏览器操作完美融合。
* **📄 原生 Office 自动化：** 内置 `excel_write` 和 `word_write`。**无需安装 Microsoft Office。** 非常适合 Linux/Docker 环境。
* **🔗 无缝集成：** 作为 OpenClaw 生态系统中的强大技能设计，同时生成标准的 Python/Playwright 代码。

---

## 🎥 有图有真相 (Show, Don't Tell)

| **记录模式 (大模型思考中)** | **重放模式 (确定性脚本)** |
| :--- | :--- |
| *Agent 分析 DOM 并规划动作...* | *以原生代码速度执行...* |
| 💸 **成本：** $$$ (消耗 Token) | 💰 **成本：** $0.00 (纯 Python) |
| 🐢 **速度：** 缓慢 (需要推理) | 🚀 **速度：** 瞬间 (直接执行) |

![shopping-hd-960p](https://github.com/user-attachments/assets/4c30d799-803e-458b-a496-ee5f38513da8)

### 竞争优势 

| 特性 | 传统 RPA (UIPath 等) | 纯 LLM Agent (Browser-use 等) | **OpenClaw-RPA (编译器模式)** |
| :--- | :--- | :--- | :--- |
| **开发成本** | **高** (人工编写选择器与逻辑) | **低** (自然语言描述) | **极低 (自动记录并编译)** |
| **运行成本** | **高** (昂贵的商业授权) | **极高** (每次运行均消耗 Token) | **接近零 (原生 Python 脚本运行)** |
| **执行速度** | **中等** | **缓慢** (受大模型推理延迟影响) | **极快 (代码级原生执行速度)** |
| **稳定性** | **脆弱** (网页改版即失效) | **随机性** (存在模型幻觉风险) | **确定性 (高可靠代码执行)** |
| **2FA 处理** | **极其复杂** | **昂贵** (需实时推理配合) | **简单 (Session 一次性捕获)** |
| **部署环境** | **Windows & MS Office 依赖** | **灵活** (但运行成本高) | **云原生 (支持 Linux/Docker)** |
| **技术架构** | 人工绘制流程图 | 实时在线推理 | **一次推理 → 编译 → 永久重放** |

## 工作原理

```
你（自然语言描述任务）
      │
      ▼
  #rpa / #RPA / #rpa-api     ← 触发
      │
      ▼
 AI 驱动真实 Chrome           ← record-step（每步截图留证）
      │
      ▼
 「结束录制」                  ← 合成脚本
      │
      ▼
 rpa/<任务名>.py               ← 独立 Playwright Python 脚本
      │
      ▼
 python3 rpa/<任务名>.py       ← 回放——无模型、无 AI、随处运行
```

**为什么不直接每次让 AI 点浏览器、Computer Use？**

| 痛点 | 说明 |
|------|------|
| 🌀 **幻觉 / 误操作** | 模型有时会点错按钮、找错元素、自己编一个不存在的操作——每次「临场发挥」都有出错风险 |
| 💸 **费用高** | 每次重复任务都调大模型，token + 工具调用 + 长上下文，单次会话轻松数美元；高频任务很快失控 |
| 🐢 **速度慢** | 每一步都要等模型推理再执行，整个流程比直接跑脚本慢一个数量级 |

**openclaw-rpa 的做法：** 用 AI 录制一次、验证一次，之后所有重复执行走本地脚本——**不调模型、不烧 token、不怕幻觉、秒级完成**。

## 快速开始

```bash
# 安装
git clone https://github.com/laziobird/openclaw-rpa.git
cd openclaw-rpa && ./scripts/install.sh

# 在 OpenClaw 对话中，选择触发词：
#rpa                   # 纯网页流程
#rpa-api               # 含 HTTP API 的流程
#rpa-login <url>       # 保存登录会话（Cookie）
#rpa-list              # 列出所有已录制任务
#rpa-run:<任务名>      # 回放已录制任务
```

完整协议与能力码（A–G）：**[SKILL.zh-CN.md](SKILL.zh-CN.md)**。

---

## 案例视频

### 1、Sauce 电商购物网站 浏览器录屏

**Sauce **（[saucedemo.com](https://www.saucedemo.com)）录屏：**登录 → 按价格排序 → 加购最贵两件 → 登出**。展示从触发到录制、生成脚本的一条完整流程。

| 观看方式 | 链接 |
|:--|:--|
| **哔哩哔哩（推荐，高清）** | **[▶ 点击播放](https://www.bilibili.com/video/BV1YfXrBBE9u/)**（BV1YfXrBBE9u） |

https://github.com/user-attachments/assets/d368a81e-425a-4830-bc29-fe11e89eda92

**对话步骤**

1. 发送 **`#rpa`** / **`#RPA`**（规则见 [**SKILL.md**](SKILL.md)、[**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. **一条消息两行**：第 1 行任务名（如 **`电商网站购物`**），第 2 行能力码（如 **`A`** 仅网页；含表格用 **`D`** 等），规则见 **SKILL.zh-CN.md**「ONBOARDING」。

**任务提示词**

1. 访问 `www.saucedemo.com`，账号 **`standard_user`** / 密码 **`secret_sauce`** 登录。  
2. 价格**从高到低**排序。  
3. 将**最贵的两件**商品加入购物车。  
4. **退出登录**。

录制协议（`record-start`、`record-step`、`plan-set`、`#end` 等）见 [**SKILL.zh-CN.md**](SKILL.zh-CN.md)。**先看有哪些已录好的 RPA 可用**：发 **`#rpa-list`**；**再跑其中一个**：`#rpa-run:{任务名}` 或 `python3 rpa_manager.py run <任务名>`。

<a id="douban-movie-demo"></a>

### 2、豆瓣电影（《霸王别姬》）— 浏览器录屏

**豆瓣电影**（[movie.douban.com](https://movie.douban.com)）：**进入电影首页 → 搜索目标影片 → 打开第一条搜索结果详情页 → 抽取片名、豆瓣评分与剧情简介，并写入桌面文本文件**。本案例演示如何用 RPA 把「检索 + 打开详情 + 抽取影评页关键字段」录成可重复执行的 Playwright 脚本（与顶部 Sauce 流程同为「触发 → 录制 → 合成脚本」）。

https://github.com/user-attachments/assets/594c8970-2f11-4e2b-ae57-e563cafe6bbd

**录屏中的对话步骤**

1. 发送 **`#rpa`** / **`#RPA`**（规则见 [**SKILL.md**](SKILL.md)、[**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. 任务名示例：与 **`registry.json`** 中已有脚本对齐，如 **`豆瓣电影V6`**（`豆瓣电影v6.py`）、**`获取豆瓣电影数据`**（`获取豆瓣电影数据.py`）等。

**任务提示词（豆瓣电影片段）**

1. 访问 `https://movie.douban.com`。
2. 搜索电影 **「霸王别姬」** → 点击**搜索结果的第一条**，进入详情页 → 抽取 **片名**、**评分**、**剧情简介**。
3. 将抽取内容保存到桌面的 **`movie.txt`**。

<a id="api-quotes-news-brief-zh"></a>

### 3、行情 API + 新闻页 + 本地简报（浏览器 + API + 文件）

**雅虎财经等（浏览器）+ 网上行情数据（接口）**：**先保存一份股票日线数据到桌面 → 再打开财经网站标的页 → 切换到新闻 → 把新闻标题写入桌面文本**。本案例在「网页操作」之外多一步「向行情服务请求数据」；**接口地址、密钥怎么配**见下文 **[API 说明](#api_call_notes)**（[`api_call` 整节](#api_call)）。

**录屏中的对话步骤**

1. 发送 **`#rpa-api`**（含 API 接口的流程专用触发词；规则见 [**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. 任务名示例：与 **`registry.json`** 对齐，或新建如 **`NVDA行情新闻简报`**。

**任务提示词（行情 + 新闻 + 本地简报）**

```
#rpa-api
###
拉取 NVDA 股票的日线数据，保存到桌面的 nvda_time_series_daily.json
对应的 API 文档  https://www.alphavantage.co/documentation/#daily
对应的 API key  UXZ3BOXOH817CQWS
###
打开新浪财经 https://finance.sina.com.cn/，搜索 NVDA，等跳转新页面，点击页面左侧菜单的「公司新闻」，等跳转新页面，把页面前五条新闻标题存到桌面 nvda_news.txt
把行情数据 nvda_time_series_daily.json 和新闻 nvda_news.txt 合并成一个简报文件，叫 nvda.txt
```

也可以直接粘贴 API 文档参数片段：

```
#rpa-api
###
API Parameters
❚ Required: function → TIME_SERIES_DAILY
❚ Required: symbol   → NVDA
❚ Required: apikey
示例: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=UXZ3BOXOH817CQWS
对应的 apikey  UXZ3BOXOH817CQWS
###
打开新浪财经 https://finance.sina.com.cn/，搜索 NVDA，等跳转新页面，点击左侧「公司新闻」，把前五条标题存到桌面 nvda_news.txt
把 nvda_time_series_daily.json 和 nvda_news.txt 合并成 nvda.txt
```

### 4、Airbnb 民宿竞品比价追踪机器人（网页 + 视觉识别 + Word）

**场景：** 零代码打造一个能自动打开浏览器、提取 Airbnb 竞品价格与评分，并最终生成 Word 报告的 RPA 机器人。

- **完整案例：** **[articles/scenario-airbnb-compare.md](articles/scenario-airbnb-compare.md)**
- **说明：** 录制一次，自动生成 Python 脚本。以后每次运行直接跑底层代码，速度极快，且零 Token 消耗，不会产生 AI 幻觉。
- **视觉模式处理 SPA：** Airbnb 是高度动态的单页应用（SPA），传统爬虫几乎无法处理。本案例引入**视觉识别**模式，AI 像人一样"看"页面来提取数据，无需依赖不稳定的 DOM 结构。视觉模型采用 [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)（阿里开源），Token 消耗极小，支持本地部署。

### 4、OpenClaw + 飞书/Lark：`#rpa-list`、`#rpa-run` 定时执行 RPA 自动化程序

录屏演示在飞书/Lark 与 **OpenClaw-bot** 对话中的典型用法：

- **`#rpa-list`**：查看当前已注册、可执行的 RPA 任务；
- **`#rpa-run:电商网站购物V10`**：在新对话中执行已录制的脚本；
- **「一分钟后运行 #rpa-run:电商网站购物V10」** 等自然语言：在 OpenClaw + IM 侧预约或提醒稍后执行（具体以你的 OpenClaw 与机器人配置为准；脚本本身仍由 `rpa_manager.py run` 执行）。

https://github.com/user-attachments/assets/514e2d74-f42a-4243-8d49-52931fe6c22e

<a id="scenario-ap-reconciliation-zh"></a>

### 5、自动登录（Cookie 复用）— 免验证码录制登录后页面

**场景：** 携程、电商平台等含短信验证码 / 滑块的站点，手动登录一次后保存 Cookie，后续录制与回放**自动注入**，直接从业务页面开始，跳过登录流程。

**两个完整案例：**

| 案例 | 说明 | 资料 |
|------|------|------|
| **Sauce Demo 电商** | 保存登录态 → 直接打开商品页 → 价格从高到低排序 | 完整指令 + 截图 |
| **携程酒店查询** | 保存携程登录态 → 打开酒店详情页 → 抓取名称/评分/房型/价格 → 保存为 `hotel.docx` | 完整录制视频 |

**👉 完整教程：[articles/autologin-tutorial.md](articles/autologin-tutorial.md)**

**指令速查：**

```
#rpa-login <登录页URL>        → 打开浏览器，手动完成登录（支持短信/滑块/扫码）
#rpa-login-done               → 导出 Cookie 并关闭浏览器
#rpa-autologin <域名或URL>    → 录制/回放时自动注入已保存的 Cookie
#rpa-autologin-list           → 查看所有已保存的登录会话
```

---

### 6、应付对账 — 只拉接口数据 + 本地 Excel + Word 表格报告

**财务 / 应付：** 云端 Mock **仅 GET** 拉待对账数据；**不回写 ERP**；与桌面 **发票 Excel** 在本地对账；最终输出带**表格**的 **Word（`.docx`）**。

- **完整案例：** **[articles/scenario-ap-reconciliation.md](articles/scenario-ap-reconciliation.md)**  
- **录制：** `#rpa-api` 或 `#rpa`；能力码常用 **F**（表+Word）；步骤 2/3a 用 `excel_write`（`rows_from_json` / `rows_from_excel` 动态行），步骤 3b 用 `python_snippet` 注入匹配计算代码（录制时立即验证）。  
- **`python_snippet` 设计原理：** **[articles/python-snippet-design.md](articles/python-snippet-design.md)**（执行环境、验证机制、完整 JSON 示例）。


---

> 借助 **AI**，把**常见网页**与**本机文件**相关操作录成 **可重复运行的 Playwright Python 脚本**。日常**直接跑脚本**，少调大模型——**省算力**，步骤**更稳**、少受幻觉影响。


|         |                             |
| ------- | --------------------------- |
| **环境**  | Python **3.8+**，需网络安装依赖与浏览器 |
| **推荐大模型** | Minimax 2.7 · Google Gemini Pro 3.0 及以上 · Claude Sonnet 4.6 |
| **许可证** | [Apache 2.0](LICENSE.md) |


---

## 快速安装（OpenClaw）

技能目录：`**~/.openclaw/workspace/skills/openclaw-rpa`**

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa
cd ~/.openclaw/workspace/skills/openclaw-rpa

chmod +x scripts/install.sh && ./scripts/install.sh
python3 scripts/bootstrap_config.py
python3 scripts/set_locale.py zh-CN    # 或 en-US

python3 rpa_manager.py env-check
```

录制前若任务含 **Excel / Word**（见 **SKILL.zh-CN.md** 能力码 **B–G**），可在**同一 `python3`** 下执行：`python3 rpa_manager.py deps-check D`（示例）；缺组件时对话里会引导 `deps-install`。

**SSH 克隆：** `git@github.com:laziobird/openclaw-rpa.git`

装好后请**新开 OpenClaw 会话**（或重载技能），以便加载 `**SKILL.md`**。触发词见 `**SKILL.md**`（如 `#RPA`、`#rpa`）。

### `requirements.txt` 全量依赖是什么？

**「全量」**指：与本技能配套的 **所有 Python 包**（见仓库根目录 `requirements.txt`）以及 **`playwright install chromium`** 所安装的 Chromium，都应装在 **同一个** 用于执行 `rpa_manager.py` / 录制的 Python 环境里（例如 `./scripts/install.sh` 创建的 `.venv`）。

| 依赖 | 作用 |
|------|------|
| **playwright** | 启动 Recorder 用的有头 Chromium；生成脚本里的 `async_playwright`、页面操作 |
| **httpx** | 录制与回放中的 **`api_call`**（GET/POST 等） |
| **openpyxl** | 录制与回放中的 **`excel_write`**（.xlsx 多表、表头、行数据、冻结窗格、隐藏列等） |
| **python-docx** | 录制与回放中的 **`word_write`**（安装包名是 `python-docx`，代码里 `from docx import Document`） |
| **Chromium** | 由 `python -m playwright install chromium` 下载，**不属于** `pip` 包 |

未列在表里的系统库：一般只需本机已有 Python 3.8+；macOS/Linux 常见环境即可。若只做纯网页录制且确定不用 Excel/Word，技术上可只装 `playwright`+`httpx`，但**推荐**仍使用完整 `requirements.txt`，避免 `record-step excel_write` 时报缺包。

---

## 高级配置

手动安装、网关 Python、语言配置、路径、发布说明：
**[articles/advanced-setup.zh-CN.md](articles/advanced-setup.zh-CN.md)**

---

## 命令行快速体验

```bash
python3 rpa_manager.py env-check
python3 rpa_manager.py list
python3 rpa_manager.py run wikipedia
```

录制流程：`record-start` → `record-step` → `record-end`（见 `rpa_manager.py` 内说明）。

---

## 示例脚本（`rpa/`）


| 脚本 | 说明 |
|------|------|
| `wikipedia.py` / `wiki.py` | 维基百科（英文） |
| `获取豆瓣电影数据.py` 等 | 中文界面示例（遵守站点规则）；浏览器录屏案例见 [豆瓣电影（《霸王别姬》）](#douban-movie-demo) |
| `电商网站购物v10.py` 等 | Sauce Demo 电商流程（与顶部 [演示视频](#演示视频) 同类） |
| `apiv3.py`（`apiV3`） | **纯 API** — Alpha Vantage `TIME_SERIES_DAILY` 拉取 NVDA 日线数据 → 保存 `nvda_time_series_daily.json` 到桌面；无浏览器步骤 |
| `reconciliationv2.py`（`reconciliationV2`） | **应付对账（英文版）** — Mock GET 拉待对账数据 → `ap_draft_thisweek.xlsx`（System / Invoices / Match Results，两阶段 po_ref + 金额匹配）→ `ap_reconciliation_YYYYMMDD.docx` Word 表格报告（见[案例文档](articles/scenario-ap-reconciliation.en-US.md)） |
| `会计记账v2.py`（`会计记账V2`） | **应付对账（中文版）** — 同上流程中文化：Mock GET → `对账底稿_本周.xlsx`（系统侧 / 发票侧 / 匹配结果）→ `对账报告_YYYYMMDD.docx` Word 表格报告（见[案例文档](articles/scenario-ap-reconciliation.md)） |

---

<a id="api_call"></a>

## 调用 API 的录制（`api_call`）

录制器支持 **`api_call`** 步骤（通过 httpx 发 GET/POST，响应可选保存到桌面）。

完整指南 — 密钥写入策略、env 字段说明、示例：
**[articles/api-call-guide.zh-CN.md](articles/api-call-guide.zh-CN.md)**

---

**说明与边界**

- **合规**：请遵守各网站服务条款与使用政策；本仓库不鼓励绕过风控或在禁止场景下抓取数据。
- **强风控站点（如 LinkedIn）**：即便支持自动登录或会话复用，仍可能遇到 **2FA、设备验证、验证码、风控拦截**，需要**人工介入**。

---

Apache License 2.0 · 版权 © 2026 openclaw-rpa contributors
