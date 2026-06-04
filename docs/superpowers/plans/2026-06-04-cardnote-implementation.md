# CardNote 桌面悬浮卡片记事本 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) for syntax tracking.

**Goal:** 实现一个 PySide6 桌面悬浮卡片记事应用，支持多张独立 frameless 卡片窗口自由悬浮、快速记录、精美视觉。

**Architecture:** 三层架构 — 系统托盘 (Tray) 作为全局控制中心，卡片管理器 (CardManager) 维护所有卡片引用，每张卡片 (FloatingCard) 是一个独立的 frameless QWidget。数据层用 SQLite 持久化卡片内容和位置。

**Tech Stack:** Python 3.10+, PySide6>=6.6, SQLite, pytest+pytest-qt

---

## 文件结构总览

```
cardnote/
├── main.py                       # 应用入口
├── app/
│   ├── __init__.py
│   ├── app.py                    # CardNoteApp: QApplication 初始化 + 全局快捷键
│   ├── tray.py                   # CardTray: 系统托盘 + 右键菜单
│   ├── card_manager.py           # CardManager: 卡片 CRUD + 生命周期管理
│   └── settings.py               # Settings: 全局设置读写
├── ui/
│   ├── __init__.py
│   ├── floating_card.py          # FloatingCard: 独立悬浮卡片窗口 (frameless)
│   ├── card_widget.py            # CardWidget: 卡片内部编辑组件
│   ├── color_schemes.py          # 配色方案数据定义
│   └── resources/
│       ├── icons/
│       │   └── card.svg          # 托盘图标源文件 (生成 .ico/.png)
│       └── styles/
│           ├── light.qss         # 日间主题
│           └── dark.qss          # 夜间主题
├── db/
│   ├── __init__.py
│   ├── database.py               # Database: SQLite 连接 + 建表
│   └── repository.py             # CardRepository: 卡片 CRUD 操作
├── utils/
│   ├── __init__.py
│   └── helpers.py                # 工具函数 (uuid, timestamp)
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures (qapp, db)
│   ├── test_database.py
│   ├── test_repository.py
│   ├── test_color_schemes.py
│   ├── test_settings.py
│   └── test_card_manager.py
└── requirements.txt
```

---

### Task 1: 项目脚手架和依赖

**Files:**
- Create: `requirements.txt`
- Create: `cardnote/__init__.py`
- Create: `cardnote/app/__init__.py`
- Create: `cardnote/ui/__init__.py`
- Create: `cardnote/db/__init__.py`
- Create: `cardnote/utils/__init__.py`
- Create: `cardnote/tests/__init__.py`
- Create: `cardnote/tests/conftest.py`

- [ ] **Step 1: 创建 requirements.txt**

```
PySide6 >= 6.6
pytest >= 8.0
pytest-qt >= 4.2
```

- [ ] **Step 2: 创建所有 `__init__.py`（空文件）**

- [ ] **Step 3: 创建 tests/conftest.py**

```python
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """提供 QApplication 实例给 pytest-qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def db_path(tmp_path):
    """返回临时数据库路径."""
    return str(tmp_path / "test_cardnote.db")
```

- [ ] **Step 4: 安装依赖并验证**

```bash
cd d:/Ai-tool/0604
pip install -r requirements.txt
pytest --collect-only cardnote/tests/
```

Expected: 空测试集通过收集。

- [ ] **Step 5: Commit**

```bash
git add cardnote/ requirements.txt
git commit -m "chore: scaffold project structure and dependencies"
```

---

### Task 2: 工具函数 helpers

**Files:**
- Create: `cardnote/utils/helpers.py`

- [ ] **Step 1: 实现 helpers.py**

```python
import uuid
from datetime import datetime, timezone


def new_uuid() -> str:
    """生成 UUID4 字符串."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串."""
    return datetime.now(timezone.utc).isoformat()
```

- [ ] **Step 2: 验证 import 可用**

```bash
python -c "from cardnote.utils.helpers import new_uuid, now_iso; print(new_uuid()); print(now_iso())"
```

Expected: 输出 uuid 和时间字符串。

- [ ] **Step 3: Commit**

```bash
git add cardnote/utils/helpers.py
git commit -m "chore: add uuid and timestamp helpers"
```

---

### Task 3: 配色方案 color_schemes

**Files:**
- Create: `cardnote/ui/color_schemes.py`

- [ ] **Step 1: 实现 color_schemes.py**

