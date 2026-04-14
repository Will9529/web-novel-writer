# 🖋️ 网文 AI 辅写系统 v1.0 发布说明

**发布日期**: 2026-04-14  
**版本**: v1.0.0  
**状态**: ✅ 初始发布

---

## 📦 下载方式

### 方式一：GitHub 下载（推荐）

访问仓库页面：https://github.com/Will9529/web-novel-writer

```bash
# 克隆仓库
git clone https://github.com/Will9529/web-novel-writer.git
cd web-novel-writer
```

### 方式二：直接下载 ZIP

访问：https://github.com/Will9529/web-novel-writer/archive/refs/heads/main.zip

---

## 🚀 快速开始

### 1. 测试运行

**Windows 用户**：双击 `run_test.bat`

脚本会自动：
- 检查 Python 环境
- 创建虚拟环境
- 安装依赖
- 启动应用

### 2. 配置 API Key

编辑 `config.yaml`，填入阿里云通义 API Key：

```yaml
aliyun:
  api_key: "sk-你的 API Key"
  model: "qwen-plus"
```

获取 API Key：https://dashscope.console.aliyun.com/

### 3. 打包为 EXE

**Windows 用户**：双击 `build.bat`

打包完成后，可执行文件位于：
```
dist/网文 AI 辅写系统/网文 AI 辅写系统.exe
```

---

## ✨ 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 📜 风格宪法 | 定义写作风格，支持样章自动提炼 | ✅ |
| 📝 章纲编写 | 结构化六要素章纲，AI 辅助填充 | ✅ |
| 🌍 世界状态 | 追踪人物状态、情节债务、已用模板 | ✅ |
| ✏️ 写作助手 | 智能编辑器，AI 续写 | ✅ |
| 📖 章节生成 | 基于章纲生成章节正文 | ✅ |
| 🔍 质检中心 | 禁用词检测、相似度检查 | ✅ |
| 📊 项目看板 | 项目进度、统计信息 | ✅ |

---

## 📁 项目结构

```
web-novel-writer/
├── main.py                    # 主入口
├── config.yaml                # 配置文件
├── requirements.txt           # Python 依赖
├── run_test.bat               # 一键测试脚本
├── build.bat                  # 一键打包脚本
├── web_novel_writer.spec      # PyInstaller 配置
├── src/                       # 源代码
│   ├── app.py                 # 主窗口
│   ├── main_window.py         # 界面逻辑
│   ├── llm_client.py          # 阿里云 API 客户端
│   ├── markdown_manager.py    # Markdown 管理
│   ├── writing_assistant.py   # 写作助手
│   ├── chapter_generator.py   # 章节生成
│   ├── quality_checker.py     # 质检中心
│   └── project_dashboard.py   # 项目看板
├── templates/                 # 模板文件
└── docs/                      # 文档
    ├── 使用说明完整版.md
    ├── 功能清单.md
    └── 测试运行指南.md
```

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| GUI 框架 | PyQt6 6.4+ |
| LLM API | 阿里云通义千问 (qwen-plus) |
| 数据存储 | Markdown 文件 |
| 打包工具 | PyInstaller |
| 支持平台 | Windows 10/11 |

---

## 📋 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 |
| Python 版本 | 3.8 或更高 |
| 内存 | 至少 2GB 可用 |
| 网络 | 需要访问阿里云 API |
| 磁盘空间 | 约 500MB（含虚拟环境） |

---

## 🐛 已知问题

- [ ] 高分屏下界面可能模糊（已内置 DPI 感知，大部分设备正常）
- [ ] 首次启动较慢（PyInstaller 打包特性）
- [ ] 需要网络连接才能使用 AI 功能

---

## 📝 更新日志

### v1.0.0 (2026-04-14)

**新增功能**
- ✅ 风格宪法编辑器
- ✅ 章纲结构化编写
- ✅ 世界状态追踪
- ✅ 写作助手（智能编辑器）
- ✅ 章节生成引擎
- ✅ 质检中心
- ✅ 项目进度看板

**技术实现**
- ✅ PyQt6 界面框架
- ✅ 阿里云通义 API 集成
- ✅ Markdown 文件存储
- ✅ PyInstaller 打包

**文档**
- ✅ 完整使用说明
- ✅ 测试运行指南
- ✅ 功能清单
- ✅ 一键测试/打包脚本

---

## 📞 技术支持

**遇到问题？**

1. 查看 `使用说明完整版.md`
2. 查看 `测试运行指南.md`
3. GitHub Issues: https://github.com/Will9529/web-novel-writer/issues

**反馈建议**

欢迎提交 Issue 或 Pull Request！

---

## 📄 许可证

MIT License

---

## 👨‍💻 开发者

**Will9529**
- GitHub: https://github.com/Will9529
- 项目：https://github.com/Will9529/web-novel-writer

---

**感谢使用！🎉**
