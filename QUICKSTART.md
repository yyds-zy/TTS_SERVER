# 🚀 快速开始指南

## 第一步: 检查环境

```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 检查 pip
pip --version
```

## 第二步: 复制模型文件

从 AsLive 项目复制 Kokoro 模型到本项目:

```
D:\workspace\as_live\AsLive\checkpoints\kokoro\
    ├── kokoro-v1.1-zh.onnx
    └── config-v1.1-zh.json

复制到：

D:\workspace\tts\checkpoints\kokoro\
    ├── kokoro-v1.1-zh.onnx
    └── config-v1.1-zh.json
```

> 💡 如果没有 checkpoints 目录，请创建: `mkdir -p checkpoints/kokoro`

## 第三步: 安装依赖

### 方式 1: 使用启动脚本 (Windows)
```bash
start.bat
```

### 方式 2: 手动安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 第四步: 启动服务

```bash
# 方式 1: 使用 Python 直接运行
python api.py

# 方式 2: 使用 uvicorn (指定主机和端口)
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，你会看到:
```
🎙️  TTS 服务启动中...
✅ 模型已就绪
🌐 API 地址: http://localhost:8000
```

## 第五步: 测试服务

### 方式 1: 使用测试脚本

```bash
python test.py
```

### 方式 2: 使用 curl

```bash
# 获取说话人列表
curl http://localhost:8000/api/speakers

# 合成文本
curl -X POST http://localhost:8000/api/synthesize \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"你好世界\"}"
```

### 方式 3: 使用 Python requests

```python
import requests

# 合成
response = requests.post(
    "http://localhost:8000/api/synthesize",
    json={"text": "你好世界", "speak_id": "zf_001"}
)
print(response.json())
```

## 常见问题

### ❓ 模型未加载

**错误信息:**
```
⚠️  模型加载失败，请检查 checkpoints/kokoro/ 目录
```

**解决方案:**
1. 确保 `checkpoints/kokoro/` 目录存在
2. 检查文件:
   - `kokoro-v1.1-zh.onnx` (存在且大小 > 100MB)
   - `config-v1.1-zh.json` (存在)
3. 查看 config.py 中的 MODEL_PATH 配置

### ❓ 端口已被占用

**错误信息:**
```
Address already in use
```

**解决方案:**
```bash
# 使用其他端口启动
uvicorn api:app --host 0.0.0.0 --port 8001
```

### ❓ 依赖安装失败

**常见原因:**
- Kokoro ONNX 或 Misaki 包不可用
- Python 版本过低

**解决方案:**
```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt -v
```

## 文件结构

```
D:\workspace\tts\
├── api.py              ⭐ 主程序
├── config.py           ⭐ 配置文件
├── test.py            🧪 测试脚本
├── start.bat          🚀 启动脚本 (Windows)
├── README.md          📖 完整文档
├── requirements.txt   📦 依赖列表
├── .gitignore
├── checkpoints/
│   └── kokoro/
│       ├── kokoro-v1.1-zh.onnx
│       └── config-v1.1-zh.json
├── outputs/           📁 音频输出目录
│   └── (自动生成的 .wav 文件)
└── core/
    ├── __init__.py
    └── tts.py         ⭐ TTS 核心引擎
```

## 快速链接

- 📚 **API 文档 (Swagger)**: http://localhost:8000/docs
- 📚 **API 文档 (ReDoc)**: http://localhost:8000/redoc
- 📁 **音频文件**: http://localhost:8000/outputs/
- 📖 **完整说明**: README.md

## 生产部署

### 使用 Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 api:app
```

### 使用 Systemd (Linux)

创建 `/etc/systemd/system/tts.service`:

```ini
[Unit]
Description=TTS Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/tts
ExecStart=/path/to/tts/venv/bin/python api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

然后:
```bash
sudo systemctl enable tts
sudo systemctl start tts
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "api.py"]
```

构建并运行:
```bash
docker build -t tts-service .
docker run -p 8000:8000 tts-service
```

## 获取帮助

- 📖 查看 README.md 获取完整文档
- 🔍 查看 config.py 中的配置选项
- 📝 查看 api.py 中的路由定义

---

**祝你使用愉快！** 🎉