```python
from dataclasses import dataclass


@dataclass
class ColorScheme:
    name: str
    light_start: str
    light_end: str
    dark_start: str
    dark_end: str


SCHEMES: list[ColorScheme] = [
    ColorScheme("暖阳", "#FFF5E1", "#FFE4B5", "#4A3F30", "#3D3528"),
    ColorScheme("樱花", "#FFE4E1", "#FFB6C1", "#4A3035", "#3D282E"),
    ColorScheme("薄荷", "#E0FFF0", "#B2F2D8", "#2D4038", "#25352E"),
    ColorScheme("天空", "#E0F4FF", "#B8DFFF", "#2A3645", "#222E3D"),
    ColorScheme("薰衣草", "#F0E6FF", "#D4B8FF", "#352E45", "#2C263D"),
    ColorScheme("蜜桃", "#FFE8D0", "#FFD4A0", "#45382A", "#3D3025"),
    ColorScheme("抹茶", "#E8F5E0", "#C8E6B0", "#303A28", "#283522"),
    ColorScheme("雾蓝", "#E8EEFF", "#C8D8FF", "#2A2E3D", "#22283A"),
    ColorScheme("玫瑰", "#FFE8EC", "#FFC8D0", "#452E33", "#3D282E"),
    ColorScheme("月光", "#F5F0E8", "#E8E0D0", "#3D3830", "#353028"),
]


def get_scheme(index: int) -> ColorScheme:
    """按索引获取配色方案，越界则循环."""
    return SCHEMES[index % len(SCHEMES)]


def random_scheme_index() -> int:
    """生成随机配色索引."""
    import random
    return random.randint(0, len(SCHEMES) - 1)
```

- [ ] **Step 2: 验证**

```bash
python -c "from cardnote.ui.color_schemes import SCHEMES, get_scheme, random_scheme_index; print(len(SCHEMES)); print(get_scheme(3))"
```

Expected: 10 个配色方案，索引 3 返回天空色。

- [ ] **Step 3: Commit**

```bash
git add cardnote/ui/color_schemes.py
git commit -m "feat: add 10 color schemes for cards"
```

---

### Task 4: 数据库层 database

**Files:**
- Create: `cardnote/db/database.py`
- Create: `cardnote/tests/test_database.py`

- [ ] **Step 1: 实现 database.py**

```python
import sqlite3
import os


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cards (
    id          TEXT PRIMARY KEY,
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

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Database:
    """SQLite 数据库连接与初始化."""

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            from PySide6.QtCore import QStandardPaths
            data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "cardnote.db")
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """建立连接并初始化表结构."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        return self.conn

    def close(self):
        """关闭连接."""
        if self.conn:
            self.conn.close()
            self.conn = None
```

- [ ] **Step 2: 实现 test_database.py**

```python
import pytest
from cardnote.db.database import Database
from cardnote.db.database import SCHEMA_SQL


class TestDatabase:
    def test_connect_creates_tables(self, db_path):
        db = Database(db_path)
        conn = db.connect()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [r["name"] for r in tables]
        assert "cards" in table_names
        assert "settings" in table_names
        db.close()

    def test_connect_idempotent(self, db_path):
        """多次调用 connect 不会重复创建表."""
        db = Database(db_path)
        db.connect()
        db.conn.execute("INSERT INTO settings (key, value) VALUES ('k', 'v')")
        db.conn.commit()
        db.close()
        # 第二次打开
        db2 = Database(db_path)
        conn2 = db2.connect()
        row = conn2.execute("SELECT value FROM settings WHERE key='k'").fetchone()
        assert row["value"] == "v"
        db2.close()

    def test_custom_path(self, db_path):
        db = Database(db_path)
        assert db.db_path == db_path

    def test_schema_sql_contains_both_tables(self):
        assert "CREATE TABLE IF NOT EXISTS cards" in SCHEMA_SQL
        assert "CREATE TABLE IF NOT EXISTS settings" in SCHEMA_SQL
```

- [ ] **Step 3: 运行测试**

```bash
cd d:/Ai-tool/0604
pytest cardnote/tests/test_database.py -v
```

Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add cardnote/db/database.py cardnote/tests/test_database.py
git commit -m "feat: add database layer with SQLite initialization"
```

---

### Task 5: 数据仓库 repository

**Files:**
- Create: `cardnote/db/repository.py`
- Create: `cardnote/tests/test_repository.py`

- [ ] **Step 1: 实现 repository.py**

```python
from cardnote.utils.helpers import new_uuid, now_iso
from cardnote.ui.color_schemes import random_scheme_index


class CardRepository:
    """卡片数据的 CRUD 操作."""

    def __init__(self, conn):
        self.conn = conn

    def create(self, pos_x: float = 400, pos_y: float = 300,
               width: float = 260, height: float = 260) -> dict:
        now = now_iso()
        card = {
            "id": new_uuid(),
            "content": "",
            "color_scheme": random_scheme_index(),
            "pos_x": pos_x,
            "pos_y": pos_y,
            "width": width,
            "height": height,
            "z_index": 0,
            "is_visible": 1,
            "is_deleted": 0,
            "created_at": now,
            "updated_at": now,
        }
        self.conn.execute(
            """INSERT INTO cards (id, content, color_scheme, pos_x, pos_y,
             width, height, z_index, is_visible, is_deleted, created_at, updated_at)
             VALUES (:id, :content, :color_scheme, :pos_x, :pos_y,
             :width, :height, :z_index, :is_visible, :is_deleted, :created_at, :updated_at)""",
            card,
        )
        self.conn.commit()
        return card

    def get(self, card_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM cards WHERE id = ? AND is_deleted = 0", (card_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_active(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM cards WHERE is_deleted = 0 ORDER BY z_index DESC, updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def update_content(self, card_id: str, content: str):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, card_id),
        )
        self.conn.commit()

    def update_position(self, card_id: str, pos_x: float, pos_y: float):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET pos_x = ?, pos_y = ?, updated_at = ? WHERE id = ?",
            (pos_x, pos_y, now, card_id),
        )
        self.conn.commit()

    def update_size(self, card_id: str, width: float, height: float):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET width = ?, height = ?, updated_at = ? WHERE id = ?",
            (width, height, now, card_id),
        )
        self.conn.commit()

    def update_color_scheme(self, card_id: str, scheme_index: int):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET color_scheme = ?, updated_at = ? WHERE id = ?",
            (scheme_index, now, card_id),
        )
        self.conn.commit()

    def soft_delete(self, card_id: str):
        now = now_iso()
        self.conn.execute(
            "UPDATE cards SET is_deleted = 1, updated_at = ? WHERE id = ?",
            (now, card_id),
        )
        self.conn.commit()

    def count_active(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM cards WHERE is_deleted = 0"
        ).fetchone()
        return row["cnt"]
