"""
写作助手模块 - 集成写作功能
包含：编辑器、实时保存、字数统计、AI 辅助写作
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QSpinBox, QComboBox, QMessageBox, QProgressBar,
    QSplitter, QFrame, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
import re
from typing import Optional, Dict, Any


class WritingAssistantTab(QWidget):
    """写作助手标签页"""
    
    def __init__(self, md_manager, llm_client, quality_checker):
        super().__init__()
        self.md_manager = md_manager
        self.llm_client = llm_client
        self.quality_checker = quality_checker
        
        self.current_chapter = 1
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)  # 60 秒自动保存
        
        self.init_ui()
        self.load_chapter()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # ===== 顶部工具栏 =====
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)
        
        # ===== 主编辑区域 =====
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：编辑器
        editor_frame = self._create_editor_panel()
        main_splitter.addWidget(editor_frame)
        
        # 右侧：辅助面板
        assistant_panel = self._create_assistant_panel()
        main_splitter.addWidget(assistant_panel)
        
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
    
    def _create_toolbar(self):
        """创建顶部工具栏"""
        layout = QHBoxLayout()
        
        # 章节选择
        layout.addWidget(QLabel("第"))
        self.chapter_spin = QSpinBox()
        self.chapter_spin.setRange(1, 9999)
        self.chapter_spin.setValue(1)
        self.chapter_spin.setFixedWidth(60)
        self.chapter_spin.valueChanged.connect(self.on_chapter_changed)
        layout.addWidget(self.chapter_spin)
        layout.addWidget(QLabel("章"))
        
        # 章节标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("输入章节标题...")
        self.title_input.setFixedWidth(200)
        layout.addWidget(self.title_input)
        
        layout.addStretch()
        
        # 加载/保存按钮
        self.btn_load = QPushButton("📂 加载")
        self.btn_load.clicked.connect(self.load_chapter)
        layout.addWidget(self.btn_load)
        
        self.btn_save = QPushButton("💾 保存")
        self.btn_save.clicked.connect(self.save_chapter)
        layout.addWidget(self.btn_save)
        
        # 自动保存指示
        self.lbl_auto_save = QLabel("🟢 自动保存已开启")
        self.lbl_auto_save.setStyleSheet("color: green; font-size: 12px;")
        layout.addWidget(self.lbl_auto_save)
        
        return layout
    
    def _create_editor_panel(self):
        """创建编辑器面板"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        
        # 编辑器
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("开始写作吧...\n\n提示：可以使用右侧的 AI 辅助功能帮助写作。")
        self.editor.setFont(QFont("Microsoft YaHei", 12))
        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor)
        
        # 底部状态栏
        status_layout = QHBoxLayout()
        
        self.lbl_word_count = QLabel("字数：0")
        status_layout.addWidget(self.lbl_word_count)
        
        self.lbl_target_words = QLabel("目标：2750")
        status_layout.addWidget(self.lbl_target_words)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3000)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(200)
        status_layout.addWidget(self.progress_bar)
        
        self.lbl_quality_score = QLabel("质检分：--")
        status_layout.addWidget(self.lbl_quality_score)
        
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        frame.setLayout(layout)
        return frame
    
    def _create_assistant_panel(self):
        """创建辅助面板"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        
        # ===== AI 辅助写作 =====
        ai_group = QGroupBox("🤖 AI 辅助写作")
        ai_layout = QVBoxLayout()
        
        # 续写
        self.btn_continue = QPushButton("✍️ 智能续写 (500 字)")
        self.btn_continue.clicked.connect(self.ai_continue)
        ai_layout.addWidget(self.btn_continue)
        
        # 润色
        self.btn_polish = QPushButton("✨ 润色段落")
        self.btn_polish.clicked.connect(self.ai_polish)
        ai_layout.addWidget(self.btn_polish)
        
        # 扩写
        self.btn_expand = QPushButton("📝 扩写场景")
        self.btn_expand.clicked.connect(self.ai_expand)
        ai_layout.addWidget(self.btn_expand)
        
        # 生成对话
        self.btn_dialogue = QPushButton("💬 生成对话")
        self.btn_dialogue.clicked.connect(self.ai_generate_dialogue)
        ai_layout.addWidget(self.btn_dialogue)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # ===== 快捷工具 =====
        tool_group = QGroupBox("🛠️ 快捷工具")
        tool_layout = QVBoxLayout()
        
        self.btn_check_quality = QPushButton("🔍 质检本章")
        self.btn_check_quality.clicked.connect(self.check_quality)
        tool_layout.addWidget(self.btn_check_quality)
        
        self.btn_find_replace = QPushButton("🔄 查找替换")
        self.btn_find_replace.clicked.connect(self.open_find_replace)
        tool_layout.addWidget(self.btn_find_replace)
        
        self.btn_insert_template = QPushButton("📋 插入模板")
        self.btn_insert_template.clicked.connect(self.insert_template)
        tool_layout.addWidget(self.btn_insert_template)
        
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)
        
        # ===== 写作提示 =====
        tip_group = QGroupBox("💡 写作提示")
        tip_layout = QVBoxLayout()
        
        self.lbl_outline_hint = QLabel("本章纲：暂无")
        self.lbl_outline_hint.setWordWrap(True)
        self.lbl_outline_hint.setStyleSheet("background: #f0f0f0; padding: 5px; border-radius: 3px;")
        tip_layout.addWidget(self.lbl_outline_hint)
        
        self.lbl_state_hint = QLabel("状态：暂无")
        self.lbl_state_hint.setWordWrap(True)
        self.lbl_state_hint.setStyleSheet("background: #f0f0f0; padding: 5px; border-radius: 3px;")
        tip_layout.addWidget(self.lbl_state_hint)
        
        tip_group.setLayout(tip_layout)
        layout.addWidget(tip_group)
        
        layout.addStretch()
        
        frame.setLayout(layout)
        return frame
    
    def on_chapter_changed(self, value):
        self.current_chapter = value
        self.load_chapter()
        self.update_hints()
    
    def on_text_changed(self):
        """文本变化时更新状态"""
        text = self.editor.toPlainText()
        word_count = len(text)
        
        self.lbl_word_count.setText(f"字数：{word_count}")
        self.progress_bar.setValue(word_count)
        
        # 颜色提示
        if word_count < 2500:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background: #ffa500; }")
        elif word_count > 3000:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background: #ff6b6b; }")
        else:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background: #4caf50; }")
    
    def load_chapter(self):
        """加载章节"""
        content = self.md_manager.load_chapter(self.current_chapter)
        if content:
            # 提取标题
            for line in content.split('\n')[:5]:
                if line.startswith('# 第') and '章' in line:
                    if '章 ' in line:
                        self.title_input.setText(line.split('章 ')[1].strip())
                    break
            
            # 提取正文（去除标题行）
            lines = content.split('\n')
            body_start = 0
            for i, line in enumerate(lines):
                if line.startswith('# 第') and '章' in line:
                    body_start = i + 1
                    break
            
            body = '\n'.join(lines[body_start:])
            self.editor.setPlainText(body.strip())
        else:
            self.editor.clear()
            self.title_input.clear()
        
        self.update_hints()
    
    def save_chapter(self):
        """保存章节"""
        content = self.editor.toPlainText()
        title = self.title_input.text().strip()
        
        if not content.strip():
            QMessageBox.warning(self, "警告", "章节内容不能为空")
            return
        
        filepath = self.md_manager.save_chapter(self.current_chapter, content, title)
        self.lbl_auto_save.setText(f"✅ 已保存：{filepath.split('/')[-1]}")
        self.lbl_auto_save.setStyleSheet("color: blue; font-size: 12px;")
        
        # 2 秒后恢复
        QTimer.singleShot(2000, lambda: self.lbl_auto_save.setText("🟢 自动保存已开启"))
        self.lbl_auto_save.setStyleSheet("color: green; font-size: 12px;")
    
    def auto_save(self):
        """自动保存"""
        content = self.editor.toPlainText()
        if content.strip():
            title = self.title_input.text().strip() or f"第{self.current_chapter}章"
            self.md_manager.save_chapter(self.current_chapter, content, title)
    
    def update_hints(self):
        """更新写作提示"""
        # 加载章纲提示
        outline = self.md_manager.load_chapter_outline(self.current_chapter)
        if outline:
            raw = outline.get('raw', '')
            # 提取核心事件
            for line in raw.split('\n'):
                if '核心事件' in line:
                    self.lbl_outline_hint.setText(f"本章核心：{line.split('：')[-1].strip()[:50]}...")
                    break
        
        # 加载世界状态提示
        world_state = self.md_manager.load_latest_world_state()
        if world_state:
            self.lbl_state_hint.setText("世界状态：已加载")
        else:
            self.lbl_state_hint.setText("世界状态：暂无")
    
    # ========== AI 辅助功能 ==========
    
    def ai_continue(self):
        """智能续写"""
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "警告", "请先输入一些内容")
            return
        
        # 获取最后一段
        paragraphs = text.split('\n\n')
        last_para = paragraphs[-1] if paragraphs else ""
        
        prompt = f"""请根据以下内容的风格和情节，续写 500 字：

