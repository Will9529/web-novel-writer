"""
章节生成与质检标签页
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QSpinBox, QProgressBar, QMessageBox, QGroupBox,
    QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

try:
    from chapter_generator import ChapterGenerator, GenerationWorker
    from quality_checker import QualityChecker, QualityCheckWorker
    from markdown_manager import MarkdownManager
except ImportError:
    from src.chapter_generator import ChapterGenerator, GenerationWorker
    from src.quality_checker import QualityChecker, QualityCheckWorker
    from src.markdown_manager import MarkdownManager


class ChapterGenerationTab(QWidget):
    """章节生成标签页"""
    
    def __init__(self, md_manager, llm_client):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        self.generator = ChapterGenerator(llm_client, md_manager)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("📖 章节生成引擎")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("基于五层 Prompt 组装生成章节正文：风格宪法 + 世界状态 + 上章末尾 + 章纲 + 生成指令")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 章节选择
        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("生成第"))
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(1, 9999)
        self.chapter_spin.setValue(1)
        chapter_layout.addWidget(self.chapter_spin)
        chapter_layout.addWidget(QLabel("章"))
        chapter_layout.addStretch()
        layout.addLayout(chapter_layout)
        
        # 主区域
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：配置和预览
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：生成结果
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def _create_left_panel(self):
        """左侧面板"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        
        # 生成按钮
        self.btn_generate = QPushButton("🚀 开始生成")
        self.btn_generate.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.clicked.connect(self.start_generation)
        layout.addWidget(self.btn_generate)
        
        # 进度显示
        progress_group = QGroupBox("生成进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("就绪")
        progress_layout.addWidget(self.lbl_status)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Prompt 预览
        prompt_group = QGroupBox("📋 Prompt 预览")
        prompt_layout = QVBoxLayout()
        
        self.prompt_preview = QTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setFixedHeight(300)
        prompt_layout.addWidget(self.prompt_preview)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        frame.setLayout(layout)
        return frame
    
    def _create_right_panel(self):
        """右侧面板"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        
        # 结果标题
        result_header = QHBoxLayout()
        result_header.addWidget(QLabel("生成结果"))
        result_header.addStretch()
        
        self.btn_save = QPushButton("💾 保存章节")
        self.btn_save.clicked.connect(self.save_result)
        self.btn_save.setEnabled(False)
        result_header.addWidget(self.btn_save)
        
        layout.addLayout(result_header)
        
        # 结果编辑器
        self.result_editor = QTextEdit()
        self.result_editor.setReadOnly(True)
        self.result_editor.setPlaceholderText("生成内容将显示在这里...")
        layout.addWidget(self.result_editor)
        
        frame.setLayout(layout)
        return frame
    
    def start_generation(self):
        """开始生成"""
        chapter_num = self.chapter_spin.value()
        
        # 检查是否有章纲
        outline = self.md_manager.load_chapter_outline(chapter_num)
        if not outline:
            reply = QMessageBox.question(
                self, "警告", 
                f"第{chapter_num}章暂无章纲，是否继续生成？\n\n建议先编写章纲再生成。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 组装 Prompt 预览
        system_prompt, user_prompt = self.generator.build_prompt(chapter_num)
        self.prompt_preview.setPlainText(f"=== 系统提示词 ===\n{system_prompt[:1000]}...\n\n=== 用户提示词 ===\n{user_prompt[:1000]}...")
        
        # 禁用按钮
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("⏳ 生成中...")
        self.progress_bar.setValue(20)
        self.lbl_status.setText("正在调用 AI 生成...")
        
        # 启动生成任务
        self.worker = GenerationWorker(self.generator, chapter_num)
        self.worker.progress.connect(self.on_generation_progress)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.start()
    
    def on_generation_progress(self, msg):
        self.lbl_status.setText(msg)
        self.progress_bar.setValue(50)
    
    def on_generation_finished(self, success, result):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("🚀 开始生成")
        
        if success:
            self.progress_bar.setValue(100)
            self.lbl_status.setText("✅ 生成完成！")
            self.result_editor.setPlainText(result)
            self.btn_save.setEnabled(True)
        else:
            self.progress_bar.setValue(0)
            self.lbl_status.setText(f"❌ 生成失败：{result}")
            QMessageBox.critical(self, "错误", f"生成失败：\n{result}")
    
    def save_result(self):
        """保存结果"""
        content = self.result_editor.toPlainText()
        chapter_num = self.chapter_spin.value()
        
        if not content.strip():
            return
        
        # 获取标题
        outline = self.md_manager.load_chapter_outline(chapter_num)
        title = ""
        if outline:
            raw = outline.get('raw', '')
            for line in raw.split('\n'):
                if line.startswith('# 第') and '章：' in line:
                    title = line.split('章：')[1].strip()
                    break
        
        filepath = self.md_manager.save_chapter(chapter_num, content, title)
        QMessageBox.information(self, "成功", f"章节已保存:\n{filepath}")
        self.btn_save.setEnabled(False)


class QualityCheckTab(QWidget):
    """质检标签页"""
    
    def __init__(self, md_manager, llm_client):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        self.quality_checker = QualityChecker(md_manager)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🔍 质检中心")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("三道检查机制：禁用词检测 + 结构相似度 + 情节债务核查")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 章节选择
        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("质检第"))
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(1, 9999)
        self.chapter_spin.setValue(1)
        chapter_layout.addWidget(self.chapter_spin)
        chapter_layout.addWidget(QLabel("章"))
        
        self.btn_check = QPushButton("🔍 开始质检")
        self.btn_check.clicked.connect(self.start_check)
        chapter_layout.addWidget(self.btn_check)
        
        chapter_layout.addStretch()
        layout.addLayout(chapter_layout)
        
        # 结果区域
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 上部：检查结果
        result_group = QGroupBox("质检结果")
        result_layout = QVBoxLayout()
        
        self.result_summary = QLabel("尚未进行质检")
        self.result_summary.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        result_layout.addWidget(self.result_summary)
        
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        result_layout.addWidget(self.result_detail)
        
        result_group.setLayout(result_layout)
        splitter.addWidget(result_group)
        
        # 下部：修改建议
        suggestion_group = QGroupBox("💡 修改建议")
        suggestion_layout = QVBoxLayout()
        
        self.suggestion_editor = QTextEdit()
        self.suggestion_editor.setPlaceholderText("AI 生成的修改建议将显示在这里...")
        suggestion_layout.addWidget(self.suggestion_editor)
        
        self.btn_apply_suggestion = QPushButton("✨ 应用建议修改")
        self.btn_apply_suggestion.clicked.connect(self.apply_suggestion)
        self.btn_apply_suggestion.setEnabled(False)
        suggestion_layout.addWidget(self.btn_apply_suggestion)
        
        suggestion_group.setLayout(suggestion_layout)
        splitter.addWidget(suggestion_group)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def start_check(self):
        """开始质检"""
        chapter_num = self.chapter_spin.value()
        content = self.md_manager.load_chapter(chapter_num)
        
        if not content:
            QMessageBox.warning(self, "警告", f"第{chapter_num}章暂无内容")
            return
        
        # 提取正文
        lines = content.split('\n')
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('# 第') and '章' in line:
                body_start = i + 1
                break
        body = '\n'.join(lines[body_start:])
        
        # 执行质检
        result = self.quality_checker.check_all(chapter_num, body)
        report = self.quality_checker.generate_report(result)
        
        # 显示结果
        score = result['score']
        if score >= 90:
            self.result_summary.setText(f"✅ 质检通过 - 得分：{score}/100（优秀）")
            self.result_summary.setStyleSheet("color: green;")
        elif score >= 70:
            self.result_summary.setText(f"⚠️ 质检通过 - 得分：{score}/100（良好）")
            self.result_summary.setStyleSheet("color: orange;")
        else:
            self.result_summary.setText(f"❌ 质检未通过 - 得分：{score}/100（需修改）")
            self.result_summary.setStyleSheet("color: red;")
        
        self.result_detail.setPlainText(report)
        
        # 生成修改建议
        if not result['passed']:
            self.generate_suggestions(chapter_num, body, result)
    
    def generate_suggestions(self, chapter_num, content, check_result):
        """生成修改建议"""
        prompt = f"""请根据以下质检结果，为第{chapter_num}章生成修改建议：

质检结果：
得分：{check_result['score']}/100
问题清单：
{check_result['issues']}

原文（节选）：
{content[:1500]}...

请给出：
1. 具体修改建议（针对每个问题）
2. 修改示例（展示如何改写）
3. 优先级排序（高/中/低）"""
        
        self.suggestion_editor.setPlainText("正在生成修改建议...")
        
        self.worker = SuggestionWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_suggestion_finished)
        self.worker.start()
    
    def on_suggestion_finished(self, result):
        if result and not result.startswith("["):
            self.suggestion_editor.setPlainText(result)
            self.btn_apply_suggestion.setEnabled(True)
    
    def apply_suggestion(self):
        """应用建议修改"""
        QMessageBox.information(self, "提示", "自动修改功能开发中...\n\n请根据建议手动修改。")


class SuggestionWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, llm_client, prompt):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt, max_tokens=1500)
        self.finished.emit(result)


class ProjectDashboardTab(QWidget):
    """项目进度看板标签页"""
    
    def __init__(self, md_manager):
        super().__init__()
        self.md_manager = md_manager
        
        try:
            from project_dashboard import ProjectDashboard
            self.dashboard = ProjectDashboard(md_manager)
        except ImportError:
            from src.project_dashboard import ProjectDashboard
            self.dashboard = ProjectDashboard(md_manager)
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题和刷新按钮
        header = QHBoxLayout()
        title = QLabel("📊 项目进度看板")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self.refresh)
        header.addWidget(self.btn_refresh)
        
        layout.addLayout(header)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        
        # 核心数据卡片
        self.lbl_overview = QLabel()
        self.lbl_overview.setStyleSheet("""
            QLabel {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        self.lbl_overview.setWordWrap(True)
        content_layout.addWidget(self.lbl_overview)
        
        # 章节列表
        chapters_group = QGroupBox("📚 章节列表")
        chapters_layout = QVBoxLayout()
        
        self.lbl_chapters = QLabel()
        self.lbl_chapters.setWordWrap(True)
        chapters_layout.addWidget(self.lbl_chapters)
        
        chapters_group.setLayout(chapters_layout)
        content_layout.addWidget(chapters_group)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def refresh(self):
        """刷新看板"""
        overview = self.dashboard.get_overview()
        pace = self.dashboard.get_writing_pace()
        
        # 更新概览
        overview_text = f"""
        <h3>📈 核心数据</h3>
        <table style="width:100%">
        <tr>
            <td style="padding:10px"><b>已完成章节</b><br><span style="font-size:24px;color:#4caf50">{overview['total_chapters']}</span> 章</td>
            <td style="padding:10px"><b>总字数</b><br><span style="font-size:24px;color:#2196f3">{overview['total_words']:,}</span> 字</td>
            <td style="padding:10px"><b>平均每章</b><br><span style="font-size:24px;color:#ff9800">{pace.get('avg_words_per_chapter', 0):.0f}</span> 字</td>
            <td style="padding:10px"><b>章纲完成率</b><br><span style="font-size:24px;color:#9c27b0">{pace.get('outline_completion_rate', 0):.1f}%</span></td>
        </tr>
        </table>
        
        <h3>✅ 项目状态</h3>
        <ul>
            <li>风格宪法：{'✅ 已建立' if overview['has_style_constitution'] else '❌ 未建立'}</li>
            <li>世界状态：{'✅ 已更新' if overview['total_world_states'] > 0 else '❌ 未更新'}</li>
            <li>字数健康度：{'✅ 正常' if pace.get('word_count_health') == 'good' else '⚠️ 需调整'}</li>
        </ul>
        
        <h3>📌 情节债务</h3>
        <p>总伏笔数：{overview['debt_stats']['total']} | 待填坑：{overview['debt_stats']['pending']}</p>
        """
        
        self.lbl_overview.setText(overview_text)
        
        # 更新章节列表
        chapters = overview.get('chapters', [])
        if chapters:
            chapter_text = "<ul>"
            for chap in chapters[-20:]:  # 最近 20 章
                outline_icon = "📝" if chap['has_outline'] else ""
                chapter_text += f"<li>第{chap['number']}章 {chap['title']} {outline_icon} ({chap['word_count']}字)</li>"
            chapter_text += "</ul>"
            self.lbl_chapters.setText(chapter_text)
        else:
            self.lbl_chapters.setText("暂无章节")