```

- [ ] **Step 2: 实现 test_repository.py**

```python
import pytest
from cardnote.db.database import Database
from cardnote.db.repository import CardRepository


@pytest.fixture
def repo(db_path):
    db = Database(db_path)
    conn = db.connect()
    return CardRepository(conn)


class TestCardRepository:
    def test_create_card(self, repo):
        card = repo.create(pos_x=100, pos_y=200)
        assert card["id"] is not None
        assert card["content"] == ""
        assert card["pos_x"] == 100
        assert card["pos_y"] == 200
        assert card["is_deleted"] == 0

    def test_get_card(self, repo):
        created = repo.create()
        fetched = repo.get(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]

    def test_get_nonexistent(self, repo):
        assert repo.get("nonexistent-id") is None

    def test_get_all_active(self, repo):
        repo.create()
        repo.create()
        all_cards = repo.get_all_active()
        assert len(all_cards) >= 2

    def test_soft_delete(self, repo):
        card = repo.create()
        repo.soft_delete(card["id"])
        assert repo.get(card["id"]) is None
        assert repo.count_active() == 0

    def test_update_content(self, repo):
        card = repo.create()
        repo.update_content(card["id"], "hello world")
        updated = repo.get(card["id"])
        assert updated["content"] == "hello world"

    def test_update_position(self, repo):
        card = repo.create()
        repo.update_position(card["id"], 500, 600)
        updated = repo.get(card["id"])
        assert updated["pos_x"] == 500
        assert updated["pos_y"] == 600

    def test_update_size(self, repo):
        card = repo.create()
        repo.update_size(card["id"], 300, 200)
        updated = repo.get(card["id"])
        assert updated["width"] == 300
        assert updated["height"] == 200

    def test_update_color_scheme(self, repo):
        card = repo.create()
        repo.update_color_scheme(card["id"], 5)
        updated = repo.get(card["id"])
        assert updated["color_scheme"] == 5

    def test_count_active(self, repo):
        assert repo.count_active() == 0
        repo.create()
        assert repo.count_active() == 1
```

- [ ] **Step 3: 运行测试**

```bash
cd d:/Ai-tool/0604
pytest cardnote/tests/test_repository.py -v
```

Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add cardnote/db/repository.py cardnote/tests/test_repository.py
git commit -m "feat: add card repository with full CRUD operations"
```

---

### Task 6: 设置管理 settings

**Files:**
- Create: `cardnote/app/settings.py`
- Create: `cardnote/tests/test_settings.py`

- [ ] **Step 1: 实现 settings.py**

```python
DEFAULTS = {
    "theme": "light",
    "auto_theme": "false",
    "launch_at_startup": "false",
    "default_card_width": "260",
    "default_card_height": "260",
}


class Settings:
    """全局设置管理，读写 settings 表."""

    def __init__(self, conn):
        self.conn = conn
        self._ensure_defaults()

    def _ensure_defaults(self):
        for key, value in DEFAULTS.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        self.conn.commit()

    def get(self, key: str, default: str | None = None) -> str:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return default if default is not None else DEFAULTS.get(key, "")
        return row["value"]

    def set(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    def get_bool(self, key: str) -> bool:
        return self.get(key).lower() in ("true", "1", "yes")

    def get_int(self, key: str, default: int = 260) -> int:
        try:
            return int(self.get(key))
        except (ValueError, TypeError):
            return default
```

- [ ] **Step 2: 实现 test_settings.py**

```python
import pytest
from cardnote.db.database import Database
from cardnote.app.settings import Settings, DEFAULTS


@pytest.fixture
def settings(db_path):
    db = Database(db_path)
    conn = db.connect()
    return Settings(conn)


class TestSettings:
    def test_defaults_exist(self, settings):
        for key, default_val in DEFAULTS.items():
            assert settings.get(key) == default_val

    def test_set_and_get(self, settings):
        settings.set("theme", "dark")
        assert settings.get("theme") == "dark"

    def test_get_bool_false(self, settings):
        assert settings.get_bool("auto_theme") is False

    def test_get_bool_true(self, settings):
        settings.set("auto_theme", "true")
        assert settings.get_bool("auto_theme") is True

    def test_get_int_default(self, settings):
        assert settings.get_int("default_card_width") == 260

    def test_get_int_custom(self, settings):
        settings.set("default_card_width", "300")
        assert settings.get_int("default_card_width") == 300

    def test_unknown_key_returns_default(self, settings):
        assert settings.get("nonexistent", "fallback") == "fallback"
```

