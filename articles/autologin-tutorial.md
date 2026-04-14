# OpenClaw RPA 自动登录使用教程

> **功能背景：** 电商下单、酒店查询、企业内网等场景，登录环节往往带有短信验证码、滑块、扫码等强认证，自动化脚本无法直接绕过。OpenClaw RPA 的「自动登录」方案是：**用户手动完成一次真实登录 → 框架自动保存 Cookie → 后续录制与回放自动注入**，彻底绕开验证码难题，同时把录制内容聚焦在业务操作而非登录流程上。

---

## 核心指令速查

| 指令 | 说明 |
|------|------|
| `#rpa-login <登录页URL>` | 打开 headed 浏览器到指定登录页，等待你手动完成登录 |
| `#rpa-login-done` | 登录完毕后发送此指令，自动导出 Cookie 并关闭浏览器 |
| `#rpa-autologin <域名或URL>` | 在任务描述里加此指令，录制或回放前自动注入已保存的 Cookie |
| `#rpa-autologin-list` | 查看所有已保存的登录会话及参考过期时间 |
| `#rpa-help` | 显示完整指令参考（中英双语） |

Cookie 默认保存路径：`~/.openclaw/rpa/sessions/<域名>/cookies.json`（**请勿提交到 git**）

---

## 工作流程

```
① #rpa-login <url>          打开浏览器 → 你手动登录（账号/密码/短信/滑块随便来）
         ↓
② #rpa-login-done           框架导出 Cookie → 保存到本地会话文件
         ↓
③ 开始录制任务               在任务描述里加 #rpa-autologin <域名>
         ↓
④ 浏览器自动注入 Cookie      直接打开登录后页面，无需再走登录流程
         ↓
⑤ 只录业务操作               搜索、排序、提交、截图……
         ↓
⑥ 生成脚本                   CONFIG 里自动带上 cookies_path，回放同样注入
```

---

## 案例一：Sauce Demo 电商 — 价格从高到低排序

