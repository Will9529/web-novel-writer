"""
网文 AI 辅写系统 - 主界面
"""
import sys
import yaml
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QLineEdit,
    QFileDialog, QMessageBox, QSplitter, QFrame, QScrollArea,
    QFormLayout, QGroupBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

try:
    from llm_client import AliyunLLMClient
    from markdown_manager import MarkdownManager
except ImportError:
    from src.llm_client import AliyunLLMClient
    from src.markdown_manager import MarkdownManager


class StyleConstitutionTab(QWidget):
    """风格宪法编辑器"""
    
    def __init__(self, md_manager: MarkdownManager, llm_client: AliyunLLMClient):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        
        self.init_ui()
        self.load_existing()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("📜 风格宪法编辑器")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("在此定义你的写作风格，LLM 将严格按照此风格生成内容。可以从样章中自动提炼，也可以手动编写。")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 提炼按钮
        btn_layout = QHBoxLayout()
        self.btn_extract = QPushButton("📖 从样章自动提炼风格")
        self.btn_extract.clicked.connect(self.extract_style)
        btn_layout.addWidget(self.btn_extract)
        
        self.btn_save = QPushButton("💾 保存风格宪法")
        self.btn_save.clicked.connect(self.save_style)
        btn_layout.addWidget(self.btn_save)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("""## 风格宪法 v1

### 叙事视角
- 例如：第三人称限知视角，紧贴主角

### 句式偏好
- 例如：短句为主（<15 字），情绪高潮处用长句

### 描写密度
- 例如：动作：对话：心理：环境 = 3:3:3:1

### 禁用词表
- 例如：突然、瞬间、顿时、不禁、只见

### 标志性手法
- 例如：战斗场面必须有"感官细节"（气味/触觉）

### 节奏控制
- 例如：每章前 1/3 铺垫，中 1/3 推进，后 1/3 反转或钩子
""")
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
    
    def load_existing(self):
        """加载已存在的风格宪法"""
        content = self.md_manager.load_latest_style_constitution()
        if content:
            self.editor.setPlainText(content)
    
    def extract_style(self):
        """从样章提炼风格"""
        sample_chapters = QFileDialog.getOpenFileName(
            self, "选择样章文件", "", "Markdown Files (*.md);;All Files (*)"
        )[0]
        
        if not sample_chapters:
            return
        
        # 读取样章
        with open(sample_chapters, 'r', encoding='utf-8') as f:
            sample_content = f.read()
        
        prompt = f"""请分析以下样章的写作风格，提炼出一份《作者风格宪法》，包含：
1. 叙事视角
2. 句式偏好（平均句长、长短句使用规律）
3. 描写密度（动作/对话/心理/环境的比例）
4. 高频用词特点
5. 标志性手法（独特的描写方式）
6. 节奏控制规律

样章内容：
{sample_content[:8000]}  # 限制长度

请以 Markdown 格式输出，简洁清晰。"""
        
        self.btn_extract.setEnabled(False)
        self.btn_extract.setText("⏳ 分析中...")
        
        # 异步调用 LLM
        self.worker = StyleExtractWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_extract_finished)
        self.worker.start()
    
    def on_extract_finished(self, result: str):
        self.btn_extract.setEnabled(True)
        self.btn_extract.setText("📖 从样章自动提炼风格")
        
        if result:
            current = self.editor.toPlainText()
            if current.strip():
                self.editor.append("\n---\n\n## 自动提炼结果\n")
            self.editor.append(result)
    
    def save_style(self):
        """保存风格宪法"""
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "警告", "风格宪法内容不能为空")
            return
        
        version = "v1"  # 可以从 UI 获取
        filepath = self.md_manager.save_style_constitution(content, version)
        QMessageBox.information(self, "成功", f"风格宪法已保存:\n{filepath}")


class StyleExtractWorker(QThread):
    """风格提炼后台任务"""
    finished = pyqtSignal(str)
    
    def __init__(self, llm_client: AliyunLLMClient, prompt: str):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt)
        self.finished.emit(result)


