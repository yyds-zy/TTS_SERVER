"""
TTS 服务测试脚本
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
OUTPUTS_DIR = Path(__file__).parent / "outputs"


def test_speakers():
    """测试获取说话人列表"""
    print("\n" + "=" * 50)
    print("📋 测试: 获取说话人列表")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/speakers")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 请求成功")
        print(f"   模型状态: {data['model_loaded']}")
        print(f"   可用说话人:")
        for key, value in data['speakers'].items():
            print(f"     - {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_synthesize(text="你好世界", speak_id="zf_001", speed=1.0):
    """测试单文本合成"""
    print("\n" + "=" * 50)
    print(f"🎙️  测试: 合成文本")
    print("=" * 50)
    
    try:
        payload = {
            "text": text,
            "speak_id": speak_id,
            "speed": speed
        }
        
        print(f"📝 参数:")
        print(f"   文本: {text}")
        print(f"   说话人: {speak_id}")
        print(f"   语速: {speed}")
        
        response = requests.post(
            f"{BASE_URL}/api/synthesize",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✅ 合成成功")
        print(f"   状态: {data['status']}")
        print(f"   音频 URL: {data['audio_url']}")
        
        # 下载音频验证
        filename = Path(data['audio_url']).name
        audio_path = OUTPUTS_DIR / filename
        print(f"   本地路径: {audio_path}")
        
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_batch(texts=None):
    """测试批量合成"""
    print("\n" + "=" * 50)
    print("📦 测试: 批量合成")
    print("=" * 50)
    
    if texts is None:
        texts = ["你好", "世界", "TTS", "服务"]
    
    try:
        payload = {
            "texts": texts,
            "speak_id": "zf_001",
            "speed": 1.0
        }
        
        print(f"📝 参数:")
        print(f"   文本列表: {texts}")
        print(f"   总数: {len(texts)}")
        
        response = requests.post(
            f"{BASE_URL}/api/batch",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✅ 批量合成成功")
        print(f"   状态: {data['status']}")
        print(f"   会话 ID: {data['session_id']}")
        print(f"   总数: {data['total']}")
        print(f"   成功: {data['success']}")
        
        if data['audio_files']:
            print(f"   首个音频 URL: {data['audio_files'][0]['url']}")
        
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_speakers_variety():
    """测试不同说话人"""
    print("\n" + "=" * 50)
    print("👥 测试: 不同说话人")
    print("=" * 50)
    
    speakers = ["zf_001", "zf_002", "zm_001"]
    
    for speaker in speakers:
        try:
            print(f"\n🎙️  合成说话人: {speaker}")
            
            response = requests.post(
                f"{BASE_URL}/api/synthesize",
                json={"text": "欢迎使用 TTS 服务", "speak_id": speaker},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"   ✅ 成功: {data['audio_url']}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    return True


def test_speed_variation():
    """测试不同语速"""
    print("\n" + "=" * 50)
    print("🚀 测试: 不同语速")
    print("=" * 50)
    
    speeds = [0.5, 1.0, 1.5, 2.0]
    
    for speed in speeds:
        try:
            print(f"\n⏱️  合成语速: {speed}")
            
            response = requests.post(
                f"{BASE_URL}/api/synthesize",
                json={"text": "语速测试", "speed": speed},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"   ✅ 成功: {data['audio_url']}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("#" * 50)
    print("# TTS 服务 - 完整测试套件")
    print("#" * 50)
    
    print(f"\n🔗 服务地址: {BASE_URL}")
    print(f"📁 输出目录: {OUTPUTS_DIR}")
    
    results = []
    
    # 测试 1: 说话人列表
    results.append(("获取说话人列表", test_speakers()))
    time.sleep(1)
    
    # 测试 2: 单文本合成
    results.append(("合成文本", test_synthesize("你好世界", "zf_001", 1.0)))
    time.sleep(2)
    
    # 测试 3: 批量合成
    results.append(("批量合成", test_batch(["你好", "世界"])))
    time.sleep(2)
    
    # 测试 4: 不同说话人
    results.append(("不同说话人", test_speakers_variety()))
    time.sleep(2)
    
    # 测试 5: 不同语速
    results.append(("不同语速", test_speed_variation()))
    
    # 生成测试报告
    print("\n" + "=" * 50)
    print("📊 测试报告")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
