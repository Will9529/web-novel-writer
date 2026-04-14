"""
项目进度看板 - 统计和可视化
"""
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


class ProjectDashboard:
    """项目进度看板"""
    
    def __init__(self, md_manager):
        self.md_manager = md_manager
    
    def get_overview(self) -> Dict[str, Any]:
        """获取项目概览"""
        stats = self.md_manager.get_project_stats()
        
        # 计算总字数
        total_words = self._count_total_words()
        
        # 获取章节列表
        chapters = self._get_chapter_list()
        
        # 获取情节债务统计
        debt_stats = self._get_debt_stats()
        
        return {
            'total_chapters': stats['total_chapters'],
            'total_outlines': stats['total_outlines'],
            'total_world_states': stats['total_world_states'],
            'has_style_constitution': stats['has_style_constitution'],
            'total_words': total_words,
            'estimated_total_words': stats['total_chapters'] * 2750,
            'chapters': chapters,
            'debt_stats': debt_stats,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _count_total_words(self) -> int:
        """统计总字数"""
        total = 0
        chapters_path = self.md_manager.data_path / "chapters"
        
        if not chapters_path.exists():
            return 0
        
        for file in chapters_path.glob("*.md"):
            content = file.read_text(encoding='utf-8')
            # 去除 markdown 标记
            text = content.replace('#', '').replace('*', '').strip()
            total += len(text)
        
        return total
    
    def _get_chapter_list(self) -> List[Dict[str, Any]]:
        """获取章节列表"""
        chapters = []
        chapters_path = self.md_manager.data_path / "chapters"
        outlines_path = self.md_manager.data_path / "outlines"
        
        if not chapters_path.exists():
            return chapters
        
        for file in sorted(chapters_path.glob("*.md")):
            chapter_num = self._extract_chapter_number(file.name)
            content = file.read_text(encoding='utf-8')
            
            # 提取标题
            title = "无标题"
            for line in content.split('\n')[:5]:
                if line.startswith('# 第') and '章' in line:
                    if '章 ' in line:
                        title = line.split('章 ')[1].strip()
                    break
            
            # 检查是否有章纲
            has_outline = (outlines_path / f"chapter_{chapter_num:03d}_outline.md").exists()
            
            chapters.append({
                'number': chapter_num,
                'title': title,
                'word_count': len(content),
                'has_outline': has_outline,
                'file': str(file)
            })
        
        return chapters
    
    def _extract_chapter_number(self, filename: str) -> int:
        """从文件名提取章节号"""
        # 格式：chapter_001.md
        try:
            num_str = filename.replace('chapter_', '').replace('.md', '')
            return int(num_str)
        except:
            return 0
    
    def _get_debt_stats(self) -> Dict[str, Any]:
        """获取情节债务统计"""
        world_state = self.md_manager.load_latest_world_state()
        
        if not world_state:
            return {'total': 0, 'fulfilled': 0, 'pending': 0}
        
        content = world_state['content']
        
        # 简单统计
        debt_lines = [l for l in content.split('\n') if l.strip().startswith('- 第') and ('→' in l or '伏笔' in l)]
        
        return {
            'total': len(debt_lines),
            'fulfilled': 0,  # 需要更复杂的逻辑来统计
            'pending': len(debt_lines)
        }
    
    def get_writing_pace(self) -> Dict[str, Any]:
        """获取写作进度分析"""
        chapters = self._get_chapter_list()
        
        if not chapters:
            return {'status': 'no_data'}
        
        total_chapters = len(chapters)
        total_words = sum(c['word_count'] for c in chapters)
        avg_words = total_words / total_chapters if total_chapters > 0 else 0
        
        # 完成率
        outlines_completed = sum(1 for c in chapters if c['has_outline'])
        outline_rate = outlines_completed / total_chapters if total_chapters > 0 else 0
        
        return {
            'status': 'active',
            'total_chapters': total_chapters,
            'total_words': total_words,
            'avg_words_per_chapter': round(avg_words, 0),
            'outline_completion_rate': round(outline_rate * 100, 1),
            'target_words_per_chapter': 2750,
            'word_count_health': 'good' if 2500 <= avg_words <= 3000 else 'warning'
        }
    
    def generate_report(self) -> str:
        """生成项目进度报告"""
        overview = self.get_overview()
        pace = self.writing_pace = self.get_writing_pace()
        
        lines = []
        lines.append("# 📊 项目进度报告")
        lines.append(f"生成时间：{overview['last_updated']}")
        lines.append("")
        
        lines.append("## 核心数据")
        lines.append(f"- 已完成章节：{overview['total_chapters']} 章")
        lines.append(f"- 总字数：{overview['total_words']:,} 字")
        lines.append(f"- 平均每章：{pace.get('avg_words_per_chapter', 0):.0f} 字")
        lines.append(f"- 章纲完成率：{pace.get('outline_completion_rate', 0):.1f}%")
        lines.append("")
        
        lines.append("## 项目状态")
        status_items = [
            ("风格宪法", "✅" if overview['has_style_constitution'] else "❌"),
            ("世界状态", "✅" if overview['total_world_states'] > 0 else "❌"),
            ("字数健康度", "✅" if pace.get('word_count_health') == 'good' else "⚠️"),
        ]
        for name, icon in status_items:
            lines.append(f"- {name}: {icon}")
        lines.append("")
        
        lines.append("## 情节债务")
        debt = overview['debt_stats']
        lines.append(f"- 总伏笔数：{debt['total']}")
        lines.append(f"- 待填坑：{debt['pending']}")
        lines.append("")
        
        if overview['chapters']:
            lines.append("## 章节列表")
            for chap in overview['chapters'][-10:]:  # 最近 10 章
                outline_icon = "📝" if chap['has_outline'] else ""
                lines.append(f"- 第{chap['number']}章 {chap['title']} {outline_icon} ({chap['word_count']}字)")
        
        return '\n'.join(lines)
