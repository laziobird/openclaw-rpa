# 🏨 案例教程：零代码打造 Airbnb 竞品民宿比价追踪机器人

本教程将手把手教你如何使用 OpenClaw-RPA 技能，通过一段简单的“大白话”，制作一个能自动打开浏览器、提取 Airbnb 竞品价格与评分，并最终生成 Word 报告的 RPA 机器人。

**核心优势：** 录制一次，自动生成 Python 脚本。以后每次运行直接跑底层代码，**速度极快，且零 Token 消耗，不会产生 AI 幻觉。**

---

## 🛠️ 第一步：安装与准备

1. **安装 OpenClaw RPA 技能**
   如果你还没有安装该技能，请在 OpenClaw 中安装：
   * **Skill 地址**：[https://clawhub.ai/laziobird/openclaw-rpa](https://clawhub.ai/laziobird/openclaw-rpa)
   * 或者参考 GitHub 首页的命令行安装方式。

2. **选择合适的 AI 模型**
   为了确保 AI 能精准理解网页结构并生成正确的代码，推荐在 OpenClaw 中切换到以下大模型：
   * Minimax 2.7
   * Gemini Pro 3.0 及以上
   * Claude Sonnet 4.6

---

## 🎬 第二步：发送提示词，开始录制

打开 OpenClaw 的对话框（确保已启用 RPA 技能），直接将下面的**全部内容**复制并发送给 AI。

> **💡 提示：** 
> * 第一行的 `#RPA` 是触发词。
> * 第二行的 `Airbnb比价追踪` 是你给这个机器人起的名字。
> * 第三行的 `F` 是能力码（代表需要使用网页 + Word 表格能力）。

```text
#RPA
Airbnb比价追踪
F

[变量]
query_time = ### 系统当前时间，精确到分钟，格式XX月XX日XX时XX分 ###

output_path = '~/Desktop/Airbnb/hotelCompare.docx'

urls:
  https://www.airbnb.cn/rooms/1517880824760006835?location=%C5%8Csaka-shi%2C%20%C5%8Csaka-fu%2C%20JP&search_mode=regular_search&adults=1&check_in=2026-04-20&check_out=2026-04-27
  https://www.airbnb.cn/rooms/1520897875971878894?location=%C5%8Csaka-shi%2C%20%C5%8Csaka-fu%2C%20JP&search_mode=regular_search&adults=1&check_in=2026-04-20&check_out=2026-04-27
  https://www.airbnb.cn/rooms/1239558906468787551?check_in=2026-04-20&check_out=2026-04-27&location=%E6%96%B0%E4%BB%8A%E5%AE%AB%E7%AB%99&search_mode=regular_search&adults=1
  
入住时间 = '2026-04-20 到 2026-04-27'

[步骤]
1. 遍历 ${urls}，逐一访问每个网址
2. 每个网页提取 3 个字段：民宿名字、房间名称、价格,评分， 同时加上两个字段 ${query_time}、${入住时间}
3. 将所有数据整理成表格，表头：民宿名字 | 房间名称 | 价格 | 评分 | 查询时间 | 入住时间
4. 追加到 ${output_path} 指定的 Word 文档末尾并保存（文件不存在则自动新建）

[约束]
网址 ${urls} 都来自同一网站，要循环复用
```

---

## ⏳ 第三步：等待 AI 录制与生成脚本

发送上述指令后，你会看到 AI 开始工作：
1. 它会在后台启动真实的 Chrome 浏览器。
2. 逐一访问你提供的 Airbnb 链接。
3. 像人眼一样“看”网页，提取价格、评分等信息。
4. 最终，它会提示你“录制完成”，并在本地生成一个名为 `Airbnb比价追踪.py` 的独立 Python 脚本。

*(这个过程 AI 会消耗少量 Token 进行推理，但这是**一次性**的。)*

---

## 🚀 第四步：日常运行（零成本回放）

脚本生成后，你以后每天需要查价格时，**不需要再发送那一长串提示词了**！

你有两种方式可以极速运行它：

**方式一：在聊天框中快捷触发**
直接在 OpenClaw（或绑定的飞书/钉钉）中发送：
```text
#rpa-run:Airbnb比价追踪
```
系统会瞬间在后台执行脚本，几秒钟后，你的桌面上就会多出一个包含最新数据的 Word 文档。

**方式二：脱离 AI，本地定时运行**
你也可以直接在电脑的终端（Terminal）里运行这个生成的脚本，甚至用系统的定时任务（Crontab/Windows 任务计划）让它每天早上 8 点自动跑：
```bash
python3 rpa/Airbnb比价追踪.py
```

---

## 📊 预期结果展示

运行结束后，打开你桌面上的 `~/Desktop/Airbnb/hotelCompare.docx` 文件，你会看到类似下面这样排版整齐的表格。每次运行，新的数据都会自动追加到文档末尾，方便你对比历史价格！

| 民宿名字 | 房间名称 | 价格 | 评分 | 查询时间 | 入住时间 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 大阪难波温馨民宿 | 豪华双人床房 | ￥450 | 4.8 | 04月14日10时30分 | 2026-04-20 到 2026-04-27 |
| 心斋桥附近公寓 | 舒适单间 | ￥380 | 4.9 | 04月14日10时30分 | 2026-04-20 到 2026-04-27 |
| 新今宫站旁和风旅馆 | 传统榻榻米房 | ￥520 | 4.7 | 04月14日10时30分 | 2026-04-20 到 2026-04-27 |

*(注：以上数据为示例，实际运行将抓取网页上的真实实时数据)*