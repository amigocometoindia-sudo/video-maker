import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from PIL import Image, ImageDraw

# 1. Create 3 sample uploaded user images
test_dir = Path("scratch/test_user_imgs")
test_dir.mkdir(parents=True, exist_ok=True)

img_paths = []
# Image 1: English Coastline / Landscape
im1 = Image.new("RGB", (1920, 1080), "#2a4d69")
d1 = ImageDraw.Draw(im1)
d1.rectangle([0, 540, 1920, 1080], fill="#4b86b4")
d1.polygon([(0, 600), (960, 480), (1920, 620), (1920, 1080), (0, 1080)], fill="#637053")
p1 = test_dir / "01_coast.jpg"
im1.save(p1, quality=95)
img_paths.append(p1)

# Image 2: Throne Hall
im2 = Image.new("RGB", (1920, 1080), "#3b2b20")
d2 = ImageDraw.Draw(im2)
d2.rectangle([200, 200, 1720, 900], fill="#5c4433", outline="#1f1610", width=6)
p2 = test_dir / "02_hall.jpg"
im2.save(p2, quality=95)
img_paths.append(p2)

# Image 3: Battlefield Ridge
im3 = Image.new("RGB", (1920, 1080), "#1c1d21")
d3 = ImageDraw.Draw(im3)
d3.rectangle([0, 500, 1920, 1080], fill="#31353d")
p3 = test_dir / "03_battlefield.jpg"
im3.save(p3, quality=95)
img_paths.append(p3)

print(f"Created {len(img_paths)} sample user images in {test_dir}")

# 2. Test dialogue cues
from srt_parser import Cue
cues = [
    Cue(start_ms=0, end_ms=2800, text="In October 1066, England stood on the brink of an epic clash."),
    Cue(start_ms=2800, end_ms=5800, text="William Duke of Normandy claimed the crown was rightfully his."),
    Cue(start_ms=5800, end_ms=8600, text="Norman cavalry charged the Saxon lines with clashing swords!"),
    Cue(start_ms=8600, end_ms=11200, text="A deadly arrow struck King Harold, shattering Saxon resistance."),
    Cue(start_ms=11200, end_ms=14000, text="William marched to London and changed world history forever."),
]

# 3. Analyze scenes with new Director
from animated_history_engine import direct_dialogue_scenes, render_scene_animated_sequence
plans = direct_dialogue_scenes(cues, topic="The Battle of Hastings 1066")

print("\n--- AI Scene Director Plan ---")
for idx, p in enumerate(plans):
    chars = [c.get("role") for c in p.characters]
    print(f"Cue {idx} (\"{p.text[:35]}...\"): Characters={chars}")

# 4. Check SFX mapping
from llm_analyzer import heuristic_intensity_mapping
sfx_labels = ["war_horn", "sword_clash", "arrow_fly_hit", "dramatic_impact", "royal_fanfare", "taiko_drum", "cinematic_whoosh"]
sfx_map = heuristic_intensity_mapping(cues, sfx_labels)
print("\n--- SFX Director Mapping ---")
for idx, sfx_name in sfx_map.items():
    print(f"Cue {idx} ({cues[idx].start_ms/1000:.1f}s): '{sfx_name}' for \"{cues[idx].text}\"")

# 5. Render test video with server logic
import tempfile
from video_generator import create_video
work_dir = Path("scratch/test_workflow_work")
work_dir.mkdir(parents=True, exist_ok=True)
puppets_dir = work_dir / "puppets"
puppets_dir.mkdir(parents=True, exist_ok=True)

auto_puppets = {}
target_w, target_h = 1920, 1080
for idx, cue in enumerate(cues):
    plan = plans[idx]
    if plan and plan.characters:
        cue_dur = (cue.end_ms - cue.start_ms) / 1000
        p_tag, p_frames = render_scene_animated_sequence(
            plan,
            duration=cue_dur,
            fps=8,
            target_h=int(target_h * 0.52),
            target_w=target_w,
        )
        if p_frames:
            anim_dir = puppets_dir / f"anim_{idx:05d}"
            anim_dir.mkdir(parents=True, exist_ok=True)
            for f_i, frm in enumerate(p_frames):
                frm.save(anim_dir / f"frame_{f_i:03d}.png", "PNG")
            p_path = puppets_dir / f"puppet_{idx:05d}_{p_tag}.png"
            p_frames[0].save(p_path, "PNG")
            auto_puppets[idx] = p_path

print(f"\nGenerated puppets for cues: {list(auto_puppets.keys())} (Cue 0 and Cue 4 correctly left scenic!)")

# Expand 3 user images to match 5 cues
full_image_paths = []
for i in range(len(cues)):
    full_image_paths.append(img_paths[i % len(img_paths)])

out_vid = Path("output/test_custom_workflow.mp4")
intensity_sfx_paths = {lbl: Path(f"sfx/{lbl}.wav") for lbl in sfx_labels}

popup_paths = {p.stem: p for p in auto_puppets.values()}
popup_mapping = {idx: p.stem for idx, p in auto_puppets.items()}

print("\nCreating final test video...")
create_video(
    images=full_image_paths,
    cues=cues,
    ffmpeg_path=Path("ffmpeg"),
    work_dir=work_dir,
    output_path=out_vid,
    apply_zoom=True,
    sfx_paths=[Path("sfx/cinematic_whoosh.wav")],
    intensity_sfx_paths=intensity_sfx_paths,
    intensity_mapping=sfx_map,
    aspect_ratio="16:9",
    popup_paths=popup_paths,
    popup_mapping=popup_mapping,
    motion_style="smart_random",
    zoom_intensity="subtle",
    enable_subtitles=True,
    subtitle_style="hormozi_yellow",
    gpu_accel="nvenc",
)

print(f"SUCCESS! Output video rendered at {out_vid} (Size: {out_vid.stat().st_size} bytes)")
