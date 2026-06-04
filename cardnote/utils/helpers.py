import uuid
from datetime import datetime, timezone


def new_uuid() -> str:
    """生成 UUID4 字符串."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串."""
    return datetime.now(timezone.utc).isoformat()