{last_para[-300:]}

要求：
1. 保持文风一致
2. 情节自然推进
3. 不要总结，保持开放性"""
        
        self.btn_continue.setEnabled(False)
        self.btn_continue.setText("⏳ 生成中...")
        
        self.worker = AIContinueWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_ai_continue_finished)
        self.worker.start()
    
    def on_ai_continue_finished(self, result: str):
        self.btn_continue.setEnabled(True)
        self.btn_continue.setText("✍️ 智能续写 (500 字)")
        
        if result and not result.startswith("["):
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText("\n\n" + result)
            self.editor.setTextCursor(cursor)
    
    def ai_polish(self):
        """润色段落"""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        if not selected.strip():
            QMessageBox.warning(self, "警告", "请先选择要润色的段落")
            return
        
        prompt = f"""请润色以下段落，保持原意但提升文笔：

{selected}

要求：
1. 优化句式结构
2. 增强画面感
3. 保持原有风格"""
        
        self.btn_polish.setEnabled(False)
        self.btn_polish.setText("⏳ 润色中...")
        
        self.worker = AIPolishWorker(self.llm_client, prompt)
        self.worker.finished.connect(lambda r: self.on_ai_polish_finished(r, selected))
        self.worker.start()
    
    def on_ai_polish_finished(self, result: str, original: str):
        self.btn_polish.setEnabled(True)
        self.btn_polish.setText("✨ 润色段落")
        
        if result and not result.startswith("["):
            cursor = self.editor.textCursor()
            cursor.insertText(result)
    
    def ai_expand(self):
        """扩写场景"""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        if not selected.strip():
            QMessageBox.warning(self, "警告", "请先选择要扩写的场景")
            return
        
        prompt = f"""请扩写以下场景描述，增加到 300 字左右：

