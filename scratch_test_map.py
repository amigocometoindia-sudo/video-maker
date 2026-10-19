import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def render_parchment_map(topic: str, cue_text: str, index: int, target_w: int = 1920, target_h: int = 1080) -> Image.Image:
    # 1. Warm antique parchment background
    im = Image.new("RGB", (target_w, target_h), "#ede1cb")
    draw = ImageDraw.Draw(im)

    # 2. Vignette aged edges
    for i in range(16):
        margin = i * 4
        alpha_tint = (160 - i * 5, 130 - i * 4, 90 - i * 3)
        draw.rounded_rectangle([margin, margin, target_w - margin, target_h - margin], radius=24, outline=alpha_tint, width=4)

    # 3. Outer antique double map frame
    draw.rounded_rectangle([60, 60, target_w - 60, target_h - 60], radius=16, outline="#785938", width=5)
    draw.rounded_rectangle([72, 72, target_w - 72, target_h - 72], radius=12, outline="#b8935c", width=2)

    # 4. Vintage navigation grid lines (faint 30-degree lines across map)
    grid_color = "#e0d0b4"
    for x in range(150, target_w - 100, 240):
        draw.line([x, 80, x, target_h - 80], fill=grid_color, width=2)
    for y in range(150, target_h - 100, 200):
        draw.line([80, y, target_w - 80, y], fill=grid_color, width=2)

    # 5. Ornamental Compass Rose (Top-Right)
    cx, cy, r = target_w - 180, 180, 75
    # Ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#a88554", width=3)
    draw.ellipse([cx - r + 15, cy - r + 15, cx + r - 15, cy + r - 15], outline="#c4a572", width=1)
    # 8 points of compass rose
    points = [
        (cx, cy - r + 5), (cx + 12, cy - 25), (cx + r - 5, cy), (cx + 25, cy + 12),
        (cx, cy + r - 5), (cx - 12, cy + 25), (cx - r + 5, cy), (cx - 25, cy - 12)
    ]
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        rad_r = math.radians(angle + 45)
        tip_x = cx + math.sin(rad) * (r - 8)
        tip_y = cy - math.cos(rad) * (r - 8)
        draw.polygon([(cx, cy), (tip_x, tip_y), (cx + math.sin(rad + 0.3)*25, cy - math.cos(rad + 0.3)*25)], fill="#785938")
        draw.polygon([(cx, cy), (tip_x, tip_y), (cx + math.sin(rad - 0.3)*25, cy - math.cos(rad - 0.3)*25)], fill="#d4af72")

    # Fonts
    font_badge = None
    font_title = None
    for fc in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if Path(fc).exists():
            font_badge = ImageFont.truetype(fc, 34)
            font_title = ImageFont.truetype(fc, 40)
            break

    # 6. Era Badge (Top-Left)
    import re
    year_match = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", cue_text, re.IGNORECASE)
    era_text = year_match.group(0).upper() if year_match else f"SCENE {index + 1:02d}"
    badge_w = 240 if len(era_text) <= 8 else 300
    draw.rounded_rectangle([95, 95, 95 + badge_w, 165], radius=14, fill="#1c1917", outline="#f59e0b", width=3)
    if font_badge:
        draw.text((95 + badge_w // 2, 130), f"⏳ {era_text}", fill="#fbbf24", font=font_badge, anchor="mm")
    else:
        draw.text((95 + badge_w // 2, 130), f"⏳ {era_text}", fill="#fbbf24", anchor="mm")

    # 7. Chapter Title Banner (Top-Center)
    title_text = f"⚔️ {topic.upper()} ⚔️"
    if font_title:
        draw.text((target_w // 2, 125), title_text, fill="#45321c", font=font_title, anchor="mm")
        draw.text((target_w // 2, 165), f"— Chapter {index + 1} —", fill="#8c6d48", anchor="mm")

    # 8. Subtle ground terrain line for stickmen to stand on (at H - 160)
    ground_y = target_h - 160
    draw.line([90, ground_y, target_w - 90, ground_y], fill="#b8935c", width=4)
    # Texture hatch marks under ground line
    for gx in range(120, target_w - 120, 35):
        draw.line([gx, ground_y + 4, gx - 15, ground_y + 22], fill="#d4ba8a", width=2)

    return im

im = render_parchment_map("1000 Years of Dutch History", "In 1581, the Dutch declared independence with the Act of Abjuration.", 0)
im.save("test_parchment_map.jpg", "JPEG", quality=95)
print("Saved test_parchment_map.jpg successfully! Size:", im.size)
