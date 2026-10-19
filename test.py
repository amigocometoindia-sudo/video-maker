import requests
import json
url = 'https://integrate.api.nvidia.com/v1/chat/completions'
headers = {
    'Authorization': 'Bearer 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', 
    'Content-Type': 'application/json'
}
payload = {
    'model': 'meta/llama-3.1-8b-instruct',
    'messages': [{'role': 'user', 'content': 'Output {"test": 123} in JSON'}]
}
resp = requests.post(url, headers=headers, json=payload, timeout=10)
print(resp.status_code)
print(resp.text)