- [ ] **Step 3: 运行测试**

```bash
cd d:/Ai-tool/0604
pytest cardnote/tests/test_settings.py -v
```

Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add cardnote/app/settings.py cardnote/tests/test_settings.py
git commit -m "feat: add settings manager with defaults"
```

---

### Task 7: 卡片内容组件 CardWidget

**Files:**
- Create: `cardnote/ui/card_widget.py`

- [ ] **Step 1: 实现 card_widget.py**

```python
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class CardWidget(QWidget):
    """卡片内部内容组件，包含编辑区和信号."""

    content_changed = Signal(str)
    editing_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 16)

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("在这里写下你的想法...")
        self.text_edit.setFrameShape(QTextEdit.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)

        self._debounce_timer = None

    def _on_text_changed(self):
        content = self.text_edit.toPlainText()
        self.content_changed.emit(content)

    def set_content(self, text: str):
        """设置文本内容（不触发 textChanged 信号循环）. """
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.text_edit.blockSignals(False)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def focus_edit(self):
        """聚焦到编辑区."""
        self.text_edit.setFocus()
        self.text_edit.selectAll()
```

- [ ] **Step 2: 验证导入**

```bash
python -c "from PySide6.QtWidgets import QApplication; app = QApplication.instance() or QApplication([]); from cardnote.ui.card_widget import CardWidget; print('CardWidget OK')"
```

Expected: CardWidget OK

- [ ] **Step 3: Commit**

```bash
git add cardnote/ui/card_widget.py
git commit -m "feat: add card widget with QTextEdit and signals"
```

---

### Task 8: 悬浮卡片窗口 FloatingCard

**Files:**
- Create: `cardnote/ui/floating_card.py`

- [ ] **Step 1: 实现 floating_card.py**

```python
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPen, QPainterPath, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QSizeGrip

from cardnote.ui.card_widget import CardWidget
from cardnote.ui.color_schemes import get_scheme, SCHEMES


