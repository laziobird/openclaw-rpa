# openclaw-rpa

**[English](README.md)** | 中文

## 演示视频

Sauce Demo（[saucedemo.com](https://www.saucedemo.com)）电商购物流程录屏。

> **说明：** GitHub 的 README **不会渲染** B 站等第三方 `<iframe>`，嵌入代码会显示成纯文本；**在线观看请点下方链接**，在哔哩哔哩站内播放。

### [▶ 在哔哩哔哩观看演示视频（BV1YfXrBBE9u）](https://www.bilibili.com/video/BV1YfXrBBE9u/)

<p align="center">
  <a href="https://www.bilibili.com/video/BV1YfXrBBE9u/"><img src="https://img.shields.io/badge/bilibili-点击播放演示-00A1D6?style=for-the-badge&logo=bilibili&logoColor=white" alt="在哔哩哔哩播放"></a>
</p>

<p align="center">
  <sub>
    备用：<a href="https://github.com/laziobird/openclaw-rpa/blob/main/output.mp4">GitHub 预览</a>
    · <a href="https://github.com/laziobird/openclaw-rpa/raw/main/output.mp4">MP4 直链</a>
    · 仓库 <a href="output.mp4"><code>output.mp4</code></a>
  </sub>
</p>

**与视频一致的对话步骤**

1. 发送 **`#rpa`** / **`#RPA`**，或消息中含 **`RPA`** / **「自动化机器人」**（规则见 [**SKILL.md**](SKILL.md)、[**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. 任务名示例：**`电商网站购物`**，或与已有脚本对齐如 **`电商网站购物V10`**（见 **`registry.json`**）。

**本段任务提示词**

1. 访问 `www.saucedemo.com`，账号 **`standard_user`** / 密码 **`secret_sauce`** 登录。  
2. 价格**从高到低**排序。  
3. 将**最贵的两件**商品加入购物车。  
4. **退出登录**。

录制协议（`record-start`、`record-step`、`plan-set`、结束录制等）见 [**SKILL.zh-CN.md**](SKILL.zh-CN.md)。回放：`运行：{任务名}` 或 `python3 rpa_manager.py run <任务名>`。

---

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
| `wikipedia.py` / `wiki.py` | 维基百科（英文） |
| `豆瓣电影.py` | 中文界面示例（遵守站点规则） |
| `电商网站购物v10.py` 等 | Sauce Demo 电商流程（与顶部 [演示视频](#演示视频) 同类） |

更多说明见 **`examples/README.md`**。

---

<p align="center">
  <sub>Apache License 2.0 · 版权 © 2026 openclaw-rpa contributors</sub>
</p>
