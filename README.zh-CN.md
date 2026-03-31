# openclaw-rpa

**[English](README.md)** | 中文

借助 **AI**，把你在**常见网站**上的操作，以及需要的**本机文件**行为，录制成可重复运行的 **RPA 脚本**（Python / Playwright）。日常执行**直接跑脚本**，不必每次让模型现场点网页——**省算力**，且步骤按录制固定执行，**更稳、少受模型幻觉影响**。

**涵盖：** 浏览器里的真实交互；脚本中也可包含读写、整理本机文件等（可与网页分开或组合）。

**举例：** 定时跑同一段下单/填表脚本；或在脚本里加几行只整理下载目录——重复执行时都不再走一遍「模型当场操作」。

## 在 OpenClaw 中配置（完整步骤）

把本仓库当作 **OpenClaw 技能** 使用：智能体会加载本目录下的 **`SKILL.md`**（路由）以及 **`SKILL.zh-CN.md`** / **`SKILL.en-US.md`**，并通过 **`rpa_manager.py`** 执行录制。

### 1. 技能目录位置

| | 默认路径 |
|---|----------|
| OpenClaw 工作区根目录 | `~/.openclaw/workspace` |
| 本技能目录（文件夹名） | `~/.openclaw/workspace/skills/openclaw-rpa` |

若尚未克隆，执行：

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa
```

SSH：`git clone git@github.com:laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa`

### 2. Python、Playwright、Chromium

在技能目录下执行：

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
chmod +x scripts/install.sh
./scripts/install.sh
```

会创建 **`.venv`**，安装 **`requirements.txt`** 并执行 **`playwright install chromium`**。

### 3. 技能配置（`config.json`）

**`SKILL.md`** 里 **`metadata.openclaw.localeConfig`** 指向 **`config.json`**。从示例生成（默认语言 **`en-US`**）：

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
python3 scripts/bootstrap_config.py
python3 scripts/set_locale.py zh-CN    # 或 en-US
```

详见 **`LOCALE.md`**。若无 **`config.json`**，按 **`SKILL.md`** 说明可读 **`config.example.json`** 的 `locale`。修改语言后请**新开会话**或让智能体**重新读取** **`SKILL.md`** / **`SKILL.*.md`**。

### 4. 实际执行用的 Python

录制相关命令使用 **`sys.executable`**。启动 **`rpa_manager.py`** 的解释器必须已安装 **Playwright**。若网关用系统 **`python3`** 调工具，请在该环境安装依赖，或把网关配置为使用：

`~/.openclaw/workspace/skills/openclaw-rpa/.venv/bin/python`

来运行 **`rpa_manager.py`** 及 **`rpa/`** 下生成的脚本。

### 5. 重新加载技能

首次安装或修改 **`SKILL*.md`**、**`config.json`** 后，请**新开会话**或重新加载技能，使智能体读到最新说明。

### 6. 触发词与发现

触发词与关键词见 **`SKILL.md`**（YAML `description` 与路由说明），例如 `#RPA`、`自动化机器人` 等。若需对外发布，可通过 **[ClawHub](https://clawhub.ai/publish-skill)** 绑定本 GitHub 仓库。

### 7. 自检

```bash
cd ~/.openclaw/workspace/skills/openclaw-rpa
source .venv/bin/activate   # 可选
python3 rpa_manager.py env-check
```

### 8. 技能正文里的路径

**`SKILL.en-US.md`** / **`SKILL.zh-CN.md`** 中的示例命令可能写 **`~/.openclaw/workspace/skills/openclaw-rpa/`**。若你的工作区不在默认路径，请改为本机实际技能目录，或使用符号链接。

---

## 环境要求

- **Python 3.8+**（建议 3.10+）
- **pip** 以及用于 `pip install` 与 Playwright 浏览器下载的网络

## 安装（推荐）

若已在上方「在 OpenClaw 中配置」里执行过 **`./scripts/install.sh`**，可跳过本节。

在本仓库（技能）根目录执行：

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

将创建 **`.venv`**，按 `requirements.txt` 安装 Python 依赖，并执行 **`playwright install chromium`**。

之后每次使用本技能前先激活虚拟环境：

```bash
source .venv/bin/activate
```

### 手动安装

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
python -m playwright install chromium
```

### 环境自检

```bash
python3 envcheck.py
# 或
python3 rpa_manager.py env-check
```

`record-start` 与 `run` 也会检查 Python + Playwright，并在可能时**自动安装 Chromium**（与原先行为一致）。

**`config.json` / 对话语言** 见上文「在 OpenClaw 中配置」第 3 步。

## 快速开始（命令行）

```bash
python3 rpa_manager.py env-check
python3 rpa_manager.py list
python3 rpa_manager.py run wikipedia
```

录制流程：`record-start` → `record-step` → `record-end`（详见 `rpa_manager.py` 文件内说明）。

## 示例脚本

预生成脚本与指令日志在 **`rpa/`** 下。建议入门：

| 脚本 | 说明 |
|------|------|
| `rpa/wikipedia.py` | 稳定公网站点（英文） |
| `rpa/wiki.py` | 同类流程，不同命名 |
| `rpa/豆瓣电影.py` | 中文界面示例（请遵守站点规则） |
| `rpa/电商网站购物v10.py` | 电商类流程示例（仅供演示） |

**examples/README.md** 中有更完整的推荐与注意事项。

## 许可证

[Apache License 2.0](LICENSE) — 版权 © 2026 openclaw-rpa contributors。