class FloatingCard(QWidget):
    """独立悬浮卡片窗口 (FramelessWindowHint)."""

    CARD_RADIUS = 16
    SHADOW_MARGIN = 10
    TITLE_BAR_HEIGHT = 32

    delete_requested = Signal(str)  # card_id

    def __init__(self, card_id: str, card_data: dict, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self.card_data = card_data
        self._dragging = False
        self._drag_pos = QPoint()
        self._resizing = False
        self._edit_mode = False
        self._delete_animation = None

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)

        # 根据数据设置几何位置
        scheme = get_scheme(card_data.get("color_scheme", 0))
        self.color_start = QColor(scheme.light_start)
        self.color_end = QColor(scheme.light_end)
        w = int(card_data.get("width", 260))
        h = int(card_data.get("height", 260))
        self.setGeometry(
            int(card_data.get("pos_x", 400)),
            int(card_data.get("pos_y", 300)),
            w + self.SHADOW_MARGIN * 2,
            h + self.SHADOW_MARGIN * 2,
        )

        self._build_ui()
        self._setup_menu()

    def _build_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(self.SHADOW_MARGIN, self.SHADOW_MARGIN,
                                       self.SHADOW_MARGIN, self.SHADOW_MARGIN)
        main_layout.setSpacing(0)

        # 内容容器
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("cardContent")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(self.TITLE_BAR_HEIGHT)
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 0, 4, 0)

        self.pin_label = QLabel("📌")
        self.pin_label.setFixedWidth(24)

        title_layout.addWidget(self.pin_label)
        title_layout.addStretch()

        self.menu_btn = QLabel("⋯")
        self.menu_btn.setFixedWidth(24)
        self.menu_btn.mousePressEvent = self._show_context_menu
        title_layout.addWidget(self.menu_btn)

        content_layout.addWidget(title_bar)

        # 编辑区
        self.card_widget = CardWidget(self.content_widget)
        self.card_widget.set_content(self.card_data.get("content", ""))
        content_layout.addWidget(self.card_widget, 1)

        main_layout.addWidget(self.content_widget)

        # 大小缩放把手
        self.size_grip = QSizeGrip(self.content_widget)
        self.size_grip.setFixedSize(16, 16)
        self.size_grip.setObjectName("sizeGrip")

        # 样式
        self._apply_styles()

    def _apply_styles(self):
        self.content_widget.setStyleSheet(f"""
            #cardContent {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color_start.name()},
                    stop:1 {self.color_end.name()});
                border-radius: {self.CARD_RADIUS}px;
            }}
            #titleBar {{
                background: transparent;
                border-top-left-radius: {self.CARD_RADIUS}px;
                border-top-right-radius: {self.CARD_RADIUS}px;
            }}
            #sizeGrip {{
                background: transparent;
            }}
        """)

    def _setup_menu(self):
        self.context_menu = QMenu(self)
        act_change = self.context_menu.addAction("🎨 更换配色")
        act_change.triggered.connect(self._cycle_color)
        self.context_menu.addSeparator()
        act_delete = self.context_menu.addAction("🗑️ 删除卡片")
        act_delete.triggered.connect(lambda: self.delete_requested.emit(self.card_id))

    def _show_context_menu(self, event):
        self.context_menu.exec(self.mapToGlobal(self.menu_btn.pos()))

    def _cycle_color(self):
        current = self.card_data.get("color_scheme", 0)
        next_idx = (current + 1) % len(SCHEMES)
        self.card_data["color_scheme"] = next_idx
        scheme = get_scheme(next_idx)
        self.color_start = QColor(scheme.light_start)
        self.color_end = QColor(scheme.light_end)
        self._apply_styles()
        self.update()
        # 通知外部保存
        self._emit_save()

    def _emit_save(self):
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._do_save())
        self.card_data["content"] = self.card_widget.get_content()
        self.card_data["pos_x"] = self.x()
        self.card_data["pos_y"] = self.y()
        self.card_data["width"] = self.width() - self.SHADOW_MARGIN * 2
        self.card_data["height"] = self.height() - self.SHADOW_MARGIN * 2

    def _do_save(self):
        """由外部 CardManager 绑定."""
        pass  # 会被 CardManager 替换

    def set_save_callback(self, callback):
        self._do_save = callback

    def set_delete_callback(self, callback):
        self._delete_callback = callback

    # ---------- 鼠标事件 ----------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_on_title_bar(event.pos()):
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self.card_data["pos_x"] = self.x()
            self.card_data["pos_y"] = self.y()
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self._emit_save()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.card_widget.focus_edit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setFocus()
            self.card_widget.clearFocus()
        super().keyPressEvent(event)

    def _is_on_title_bar(self, pos: QPoint) -> bool:
        margin = self.SHADOW_MARGIN
        return margin <= pos.y() <= margin + self.TITLE_BAR_HEIGHT

    # ---------- 绘制 ----------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(
            self.SHADOW_MARGIN, self.SHADOW_MARGIN,
            -self.SHADOW_MARGIN, -self.SHADOW_MARGIN
        )

        # 圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRect(rect), self.CARD_RADIUS, self.CARD_RADIUS)

        # 渐变色背景
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, self.color_start)
        gradient.setColorAt(1, self.color_end)
        painter.fillPath(path, QBrush(gradient))

        # 阴影外发光
        painter.setPen(Qt.NoPen)
        for i in range(5):
            alpha = 15 - i * 3
            offset = i * 2
            shadow_rect = rect.adjusted(-offset, -offset, offset, offset)
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(QRect(shadow_rect), self.CARD_RADIUS + offset)
            painter.fillPath(shadow_path, QColor(0, 0, 0, alpha))

    def _animate_delete(self):
        """删除动画并关闭."""
        self._delete_animation = QPropertyAnimation(self, b"geometry")
        self._delete_animation.setDuration(300)
        self._delete_animation.setEasingCurve(QEasingCurve.InOutQuad)
        g = self.geometry()
        center = g.center()
        self._delete_animation.setStartValue(g)
        self._delete_animation.setEndValue(QRect(center.x(), center.y(), 0, 0))
        self._delete_animation.finished.connect(self._on_delete_finished)
        self._delete_animation.start()

    def _on_delete_finished(self):
        if hasattr(self, '_delete_callback'):
            self._delete_callback()
        else:
            self.close()
```

- [ ] **Step 2: 验证导入**

```bash
python -c "from PySide6.QtWidgets import QApplication; app = QApplication.instance() or QApplication([]); from cardnote.ui.floating_card import FloatingCard; print('FloatingCard OK')"
```

Expected: FloatingCard OK

- [ ] **Step 3: Commit**

```bash
git add cardnote/ui/floating_card.py
git commit -m "feat: add floating card window with frameless design and animations"
```

---

### Task 9: 卡片管理器 CardManager

**Files:**
- Create: `cardnote/app/card_manager.py`
- Create: `cardnote/tests/test_card_manager.py`

- [ ] **Step 1: 实现 card_manager.py**

```python
from PySide6.QtCore import QObject, Signal, QTimer

from cardnote.db.repository import CardRepository
from cardnote.ui.floating_card import FloatingCard