class ChapterOutlineTab(QWidget):
    """章纲结构化编写器"""
    
    def __init__(self, md_manager: MarkdownManager, llm_client: AliyunLLMClient):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        
        self.current_chapter = 1
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("📝 章纲结构化编写")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 章节选择
        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("第"))
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(1, 9999)
        self.chapter_spin.setValue(1)
        self.chapter_spin.valueChanged.connect(self.on_chapter_changed)
        chapter_layout.addWidget(self.chapter_spin)
        chapter_layout.addWidget(QLabel("章"))
        
        self.btn_load = QPushButton("📂 加载")
        self.btn_load.clicked.connect(self.load_outline)
        chapter_layout.addWidget(self.btn_load)
        
        self.btn_new = QPushButton("📄 新建")
        self.btn_new.clicked.connect(self.new_outline)
        chapter_layout.addWidget(self.btn_new)
        
        chapter_layout.addStretch()
        layout.addLayout(chapter_layout)
        
        # 表单区域
        form_frame = QScrollArea()
        form_frame.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QFormLayout()
        
        # 章名
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("本章标题")
        form_layout.addRow("章名", self.title_input)
        
        # 场景
        self.scene_input = QTextEdit()
        self.scene_input.setMaximumHeight(60)
        self.scene_input.setPlaceholderText("具体地点 + 时间 + 天气/氛围")
        form_layout.addRow("场景", self.scene_input)
        
        # 人物在场
        self.chars_input = QTextEdit()
        self.chars_input.setMaximumHeight(60)
        self.chars_input.setPlaceholderText("谁在场，各自状态")
        form_layout.addRow("人物在场", self.chars_input)
        
        # 核心事件
        self.event_input = QTextEdit()
        self.event_input.setMaximumHeight(60)
        self.event_input.setPlaceholderText("一句话，唯一事件")
        form_layout.addRow("核心事件", self.event_input)
        
        # 开场钩子
        self.opening_input = QTextEdit()
        self.opening_input.setMaximumHeight(60)
        self.opening_input.setPlaceholderText("首句或首段的具体形式")
        form_layout.addRow("开场钩子", self.opening_input)
        
        # 结尾钩子
        self.ending_input = QTextEdit()
        self.ending_input.setMaximumHeight(60)
        self.ending_input.setPlaceholderText("悬念/反转/情感落点")
        form_layout.addRow("结尾钩子", self.ending_input)
        
        # 承上
        self.connect_prev_input = QTextEdit()
        self.connect_prev_input.setMaximumHeight(60)
        self.connect_prev_input.setPlaceholderText("必须呼应上章哪个细节")
        form_layout.addRow("承上", self.connect_prev_input)
        
        # 启下
        self.connect_next_input = QTextEdit()
        self.connect_next_input.setMaximumHeight(60)
        self.connect_next_input.setPlaceholderText("必须为下章埋哪个伏笔")
        form_layout.addRow("启下", self.connect_next_input)
        
        # 禁止出现
        self.forbidden_input = QTextEdit()
        self.forbidden_input.setMaximumHeight(60)
        self.forbidden_input.setPlaceholderText("本章不得出现的内容")
        form_layout.addRow("禁止出现", self.forbidden_input)
        
        form_widget.setLayout(form_layout)
        form_frame.setWidget(form_widget)
        layout.addWidget(form_frame)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.btn_auto_fill = QPushButton("🤖 AI 辅助填充")
        self.btn_auto_fill.clicked.connect(self.auto_fill_outline)
        btn_layout.addWidget(self.btn_auto_fill)
        
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("💾 保存章纲")
        self.btn_save.clicked.connect(self.save_outline)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def on_chapter_changed(self, value):
        self.current_chapter = value
    
    def new_outline(self):
        """新建章纲"""
        self.title_input.clear()
        self.scene_input.clear()
        self.chars_input.clear()
        self.event_input.clear()
        self.opening_input.clear()
        self.ending_input.clear()
        self.connect_prev_input.clear()
        self.connect_next_input.clear()
        self.forbidden_input.clear()
    
    def load_outline(self):
        """加载章纲"""
        outline = self.md_manager.load_chapter_outline(self.current_chapter)
        if outline:
            # 简单解析（可以改进）
            QMessageBox.information(self, "提示", "已加载章纲（解析功能待完善）")
        else:
            QMessageBox.information(self, "提示", "该章节暂无章纲")
    
    def auto_fill_outline(self):
        """AI 辅助填充"""
        # 获取世界状态和上章信息
        world_state = self.md_manager.load_latest_world_state()
        prev_chapter = self.md_manager.load_chapter(self.current_chapter - 1)
        
        prompt = f"""请根据以下信息，为第{self.current_chapter}章生成一个结构化章纲：

世界状态摘要：
{world_state['content'] if world_state else '暂无'}

上章末尾（如有）：
{prev_chapter[-500:] if prev_chapter else '暂无'}

请按照以下六要素生成章纲：
1. 场景（具体地点 + 时间 + 天气/氛围）
2. 人物在场（谁在场，各自状态）
3. 本章核心事件（一句话，唯一事件）
4. 开场钩子（首句或首段的具体形式）
5. 结尾钩子（悬念/反转/情感落点）
6. 承上启下（呼应上章细节，为下章埋伏笔）
7. 禁止出现（本章不得出现的内容）

请以简洁的条目形式输出。"""
        
        self.btn_auto_fill.setEnabled(False)
        self.btn_auto_fill.setText("⏳ 生成中...")
        
        self.worker = OutlineFillWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_auto_fill_finished)
        self.worker.start()
    
    def on_auto_fill_finished(self, result: str):
        self.btn_auto_fill.setEnabled(True)
        self.btn_auto_fill.setText("🤖 AI 辅助填充")
        
        if result:
            # 简单解析结果填充到各字段（可以改进为更智能的解析）
            self.scene_input.append(result)
    
    def save_outline(self):
        """保存章纲"""
        outline = {
            "title": self.title_input.text(),
            "scene": self.scene_input.toPlainText(),
            "characters": self.chars_input.toPlainText(),
            "core_event": self.event_input.toPlainText(),
            "opening_hook": self.opening_input.toPlainText(),
            "ending_hook": self.ending_input.toPlainText(),
            "connect_previous": self.connect_prev_input.toPlainText(),
            "connect_next": self.connect_next_input.toPlainText(),
            "forbidden": self.forbidden_input.toPlainText(),
        }
        
        filepath = self.md_manager.save_chapter_outline(self.current_chapter, outline)
        QMessageBox.information(self, "成功", f"章纲已保存:\n{filepath}")


