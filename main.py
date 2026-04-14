#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网文 AI 辅写系统 - 主入口

基于工程化方案的桌面应用，包含：
- 风格宪法编辑器
- 章纲结构化编写
- 世界状态追踪面板
- 写作助手（智能编辑器）
- 章节生成引擎
- 质检中心
- 项目进度看板
"""
import sys
import os

# 添加 src 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, 'src'))

# Windows 兼容性：设置 DPI 感知
if sys.platform == 'win32':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from src.app import main

if __name__ == "__main__":
    main()
