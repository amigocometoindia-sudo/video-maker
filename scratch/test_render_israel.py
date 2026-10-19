import urllib.request
import json
import time

url = "http://127.0.0.1:8765/api/generate-auto"

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body_parts = [
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"topic\"\r\n\r\n2000 Years of Israel History\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"duration_minutes\"\r\n\r\n0.35\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"aspect_ratio\"\r\n\r\n16:9\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"enable_popups\"\r\n\r\ntrue\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"enable_subtitles\"\r\n\r\ntrue\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"subtitle_style\"\r\n\r\nhormozi_yellow\r\n",
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"bundled_sfx\"\r\n\r\nclick.wav\r\n",
    f"--{boundary}--\r\n"
]

data = "".join(body_parts).encode("utf-8")
headers = {
    "Content-Type": f"multipart/form-data; boundary={boundary}"
}

req = urllib.request.Request(url, data=data, headers=headers)
print("Submitting Israel History auto generation job...")
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        job_id = res["job_id"]
        print(f"Job started successfully: {job_id}")

    status_url = f"http://127.0.0.1:8765/api/jobs/{job_id}"
    while True:
        with urllib.request.urlopen(status_url) as s_resp:
            job_status = json.loads(s_resp.read().decode())
            state = job_status.get("state")
            phase = job_status.get("phase", "")
            prog = job_status.get("progress", 0)
            print(f"[{prog}%] State: {state} | Phase: {phase}")
            if state in ("complete", "error", "canceled"):
                if state == "complete":
                    print(f"\nSUCCESS! Video generated: {job_status.get('output_name')}")
                else:
                    print(f"\nFAILED: {job_status.get('error')}")
                break
        time.sleep(2)
except Exception as e:
    print(f"Test error: {e}")