class OutlineFillWorker(QThread):
    """章纲填充后台任务"""
    finished = pyqtSignal(str)
    
    def __init__(self, llm_client: AliyunLLMClient, prompt: str):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt)
        self.finished.emit(result)


class WorldStateTab(QWidget):
    """世界状态追踪面板"""
    
    def __init__(self, md_manager: MarkdownManager, llm_client: AliyunLLMClient):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        
        self.init_ui()
        self.load_latest()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🌍 世界状态追踪")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("维护世界状态表，追踪人物状态、情节债务和已用模板，确保前后文一致性。")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("📂 加载最新状态")
        self.btn_load.clicked.connect(self.load_latest)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_update = QPushButton("✏️ 更新状态")
        self.btn_update.clicked.connect(self.update_state)
        btn_layout.addWidget(self.btn_update)
        
        self.btn_diff = QPushButton("🔍 生成状态变更 Diff")
        self.btn_diff.clicked.connect(self.generate_diff)
        btn_layout.addWidget(self.btn_diff)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("""## 人物状态

### 主角
- 当前位置：
- 实力：
- 持有物品：
- 情绪状态：
- 未了结的承诺：

### 主要配角
- （名称）：状态描述

### 反派
- 最后出现章节：
- 已知信息：
- 当前目的：

## 情节债务（已埋未填的伏笔）
- 第 X 章提到的 XXX → 预计第 Y 章揭示

## 已用情节模板
- 模板名称：第 X 章（用过，近期禁用）
""")
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
    
    def load_latest(self):
        """加载最新世界状态"""
        state = self.md_manager.load_latest_world_state()
        if state:
            self.editor.setPlainText(state['content'])
        else:
            self.editor.clear()
    
    def update_state(self):
        """更新状态"""
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "警告", "状态内容不能为空")
            return
        
        # 简单解析（可以改进）
        chapter = self.guess_chapter_number()
        state = {
            "protagonist": "",
            "supporting_chars": "",
            "antagonist": "",
            "plot_debts": "",
            "used_templates": "",
            "changes_diff": ""
        }
        
        filepath = self.md_manager.save_world_state(state, chapter)
        QMessageBox.information(self, "成功", f"世界状态已保存:\n{filepath}")
    
    def generate_diff(self):
        """生成状态变更 Diff"""
        prev_state = self.md_manager.load_latest_world_state()
        
        prompt = f"""请对比当前世界状态和上一章状态，生成一份状态变更 Diff。

当前状态：
{self.editor.toPlainText()}

上一状态：
{prev_state['content'] if prev_state else '暂无'}

请列出：
1. 人物状态变更（位置、实力、物品、情绪等）
2. 新增/已填的情节债务
3. 新增的已用情节模板

以简洁的条目形式输出。"""
        
        self.btn_diff.setEnabled(False)
        self.btn_diff.setText("⏳ 生成中...")
        
        self.worker = DiffGenerateWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_diff_finished)
        self.worker.start()
    
    def on_diff_finished(self, result: str):
        self.btn_diff.setEnabled(True)
        self.btn_diff.setText("🔍 生成状态变更 Diff")
        
        if result:
            self.editor.append("\n---\n\n## 本章状态变更 Diff\n")
            self.editor.append(result)
    
    def guess_chapter_number(self) -> int:
        """猜测当前章节号"""
        # 简单实现，可以从文件名或内容解析
        return 1
    
    def load_latest(self):
        """加载最新世界状态"""
        state = self.md_manager.load_latest_world_state()
        if state:
            self.editor.setPlainText(state['content'])
        else:
            self.editor.clear()


