# Changelog

## v1.1.0 — 待办清单功能

> 基于 v1.0.0 的增量更新

### ✨ 新功能

- **待办清单**：每张卡片底部新增待办清单区，支持添加、勾选完成、编辑、删除待办项
- **自适应高度**：新增或删除待办项时，卡片高度自动伸缩适配内容
- **数据持久化**：新增 `todos` 数据表，清单项即时写入 SQLite

### 🐛 修复

- 修复编辑区白色背景问题（QTextEdit viewport 透明化）
- 修复待办项白色背景问题（QLineEdit 背景透明）
- 修复右下角缩放把手阴影不美观（改为完全透明）
- 修复删除按钮始终显示（改为鼠标悬浮时显示）
- 修复打包后托盘图标不显示（改用程序化绘制图标）
- 修复 QSS 文件在 Windows 下 GBK 编码报错
- 修复全局快捷键无效（`Qt.ApplicationShortcut` 上下文）

### 🔧 优化

- 右下角缩放把手改为透明不可见，保留功能区域
- 系统托盘图标改用 QPainter 程序化绘制，不依赖外部 SVG 文件
- 数据库自动迁移兼容旧版本数据（新增 `is_completed` 列）

### 📦 文件变更

| 新增 | 修改 |
|------|------|
| `ui/todo_list_widget.py` | `db/database.py`、`db/repository.py` |
| | `ui/card_widget.py`、`ui/floating_card.py` |
| | `app/card_manager.py`、`app/tray.py` |
| | `app/app.py`、`utils/helpers.py` |
| | `tests/`（33 个测试，↑7） |
