"""
章节生成引擎 - 五层 Prompt 组装生成
"""
from typing import Optional, Dict, Any
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal


class ChapterGenerator:
    """章节正文生成引擎"""
    
    def __init__(self, llm_client, md_manager):
        self.llm_client = llm_client
        self.md_manager = md_manager
    
    def build_prompt(self, chapter_num: int) -> tuple[str, str]:
        """
        组装五层 Prompt
        
        Returns:
            (system_prompt, user_prompt)
        """
        # 1. 加载风格宪法
        style_constitution = self.md_manager.load_latest_style_constitution()
        if not style_constitution:
            style_constitution = "暂无风格宪法，请按通用网文风格生成。"
        
        # 2. 加载世界状态
        world_state = self.md_manager.load_latest_world_state()
        world_state_summary = world_state['content'] if world_state else "暂无世界状态记录。"
        
        # 3. 加载上章末尾
        prev_chapter = self.md_manager.load_chapter(chapter_num - 1)
        prev_ending = ""
        if prev_chapter:
            # 提取最后 200 字
            lines = prev_chapter.split('\n')
            prev_ending = '\n'.join(lines[-5:]) if len(lines) > 5 else prev_chapter[-300:]
        else:
            prev_ending = "这是第一章，无需承接上章。"
        
        # 4. 加载章纲
        outline = self.md_manager.load_chapter_outline(chapter_num)
        outline_text = outline['raw'] if outline else "暂无章纲，请自由发挥。"
        
        # 5. 生成指令
        generation_instruction = self._build_generation_instruction(chapter_num, outline)
        
        # 组装系统提示词
        system_prompt = f"""你是一名专业的网文作家助手。请严格按照以下要求生成内容：

{style_constitution}

## 生成规则
1. 必须遵循风格宪法中的所有要求
2. 必须呼应世界状态中的人物设定和情节债务
3. 必须按照章纲的六要素结构生成
4. 字数控制在 2500-3000 字
5. 不得出现禁用词表中的词汇"""

        # 组装用户提示词
        user_prompt = f"""## 任务：生成第{chapter_num}章正文

### 世界状态摘要
{world_state_summary}

### 上章末尾
{prev_ending}

### 本章章纲
{outline_text}

### 生成指令
{generation_instruction}

---

请开始生成第{chapter_num}章正文："""
        
        return system_prompt, user_prompt
    
    def _build_generation_instruction(self, chapter_num: int, outline: Optional[Dict]) -> str:
        """构建生成指令"""
        if not outline:
            return "按通用网文风格生成，注意节奏和钩子。"
        
        # 从章纲中提取特殊要求
        instructions = []
        
        # 检查是否有禁止出现的内容
        raw = outline.get('raw', '')
        if '禁止出现' in raw:
            instructions.append("特别注意：本章禁止出现章纲中列出的内容")
        
        # 检查承上启下要求
        if '承上' in raw:
            instructions.append("必须呼应上章指定的细节")
        
        if '启下' in raw:
            instructions.append("必须为下章埋下指定的伏笔")
        
        # 默认指令
        instructions.extend([
            "开场不得以纯景物描写开头（除非章纲特别要求）",
            "对话不超过连续 4 轮，插入动作或心理描写打断",
            "结尾最后一句必须是悬念句或情感落点，不得是总结句",
            "字数控制在 2500-3000 字"
        ])
        
        return '\n'.join([f"{i+1}. {inst}" for i, inst in enumerate(instructions)])
    
    def generate_chapter(self, chapter_num: int, callback=None) -> tuple[bool, str]:
        """
        生成章节正文
        
        Args:
            chapter_num: 章节号
            callback: 进度回调函数
        
        Returns:
            (success, content_or_error)
        """
        if callback:
            callback("正在组装 Prompt...")
        
        system_prompt, user_prompt = self.build_prompt(chapter_num)
        
        if callback:
            callback("正在调用 AI 生成...")
        
        # 调用 LLM 生成
        result = self.llm_client.generate_with_retry(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4000,
            max_retries=3
        )
        
        if result.startswith("["):
            return False, result
        
        # 提取正文（去除可能的额外说明）
        content = self._extract_content(result)
        
        if callback:
            callback("生成完成！")
        
        return True, content
    
    def _extract_content(self, raw_text: str) -> str:
        """从原始文本中提取正文章节"""
        # 尝试提取 # 第 X 章 之后的内容
        lines = raw_text.split('\n')
        content_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('# 第') and '章' in line:
                in_content = True
                continue
            if in_content:
                content_lines.append(line)
        
        if content_lines:
            return '\n'.join(content_lines).strip()
        
        # 如果没有找到标记，返回原文（去除首尾空白）
        return raw_text.strip()
    
    def save_chapter(self, chapter_num: int, content: str, title: str = "") -> str:
        """保存生成的章节"""
        if not title:
            # 尝试从内容提取标题
            outline = self.md_manager.load_chapter_outline(chapter_num)
            if outline:
                # 简单解析标题
                for line in outline.get('raw', '').split('\n'):
                    if line.startswith('# 第') and '章：' in line:
                        title = line.split('章：')[1].strip()
                        break
        
        filepath = self.md_manager.save_chapter(chapter_num, content, title)
        return filepath


class GenerationWorker(QThread):
    """章节生成后台任务"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, generator: ChapterGenerator, chapter_num: int):
        super().__init__()
        self.generator = generator
        self.chapter_num = chapter_num
    
    def run(self):
        def callback(msg):
            self.progress.emit(msg)
        
        success, result = self.generator.generate_chapter(self.chapter_num, callback)
        self.finished.emit(success, result)