class CardManager(QObject):
    """卡片管理器: 维护卡片生命周期、与数据库同步."""

    card_created = Signal(str)   # card_id
    card_deleted = Signal(str)   # card_id
    card_count_changed = Signal(int)

    def __init__(self, repository: CardRepository, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.cards: dict[str, FloatingCard] = {}
        self._save_timers: dict[str, QTimer] = {}
        self._debounce_ms = 3000

    def load_all(self):
        """从数据库加载所有活跃卡片并创建窗口."""
        records = self.repository.get_all_active()
        for record in records:
            self._create_card_from_data(record)

    def create_card(self, pos_x: float = 400, pos_y: float = 300,
                    width: float = 260, height: float = 260) -> FloatingCard:
        """创建新卡片."""
        data = self.repository.create(pos_x, pos_y, width, height)
        card = self._create_card_from_data(data)
        self.card_created.emit(data["id"])
        self.card_count_changed.emit(len(self.cards))
        return card

    def _create_card_from_data(self, data: dict) -> FloatingCard:
        """根据数据库记录创建卡片窗口."""
        card = FloatingCard(data["id"], data)
        card.set_save_callback(lambda: self._save_card(card.card_id))
        card.set_delete_callback(lambda: self.delete_card(card.card_id))
        card.destroyed.connect(lambda: self._on_card_closed(card.card_id))
        card.delete_requested.connect(self._on_delete_requested)
        card.card_widget.content_changed.connect(
            lambda text: self._debounce_save(card.card_id, text)
        )
        card.show()
        self.cards[data["id"]] = card
        return card

    def _save_card(self, card_id: str):
        """保存卡片当前状态到数据库."""
        card = self.cards.get(card_id)
        if card is None:
            return
        data = card.card_data
        self.repository.update_content(card_id, data.get("content", ""))
        self.repository.update_position(card_id, data["pos_x"], data["pos_y"])
        self.repository.update_size(card_id, data["width"], data["height"])
        self.repository.update_color_scheme(card_id, data.get("color_scheme", 0))

    def _on_delete_requested(self, card_id: str):
        """处理卡片删除请求: 播放动画后自动触发 delete_card. """
        card = self.cards.get(card_id)
        if card:
            card._animate_delete()
        else:
            self.delete_card(card_id)

    def _debounce_save(self, card_id: str, text: str):
        """防抖保存: 内容变化后 3s 自动保存."""
        if card_id in self._save_timers:
            self._save_timers[card_id].stop()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._save_card(card_id))
        timer.start(self._debounce_ms)
        self._save_timers[card_id] = timer
        # 同步更新内存中的数据
        if card_id in self.cards:
            self.cards[card_id].card_data["content"] = text

    def delete_card(self, card_id: str):
        """删除卡片."""
        if card_id in self.cards:
            self.cards[card_id].close()
        self.repository.soft_delete(card_id)
        self.card_deleted.emit(card_id)
        self.card_count_changed.emit(len(self.cards))

    def _on_card_closed(self, card_id: str):
        """卡片窗口关闭后的清理."""
        self.cards.pop(card_id, None)
        if card_id in self._save_timers:
            self._save_timers[card_id].stop()
            del self._save_timers[card_id]

    def hide_all(self):
        """隐藏所有卡片窗口."""
        for card in self.cards.values():
            card.hide()

    def show_all(self):
        """显示所有卡片窗口."""
        for card in self.cards.values():
            card.show()

    def toggle_visible(self):
        """切换所有卡片的可见性."""
        if any(card.isVisible() for card in self.cards.values()):
            self.hide_all()
        else:
            self.show_all()

    def save_all(self):
        """立即保存所有卡片."""
        for card_id in list(self.cards.keys()):
            self._save_card(card_id)
```

- [ ] **Step 2: 实现 test_card_manager.py**

```python
import pytest
from PySide6.QtWidgets import QApplication
from cardnote.db.database import Database
from cardnote.db.repository import CardRepository
from cardnote.app.card_manager import CardManager


@pytest.fixture
def card_manager(db_path):
    app = QApplication.instance() or QApplication([])
    db = Database(db_path)
    conn = db.connect()
    repo = CardRepository(conn)
    mgr = CardManager(repo)
    yield mgr
    # 清理
    for card_id in list(mgr.cards.keys()):
        mgr.cards[card_id].close()


class TestCardManager:
    def test_create_card(self, card_manager):
        card = card_manager.create_card(100, 200, 260, 260)
        assert card.card_id in card_manager.cards
        assert card_manager.repository.count_active() == 1

    def test_load_all(self, card_manager):
        card_manager.create_card()
        card_manager.create_card()
        # 模拟重启: 新建一个 manager 并 load_all
        repo = card_manager.repository
        mgr2 = CardManager(repo)
        mgr2.load_all()
        assert len(mgr2.cards) == 2
        # 清理
        for cid in list(mgr2.cards.keys()):
            mgr2.cards[cid].close()

    def test_delete_card(self, card_manager):
        card = card_manager.create_card()
        card_id = card.card_id
        assert card_id in card_manager.cards
        card_manager.delete_card(card_id)
        assert card_id not in card_manager.cards
        assert card_manager.repository.count_active() == 0

    def test_toggle_visible(self, card_manager):
        card_manager.create_card()
        card_manager.hide_all()
        assert all(not c.isVisible() for c in card_manager.cards.values())
        card_manager.show_all()
        assert all(c.isVisible() for c in card_manager.cards.values())

    def test_save_all(self, card_manager):
        card = card_manager.create_card()
        card.card_widget.set_content("test content")
        card.card_data["content"] = "test content"
        card_manager.save_all()
        saved = card_manager.repository.get(card.card_id)
        assert saved["content"] == "test content"
