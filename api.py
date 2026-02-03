"""
精简 TTS 服务 - FastAPI 服务器
"""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.tts import TTSEngine
import config

# 初始化应用
app = FastAPI(title=config.API_TITLE)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载输出目录
app.mount("/outputs", StaticFiles(directory=str(config.OUTPUT_DIR)), name="outputs")

# TTS 引擎实例（懒加载）
_tts_engine: Optional[TTSEngine] = None


def get_tts_engine() -> TTSEngine:
    """获取 TTS 引擎实例"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine(config.TTS_CONFIG)
    return _tts_engine


class SynthesizeRequest(BaseModel):
    """合成请求"""
    text: str
    speak_id: str = "zf_001"
    speed: float = 1.0


class BatchRequest(BaseModel):
    """批量合成请求"""
    texts: list[str]
    speak_id: str = "zf_001"
    speed: float = 1.0


# ======================== 路由定义 ========================

@app.get("/")
async def index():
    """根目录"""
    return {"message": "TTS Service API", "version": "1.0"}


@app.get("/api/speakers")
async def get_speakers():
    """获取可用说话人"""
    tts = get_tts_engine()
    return {
        "speakers": tts.get_speakers(),
        "model_loaded": tts.model_loaded
    }


@app.post("/api/synthesize")
async def synthesize(request_data: SynthesizeRequest, request: Request):
    """
    合成文本为音频
    
    Args:
        text: 要合成的文本
        speak_id: 说话人 ID (默认: zf_001)
        speed: 语速 0.5-2.0 (默认: 1.0)
    
    Returns:
        包含音频 URL 的 JSON
    """
    tts = get_tts_engine()
    
    if not tts.model_loaded:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    if not request_data.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    try:
        # 生成文件名
        session_id = str(uuid.uuid4())[:8]
        audio_filename = f"tts_{session_id}.wav"
        audio_path = config.OUTPUT_DIR / audio_filename
        
        # 合成
        success = tts.synthesize_to_file(
            text=request_data.text,
            output_path=str(audio_path),
            speak_id=request_data.speak_id,
            speed=request_data.speed
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="合成失败")
        
        # 构建完整 URL
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        audio_url = f"{base_url}/outputs/{audio_filename}"
        
        return {
            "status": "success",
            "audio_url": audio_url,
            "text": request_data.text,
            "speaker": request_data.speak_id,
            "speed": request_data.speed
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"错误: {str(e)}")


@app.post("/api/batch")
async def batch_synthesize(request_data: BatchRequest, request: Request):
    """
    批量合成文本
    
    Args:
        texts: 文本列表
        speak_id: 说话人 ID
        speed: 语速
    
    Returns:
        包含所有音频 URL 的 JSON
    """
    tts = get_tts_engine()
    
    if not tts.model_loaded:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    if not request_data.texts:
        raise HTTPException(status_code=400, detail="文本列表不能为空")
    
    try:
        # 创建会话目录
        session_id = str(uuid.uuid4())[:8]
        session_dir = config.OUTPUT_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建基础 URL
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # 批量合成
        audio_files = []
        for i, text in enumerate(request_data.texts):
            audio_filename = f"tts_{i:03d}.wav"
            audio_path = session_dir / audio_filename
            
            if tts.synthesize_to_file(
                text=text,
                output_path=str(audio_path),
                speak_id=request_data.speak_id,
                speed=request_data.speed
            ):
                audio_url = f"{base_url}/outputs/{session_id}/{audio_filename}"
                audio_files.append({
                    "index": i,
                    "text": text,
                    "url": audio_url
                })
        
        return {
            "status": "success",
            "session_id": session_id,
            "total": len(request_data.texts),
            "success": len(audio_files),
            "audio_files": audio_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"错误: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """启动事件 - 预加载模型"""
    print("=" * 50)
    print("🎙️  TTS 服务启动中...")
    print("=" * 50)
    
    tts = get_tts_engine()
    
    if tts.model_loaded:
        print("✅ 模型已就绪")
    else:
        print("⚠️  模型加载失败，请检查 checkpoints/kokoro/ 目录")
    
    print("=" * 50)
    print(f"🌐 API 地址: http://localhost:{config.API_PORT}")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
