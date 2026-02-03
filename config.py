"""
TTS 服务配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.absolute()

# TTS 模型配置
TTS_MODEL_DIR = BASE_DIR / "checkpoints" / "kokoro"
TTS_CONFIG = {
    "model": str(TTS_MODEL_DIR / "kokoro-v1.1-zh.onnx"),
    "voice": str(TTS_MODEL_DIR / "voices-v1.1-zh.bin"),
    "vocab": str(TTS_MODEL_DIR / "config-v1.1-zh.json")
}

# 输出目录
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "TTS Service API"

# 日志配置
LOG_LEVEL = "INFO"
