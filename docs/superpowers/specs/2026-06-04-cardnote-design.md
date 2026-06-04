# CardNote — 桌面悬浮卡片记事本

> 日期: 2026-06-04
> 技术栈: PySide6 + SQLite
> 状态: 设计定稿

## 1. 概述

CardNote 是一款桌面端悬浮卡片记事应用。每张卡片是一个独立的 frameless 窗口，可以自由散落在桌面上，像真实的便利贴一样随手记录、随时查看。精致圆角 + 柔和渐变色 + 阴影，强调快速记录和视觉美感。

### 核心理念

- **极速记录** — 打开即写，写完即走
- **悬浮自由** — 每张卡片独立悬浮，随意摆放
- **精美视觉** — 每张卡片都是精心设计的视觉元素

## 2. 技术栈

| 技术 | 用途 |
|---|---|
| Python 3.10+ | 开发语言 |
| PySide6 >= 6.6 | 桌面 GUI 框架 |
| SQLite (python `sqlite3`) | 本地数据存储 |
| QSS | 主题样式 |
| QPropertyAnimation | 卡片动画 |
| PyInstaller | 打包为单 exe |

## 3. 系统架构

三层次架构：

```
系统托盘 (Tray)          ← 全局控制中心
      │
卡片管理器 (CardManager)  ← 核心调度层，维护所有卡片引用
      │
悬浮卡片 (FloatingCard)   ← 每张卡片 = 独立 QWidget × N
      │
数据层 (Data Layer)       ← SQLite 持久化
```

### 3.1 启动流程

1. `main.py` → 创建 `QApplication`
2. 初始化 `Database`（创建/连接 SQLite）
3. 初始化 `CardManager`（从数据库加载所有活跃卡片）
4. 为每张卡片创建 `FloatingCard` 窗口，恢复到上次位置
5. 创建 `TrayIcon`（系统托盘），应用常驻
6. 进入事件循环

## 4. 悬浮卡片 (FloatingCard)

### 4.1 窗口实现

- 继承 `QWidget` + `Qt.FramelessWindowHint` + `Qt.WindowStaysOnTopHint`
- 默认尺寸 260×260，最小 180×180
- 圆角 16px，使用 `setMask()` 遮罩 + `paintEvent` 自绘背景和阴影
- `QGraphicsDropShadowEffect` 实现外发光阴影

### 4.2 卡片布局

```
┌──────────────────────┐
│  📌            ⋮     │  ← 顶栏: 拖拽把手 + 右键菜单
│                      │
│  在这里写下你的想法...  │  ← QTextEdit 编辑区
│                      │
│                      │
│                  ─ ┤ │  ← 右下角缩放把手 (QSplitter)
└──────────────────────┘
```

### 4.3 配色方案

预设 10 套柔和渐变色，每张卡片随机分配：

| ID | 配色名称 | 渐变 (hex→hex) |
|---|---|---|
| 0 | 暖阳 | #FFF5E1 → #FFE4B5 |
| 1 | 樱花 | #FFE4E1 → #FFB6C1 |
| 2 | 薄荷 | #E0FFF0 → #B2F2D8 |
| 3 | 天空 | #E0F4FF → #B8DFFF |
| 4 | 薰衣草 | #F0E6FF → #D4B8FF |
| 5 | 蜜桃 | #FFE8D0 → #FFD4A0 |
| 6 | 抹茶 | #E8F5E0 → #C8E6B0 |
| 7 | 雾蓝 | #E8EEFF → #C8D8FF |
| 8 | 玫瑰 | #FFE8EC → #FFC8D0 |
| 9 | 月光 | #F5F0E8 → #E8E0D0 |

深色模式下自动切换为对应的暗色版本。

### 4.4 交互操作

