# 🖋️ 网文 AI 辅写系统 - Windows 版

基于《网文 AI 辅写工程化方案》开发的桌面应用，帮助作者高效创作网文。

## 📦 Windows 安装方式

### 方式一：源码运行（推荐开发测试用）

1. **安装 Python 3.8+**
   - 下载地址：https://www.python.org/downloads/
   - ⚠️ 安装时勾选 "Add Python to PATH"

2. **解压项目文件**
   - 将 `web_novel_writer` 文件夹放到任意位置（如 `D:\NovelWriter`）

3. **运行安装脚本**
   - 双击 `install.bat`
   - 等待依赖安装完成

4. **配置 API Key**
   - 用记事本打开 `config.yaml`
   - 填入阿里云通义 API 密钥

5. **启动应用**
   - 双击 `start.bat`

---

### 方式二：打包成 EXE（推荐分发给他人）

1. **完成方式一的步骤 1-3**

2. **运行打包脚本**
   - 双击 `build.bat`
   - 等待打包完成（约 1-2 分钟）

3. **获取可执行文件**
   - 生成的 exe 在 `dist\网文 AI 辅写系统.exe`
   - 将 `config.yaml` 复制到 exe 同目录

4. **创建快捷方式**
   - 右键 exe → 发送到 → 桌面快捷方式

---

## ⚙️ 配置说明

### 获取阿里云 API Key

1. 访问 https://dashscope.console.aliyun.com/
2. 登录/注册阿里云账号
3. 进入 "API-KEY 管理"
4. 创建新 Key 并复制

### 编辑 config.yaml

```yaml
aliyun:
  api_key: "sk-xxxxxxxxxxxx"  # 填入你的 Key
  secret_key: ""               # 可选
  model: "qwen-plus"           # 可选：qwen-turbo, qwen-plus, qwen-max
```

---

## 📁 项目结构

```
web_novel_writer/
├── main.py              # 主程序入口
├── config.yaml          # 配置文件
├── install.bat          # 一键安装脚本
├── start.bat            # 启动脚本
├── build.bat            # 打包成 EXE 脚本
├── novel_writer.spec    # PyInstaller 配置
├── README.md            # 说明文档
├── src/
│   ├── main_window.py   # 主界面
│   ├── llm_client.py    # API 客户端
│   └── markdown_manager.py  # 文件管理
└── requirements.txt     # Python 依赖
```

---

## 🎯 使用流程

```
1. 双击 start.bat 启动应用
   ↓
2. 点击"新建项目"选择保存位置
   ↓
3. 📜 风格宪法：上传样章或手动编写
   ↓
4. 📝 章纲编写：填写六要素，AI 辅助填充
   ↓
5. 🌍 世界状态：每章更新状态表
   ↓
6. 生成的内容自动保存在项目 data/ 目录
```

---

## ❓ 常见问题

### Q: 双击 bat 文件闪退
A: 右键 → 以管理员身份运行，或打开 cmd 拖入文件执行

### Q: 依赖安装失败
A: 检查网络连接，或手动执行：
```
pip install PyQt6 qianfan PyYAML markdown requests
```

### Q: 提示找不到 API Key
A: 确保 config.yaml 和 main.py 在同一目录，且 api_key 已填写

### Q: 想要修改默认模型
A: 编辑 config.yaml 中的 `model` 字段：
- `qwen-turbo` - 速度快，成本低
- `qwen-plus` - 平衡（推荐）
- `qwen-max` - 效果最好，成本高

---

## 📝 待实现功能

- [ ] 章节正文生成引擎
- [ ] 质检层（禁用词检测、相似度检查）
- [ ] 项目进度看板
- [ ] 批量导出为 Word/PDF

---

## 📞 技术支持

如遇问题，请检查：
1. Python 版本是否 3.8+
2. 网络连接是否正常
3. API Key 是否有效
4. 控制台错误信息（可运行 `python main.py` 查看详细错误）
