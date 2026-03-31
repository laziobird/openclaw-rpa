# openclaw-rpa

**[English](README.md)** | 中文

> 借助 **AI**，把**常见网页**与**本机文件**相关操作录成 **可重复运行的 Playwright Python 脚本**。日常**直接跑脚本**，少调大模型——**省算力**，步骤**更稳**、少受幻觉影响。

| | |
|:---|:---|
| **环境** | Python **3.8+**，需网络安装依赖与浏览器 |
| **许可证** | [Apache 2.0](LICENSE) |

---

## 快速安装（OpenClaw）

技能目录：**`~/.openclaw/workspace/skills/openclaw-rpa`**

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/laziobird/openclaw-rpa.git ~/.openclaw/workspace/skills/openclaw-rpa
cd ~/.openclaw/workspace/skills/openclaw-rpa

chmod +x scripts/install.sh && ./scripts/install.sh
python3 scripts/bootstrap_config.py
python3 scripts/set_locale.py zh-CN    # 或 en-US

python3 rpa_manager.py env-check
```

**SSH 克隆：** `git@github.com:laziobird/openclaw-rpa.git`

装好后请**新开 OpenClaw 会话**（或重载技能），以便加载 **`SKILL.md`**。触发词见 **`SKILL.md`**（如 `#RPA`、`自动化机器人`）。

---

## 高级配置

<details>
<summary><b>手动安装 · 网关 Python · 路径 · 发布</b></summary>

### 手动安装（不用 `install.sh`）

```bash
cd /path/to/openclaw-rpa
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
python -m playwright install chromium
```

### 网关实际调用的 Python

`rpa_manager.py` 使用 **`sys.executable`**，该解释器必须已装 **Playwright**。若网关用系统 **`python3`**，请在同一环境装依赖，或把工具指向：

`~/.openclaw/workspace/skills/openclaw-rpa/.venv/bin/python`

### 语言与 `config.json`

- **`SKILL.md`** 中 **`localeConfig`** 指向 **`config.json`**
- 若无 **`config.json`**，可按 **`SKILL.md`** 用 **`config.example.json`** 读 `locale`
- 详见 **`LOCALE.md`**

### `SKILL.*.md` 里的路径

示例中的 `~/.openclaw/workspace/skills/openclaw-rpa/` 若与你的本机不一致，请改成实际技能目录。

### 对外发布技能

**[ClawHub — 发布 skill](https://clawhub.ai/publish-skill)**（绑定本 GitHub 仓库）。

### 环境自检

```bash
python3 envcheck.py
# 或
python3 rpa_manager.py env-check
```

`record-start` / `run` 在可能时会自动安装 Chromium。

</details>

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
| `wikipedia.py` | 稳定公网（英文） |
| `wiki.py` | 同类流程，不同命名 |
| `豆瓣电影.py` | 中文界面示例（遵守站点规则） |
| `电商网站购物v10.py` | 电商类演示（示例） |

更多说明见 **`examples/README.md`**。

---

<p align="center">
  <sub>Apache License 2.0 · 版权 © 2026 openclaw-rpa contributors</sub>
</p>