> **网站：** [saucedemo.com](https://www.saucedemo.com)  
> **场景：** 保存登录态 → 直接打开商品列表页 → 按价格从高到低排序  
> **资料：** 完整指令与截图如下

### 第一步：保存登录会话

在 OpenClaw 对话框发送：

```
#rpa-login https://www.saucedemo.com/
```

![Sauce Demo 登录页](../images/autoLogin_1.png)

浏览器弹出并跳转到登录页：

在浏览器中填入账号密码（Sauce Demo 固定账号）：

- 用户名：`standard_user`  
- 密码：`secret_sauce`

点击 **LOGIN** 按钮，进入商品列表页后，回到对话框发送：

```
#rpa-login-done
```

框架输出确认信息：

```
✅ Cookie 已保存 → ~/.openclaw/rpa/sessions/saucedemo.com/cookies.json
   域名：saucedemo.com，共 1 条（其中 1 条为会话型）
   ⚠️  所有 Cookie 均为会话类型，无固定过期时间，以页面是否仍登录为准

   下次录制或回放自动注入：在任务描述中加入 #rpa-autologin saucedemo.com
```

![login-done 输出](../images/autoLogin_2.png)

### 第二步：录制排序业务操作

发送以下任务提示词（**一次性粘贴**）：

```
#rpa-autologin saucedemo.com

1. 访问 https://www.saucedemo.com/inventory.html
2. 价格从高到低进行排序
```

系统检测到 `#rpa-autologin saucedemo.com`，确认 Cookie 存在后提示：

```
✅ 已找到 saucedemo.com 的登录 Cookie，下次录制时将自动注入。
   现在可以开始任务，请告诉我任务名称。
```

回复任务名（如 `自动登录V3`），进入正常录制流程：

```
python3 rpa_manager.py record-start "Sauce排序" --autologin saucedemo.com
```

浏览器直接打开 `inventory.html`，**无需重新登录**：

![注入 Cookie 后直接进入商品页](../images/autoLogin_3.png)

AI 接着执行排序操作：

排序后截图确认：

![价格从高到低排序结果](../images/autoLogin_5.png)

发送 `#end`，生成 `rpa/自动登录V3.py`，生成脚本 `CONFIG` 中自动包含：

```python
CONFIG = {
    ...
    # 已保存的登录 Cookie 路径（由 #rpa-login 生成；留空则不注入）
    "cookies_path": "/Users/<你的用户名>/.openclaw/rpa/sessions/saucedemo.com/cookies.json",
}
```

### 第三步：回放验证

```bash
# 或在新对话发送：#rpa-run:自动登录V3
或者
# python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa/自动登录v3.py
```

脚本启动，自动注入 Cookie，直接到达商品列表页并完成排序。


https://github.com/user-attachments/assets/233659db-f5c4-44c1-9245-0bcf53b9dfa1




---

## 案例二：携程酒店 — 查询指定酒店信息并保存为 Word

> **网站：** [携程旅行 passport.ctrip.com](https://passport.ctrip.com/user/login)  
> **场景：** 保存携程登录态 → 打开指定酒店详情页 → 抓取酒店名称、评分、房型与价格 → 保存为 `hotel.docx`  

### 案例完整视频

https://github.com/user-attachments/assets/696e7b4b-5000-469f-abb8-9b8c2f023aea



---

### 第一步：保存携程登录会话

在 OpenClaw 对话框发送：

```
#rpa-login https://passport.ctrip.com/user/login
```

浏览器跳转到携程登录页。由于携程登录可能涉及**短信验证码、滑块验证**等，请按页面提示正常操作，完成登录后跳转到携程首页。

回到对话框发送：

```
#rpa-login-done
```

框架输出示例：

```
✅ Cookie 已保存 → ~/.openclaw/rpa/sessions/passport.ctrip.com/cookies.json
   域名：passport.ctrip.com，共 42 条（其中 3 条为会话型）
   ⏰ 参考过期时间（最早一条）：2026-05-05（实际以服务端策略为准，可能更早）

   下次录制或回放自动注入：在任务描述中加入 #rpa-autologin passport.ctrip.com
```

### 第二步：录制酒店信息抓取任务

发送以下任务提示词（**一次性粘贴**）：

```
#rpa-autologin passport.ctrip.com

1. 访问 https://hotels.ctrip.com/hotels/detail/?hotelId=940417&checkIn=2026-04-07&checkOut=2026-04-08&fromType=ctrip
2. 获取网页中该酒店的名称、评分和各种房型介绍和价格
3. 保存为 Word 格式，放到桌面 hotel.docx 中
```

系统确认 Cookie 存在后提示：

```
✅ 已找到 passport.ctrip.com 的登录 Cookie，下次录制时将自动注入。
   现在可以开始任务，请告诉我任务名称。
```

回复任务名（如 `携程酒店v3`）和能力码（Word 输出选 **`G`**），进入录制：

```
python3 rpa_manager.py record-start "携程酒店查询" --profile G --autologin passport.ctrip.com
```

浏览器直接打开酒店详情页（已处于登录态，价格与房型信息完整展示）。

酒店抓取的信息

```bash
python3 ~/.openclaw/workspace/skills/openclaw-rpa/rpa/携程酒店v3.py
# 或：#rpa-run:携程酒店v3
```
最终本地桌面调用 Word 保存内容
![酒店](../images/autoLogin_hotel.png)
---

## Cookie 过期了怎么办？

| 现象 | 处理方式 |
|------|---------|
| 脚本或录制中被跳转回登录页 | 会话已失效，按下方步骤更新 |
| `login-list` 显示 🔴 已过参考期 | 参考期过，实际可能也失效了 |
| `login-list` 显示 🟡 即将到期（≤7天） | 建议提前刷新 |

**更新步骤（只需两条指令）：**

```
#rpa-login <原登录页URL>
→ 在浏览器中重新登录
#rpa-login-done
```

新 Cookie 自动覆盖旧文件，下次录制/回放自动使用新会话。

---

## 查看所有已保存的登录会话

```
#rpa-autologin-list
```

或直接在终端运行：

```bash
python3 rpa_manager.py login-list
```

输出示例：

```
域名                             条数  会话型  保存时间               状态
────────────────────────────────────────────────────────────────────────────────────────────
passport.ctrip.com                 42      3  2026-04-07T10:23:15    🟢 28天后参考过期（2026-05-05）
saucedemo.com                       1      1  2026-04-07T11:01:00    ⚠️  无固定过期时间（会话型）
```

---

## 常见问题

**Q：`#rpa-autologin` 发送后提示「未找到登录会话」？**  
A：你还没有保存该域名的 Cookie，请先发送 `#rpa-login <登录页URL>` 完成一次真实登录。

**Q：Cookie 文件在哪里，能手动提供吗？**  
A：默认路径 `~/.openclaw/rpa/sessions/<域名>/cookies.json`。如果你已有从 Chrome DevTools 或其他工具导出的 Playwright 兼容格式 Cookie JSON，可以直接放到对应路径，无需执行 `#rpa-login`。

**Q：多个域名都需要登录怎么办？**  
A：对每个域名分别执行一次 `#rpa-login` + `#rpa-login-done`，保存的会话按域名隔离，互不干扰。

**Q：生成的脚本在其他机器上还能用 Cookie 吗？**  
A：可以。把 `~/.openclaw/rpa/sessions/<域名>/cookies.json` 复制到目标机器对应路径，脚本里 `CONFIG["cookies_path"]` 指向该文件即可。

**Q：携程登录后 Cookie 里的 `httpOnly` 字段 Playwright 能注入吗？**  
A：可以。`context.add_cookies()` 支持 `httpOnly`、`secure`、`sameSite` 全部字段，与浏览器原生行为一致。

---

## 相关文档

- [SKILL.zh-CN.md](../SKILL.zh-CN.md) — 完整状态机与录制协议
- [scenario-ap-reconciliation.md](scenario-ap-reconciliation.md) — 应付对账案例（API + Excel + Word）
- [python-snippet-design.md](python-snippet-design.md) — python_snippet 设计原理
