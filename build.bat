@echo off
chcp 65001 >nul
echo ========================================
echo   网文 AI 辅写系统 - 打包工具
echo   Build Tool for Web Novel AI Writer
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
python --version

REM 激活虚拟环境
if exist "venv" (
    echo [2/4] 使用现有虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [2/4] 创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM 安装打包依赖
echo [3/4] 安装 PyInstaller...
pip install pyinstaller -q

REM 清理旧构建
echo [4/4] 清理旧构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 开始打包
echo.
echo ========================================
echo   开始打包...
echo   这可能需要 1-3 分钟
echo ========================================
echo.

pyinstaller --clean web_novel_writer.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    echo 请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 可执行文件位置：
echo   dist\网文 AI 辅写系统\网文 AI 辅写系统.exe
echo.
echo 压缩包位置：
echo   dist\web_novel_writer_v1.0.zip (需要手动创建)
echo.

call venv\Scripts\deactivate.bat
pause