class DiffGenerateWorker(QThread):
    """Diff 生成后台任务"""
    finished = pyqtSignal(str)
    
    def __init__(self, llm_client: AliyunLLMClient, prompt: str):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.md_manager = None
        self.llm_client = None
        
        self.init_ui()
        self.init_components()
    
    def init_ui(self):
        self.setWindowTitle("🖋️ 网文 AI 辅写系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        self.lbl_project = QLabel("📁 项目：未选择")
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
        layout.addWidget(self.tabs)
        
        # 标签页将在初始化组件后添加
        
        self.statusBar().showMessage("就绪 - 请选择或新建项目")
    
    def init_components(self):
        """初始化组件（需要项目路径）"""
        pass
    
    def select_project(self):
        """选择项目目录"""
        path = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if path:
            self.setup_project(path)
    
    def new_project(self):
        """新建项目"""
        path = QFileDialog.getExistingDirectory(self, "选择项目保存位置")
        if path:
            project_name = "novel_project"  # 可以添加对话框让用户输入
            project_path = f"{path}/{project_name}"
            import os
            os.makedirs(project_path, exist_ok=True)
            self.setup_project(project_path)
    
    def setup_project(self, project_path: str):
        """设置项目"""
        self.project_path = project_path
        self.lbl_project.setText(f"📁 项目：{project_path}")
        
        # 初始化组件
        self.md_manager = MarkdownManager(project_path)
        
        api_key = self.config.get('aliyun', {}).get('api_key', '')
        if not api_key:
            QMessageBox.warning(self, "警告", "请在 config.yaml 中配置阿里云 API Key")
            return
        
        self.llm_client = AliyunLLMClient(api_key, self.config.get('aliyun', {}).get('model', 'qwen-plus'))
        
        # 添加标签页
        while self.tabs.count():
            self.tabs.removeTab(0)
        
        self.tabs.addTab(StyleConstitutionTab(self.md_manager, self.llm_client), "📜 风格宪法")
        self.tabs.addTab(ChapterOutlineTab(self.md_manager, self.llm_client), "📝 章纲编写")
        self.tabs.addTab(WorldStateTab(self.md_manager, self.llm_client), "🌍 世界状态")
        
        self.statusBar().showMessage(f"项目已加载：{project_path}")


def main():
    # 加载配置
    config_path = "config.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {"aliyun": {"api_key": "", "model": "qwen-plus"}}
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
