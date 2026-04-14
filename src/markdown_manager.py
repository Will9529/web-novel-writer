"""
Markdown 文件管理模块
负责项目文件的读写和管理
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class MarkdownManager:
    """Markdown 文件管理器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.data_path = self.project_path / "data"
        self.templates_path = self.project_path / "templates"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        # 子目录
        (self.data_path / "style_constitution").mkdir(exist_ok=True)
        (self.data_path / "outlines").mkdir(parents=True, exist_ok=True)
        (self.data_path / "world_state").mkdir(exist_ok=True)
        (self.data_path / "chapters").mkdir(parents=True, exist_ok=True)
    
    # ========== 风格宪法 ==========
    def save_style_constitution(self, content: str, version: str = "v1") -> str:
        """保存风格宪法"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"style_constitution_{version}_{timestamp}.md"
        filepath = self.data_path / "style_constitution" / filename
        
        full_content = f"""# 作者风格宪法 {version}

> 创建时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

---

{content}
"""
        filepath.write_text(full_content, encoding='utf-8')
        return str(filepath)
    
    def load_latest_style_constitution(self) -> Optional[str]:
        """加载最新版风格宪法"""
        sc_path = self.data_path / "style_constitution"
        if not sc_path.exists():
            return None
        
        files = sorted(sc_path.glob("*.md"), reverse=True)
        if files:
            return files[0].read_text(encoding='utf-8')
        return None
    
    # ========== 章纲管理 ==========
    def save_chapter_outline(self, chapter_num: int, outline: Dict[str, Any]) -> str:
        """保存章纲"""
        filename = f"chapter_{chapter_num:03d}_outline.md"
        filepath = self.data_path / "outlines" / filename
        
        content = f"""# 第{chapter_num}章：{outline.get('title', '未命名')}

## 基本信息
- **场景**: {outline.get('scene', '')}
- **人物在场**: {outline.get('characters', '')}
- **核心事件**: {outline.get('core_event', '')}

## 结构设计
- **开场钩子**: {outline.get('opening_hook', '')}
- **结尾钩子**: {outline.get('ending_hook', '')}

## 前后呼应
- **承上**: {outline.get('connect_previous', '')}
- **启下**: {outline.get('connect_next', '')}

## 限制条件
- **禁止出现**: {outline.get('forbidden', '')}

---
*创建时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)
    
    def load_chapter_outline(self, chapter_num: int) -> Optional[Dict[str, Any]]:
        """加载章纲"""
        filename = f"chapter_{chapter_num:03d}_outline.md"
        filepath = self.data_path / "outlines" / filename
        
        if not filepath.exists():
            return None
        
        content = filepath.read_text(encoding='utf-8')
        # 简单解析（可以扩展为更完善的 markdown 解析）
        return {"raw": content, "chapter": chapter_num}
    
    # ========== 世界状态管理 ==========
    def save_world_state(self, state: Dict[str, Any], chapter_num: int) -> str:
        """保存世界状态"""
        filename = f"world_state_ch{chapter_num:03d}.md"
        filepath = self.data_path / "world_state" / filename
        
        content = f"""# 世界状态表（更新至第{chapter_num}章）

> 更新时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 人物状态

### 主角
{state.get('protagonist', '- 暂无信息')}

### 主要配角
{state.get('supporting_chars', '- 暂无信息')}

### 反派
{state.get('antagonist', '- 暂无信息')}

---

## 情节债务（已埋未填的伏笔）

{state.get('plot_debts', '- 暂无未填伏笔')}

---

## 已用情节模板

{state.get('used_templates', '- 暂无记录')}

---

## 本章状态变更 Diff

{state.get('changes_diff', '- 无变更')}
"""
        filepath.write_text(content, encoding='utf-8')
        return str(filepath)
    
    def load_latest_world_state(self) -> Optional[Dict[str, Any]]:
        """加载最新世界状态"""
        ws_path = self.data_path / "world_state"
        if not ws_path.exists():
            return None
        
        files = sorted(ws_path.glob("*.md"), reverse=True)
        if files:
            content = files[0].read_text(encoding='utf-8')
            return {"file": str(files[0]), "content": content}
        return None
    
    # ========== 章节正文管理 ==========
    def save_chapter(self, chapter_num: int, content: str, title: str = "") -> str:
        """保存章节正文"""
        filename = f"chapter_{chapter_num:03d}.md"
        filepath = self.data_path / "chapters" / filename
        
        full_content = f"""# 第{chapter_num}章 {title}

{content}

---
*生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
        filepath.write_text(full_content, encoding='utf-8')
        return str(filepath)
    
    def load_chapter(self, chapter_num: int) -> Optional[str]:
        """加载章节正文"""
        filename = f"chapter_{chapter_num:03d}.md"
        filepath = self.data_path / "chapters" / filename
        
        if not filepath.exists():
            return None
        return filepath.read_text(encoding='utf-8')
    
    # ========== 项目信息 ==========
    def get_project_stats(self) -> Dict[str, Any]:
        """获取项目统计信息"""
        chapters = list((self.data_path / "chapters").glob("*.md"))
        outlines = list((self.data_path / "outlines").glob("*.md"))
        world_states = list((self.data_path / "world_state").glob("*.md"))
        
        return {
            "total_chapters": len(chapters),
            "total_outlines": len(outlines),
            "total_world_states": len(world_states),
            "has_style_constitution": len(list((self.data_path / "style_constitution").glob("*.md"))) > 0
        }
