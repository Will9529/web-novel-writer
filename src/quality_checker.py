"""
质检层 - 三道检查机制
"""
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher
from datetime import datetime


class QualityChecker:
    """章节质检器"""
    
    def __init__(self, md_manager, banned_words: List[str] = None):
        self.md_manager = md_manager
        self.banned_words = banned_words or [
            '突然', '瞬间', '顿时', '不禁', '只见'
        ]
    
    def check_all(self, chapter_num: int, content: str) -> Dict[str, Any]:
        """
        执行全部质检
        
        Returns:
            {
                'passed': bool,
                'issues': List[Dict],
                'score': int  # 0-100
            }
        """
        issues = []
        score = 100
        
        # 1. 禁用词检查
        banned_result = self.check_banned_words(content)
        if banned_result['hits']:
            issues.append({
                'type': '禁用词',
                'severity': 'high',
                'message': f"发现 {len(banned_result['hits'])} 个禁用词",
                'details': banned_result['hits']
            })
            score -= 20
        
        # 2. 结构相似度检查
        similarity_result = self.check_structure_similarity(chapter_num, content)
        if similarity_result['high_similarity']:
            issues.append({
                'type': '结构重复',
                'severity': 'medium',
                'message': f"与第{similarity_result['similar_chapter']}章相似度达 {similarity_result['similarity']:.0%}",
                'details': similarity_result
            })
            score -= 15
        
        # 3. 情节债务核查
        debt_result = self.check_plot_debts(chapter_num, content)
        if debt_result['unfulfilled']:
            issues.append({
                'type': '情节债务',
                'severity': 'high',
                'message': f"有 {len(debt_result['unfulfilled'])} 个应填未填的伏笔",
                'details': debt_result['unfulfilled']
            })
            score -= 20
        
        # 4. 字数检查
        word_count = len(content)
        if word_count < 2500:
            issues.append({
                'type': '字数不足',
                'severity': 'medium',
                'message': f"当前{word_count}字，要求 2500-3000 字",
                'details': {'current': word_count, 'required': 2500}
            })
            score -= 10
        elif word_count > 3500:
            issues.append({
                'type': '字数超限',
                'severity': 'low',
                'message': f"当前{word_count}字，建议控制在 3000 字以内",
                'details': {'current': word_count, 'max_recommended': 3500}
            })
            score -= 5
        
        # 5. 格式检查
        format_result = self.check_format(content)
        if format_result['issues']:
            issues.append({
                'type': '格式问题',
                'severity': 'low',
                'message': f"发现 {len(format_result['issues'])} 个格式问题",
                'details': format_result['issues']
            })
            score -= 5
        
        return {
            'passed': score >= 70,
            'issues': issues,
            'score': max(0, score),
            'word_count': word_count,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def check_banned_words(self, content: str) -> Dict[str, Any]:
        """检查禁用词"""
        hits = []
        for word in self.banned_words:
            count = content.count(word)
            if count > 0:
                # 找到出现位置
                positions = []
                start = 0
                while True:
                    pos = content.find(word, start)
                    if pos == -1:
                        break
                    # 提取上下文
                    context_start = max(0, pos - 20)
                    context_end = min(len(content), pos + len(word) + 20)
                    positions.append({
                        'position': pos,
                        'context': content[context_start:context_end]
                    })
                    start = pos + 1
                
                hits.append({
                    'word': word,
                    'count': count,
                    'positions': positions[:5]  # 最多显示 5 个位置
                })
        
        return {
            'hits': hits,
            'total_count': sum(h['count'] for h in hits)
        }
    
    def check_structure_similarity(self, chapter_num: int, content: str, threshold: float = 0.6) -> Dict[str, Any]:
        """检查与最近章节的结构相似度"""
        recent_chapters = []
        
        # 获取最近 5 章
        for i in range(chapter_num - 1, max(1, chapter_num - 6), -1):
            prev_content = self.md_manager.load_chapter(i)
            if prev_content:
                recent_chapters.append((i, prev_content))
        
        if not recent_chapters:
            return {'high_similarity': False, 'similar_chapter': None, 'similarity': 0}
        
        # 提取结构序列（段落长度序列）
        def extract_structure(text):
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            return [len(p) for p in paragraphs[:20]]  # 取前 20 段
        
        current_structure = extract_structure(content)
        
        max_similarity = 0
        most_similar_chapter = None
        
        for chap_num, chap_content in recent_chapters:
            prev_structure = extract_structure(chap_content)
            
            # 计算相似度
            similarity = self._compare_structures(current_structure, prev_structure)
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_chapter = chap_num
        
        return {
            'high_similarity': max_similarity > threshold,
            'similar_chapter': most_similar_chapter,
            'similarity': max_similarity,
            'threshold': threshold
        }
    
    def _compare_structures(self, struct1: List[int], struct2: List[int]) -> float:
        """比较两个结构序列的相似度"""
        if not struct1 or not struct2:
            return 0
        
        # 归一化
        max_len = max(max(struct1), max(struct2), 1)
        norm1 = [x / max_len for x in struct1]
        norm2 = [x / max_len for x in struct2]
        
        # 补齐长度
        min_len = min(len(norm1), len(norm2))
        norm1 = norm1[:min_len]
        norm2 = norm2[:min_len]
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(norm1, norm2))
        magnitude1 = sum(a * a for a in norm1) ** 0.5
        magnitude2 = sum(b * b for b in norm2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def check_plot_debts(self, chapter_num: int, content: str) -> Dict[str, Any]:
        """检查情节债务（应填的伏笔）"""
        world_state = self.md_manager.load_latest_world_state()
        if not world_state:
            return {'unfulfilled': [], 'fulfilled': []}
        
        # 简单解析情节债务（可以改进为更智能的解析）
        unfulfilled = []
        fulfilled = []
        
        content_lower = content.lower()
        
        # 从世界状态中提取债务（简化实现）
        lines = world_state['content'].split('\n')
        in_debt_section = False
        
        for line in lines:
            if '情节债务' in line or '伏笔' in line:
                in_debt_section = True
                continue
            if in_debt_section and line.startswith('## '):
                break
            if in_debt_section and line.strip().startswith('- 第'):
                # 解析债务项
                debt = line.strip()[2:]  # 去掉 "- "
                # 检查是否在本章被提及
                if any(keyword in content_lower for keyword in self._extract_keywords(debt)):
                    fulfilled.append(debt)
                else:
                    # 检查是否应该在本章揭示
                    if self._should_fulfill_in_chapter(debt, chapter_num):
                        unfulfilled.append(debt)
        
        return {
            'unfulfilled': unfulfilled,
            'fulfilled': fulfilled
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简化实现：提取中文字符
        keywords = []
        current = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                current.append(char)
            else:
                if current:
                    keywords.append(''.join(current))
                    current = []
        if current:
            keywords.append(''.join(current))
        return [k for k in keywords if len(k) >= 2]
    
    def _should_fulfill_in_chapter(self, debt: str, chapter_num: int) -> bool:
        """判断债务是否应该在本章揭示"""
        # 简化实现：检查文本中是否有章节提示
        if f'第{chapter_num}章' in debt or f'第{chapter_num}章' in debt:
            return True
        return False
    
    def check_format(self, content: str) -> Dict[str, Any]:
        """检查格式问题"""
        issues = []
        
        # 检查过长的段落
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if len(para) > 500:
                issues.append(f"第{i+1}段过长 ({len(para)}字)")
        
        # 检查连续对话轮数
        dialogue_count = 0
        max_dialogue = 0
        for line in content.split('\n'):
            if line.startswith('"') or line.startswith('"') or line.startswith('：'):
                dialogue_count += 1
                max_dialogue = max(max_dialogue, dialogue_count)
            else:
                dialogue_count = 0
        
        if max_dialogue > 6:
            issues.append(f"发现连续{max_dialogue}轮对话，建议插入描写")
        
        # 检查结尾
        last_sentence = content.strip()[-50:] if len(content) > 50 else content.strip()
        if last_sentence.endswith('。') or last_sentence.endswith('！'):
            # 可能是总结句
            if '总之' in last_sentence or '终于' in last_sentence:
                issues.append("结尾可能是总结句，建议改为悬念句")
        
        return {'issues': issues}
    
    def generate_report(self, check_result: Dict[str, Any]) -> str:
        """生成质检报告"""
        lines = []
        lines.append(f"# 质检报告")
        lines.append(f"生成时间：{check_result.get('timestamp', '未知')}")
        lines.append(f"字数：{check_result.get('word_count', 0)}")
        lines.append(f"质检得分：{check_result.get('score', 0)}/100")
        lines.append(f"质检结果：{'✅ 通过' if check_result.get('passed') else '❌ 需修改'}")
        lines.append("")
        
        issues = check_result.get('issues', [])
        if issues:
            lines.append("## 问题清单")
            for i, issue in enumerate(issues, 1):
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                lines.append(f"{i}. {severity_icon} [{issue['type']}] {issue['message']}")
        else:
            lines.append("## ✅ 无问题")
        
        return '\n'.join(lines)


class QualityCheckWorker(QThread):
    """质检后台任务"""
    finished = pyqtSignal(dict)
    
    def __init__(self, checker: QualityChecker, chapter_num: int, content: str):
        super().__init__()
        self.checker = checker
        self.chapter_num = chapter_num
        self.content = content
    
    def run(self):
        result = self.checker.check_all(self.chapter_num, self.content)
        self.finished.emit(result)
