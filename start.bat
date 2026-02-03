@echo off
REM TTS 服务 - Windows 启动脚本

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   TTS 服务 - 启动脚本
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请先安装 Python 3.8+ 并添加到 PATH
    pause
    exit /b 1
)

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo [信息] 未检测到虚拟环境
    echo.
    echo 是否要创建虚拟环境? (Y/N)
    set /p choice="请选择: "
    
    if /i "!choice!"=="Y" (
        echo [操作] 创建虚拟环境...
        python -m venv venv
        call venv\Scripts\activate.bat
        
        echo [操作] 安装依赖...
        pip install -r requirements.txt
    ) else (
        echo [错误] 虚拟环境不存在，无法继续
        pause
        exit /b 1
    )
)

echo.
echo [操作] 检查模型文件...
if not exist "checkpoints\kokoro\kokoro-v1.1-zh.onnx" (
    echo [警告] 模型文件不存在: checkpoints\kokoro\kokoro-v1.1-zh.onnx
    echo.
    echo 请确保以下文件已放入 checkpoints\kokoro\ 目录:
    echo   - kokoro-v1.1-zh.onnx
    echo   - config-v1.1-zh.json
    echo.
    pause
)

echo.
echo [操作] 启动 TTS 服务...
echo ============================================================
echo.
echo   🌐 服务地址: http://localhost:8000
echo   📚 API 文档: http://localhost:8000/docs
echo   🧪 测试脚本: python test.py
echo.
echo ============================================================
echo.

python api.py

pause
