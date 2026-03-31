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

## 演示视频

**场景：** Sauce Demo（[saucedemo.com](https://www.saucedemo.com)）电商购物流程，与仓库内录制 **`output.mp4`** 一致。

| | |
|:---|:---|
| **视频** | [在 GitHub 上打开](https://github.com/laziobird/openclaw-rpa/blob/main/output.mp4) · [直链下载](https://github.com/laziobird/openclaw-rpa/raw/main/output.mp4) · 仓库内 [`output.mp4`](output.mp4) |

**1. 对话里怎么开始（与视频一致）**

1. 发送触发词，例如 **`#rpa`** / **`#RPA`**，或消息中含 **`RPA`** / **「自动化机器人」**（完整规则见 [**SKILL.md**](SKILL.md) 与 [**SKILL.zh-CN.md**](SKILL.zh-CN.md) 中「触发检测」小节）。
2. 在引导中填写**任务名称**，例如 **`电商网站购物`**（也可与仓库已有脚本对齐，如 **`电商网站购物V10`**，见下表与 **`registry.json`**）。

**2. 本段录制的任务提示词（可先拆解、再逐步 `record-step`）**

1. 访问 `www.saucedemo.com`，使用账号 **`standard_user`**、密码 **`secret_sauce`** 登录。  
2. 将商品按**价格从高到低**排序。  
3. 将**价格最高的两件商品**加入购物车。  
4. **退出登录**。

**3. 详细步骤（协议与命令）**  
录制、快照、`select_option`、多步 **`plan-set`**、**「结束录制」** → `record-end` 等，均以 [**SKILL.zh-CN.md**](SKILL.zh-CN.md) 为准（见 **ONBOARDING**、**RECORDING**、防超时与 **`record-step`** 表格）。  
回放已保存任务：`运行：{任务名}`（例如 `运行：电商网站购物V10`），或 `python3 rpa_manager.py run <任务名>`（任务名以 **`registry.json`** 为准）。

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
| `wikipedia.py` / `wiki.py` | 维基百科（英文） |
| `豆瓣电影.py` | 中文界面示例（遵守站点规则） |
| `电商网站购物v10.py` 等 | Sauce Demo 电商流程（与 [演示视频](#演示视频) 同类） |

更多说明见 **`examples/README.md`**。

---

<p align="center">
  <sub>Apache License 2.0 · 版权 © 2026 openclaw-rpa contributors</sub>
</p>
