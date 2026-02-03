# TTS 服务 - 精简独立版

一个精简的、可独立部署的 TTS（文本转语音）服务，基于 Kokoro ONNX 模型。

## 功能特性

- 🎙️ 支持中文文本合成
- 🔊 6 种说话人选择
- ⚡ 快速响应和批量处理
- 📁 自动生成音频文件
- 🌐 RESTful API 接口

## 环境要求

- Python 3.8+
- 模型文件: `checkpoints/kokoro/`
  - `kokoro-v1.1-zh.onnx`
  - `config-v1.1-zh.json`

## 安装

```bash
# 1. 创建虚拟环境（可选）
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制 Kokoro 模型文件到 checkpoints/kokoro/
#    需要以下文件:
#    - kokoro-v1.1-zh.onnx
#    - config-v1.1-zh.json
```

## 快速开始

```bash
# 启动服务
python api.py

# 或使用 uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问 `http://localhost:8000`

## API 文档

### 1. 获取说话人列表

```bash
GET /api/speakers
```

**响应:**
```json
{
  "speakers": {
    "zf_001": "女声-01",
    "zf_002": "女声-02",
    "zf_003": "女声-03",
    "zm_001": "男声-01",
    "zm_002": "男声-02",
    "zm_003": "男声-03"
  },
  "model_loaded": true
}
```

### 2. 合成文本

```bash
POST /api/synthesize
Content-Type: application/json

{
  "text": "你好世界",
  "speak_id": "zf_001",
  "speed": 1.0
}
```

**参数:**
- `text` (string): 要合成的文本
- `speak_id` (string, 可选): 说话人 ID，默认 "zf_001"
- `speed` (float, 可选): 语速 0.5-2.0，默认 1.0

**响应:**
```json
{
  "status": "success",
  "audio_url": "http://localhost:8000/outputs/tts_a1b2c3d4.wav",
  "text": "你好世界",
  "speaker": "zf_001",
  "speed": 1.0
}
```

### 3. 批量合成

```bash
POST /api/batch
Content-Type: application/json

{
  "texts": ["你好", "世界", "欢迎"],
  "speak_id": "zf_001",
  "speed": 1.0
}
```

**参数:**
- `texts` (array): 文本列表
- `speak_id` (string, 可选): 说话人 ID，默认 "zf_001"
- `speed` (float, 可选): 语速 0.5-2.0，默认 1.0

**响应:**
```json
{
  "status": "success",
  "session_id": "a1b2c3d4",
  "total": 3,
  "success": 3,
  "audio_files": [
    {
      "index": 0,
      "text": "你好",
      "url": "http://localhost:8000/outputs/a1b2c3d4/tts_000.wav"
    },
    ...
  ]
}
```

## 测试示例

### 使用 curl

```bash
# 单文本合成
curl -X POST http://localhost:8000/api/synthesize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"你好世界\"}"

# 获取说话人列表
curl http://localhost:8000/api/speakers

# 批量合成
curl -X POST http://localhost:8000/api/batch \
  -H "Content-Type: application/json" \
  -d "{\"texts\": [\"你好\", \"世界\"]}"
```

### 使用 Python

```python
import requests

# 单文本合成
response = requests.post(
    "http://localhost:8000/api/synthesize",
    json={"text": "你好世界", "speak_id": "zf_001", "speed": 1.0}
)
print(response.json())

# 获取说话人
response = requests.get("http://localhost:8000/api/speakers")
print(response.json())

# 批量合成
response = requests.post(
    "http://localhost:8000/api/batch",
    json={"texts": ["你好", "世界"], "speak_id": "zf_001"}
)
print(response.json())
```

## 配置

编辑 `config.py` 调整服务设置:

- `API_HOST`: 监听地址，默认 "0.0.0.0"
- `API_PORT`: 监听端口，默认 8000
- `OUTPUT_DIR`: 音频输出目录
- `MODEL_PATH`: Kokoro 模型路径

## 文件结构

```
tts/
├── api.py              # FastAPI 主程序
├── config.py           # 配置文件
├── requirements.txt    # Python 依赖
├── core/
│   ├── __init__.py
│   └── tts.py         # TTS 核心引擎
├── outputs/            # 音频输出目录
└── checkpoints/
    └── kokoro/
        ├── kokoro-v1.1-zh.onnx
        └── config-v1.1-zh.json
```

## 常见问题

### Q: 模型文件在哪里获取?
A: Kokoro 模型文件需要从原始项目获取，放入 `checkpoints/kokoro/` 目录。

### Q: 如何修改输出路径?
A: 编辑 `config.py` 中的 `OUTPUT_DIR` 参数。

### Q: 如何改变模型路径?
A: 编辑 `config.py` 中的 `TTS_CONFIG` 参数。

### Q: 支持其他语言吗?
A: 当前配置针对中文优化，其他语言需要替换相应的 Kokoro 模型文件。

## 许可证

MIT License

## 相关项目

- 原始项目: AsLive TTS 服务
- 模型: Kokoro ONNX
- G2P: Misaki
