"""
TTS 核心模块 - 精简版本
基于 Kokoro ONNX 模型的中文语音合成
"""
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple, List
import re
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 支持的说话人
SPEAKERS = {
    "zf_001": "女性温和",
    "zm_001": "男性温和",
    "zf_002": "女性活泼",
    "zm_002": "男性活泼",
    "zf_003": "女性庄重",
    "zm_003": "男性庄重",
}


class TTSEngine:
    """TTS 文本到语音引擎"""
    
    def __init__(self, config: dict):
        """
        初始化 TTS 引擎
        
        Args:
            config: 包含模型路径的配置字典
        """
        self.config = config
        self._kokoro_model = None
        self._g2p_model = None
        self.model_loaded = False
        
        try:
            # 验证文件存在
            for key, path in config.items():
                if not Path(path).exists():
                    raise FileNotFoundError(f"文件不存在: {path}")
            
            logger.info("正在加载 Kokoro TTS 模型...")
            self._load_models()
            self.model_loaded = True
            logger.info("✅ 模型加载完成")
        except Exception as e:
            logger.warning(f"⚠️  模型加载失败: {e}")
            logger.warning("请确保 checkpoints/kokoro/ 目录中有模型文件")
    
    def _load_models(self):
        """加载 Kokoro 和 G2P 模型"""
        from misaki import zh
        from kokoro_onnx import Kokoro
        
        self._g2p_model = zh.ZHG2P(version="1.1")
        self._kokoro_model = Kokoro(
            model_path=self.config["model"],
            voices_path=self.config["voice"],
            vocab_config=self.config["vocab"]
        )
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """文本预处理"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return text.strip()
    
    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """将文本按句子分割"""
        sentences = re.split(r'([。！？；，、\n])', text)
        result = []
        current = ""
        
        for segment in sentences:
            if segment in '。！？；，、\n':
                if current.strip():
                    result.append(current.strip() + segment)
                    current = ""
            else:
                current += segment
        
        if current.strip():
            result.append(current.strip())
        
        return [s for s in result if s.strip()]
    
    @property
    def sample_rate(self) -> int:
        """采样率"""
        return 24000
    
    def synthesize(
        self,
        text: str,
        speak_id: str = "zf_001",
        speed: float = 1.0
    ) -> Tuple[Optional[np.ndarray], int]:
        """
        合成文本为音频
        
        Returns:
            (音频样本, 采样率) 或 (None, 0)
        """
        if not text or not text.strip():
            return None, 0
        
        if not self.model_loaded:
            logger.warning("模型未加载")
            return None, 0
        
        try:
            phonemes, _ = self._g2p_model(text)
            samples, sr = self._kokoro_model.create(
                phonemes,
                voice=speak_id,
                speed=speed,
                is_phonemes=True
            )
            return samples, sr
        except Exception as e:
            logger.error(f"合成失败: {e}")
            return None, 0
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speak_id: str = "zf_001",
        speed: float = 1.0
    ) -> bool:
        """
        合成文本并保存到文件
        
        Returns:
            是否成功
        """
        samples, sr = self.synthesize(text, speak_id, speed)
        
        if samples is None:
            return False
        
        try:
            sf.write(output_path, samples, sr)
            logger.info(f"✅ 已保存: {output_path}")
            return True
        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False
    
    def batch_synthesize(
        self,
        texts: List[str],
        output_dir: str,
        speak_id: str = "zf_001",
        speed: float = 1.0
    ) -> List[str]:
        """批量合成"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, text in enumerate(texts):
            output_path = output_dir / f"tts_{i:03d}.wav"
            if self.synthesize_to_file(str(output_path), text, speak_id, speed):
                results.append(str(output_path))
        
        logger.info(f"批量合成完成: {len(results)}/{len(texts)} 成功")
        return results
    
    def get_speakers(self) -> dict:
        """获取可用说话人"""
        return SPEAKERS.copy()
