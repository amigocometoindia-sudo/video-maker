import sys, os, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from srt_parser import Cue
from auto_generator import generate_ai_scene_images
from video_generator import create_video
from server import FFMPEG_PATH

def main():
    cues = [
        Cue(start_ms=0, end_ms=2800, text="In October 1066, England stood on the brink of an epic clash."),
        Cue(start_ms=2800, end_ms=5400, text="Duke William of Normandy launched his fierce invasion across the English Channel."),
    ]

    work_dir = Path("scratch/e2e_work")
    work_dir.mkdir(parents=True, exist_ok=True)
    slides_dir = work_dir / "slides"
    puppets_dir = work_dir / "puppets"
    output_path = Path("output/test_e2e_animated.mp4")

    print("[1] Generating slides and multi-frame animated puppets...")
    image_paths, auto_puppets = generate_ai_scene_images(
        cues,
        topic="Battle of Hastings",
        output_dir=slides_dir,
        aspect_ratio="16:9",
        puppets_dir=puppets_dir
    )
    print(f"Generated {len(image_paths)} slides and {len(auto_puppets)} puppets: {auto_puppets}")

    # Check anim frames for scene 0
    anim_0 = puppets_dir / "anim_00000"
    if anim_0.exists():
        frames = list(anim_0.glob("frame_*.png"))
        print(f"Scene 0 has {len(frames)} animated puppet frames in {anim_0}")

    anim_1 = puppets_dir / "anim_00001"
    if anim_1.exists():
        frames = list(anim_1.glob("frame_*.png"))
        print(f"Scene 1 has {len(frames)} animated puppet frames in {anim_1}")

    popup_paths = {p.stem: p for p in auto_puppets.values()}
    popup_mapping = {idx: p.stem for idx, p in auto_puppets.items()}

    print("[2] Creating final video...")
    create_video(
        images=image_paths,
        cues=cues,
        ffmpeg_path=FFMPEG_PATH,
        work_dir=work_dir,
        output_path=output_path,
        popup_paths=popup_paths,
        popup_mapping=popup_mapping,
        aspect_ratio="16:9",
        gpu_accel="nvenc"
    )

    print(f"Video created successfully at {output_path}! Size: {output_path.stat().st_size} bytes")

    # Extract 4 frames from the video to verify animation visually
    for sec, tag in [(0.3, "f_03"), (0.7, "f_07"), (1.2, "f_12"), (3.5, "f_35")]:
        out_f = Path(f"output/e2e_{tag}.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(sec), "-i", str(output_path), "-frames:v", "1", str(out_f)
        ], capture_output=True)
        print(f"Extracted {out_f} at {sec}s")

if __name__ == "__main__":
    main()
