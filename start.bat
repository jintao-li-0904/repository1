@echo off
echo ========================================
echo 医疗产品短名称生成器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未检测到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 运行启动脚本
python start.py

pause
