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
