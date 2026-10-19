import time
import requests

BASE_URL = "http://127.0.0.1:8765"

def test_auto_pipeline():
    print("[1] Requesting 1-Click Auto Generation for topic: 'The American Revolution'...")
    form_data = {
        "topic": "The American Revolution",
        "voice": "en-US-ChristopherNeural",
        "duration_minutes": "0.5",
        "aspect_ratio": "16:9",
        "enable_subtitles": "true",
        "subtitle_style": "hormozi_yellow",
        "enable_popups": "true",
        "motion_style": "smart_random",
        "zoom_intensity": "subtle",
        "bg_mode": "crop_fill",
    }

    resp = requests.post(f"{BASE_URL}/api/generate-auto", data=form_data)
    data = resp.json()
    job_id = data.get("job_id")
    print(f"Job launched! ID: {job_id}")

    # Poll status
    for _ in range(60):
        time.sleep(2)
        status_res = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        job = status_res.json()

        phase = job.get("phase", "")
        progress = job.get("progress", 0)
        state = job.get("state", "")
        print(f"[{progress}%] State: {state} | Phase: {phase}")

        if state == "completed":
            print(f"\nSUCCESS! Video generated: {job.get('video_filename')}")
            return True
        elif state == "error":
            print(f"\nERROR: {job.get('error')}")
            return False

    print("Timed out waiting for job completion.")
    return False

if __name__ == "__main__":
    test_auto_pipeline()
