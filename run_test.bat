@echo off
chcp 65001 >nul
echo ========================================
echo   网文 AI 辅写系统 - 测试运行
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查 Python 环境...
python --version

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo [2/3] 创建虚拟环境...
    python -m venv venv
) else (
    echo [2/3] 虚拟环境已存在
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [3/3] 安装依赖...
pip install -r requirements.txt -q

REM 运行应用
echo.
echo ========================================
echo   启动应用...
echo ========================================
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用启动失败，请检查：
    echo 1. config.yaml 中的 API Key 是否正确
    echo 2. 是否已安装 Python 3.8+
    echo 3. 查看上方错误信息
    echo.
    pause
)

call venv\Scripts\deactivate.bat
