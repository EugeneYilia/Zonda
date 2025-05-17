import json  # 加到 import 区域

# === 加载 GPU 配置 ===
with open("web_demo/system_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

is_use_gpu = config.get("is_use_gpu", True)
is_dev_mode = config.get("is_dev_mode", False)
use_local_tts = config.get("use_local_tts", False)
use_https = config.get("use_https", True)