# 🖋️ 网文 AI 辅写系统

基于《网文 AI 辅写工程化方案》开发的桌面应用，帮助作者高效创作网文。

## 核心功能

| 模块 | 功能描述 |
|------|----------|
| 📜 风格宪法 | 定义写作风格，支持从样章自动提炼 |
| 📝 章纲编写 | 结构化六要素章纲，AI 辅助填充 |
| 🌍 世界状态 | 追踪人物状态、情节债务、已用模板 |

## 快速开始

### 1. 安装依赖

```bash
cd web_novel_writer
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.yaml`，填入阿里云通义 API 密钥：

```yaml
aliyun:
  api_key: "your-api-key-here"
  secret_key: "your-secret-key-here"
  model: "qwen-plus"
```

### 3. 运行应用

```bash
python main.py
```

## 项目结构

```
web_novel_writer/
├── main.py              # 主入口
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖
├── src/
│   ├── main_window.py   # 主界面（三个核心模块）
│   ├── llm_client.py    # 阿里云 API 客户端
│   └── markdown_manager.py  # Markdown 文件管理
├── data/                # 项目数据（运行时创建）
│   ├── style_constitution/
│   ├── outlines/
│   ├── world_state/
│   └── chapters/
└── templates/           # 模板文件
```

## 使用流程

```
1. 新建/选择项目
   ↓
2. 建立风格宪法（可上传样章自动提炼）
   ↓
3. 编写章纲（六要素结构化）
   ↓
4. 维护世界状态（每章更新）
   ↓
5. 生成章节正文（待实现）
   ↓
6. 质检审核（待实现）
```

## 技术方案

- **GUI 框架**: PyQt6
- **LLM API**: 阿里云通义千问
- **数据存储**: Markdown 文件（每章一个 commit，可回滚）
- **跨平台**: Windows / macOS / Linux

## 待实现功能

- [ ] 章节正文生成引擎
- [ ] 质检层（禁用词检测、相似度检查）
- [ ] 项目进度看板
- [ ] 批量导出/导入

## 许可证

MIT