| 操作 | 行为 |
|---|---|
| 拖拽顶栏 | 移动窗口 |
| 双击编辑区 | 进入编辑模式 |
| 点击空白区域 | 退出编辑模式，自动保存 |
| 拖拽右下角缩放把手 | 调整大小（防抖动，停止后保存） |
| 鼠标悬停 | 上浮 2px + 阴影加深 |
| 右键菜单 | 删除/换色/置顶 |
| `Esc` | 退出编辑模式 |

### 4.5 删除动画

右键 → 删除 → `QPropertyAnimation` 缩放至 0 → `opacity` 淡出 → 从数据库删除 → 窗口销毁，总时长 300ms。

## 5. 系统托盘 (TrayIcon)

### 5.1 交互

| 操作 | 行为 |
|---|---|
| 左键单击 | 切换全部卡片显示/隐藏 |
| 右键单击 | 弹出菜单 |

### 5.2 菜单项

```
📝 新建卡片              Ctrl+N
──────────────────────
👁 全部显示
🙈 全部隐藏              Ctrl+Shift+H
──────────────────────
☀️ 日间模式 / 🌙 夜间模式
──────────────────────
⚙️ 设置...
❌ 退出
```

## 6. 数据层

### 6.1 数据库: `cardnote.db`

位置: `QStandardPaths.writableLocation(AppDataLocation)`

### 6.2 表结构

```sql
CREATE TABLE cards (
    id          TEXT PRIMARY KEY,        -- UUID4
    content     TEXT NOT NULL DEFAULT '',
    color_scheme INTEGER DEFAULT 0,
    pos_x       REAL,
    pos_y       REAL,
    width       REAL DEFAULT 260,
    height      REAL DEFAULT 260,
    z_index     INTEGER DEFAULT 0,
    is_visible  INTEGER DEFAULT 1,
    is_deleted  INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### 6.3 自动保存策略

- 失去焦点 → 保存
- 内容变化后 3s 防抖 → 保存
- 窗口移动/缩放停止 500ms → 保存
- 应用退出 → 保存全部

## 7. 全局设置

| Key | 默认值 | 说明 |
|---|---|---|
| `theme` | `light` | `light` / `dark` |
| `auto_theme` | `false` | 跟随系统主题 |
| `launch_at_startup` | `false` | 开机自启 |
| `default_card_width` | `260` | 新建卡片默认宽度 |
| `default_card_height` | `260` | 新建卡片默认高度 |

## 8. 项目结构

```
cardnote/
├── main.py                       # 应用入口
├── app/
│   ├── __init__.py
│   ├── app.py                    # QApp 初始化 + 全局快捷键
│   ├── tray.py                   # 系统托盘
│   ├── card_manager.py           # 卡片管理器
│   └── settings.py               # 设置管理
├── ui/
│   ├── __init__.py
│   ├── floating_card.py          # 悬浮卡片窗口
│   ├── card_widget.py            # 卡片内容组件
│   ├── color_schemes.py          # 配色方案
│   └── resources/
│       ├── icons/                # 托盘图标等
│       └── styles/
│           ├── light.qss
│           └── dark.qss
├── db/
│   ├── __init__.py
│   ├── database.py               # 连接与建表
│   └── repository.py             # CRUD 操作
├── utils/
│   ├── __init__.py
│   └── helpers.py                # 工具函数
└── requirements.txt              # PySide6>=6.6
```

## 9. 依赖与打包

### 依赖

```
PySide6 >= 6.6
```

唯一的外部依赖。

### 打包

```bash
pyinstaller --onefile --windowed --icon=app/resources/icons/card.ico main.py -n CardNote
```

预期产物: `dist/CardNote.exe`，约 60-80MB。

## 10. 不做 (YAGNI)

- ❌ 不登录/不注册/无账号系统
- ❌ 无云同步
- ❌ 不涉及网络请求
- ❌ 无富文本格式工具栏（纯文本，保留换行）
- ❌ 无图片/附件嵌入
- ❌ 无标签/分类/搜索
- ❌ 无桌面 Widget