```

- [ ] **Step 3: 运行测试**

```bash
cd d:/Ai-tool/0604
pytest cardnote/tests/test_card_manager.py -v
```

Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add cardnote/app/card_manager.py cardnote/tests/test_card_manager.py
git commit -m "feat: add card manager with lifecycle and debounce save"
```

---

### Task 10: 系统托盘 TrayIcon

**Files:**
- Create: `cardnote/app/tray.py`

- [ ] **Step 1: 实现 tray.py**

```python
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


class CardTray(QObject):
    """系统托盘图标与菜单."""

    new_card_requested = Signal()
    show_all_requested = Signal()
    hide_all_requested = Signal()
    toggle_theme_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        # 使用内置图标作为 fallback
        self.tray_icon.setIcon(QIcon.fromTheme(" accessory-text-editor",
                                                QIcon(":/icons/card.svg")))
        self.tray_icon.setToolTip("CardNote - 悬浮卡片记事本")

        self._build_menu()
        self.tray_icon.activated.connect(self._on_activated)
        self.tray_icon.show()

    def _build_menu(self):
        menu = QMenu()

        self.act_new = QAction("📝 新建卡片")
        self.act_new.setShortcut(QKeySequence("Ctrl+N"))
        self.act_new.triggered.connect(self.new_card_requested.emit)
        menu.addAction(self.act_new)

        menu.addSeparator()

        self.act_show = QAction("👁 全部显示")
        self.act_show.triggered.connect(self.show_all_requested.emit)
        menu.addAction(self.act_show)

        self.act_hide = QAction("🙈 全部隐藏")
        self.act_hide.setShortcut(QKeySequence("Ctrl+Shift+H"))
        self.act_hide.triggered.connect(self.hide_all_requested.emit)
        menu.addAction(self.act_hide)

        menu.addSeparator()

        self.act_theme = QAction("🌙 夜间模式")
        self.act_theme.triggered.connect(self.toggle_theme_requested.emit)
        menu.addAction(self.act_theme)

        menu.addSeparator()

        self.act_quit = QAction("❌ 退出")
        self.act_quit.triggered.connect(self.quit_requested.emit)
        menu.addAction(self.act_quit)

        self.tray_icon.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if hasattr(self, 'parent') and hasattr(self.parent(), 'card_manager'):
                self.parent().card_manager.toggle_visible()

    def set_theme_label(self, is_dark: bool):
        action = self.tray_icon.contextMenu().actions()[4]  # theme action
        action.setText("☀️ 日间模式" if is_dark else "🌙 夜间模式")

    def set_tooltip(self, count: int):
        self.tray_icon.setToolTip(f"CardNote - {count} 张卡片")
```

- [ ] **Step 2: 验证导入**

```bash
python -c "from PySide6.QtWidgets import QApplication; app = QApplication.instance() or QApplication([]); from cardnote.app.tray import CardTray; print('CardTray OK')"
```

Expected: CardTray OK

- [ ] **Step 3: Commit**

```bash
git add cardnote/app/tray.py
git commit -m "feat: add system tray icon with context menu"
```

---

### Task 11: App 主应用和 main 入口

**Files:**
- Create: `cardnote/app/app.py`
- Create: `cardnote/main.py`

- [ ] **Step 1: 实现 app.py**

```python
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from cardnote.db.database import Database
from cardnote.db.repository import CardRepository
from cardnote.app.settings import Settings
from cardnote.app.card_manager import CardManager
from cardnote.app.tray import CardTray


class CardNoteApp:
    """CardNote 主应用: 组装所有模块."""

    def __init__(self):
        self.qapp = QApplication(sys.argv)
        self.qapp.setApplicationName("CardNote")
        self.qapp.setOrganizationName("CardNote")
        self.qapp.setQuitOnLastWindowClosed(False)

        # 数据层
        self.database = Database()
        self.conn = self.database.connect()
        self.repository = CardRepository(self.conn)
        self.settings = Settings(self.conn)

        # 业务层
        self.card_manager = CardManager(self.repository)

        # UI
        self.tray = CardTray()
        self._connect_signals()

        # 加载已有卡片
        self.card_manager.load_all()
        self.tray.set_tooltip(len(self.card_manager.cards))

        # 设置主题
        self._is_dark = self.settings.get("theme") == "dark"
        self._apply_theme()

        # 全局快捷键 (通过 tray 的 QShortcut)
        self._setup_shortcuts()

    def _connect_signals(self):
        self.tray.new_card_requested.connect(self._on_new_card)
        self.tray.show_all_requested.connect(self.card_manager.show_all)
        self.tray.hide_all_requested.connect(self.card_manager.hide_all)
        self.tray.toggle_theme_requested.connect(self._toggle_theme)
        self.tray.quit_requested.connect(self._quit)
        self.card_manager.card_count_changed.connect(self.tray.set_tooltip)

    def _setup_shortcuts(self):
        from PySide6.QtGui import QShortcut, QKeySequence
        sc_new = QShortcut(QKeySequence("Ctrl+N"), self.qapp.activeWindow() or self.qapp)
        sc_new.activated.connect(self._on_new_card)
        sc_hide = QShortcut(QKeySequence("Ctrl+Shift+H"), self.qapp.activeWindow() or self.qapp)
        sc_hide.activated.connect(self.card_manager.hide_all)

    def _on_new_card(self):
        """创建新卡片，随机偏移位置避免重叠."""
        import random
        base_x, base_y = 400, 300
        offset_x = random.randint(-100, 100)
        offset_y = random.randint(-100, 100)
        card = self.card_manager.create_card(base_x + offset_x, base_y + offset_y)
        card.card_widget.focus_edit()

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self.settings.set("theme", "dark" if self._is_dark else "light")
        self._apply_theme()
        self.tray.set_theme_label(self._is_dark)

    def _apply_theme(self):
        theme_file = "dark.qss" if self._is_dark else "light.qss"
        import os
        qss_path = os.path.join(os.path.dirname(__file__), "..",
                                "ui", "resources", "styles", theme_file)
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.qapp.setStyleSheet(f.read())
        else:
            self.qapp.setStyleSheet("")

    def _quit(self):
        self.card_manager.save_all()
        self.database.close()
        self.qapp.quit()

    def run(self):
        sys.exit(self.qapp.exec())
```