{selected}

要求：
1. 增加感官细节（视觉、听觉、嗅觉、触觉）
2. 保持节奏感
3. 不要偏离原意"""
        
        self.btn_expand.setEnabled(False)
        self.btn_expand.setText("⏳ 扩写中...")
        
        self.worker = AIExpandWorker(self.llm_client, prompt)
        self.worker.finished.connect(lambda r: self.on_ai_expand_finished(r, selected))
        self.worker.start()
    
    def on_ai_expand_finished(self, result: str, original: str):
        self.btn_expand.setEnabled(True)
        self.btn_expand.setText("📝 扩写场景")
        
        if result and not result.startswith("["):
            cursor = self.editor.textCursor()
            cursor.insertText(result)
    
    def ai_generate_dialogue(self):
        """生成对话"""
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        
        if not selected.strip():
            QMessageBox.warning(self, "警告", "请先选择对话场景描述")
            return
        
        prompt = f"""请根据以下场景描述，生成一段自然的人物对话：

{selected}

要求：
1. 对话符合人物性格
2. 每轮对话不超过 2 句
3. 适当插入动作和心理描写
4. 3-5 轮对话"""
        
        self.btn_dialogue.setEnabled(False)
        self.btn_dialogue.setText("⏳ 生成中...")
        
        self.worker = AIDialogueWorker(self.llm_client, prompt)
        self.worker.finished.connect(self.on_ai_dialogue_finished)
        self.worker.start()
    
    def on_ai_dialogue_finished(self, result: str):
        self.btn_dialogue.setEnabled(True)
        self.btn_dialogue.setText("💬 生成对话")
        
        if result and not result.startswith("["):
            cursor = self.editor.textCursor()
            cursor.insertText("\n" + result + "\n")
            self.editor.setTextCursor(cursor)
    
    def check_quality(self):
        """质检本章"""
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "警告", "没有内容可质检")
            return
        
        result = self.quality_checker.check_all(self.current_chapter, content)
        report = self.quality_checker.generate_report(result)
        
        # 显示质检结果
        self.lbl_quality_score.setText(f"质检分：{result['score']}/100")
        
        if result['passed']:
            self.lbl_quality_score.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_quality_score.setStyleSheet("color: red; font-weight: bold;")
        
        # 显示问题清单
        msg = QMessageBox(self)
        msg.setWindowTitle("质检报告")
        msg.setText(report)
        msg.exec()
    
    def open_find_replace(self):
        """打开查找替换"""
        # 简化实现，可以扩展为独立对话框
        QMessageBox.information(self, "提示", "查找替换功能开发中...")
    
    def insert_template(self):
        """插入模板"""
        templates = {
            "战斗场景": "【感官细节】空气中弥漫着______的味道。\n【动作描写】他______，紧接着______。\n【心理活动】这一刻，他想起______。",
            "对话开场": "\"______。\"______说道，目光______。\n\n\"______。\"对方______，______。",
            "环境描写": "______的阳光下，______显得格外______。空气中飘着______的气息，远处传来______的声音。",
            "悬念结尾": "就在此时，______。\n\n他猛然回头，只见______。",
        }
        
        template, ok = QComboBox.getItem(self, "选择模板", "插入写作模板：", 
                                         list(templates.keys()), 0, False)
        if ok and template:
            cursor = self.editor.textCursor()
            cursor.insertText("\n" + templates[template] + "\n")


# ========== AI 后台任务类 ==========

class AIContinueWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, llm_client, prompt):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt, max_tokens=800)
        self.finished.emit(result)


class AIPolishWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, llm_client, prompt):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt, max_tokens=600)
        self.finished.emit(result)


class AIExpandWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, llm_client, prompt):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt, max_tokens=800)
        self.finished.emit(result)


class AIDialogueWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, llm_client, prompt):
        super().__init__()
        self.llm_client = llm_client
        self.prompt = prompt
    def run(self):
        result = self.llm_client.generate_with_retry(self.prompt, max_tokens=800)
        self.finished.emit(result)
