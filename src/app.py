#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网文 AI 辅写系统 - 主窗口
整合所有功能模块
"""
import sys
import os
import yaml
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 添加路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, 'src'))

# Windows DPI 感知
if sys.platform == 'win32':
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.md_manager = None
        self.llm_client = None
        self.quality_checker = None
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🖋️ 网文 AI 辅写系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        self.lbl_project = QLabel("📁 项目：未选择")
        self.lbl_project.setFont(QFont("Arial", 11))
        info_layout.addWidget(self.lbl_project)
        
        info_layout.addStretch()
        
        self.btn_select_project = QPushButton("📂 选择项目")
        self.btn_select_project.clicked.connect(self.select_project)
        info_layout.addWidget(self.btn_select_project)
        
        self.btn_new_project = QPushButton("📄 新建项目")
        self.btn_new_project.clicked.connect(self.new_project)
        info_layout.addWidget(self.btn_new_project)
        
        layout.addLayout(info_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 11))
        layout.addWidget(self.tabs)
        
        # 欢迎页面（未选择项目时显示）
        self.welcome_widget = self._create_welcome_page()
        layout.addWidget(self.welcome_widget)
        
        self.tabs.hide()  # 初始隐藏
        
        self.statusBar().showMessage("就绪 - 请选择或新建项目开始使用")
    
    def _create_welcome_page(self):
        """创建欢迎页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("🖋️ 网文 AI 辅写系统")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("基于工程化方案的智能写作助手")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        features = QLabel("""
        <h3>核心功能</h3>
        <table style="font-size:14px; margin:20px;">
        <tr><td>📜 风格宪法</td><td>定义写作风格，支持样章自动提炼</td></tr>
        <tr><td>📝 章纲编写</td><td>六要素结构化章纲，AI 辅助填充</td></tr>
        <tr><td>🌍 世界状态</td><td>追踪人物状态、情节债务、已用模板</td></tr>
        <tr><td>✍️ 写作助手</td><td>智能编辑器，实时保存，AI 辅助写作</td></tr>
        <tr><td>📖 章节生成</td><td>五层 Prompt 组装，一键生成章节</td></tr>
        <tr><td>🔍 质检中心</td><td>三道检查机制，确保内容质量</td></tr>
        <tr><td>📊 进度看板</td><td>项目数据统计，写作进度追踪</td></tr>
        </table>
        """)
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features)
        
        layout.addSpacing(20)
        
        help_text = QLabel("点击上方「新建项目」或「选择项目」开始使用")
        help_text.setStyleSheet("color: #666; font-style: italic;")
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_text)
        
        widget.setLayout(layout)
        return widget
    
    def select_project(self):
        """选择项目目录"""
        path = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if path:
            self.setup_project(path)
    
    def new_project(self):
        """新建项目"""
        path = QFileDialog.getExistingDirectory(self, "选择项目保存位置")
        if path:
            project_name = "novel_project"
            project_path = os.path.join(path, project_name)
            os.makedirs(project_path, exist_ok=True)
            self.setup_project(project_path)
    
    def setup_project(self, project_path: str):
        """设置项目"""
        self.project_path = project_path
        self.lbl_project.setText(f"📁 项目：{project_path}")
        
        # 导入模块
        try:
            from markdown_manager import MarkdownManager
            from llm_client import AliyunLLMClient
            from quality_checker import QualityChecker
        except ImportError:
            from src.markdown_manager import MarkdownManager
            from src.llm_client import AliyunLLMClient
            from src.quality_checker import QualityChecker
        
        # 初始化组件
        self.md_manager = MarkdownManager(project_path)
        
        api_key = self.config.get('aliyun', {}).get('api_key', '')
        if not api_key or api_key == "sk-请在此处填写你的 API Key":
            QMessageBox.warning(self, "警告", 
                "请在 config.yaml 中配置阿里云 API Key 后重启应用！\n\n"
                "获取 API Key: https://dashscope.console.aliyun.com/")
            return
        
        self.llm_client = AliyunLLMClient(
            api_key, 
            self.config.get('aliyun', {}).get('model', 'qwen-plus')
        )
        
        self.quality_checker = QualityChecker(
            self.md_manager,
            self.config.get('banned_words', ['突然', '瞬间', '顿时', '不禁', '只见'])
        )
        
        # 添加标签页
        self._add_tabs()
        
        # 切换显示
        self.welcome_widget.hide()
        self.tabs.show()
        
        self.statusBar().showMessage(f"项目已加载：{project_path}")
    
    def _add_tabs(self):
        """添加所有标签页"""
        # 清除现有标签
        while self.tabs.count():
            self.tabs.removeTab(0)
        
        # 1. 风格宪法
        try:
            from main_window import StyleConstitutionTab
        except ImportError:
            from src.main_window import StyleConstitutionTab
        
        tab1 = StyleConstitutionTab(self.md_manager, self.llm_client)
        self.tabs.addTab(tab1, "📜 风格宪法")
        
        # 2. 章纲编写
        try:
            from main_window import ChapterOutlineTab
        except ImportError:
            from src.main_window import ChapterOutlineTab
        
        tab2 = ChapterOutlineTab(self.md_manager, self.llm_client)
        self.tabs.addTab(tab2, "📝 章纲编写")
        
        # 3. 世界状态
        try:
            from main_window import WorldStateTab
        except ImportError:
            from src.main_window import WorldStateTab
        
        tab3 = WorldStateTab(self.md_manager, self.llm_client)
        self.tabs.addTab(tab3, "🌍 世界状态")
        
        # 4. 写作助手（新增）
        try:
            from writing_assistant import WritingAssistantTab
        except ImportError:
            from src.writing_assistant import WritingAssistantTab
        
        tab4 = WritingAssistantTab(self.md_manager, self.llm_client, self.quality_checker)
        self.tabs.addTab(tab4, "✍️ 写作助手")
        
        # 5. 章节生成（新增）
        try:
            from generation_and_quality import ChapterGenerationTab
        except ImportError:
            from src.generation_and_quality import ChapterGenerationTab
        
        tab5 = ChapterGenerationTab(self.md_manager, self.llm_client)
        self.tabs.addTab(tab5, "📖 章节生成")
        
        # 6. 质检中心（新增）
        try:
            from generation_and_quality import QualityCheckTab
        except ImportError:
            from src.generation_and_quality import QualityCheckTab
        
        tab6 = QualityCheckTab(self.md_manager, self.llm_client)
        self.tabs.addTab(tab6, "🔍 质检中心")
        
        # 7. 进度看板（新增）
        try:
            from generation_and_quality import ProjectDashboardTab
        except ImportError:
            from src.generation_and_quality import ProjectDashboardTab
        
        tab7 = ProjectDashboardTab(self.md_manager)
        self.tabs.addTab(tab7, "📊 进度看板")


def main():
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {"aliyun": {"api_key": "", "model": "qwen-plus"}}
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