- [ ] **Step 2: 实现 main.py**

```python
#!/usr/bin/env python3
"""CardNote - 桌面悬浮卡片记事本."""

import sys
import os

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cardnote.app.app import CardNoteApp


def main():
    app = CardNoteApp()
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 验证导入**

```bash
cd d:/Ai-tool/0604
python -c "from cardnote.app.app import CardNoteApp; print('CardNoteApp OK')"
```

Expected: CardNoteApp OK

- [ ] **Step 4: Commit**

```bash
git add cardnote/app/app.py cardnote/main.py
git commit -m "feat: add main app and entry point"
```

---

### Task 12: QSS 主题样式

**Files:**
- Create: `cardnote/ui/resources/styles/light.qss`
- Create: `cardnote/ui/resources/styles/dark.qss`
- Create: `cardnote/ui/resources/icons/card.svg`

- [ ] **Step 1: 创建 light.qss**

```css
/* CardNote 日间主题 */
QTextEdit {
    background: transparent;
    color: #2c2c2c;
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: #4a90d9;
    selection-color: white;
}

QTextEdit:focus {
    background: rgba(255, 255, 255, 0.3);
}

QMenu {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
    font-size: 13px;
}

QMenu::item:selected {
    background: #f0f0f0;
}

QMenu::separator {
    height: 1px;
    background: #e8e8e8;
    margin: 4px 12px;
}

QSizeGrip {
    background: rgba(0, 0, 0, 0.1);
    border-bottom-right-radius: 8px;
}
```

- [ ] **Step 2: 创建 dark.qss**

```css
/* CardNote 夜间主题 */
QTextEdit {
    background: transparent;
    color: #e0e0e0;
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: #5a7db0;
    selection-color: white;
}

QTextEdit:focus {
    background: rgba(255, 255, 255, 0.08);
}

QMenu {
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 4px;
    color: #e0e0e0;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
    font-size: 13px;
}

QMenu::item:selected {
    background: #3d3d3d;
}

QMenu::separator {
    height: 1px;
    background: #444;
    margin: 4px 12px;
}

QSizeGrip {
    background: rgba(255, 255, 255, 0.1);
    border-bottom-right-radius: 8px;
}
```

- [ ] **Step 3: 创建托盘图标 SVG**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect x="8" y="12" width="48" height="40" rx="8" ry="8" fill="#FFE4B5" stroke="#E8C88A" stroke-width="1.5"/>
  <rect x="8" y="12" width="48" height="8" rx="8" ry="8" fill="#FFD699" opacity="0.6"/>
  <line x1="18" y1="30" x2="46" y2="30" stroke="#CCB07A" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="18" y1="38" x2="38" y2="38" stroke="#CCB07A" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="48" cy="18" r="4" fill="#FF8A80" opacity="0.8"/>
</svg>
```

- [ ] **Step 4: 验证文件存在**

```bash
ls -la cardnote/ui/resources/styles/ cardnote/ui/resources/icons/
```

Expected: light.qss, dark.qss, card.svg 都在。

- [ ] **Step 5: Commit**

```bash
git add cardnote/ui/resources/
git commit -m "feat: add QSS themes and app icon"
```

---

## 自检清单

- [x] **Spec 覆盖**: 每个 spec 章节都有对应 Task — 数据库(Task 4,5)、配色(Task 3)、悬浮卡片(Task 8)、卡片管理器(Task 9)、系统托盘(Task 10)、设置(Task 6)、App 组装(Task 11)、QSS 主题(Task 12)
- [x] **无占位符**: 所有代码完整，无 TBD/TODO
- [x] **类型一致性**: FloatingCard 的 card_id 使用 str, CardManager.cards 使用 dict[str, FloatingCard], SQLite 用 TEXT 存 UUID — 类型一致
- [x] **测试覆盖**: 数据库、仓库、设置、卡片管理器都有完整测试
