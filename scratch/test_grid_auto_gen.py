import sys
sys.path.insert(0, ".")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import re

from auto_generator import Cue, detect_topic_domain, breakdown_dialogue_scenes, split_grid_images

def render_scene_card(
    cue_text: str,
    emotion: str,
    topic: str,
    index: int,
    w: int = 960,
    h: int = 540,
    style: str = "cinematic",
) -> Image.Image:
    """Renders a single scene panel matching dialogue and emotion."""
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    domain = detect_topic_domain(topic or cue_text)

    # Emotion color palettes
    palettes = {
        "stress_panic": {"top": (38, 12, 22), "bot": (18, 6, 12), "accent": (244, 63, 94), "pill": "#fda4af"},
        "thoughtful_pondering": {"top": (12, 24, 46), "bot": (6, 12, 24), "accent": (56, 189, 248), "pill": "#7dd3fc"},
        "joy_triumph": {"top": (10, 36, 26), "bot": (5, 18, 12), "accent": (16, 185, 129), "pill": "#6ee7b7"},
        "wealth_success": {"top": (42, 30, 10), "bot": (20, 14, 5), "accent": (245, 158, 11), "pill": "#fde68a"},
        "shock_surprise": {"top": (32, 16, 48), "bot": (16, 8, 24), "accent": (168, 85, 247), "pill": "#d8b4fe"},
        "battle_action": {"top": (44, 14, 14), "bot": (22, 6, 6), "accent": (239, 68, 68), "pill": "#fca5a5"},
        "defeat_sadness": {"top": (22, 26, 32), "bot": (10, 12, 16), "accent": (100, 116, 139), "pill": "#cbd5e1"},
        "focused_narrative": {"top": (15, 23, 42), "bot": (8, 12, 22), "accent": (14, 165, 233), "pill": "#93c5fd"},
    }

    pal = palettes.get(emotion, palettes["focused_narrative"])

    # Background gradient
    for y in range(h):
        ratio = y / max(h - 1, 1)
        r = int(pal["top"][0] + ratio * (pal["bot"][0] - pal["top"][0]))
        g = int(pal["top"][1] + ratio * (pal["bot"][1] - pal["top"][1]))
        b = int(pal["top"][2] + ratio * (pal["bot"][2] - pal["top"][2]))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Grid or texture lines
    grid_col = (pal["accent"][0] // 5, pal["accent"][1] // 5, pal["accent"][2] // 5)
    for gx in range(40, w, 80):
        draw.line([(gx, 30), (gx, h - 30)], fill=grid_col, width=1)
    for gy in range(40, h, 60):
        draw.line([(30, gy), (w - 30, gy)], fill=grid_col, width=1)

    # Outer border
    draw.rounded_rectangle([12, 12, w - 12, h - 12], radius=16, outline=pal["accent"], width=3)

    # Top Scene Pill
    pill_text = f"SCENE {index + 1:02d} • {emotion.upper().replace('_', ' ')}"
    draw.rounded_rectangle([32, 28, 32 + len(pill_text) * 11 + 24, 62], radius=8, fill=(0, 0, 0), outline=pal["accent"], width=2)
    
    font_small = None
    for fc in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if Path(fc).exists():
            font_small = ImageFont.truetype(fc, 16)
            break
    if font_small:
        draw.text((44, 37), pill_text, fill=pal["pill"], font=font_small)

    # Dialogue Quote Display (Middle-Bottom)
    clean_words = cue_text.strip().split()
    lines = []
    cur = []
    for wd in clean_words:
        cur.append(wd)
        if len(" ".join(cur)) > 36:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))

    font_text = None
    for fc in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if Path(fc).exists():
            font_text = ImageFont.truetype(fc, 22)
            break

    start_y = h - 60 - len(lines) * 32
    # Translucent caption backing
    draw.rounded_rectangle([32, start_y - 12, w - 32, h - 36], radius=10, fill=(10, 14, 23))
    draw.rounded_rectangle([32, start_y - 12, w - 32, h - 36], radius=10, outline=grid_col, width=1)
    
    for l_idx, line in enumerate(lines):
        if font_text:
            draw.text((w // 2, start_y + l_idx * 30), line, fill="#ffffff", font=font_text, anchor="mm")
        else:
            draw.text((w // 2, start_y + l_idx * 30), line, fill="#ffffff", anchor="mm")

    return im

print("Test script ready!")
