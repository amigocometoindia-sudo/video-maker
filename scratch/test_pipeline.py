import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from history_documentary_engine import run_documentary_pipeline
from srt_parser import parse_srt
import threading

def test_pipeline():
    print("Testing 1-Click Documentary Pipeline (Israel History snippet)...")
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    out_video = out_dir / "test_israel_documentary.mp4"

    # Use a concise 3-cue test script to quickly test all renderers
    test_script = (
        "In 66 AD, under the iron fist of the Roman Empire, rebellion exploded in the streets of Jerusalem. "
        "At the mountain fortress of Masada, high above the Dead Sea, Jewish defenders held out against thousands of legionaries. "
        "In 1948, following the horrors of World War Two, David Ben-Gurion declared the establishment of the State of Israel as five neighboring armies crossed the borders."
    )

    def progress_callback(job_id, **kwargs):
        print(f"[{kwargs.get('progress', 0)}%] {kwargs.get('phase', '')}", flush=True)

    run_documentary_pipeline(
        job_id="test_run_1",
        topic="2000 Years of Israel History",
        duration_minutes=0.5,
        voice="en-US-ChristopherNeural",
        aspect_ratio="16:9",
        subtitle_style="hormozi_yellow",
        sfx_volume=0.20,
        gpu_accel="auto",
        parallel_workers=2,
        output_path=out_video,
        cancel_event=threading.Event(),
        update_job_callback=progress_callback,
        custom_script=test_script,
    )

    if out_video.is_file() and out_video.stat().st_size > 1000:
        print(f"\nSUCCESS! Video generated: {out_video.name} ({out_video.stat().st_size / (1024*1024):.2f} MB)")
    else:
        print(f"\nFAILURE: Output video not created or empty: {out_video}")

if __name__ == '__main__':
    test_pipeline()
