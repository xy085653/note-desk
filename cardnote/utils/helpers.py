import os
import sys
import uuid
from datetime import datetime, timezone


def new_uuid() -> str:
    """生成 UUID4 字符串."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串."""
    return datetime.now(timezone.utc).isoformat()


def set_auto_start(enabled: bool, app_name: str = "CardNote"):
    """设置开机自启（Windows 注册表）. """
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                             winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, sys.executable)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def is_auto_start_enabled(app_name: str = "CardNote") -> bool:
    """检查是否已设置开机自启."""
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_QUERY_VALUE)
        try:
            winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径，兼容开发环境和 PyInstaller 打包后."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)
