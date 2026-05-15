# Google AdSense 注册教程（完整步骤）

## 前提条件

- 一个 Google 账号（Gmail）
- 一个有实质内容的网站（你的 https://dongned.github.io/ ）
- 网站已上线且可公开访问
- 你需要年满 18 岁
- 需要有收款信息（后续再填也行）

---

## 第一步：先部署网站内容

在注册之前，确保你的网站已经推上了新内容（index.html），否则审核会被拒。

```bash
# 1. 把新内容复制到你的网站仓库
cp ad-banner/index.html /path/to/dongned.github.io/index.html
cp ad-banner/ad.html /path/to/dongned.github.io/ad.html

# 2. 推送
cd /path/to/dongned.github.io
git add .
git commit -m "update site content"
git push
```

推送后等 1-2 分钟，访问 https://dongned.github.io/ 确认新内容已生效。

> ⚠️ 此阶段 index.html 里的 AdSense 占位符先不要改，审核通过后再替换。

---

## 第二步：注册 AdSense

1. 用浏览器访问 https://www.google.com/adsense/
2. 点击 **"开始使用"** 按钮
3. 登录你的 Google 账号
4. 填写网站地址：`dongned.github.io`
5. 选择是否接收 AdSense 优化建议 → 选"是"或"否"都行
6. 点击 **"保存并继续"**

---

## 第三步：连接网站

AdSense 会给你一段代码，类似：

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>
```

1. **把这段代码复制下来**，这就是你的 `ca-pub-XXXX` 编号
2. 把代码粘贴到 index.html 的 `</body>` 标签前面（替换掉占位符那行）
3. 把代码也粘贴到 ad.html 里
4. 推送到 GitHub，等页面更新

```bash
git add .
git commit -m "add adsense code"
git push
```

5. 回到 AdSense 页面，点击 **"我已在网站中粘贴了代码"**
6. 点击 **"验证"**

> Google 会自动访问你的网站检测代码是否存在，检测到就进入审核。

---

## 第四步：填写个人信息

验证通过后，AdSense 会要求填写：

1. **收款人姓名** — 必须和银行账户一致，中文填写
2. **地址** — 详细的通讯地址，Google 会寄验证信（PIN 码）到这个地址
3. **电话号码** — 用于验证
4. **收款方式** — 审核通过后再设置也行，支持电汇到中国银行账户

---

## 第五步：等待审核

- 审核时间：通常 **3-7 天**，最长可能 14 天
- 审核期间网站上的广告位是空白的，这是正常的
- AdSense 团队会人工审查你的网站内容

### 审核标准

| 要求 | 说明 |
|------|------|
| 有实质内容 | 不能只有广告，必须有真实有用的内容 ✅ 已满足 |
| 原创内容 | 不能抄袭 ✅ 已满足 |
| 导航清晰 | 有明确的页面结构 ✅ 已满足 |
| 隐私政策 | **需要补充** ⚠️ 见下方 |
| 可公开访问 | ✅ 已满足 |
| 无违规内容 | 无成人、暴力、违法内容 ✅ 已满足 |

### ⚠️ 补充隐私政策页面（重要！）

AdSense 要求网站必须有隐私政策，说明你使用了广告和 Cookie。创建 `privacy.html`：

```bash
cp ad-banner/privacy.html /path/to/dongned.github.io/privacy.html
```

并在 index.html 的 footer 里加上隐私政策链接。

---

## 第六步：创建广告单元

审核通过后，在 AdSense 后台创建广告单元：

1. 进入 AdSense 后台 → **广告** → **按广告单元**
2. 点击 **"+ 新广告单元"**
3. 创建两个广告单元：

   **广告单元 1：横幅广告**
   - 名称：`App横幅`
   - 尺寸：选"横向"→ 728x90
   - 创建后拿到 `data-ad-slot` 编号

   **广告单元 2：自适应广告**
   - 名称：`网站自适应`
   - 尺寸：选"自适应"
   - 创建后拿到 `data-ad-slot` 编号

4. 把 ad-slot 编号替换到 HTML 里：
   - `ad.html` → 用横幅广告的 ad-slot
   - `index.html` 顶部/底部 → 用横幅广告的 ad-slot
   - `index.html` 中间 → 用自适应广告的 ad-slot

5. 推送到 GitHub

---

## 第七步：验证 PIN 码（收款必须）

当收入累计达到 $10 时，Google 会往你填的地址寄一封信（约 2-6 周到达），里面有 PIN 码：

1. 收到信后，进入 AdSense 后台 → **设置** → **账户信息** → **验证地址**
2. 输入 PIN 码
3. 验证成功后才能收款

---

## 常见被拒原因

| 原因 | 解决方法 |
|------|---------|
| 内容不足 | 多写几篇文章/工具说明 |
| 无隐私政策 | 添加 privacy.html 页面 |
| 抄袭内容 | 确保原创 |
| 网站无法访问 | 检查 GitHub Pages 是否正常 |
| 导航不清晰 | 确保有清晰的菜单和链接 |
| 内容不符合政策 | 不放成人/暴力/违法内容 |

被拒后可以修改网站重新申请，没有次数限制。

---

## 收款门槛

- 最低提现：**$100**（约 ¥700）
- 达到 $10 需要验证 PIN
- 达到 $100 当月月底自动汇款到你的银行账户
- 电汇手续费约 ¥15-30
