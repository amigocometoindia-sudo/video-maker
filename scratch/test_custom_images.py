import requests
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw

# Create 3 sample custom scene images (simulating user-provided images)
temp_dir = Path(tempfile.mkdtemp(prefix="user_test_imgs_"))
img1_path = temp_dir / "scene1.png"
img2_path = temp_dir / "scene2.png"
img3_path = temp_dir / "scene3.png"

im1 = Image.new("RGB", (1280, 720), "#1e293b")
d1 = ImageDraw.Draw(im1)
d1.text((400, 320), "SCENE 1: THE ARMY GATHERS", fill="#f8fafc")
im1.save(img1_path)

im2 = Image.new("RGB", (1280, 720), "#7f1d1d")
d2 = ImageDraw.Draw(im2)
d2.text((400, 320), "SCENE 2: THE FIERCE BATTLE CLASH", fill="#fef2f2")
im2.save(img2_path)

im3 = Image.new("RGB", (1280, 720), "#14532d")
d3 = ImageDraw.Draw(im3)
d3.text((400, 320), "SCENE 3: VICTORY AND CROWNING", fill="#f0fdf4")
im3.save(img3_path)

print("Created sample user images.")

# Test submitting with custom_images
url = "http://127.0.0.1:8765/api/generate-auto"
data = {
    "topic": "The Norman Conquest Custom Test",
    "script_text": "In October 1066, Duke William arrived at Hastings. The two armies clashed in a brutal and bloody battle! King Harold was defeated, and William claimed the English crown.",
    "duration_minutes": "0.2",
    "aspect_ratio": "16:9",
    "enable_popups": "true",
    "enable_subtitles": "true",
    "subtitle_style": "hormozi_yellow",
}

files = [
    ("custom_images", ("scene1.png", open(img1_path, "rb"), "image/png")),
    ("custom_images", ("scene2.png", open(img2_path, "rb"), "image/png")),
    ("custom_images", ("scene3.png", open(img3_path, "rb"), "image/png")),
]

resp = requests.post(url, data=data, files=files)
print("POST status:", resp.status_code)
res_json = resp.json()
print("Response:", res_json)
job_id = res_json["job_id"]

# Poll
import time
for i in range(40):
    status_resp = requests.get(f"http://127.0.0.1:8765/api/jobs/{job_id}")
    status = status_resp.json()
    st = status.get("state")
    ph = status.get("phase")
    pr = status.get("progress")
    print(f"[{pr}%] state={st} | phase={ph}")
    if st in ("complete", "error", "canceled"):
        if st == "complete":
            print(f"SUCCESS! Output: {status.get('output_name')}")
        else:
            print(f"FAILED! Error: {status.get('error')}")
        break
    time.sleep(2)
