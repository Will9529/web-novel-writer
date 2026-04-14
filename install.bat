@echo off
chcp 65001 >nul
echo ========================================
echo   网文 AI 辅写系统 - Windows 安装脚本
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查 Python 环境...
python --version

:: 创建虚拟环境（可选，更安全）
echo.
echo [2/3] 安装依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo [3/3] 创建启动快捷方式...

:: 创建启动脚本
echo @echo off > start.bat
echo chcp 65001 ^>nul >> start.bat
echo python main.py %%* >> start.bat

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 编辑 config.yaml 填写阿里云 API Key
echo   2. 双击 start.bat 启动应用
echo.
pause
