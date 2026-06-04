# CardNote 🃏

**桌面悬浮卡片记事本** — 像便利贴一样随手记录，浮在桌面上，随时可见。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## ✨ 特性

| 功能 | 说明 |
|---|---|
| 🃏 **悬浮卡片** | 每张卡片是独立 frameless 窗口，随意摆放在桌面任意位置 |
| ☑️ **待办清单** | 每张卡片可添加多条待办项，勾选标记完成 |
| 🎨 **精美渐变** | 10 套柔和渐变色，右键一键切换 |
| ✏️ **快速记录** | 双击编辑，自动保存（3 秒防抖） |
| 🖱️ **拖拽缩放** | 拖拽标题栏移动，右下角调整大小 |
| 🗑️ **删除动画** | 300ms 缩小淡出动画 |
| 🌙 **主题切换** | 日间/夜间模式一键切换 |
| ⌨️ **快捷键** | `Ctrl+N` 新建卡片 · `Ctrl+Shift+H` 全部隐藏 |
| 🖥️ **系统托盘** | 常驻系统托盘，不占任务栏 |
| 💾 **本地存储** | SQLite 本地存储，无需登录，无需联网 |

## 📸 截图

```
┌──────────────────┐  ┌──────────────────┐
│ ☑ 📌 购物清单  ⋮  │  │ ☐ 📌 灵感      ⋮  │
│                    │  │                    │
│ 今天要去超市买：     │  │ 做一个卡片记事应用   │
│                    │  │                    │
│ ─── 待办清单 ───   │  │ ─── 待办清单 ───   │
│ ☑ 买牛奶          │  │ ☐ 画UI设计草图    │
│ ☐ 买鸡蛋          │  │ ☐ 写后端API       │
│ ☑ 买面包          │  │                    │
│ ☐ 买水果          │  │                    │
└──────────────────┘  └──────────────────┘
```

## 🚀 快速开始

### 源码运行

```bash
# 安装依赖
pip install PySide6>=6.6

# 启动
python main.py
```

### 打包版（无需 Python）

从 [Releases](../../releases) 下载 `CardNote.exe`，双击运行即可。

## ⌨️ 快捷键

| 快捷键 | 功能 |
|---|---|
| `Ctrl+N` | 新建卡片 |
| `Ctrl+Shift+H` | 全部隐藏/显示 |
| `Esc` | 退出编辑模式 |

## 🗂️ 项目结构

```
cardnote/
├── main.py              # 入口点
├── app/
│   ├── app.py           # 主应用组装
│   ├── card_manager.py  # 卡片生命周期管理
│   ├── settings.py      # 全局设置
│   └── tray.py          # 系统托盘
├── ui/
│   ├── floating_card.py # 悬浮卡片窗口
│   ├── card_widget.py   # 卡片编辑组件 + 待办清单
│   ├── todo_list_widget.py # 待办清单组件
│   ├── color_schemes.py # 10套配色方案
│   └── resources/       # 图标、主题样式
├── db/
│   ├── database.py      # SQLite 连接
│   └── repository.py    # CRUD 操作
├── utils/helpers.py     # 工具函数
└── tests/               # 33个测试
```

## 🛠️ 自行打包

```bash
pip install pyinstaller
pyinstaller --clean --onefile --windowed --name CardNote \
  --add-data "cardnote/ui/resources;ui/resources" main.py
```

输出: `dist/CardNote.exe`

## 📄 License

MIT
