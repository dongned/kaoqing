# 考勤加班计算器

一个面向内部考勤场景的桌面工具。应用会登录考勤系统、拉取当月考勤记录，并按预设规则自动计算每日与月度加班时长，适合直接打包为 macOS APP 分发使用。

## 功能概览

- 输入员工账号和密码后，一键拉取当月考勤数据
- 自动识别工作日、休息日和跨天场景
- 按半小时向下取整汇总加班时长
- 支持可选的本地记住密码
- 内置桌面界面，适合直接打包为 `.app`

## 关键文件

```text
.
├── ICT/
│   ├── 1.txt                 # 历史打包命令示例
│   ├── azwm0-ubi0j.icns      # macOS 应用图标
│   └── test.py               # 主程序
├── docs/
│   ├── index.html            # APP 发布页
│   └── styles.css            # 发布页样式
├── scripts/
│   └── build_macos.sh        # macOS 打包脚本
├── requirements.txt
└── README.md
```

## 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ICT/test.py
```

## 打包为 macOS APP

项目已经补了一份可直接执行的 PyInstaller 脚本：

```bash
bash scripts/build_macos.sh
```

默认输出：

```text
dist/加班计算器.app
```

如果你准备对外分发，建议再补一层 `.dmg` 或 `.zip` 包装后上传到 GitHub Releases。

## 发布页

仓库内提供了一个静态 APP 发布页：

- 源文件：[docs/index.html](docs/index.html)
- 样式：[docs/styles.css](docs/styles.css)

启用方式：

1. 将 `dist/加班计算器.app` 或对应压缩包上传到 GitHub Releases
2. 在 GitHub Pages 中选择从 `docs/` 目录发布
3. 页面里的“下载最新版本”按钮会跳转到仓库的 Releases 页面

如果 Pages 已启用，默认访问地址通常是：

```text
https://dongned.github.io/kaoqing/
```

## 依赖

- `requests`
- `PyQt6`
- `PyQt6-WebEngine`
- `pyinstaller`

## 使用与发布注意事项

- 当前程序内置了使用期限，截止到 `2026-12-31`
- “记住密码”当前是写入本机文件并做 Base64 编码，不属于强加密，不建议在共享电脑上启用
- 广告位地址仍是占位 URL，正式发布前需要替换 `ICT/test.py` 里的 `AD_URL`
- 目前打包脚本按 macOS 桌面应用准备，Windows 发布还需要补独立的构建流程
