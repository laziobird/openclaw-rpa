# openclaw-rpa

**[English](README.md)** | 中文

## 案例视频

### 1、Sauce 电商购物网站 浏览器录屏

**Sauce **（[saucedemo.com](https://www.saucedemo.com)）录屏：**登录 → 按价格排序 → 加购最贵两件 → 登出**。展示从触发到录制、生成脚本的一条完整流程。
=======
| 观看方式 | 链接 |
|:--|:--|
| **哔哩哔哩（推荐，高清）** | **[▶ 点击播放](https://www.bilibili.com/video/BV1YfXrBBE9u/)**（BV1YfXrBBE9u） |

https://github.com/user-attachments/assets/d368a81e-425a-4830-bc29-fe11e89eda92

**对话步骤**

1. 发送 **`#rpa`** / **`#RPA`** / **`#自动化机器人`**（规则见 [**SKILL.md**](SKILL.md)、[**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. 任务名示例：**`电商网站购物`**，或与已有脚本对齐如 **`电商网站购物V10`**（见 **`registry.json`**）。

**任务提示词**

1. 访问 `www.saucedemo.com`，账号 **`standard_user`** / 密码 **`secret_sauce`** 登录。  
2. 价格**从高到低**排序。  
3. 将**最贵的两件**商品加入购物车。  
4. **退出登录**。

录制协议（`record-start`、`record-step`、`plan-set`、`#结束录制` 等）见 [**SKILL.zh-CN.md**](SKILL.zh-CN.md)。**先看有哪些已录好的 RPA 可用**：发 **`#rpa-list`**；**再跑其中一个**：`#rpa-run:{任务名}`（新对话）或 `#运行:{任务名}` / `python3 rpa_manager.py run <任务名>`（当前会话）。

<a id="douban-movie-demo"></a>

### 2、豆瓣电影（《霸王别姬》）— 浏览器录屏

**豆瓣电影**（[movie.douban.com](https://movie.douban.com)）：**进入电影首页 → 搜索目标影片 → 打开第一条搜索结果详情页 → 抽取片名、豆瓣评分与剧情简介，并写入桌面文本文件**。本案例演示如何用 RPA 把「检索 + 打开详情 + 抽取影评页关键字段」录成可重复执行的 Playwright 脚本（与顶部 Sauce 流程同为「触发 → 录制 → 合成脚本」）。

https://github.com/user-attachments/assets/594c8970-2f11-4e2b-ae57-e563cafe6bbd

**录屏中的对话步骤**

1. 发送 **`#rpa`** / **`#RPA`** / **`#自动化机器人`**（规则见 [**SKILL.md**](SKILL.md)、[**SKILL.zh-CN.md**](SKILL.zh-CN.md)「触发检测」）。
2. 任务名示例：与 **`registry.json`** 中已有脚本对齐，如 **`豆瓣电影V6`**（`豆瓣电影v6.py`）、**`获取豆瓣电影数据`**（`获取豆瓣电影数据.py`）等。

**任务提示词（豆瓣电影片段）**

1. 访问 `https://movie.douban.com`。
2. 搜索电影 **「霸王别姬」** → 点击**搜索结果的第一条**，进入详情页 → 抽取 **片名**、**评分**、**剧情简介**。
3. 将抽取内容保存到桌面的 **`movie.txt`**。

### 3、OpenClaw + 飞书/Lark：`#rpa-list`、`#rpa-run` 定时执行 RPA 自动化程序

录屏演示在飞书/Lark 与 **OpenClaw-bot** 对话中的典型用法：

- **`#rpa-list`**：查看当前已注册、可执行的 RPA 任务；
- **`#rpa-run:电商网站购物V10`**：在新对话中执行已录制的脚本；
- **「一分钟后运行 #rpa-run:电商网站购物V10」** 等自然语言：在 OpenClaw + IM 侧预约或提醒稍后执行（具体以你的 OpenClaw 与机器人配置为准；脚本本身仍由 `rpa_manager.py run` 执行）。

https://github.com/user-attachments/assets/514e2d74-f42a-4243-8d49-52931fe6c22e


---

> 借助 **AI**，把**常见网页**与**本机文件**相关操作录成 **可重复运行的 Playwright Python 脚本**。日常**直接跑脚本**，少调大模型——**省算力**，步骤**更稳**、少受幻觉影响。


|         |                             |
| ------- | --------------------------- |
| **环境**  | Python **3.8+**，需网络安装依赖与浏览器 |
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

**SSH 克隆：** `git@github.com:laziobird/openclaw-rpa.git`

装好后请**新开 OpenClaw 会话**（或重载技能），以便加载 `**SKILL.md`**。触发词见 `**SKILL.md**`（如 `#RPA`、`#自动化机器人`）。

---

## 高级配置

**手动安装 · 网关 Python · 路径 · 发布**

### 手动安装（不用 `install.sh`）

```bash
cd /path/to/openclaw-rpa
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
python -m playwright install chromium
```

### 网关实际调用的 Python

`rpa_manager.py` 使用 `**sys.executable**`，该解释器必须已装 **Playwright**。若网关用系统 `**python3`**，请在同一环境装依赖，或把工具指向：

`~/.openclaw/workspace/skills/openclaw-rpa/.venv/bin/python`

### 语言与 `config.json`

- `**SKILL.md**` 中 `**localeConfig**` 指向 `**config.json**`
- 若无 `**config.json**`，可按 `**SKILL.md**` 用 `**config.example.json**` 读 `locale`
- 详见 `**LOCALE.md**`

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


| 脚本                         | 说明                                    |
| -------------------------- | ------------------------------------- |
| `wikipedia.py` / `wiki.py` | 维基百科（英文）                              |
| `获取豆瓣电影数据.py`、`获取豆瓣电影数据.py` 等 | 中文界面示例（遵守站点规则）；浏览器录屏案例见 [豆瓣电影（《霸王别姬》）](#douban-movie-demo) |
| `电商网站购物v10.py` 等           | Sauce Demo 电商流程（与顶部 [演示视频](#演示视频) 同类） |


更多说明见 `**examples/README.md**`。

---

Apache License 2.0 · 版权 © 2026 openclaw-rpa contributors
