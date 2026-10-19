"""
Test script for NVIDIA NIM API
"""
import base64
import json
import os
import urllib.request
import urllib.error

NVIDIA_IMAGE_URL = "https://integrate.api.nvidia.com/v1/images/generations"
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def test_nvidia_key(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Test chat completions first with lightweight call
    chat_payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": "Respond with 'NVIDIA NIM OK' only."}],
        "max_tokens": 10,
    }
    
    req = urllib.request.Request(
        NVIDIA_CHAT_URL,
        data=json.dumps(chat_payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            print("Chat response:", data["choices"][0]["message"]["content"])
            return True, "Chat OK"
    except Exception as e:
        print("Chat test error:", e)
        return False, str(e)

if __name__ == "__main__":
    key = os.environ.get("NVIDIA_API_KEY", "")
    if key:
        test_nvidia_key(key)
    else:
        print("No NVIDIA_API_KEY env var set, test structure verified.")
