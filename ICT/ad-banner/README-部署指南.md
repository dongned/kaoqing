# 部署指南

## 文件说明

| 文件 | 用途 |
|------|------|
| `index.html` | 网站主页，包含工具介绍、使用教程、FAQ 等实际内容，用于 AdSense 审核 |
| `ad.html` | App 专用的广告横幅页面，QWebEngineView 加载此页面 |

## 第一步：替换 AdSense 占位符

注册 Google AdSense 后，在两个 HTML 文件中替换以下占位符：

1. `ca-pub-XXXXXXXXXXXXXXXX` → 你的 AdSense 发布商 ID（共出现 5 处）
2. `data-ad-slot="XXXXXXXXXX"` → 你的广告单元 ID（共出现 4 处）

> 建议在 AdSense 后台创建 2 个广告单元：
> - 一个"横幅"类型（728x90），用于 App 和网站顶部/底部 → 用在 `ad.html` 和顶部/底部广告位
> - 一个"自适应"类型，用于网站中间的大广告位

## 第二步：推送到 GitHub

```bash
# 把这两个文件复制到你的 dongned.github.io 仓库
cp index.html /path/to/dongned.github.io/index.html
cp ad.html /path/to/dongned.github.io/ad.html

cd /path/to/dongned.github.io
git add index.html ad.html
git commit -m "add content and adsense"
git push
```

## 第三步：更新 test.py 的 AD_URL

```python
AD_URL = "https://dongned.github.io/ad.html"
```

## 第四步：AdSense 审核

1. 访问 https://www.google.com/adsense 注册
2. 网站地址填 `https://dongned.github.io`
3. 等待审核（1-14 天，通常 3-7 天）
4. 审核通过后广告自动展示

### 审核注意事项
- 网站必须有**实质性内容**（已帮你填充了工具介绍、教程、FAQ）
- 不能只有广告没有内容
- 审核期间广告位置会显示空白，这是正常的
- 如果被拒，检查 AdSense 后台的拒绝原因，通常需要补充更多原创内容

## 收入预估

| 场景 | CPM（千次展示收入） |
|------|-------------------|
| 国内桌面流量 | 约 ¥2-10 |
| 50 人每天打开 1 次 | 约 ¥3-15 / 月 |
| 200 人每天打开 1 次 | 约 ¥12-60 / 月 |

> AdSense 最低提现门槛：$100（约 ¥700），达到后自动汇款
