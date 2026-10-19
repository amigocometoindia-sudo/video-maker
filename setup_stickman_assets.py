import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STICKMEN_DIR = Path("stickmen")
STICKMEN_DIR.mkdir(exist_ok=True)
POPUPS_DIR = Path("popups")
POPUPS_DIR.mkdir(exist_ok=True)

# Helper font
font_bold = None
font_large = None
for fc in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]:
    if Path(fc).exists():
        try:
            font_bold = ImageFont.truetype(fc, 36)
            font_large = ImageFont.truetype(fc, 72)
            break
        except Exception:
            pass

def create_base(w=512, h=512):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def draw_head(draw, cx, cy, r=42, fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=6):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

def draw_face(draw, cx, cy, mood="neutral"):
    # Eyes
    if mood == "neutral":
        draw.ellipse([cx - 16, cy - 8, cx - 8, cy], fill=(20, 20, 20, 255))
        draw.ellipse([cx + 8, cy - 8, cx + 16, cy], fill=(20, 20, 20, 255))
        draw.line([cx - 10, cy + 14, cx + 10, cy + 14], fill=(20, 20, 20, 255), width=4)
    elif mood == "shock":
        draw.ellipse([cx - 18, cy - 12, cx - 6, cy], fill=(20, 20, 20, 255))
        draw.ellipse([cx + 6, cy - 12, cx + 18, cy], fill=(20, 20, 20, 255))
        draw.ellipse([cx - 10, cy + 8, cx + 10, cy + 28], fill=(20, 20, 20, 255))
    elif mood == "dead":
        # X eyes
        for ex in [cx - 14, cx + 14]:
            draw.line([ex - 8, cy - 8, ex + 8, cy + 8], fill=(20, 20, 20, 255), width=5)
            draw.line([ex - 8, cy + 8, ex + 8, cy - 8], fill=(20, 20, 20, 255), width=5)
        draw.line([cx - 14, cy + 16, cx + 14, cy + 16], fill=(20, 20, 20, 255), width=4)
    elif mood == "angry":
        draw.ellipse([cx - 16, cy - 6, cx - 8, cy + 2], fill=(20, 20, 20, 255))
        draw.ellipse([cx + 8, cy - 6, cx + 16, cy + 2], fill=(20, 20, 20, 255))
        # Eyebrows
        draw.line([cx - 22, cy - 18, cx - 6, cy - 10], fill=(20, 20, 20, 255), width=5)
        draw.line([cx + 22, cy - 18, cx + 6, cy - 10], fill=(20, 20, 20, 255), width=5)
        # Mouth scowl
        draw.arc([cx - 14, cy + 10, cx + 14, cy + 26], start=0, end=180, fill=(20, 20, 20, 255), width=5)
    elif mood == "confused":
        draw.ellipse([cx - 18, cy - 10, cx - 8, cy], fill=(20, 20, 20, 255))
        draw.ellipse([cx + 8, cy - 4, cx + 16, cy + 4], fill=(20, 20, 20, 255))
        draw.arc([cx - 12, cy + 12, cx + 12, cy + 24], start=45, end=190, fill=(20, 20, 20, 255), width=4)
        draw.line([cx - 20, cy - 16, cx - 6, cy - 20], fill=(20, 20, 20, 255), width=4)

def draw_body_and_legs(draw, cx, cy, neck_len=130, leg_len=140, leg_spread=45, color=(20, 20, 20, 255), width=7):
    # Torso
    torso_bottom = cy + neck_len
    draw.line([cx, cy, cx, torso_bottom], fill=color, width=width)
    # Legs
    draw.line([cx, torso_bottom, cx - leg_spread, torso_bottom + leg_len], fill=color, width=width)
    draw.line([cx, torso_bottom, cx + leg_spread, torso_bottom + leg_len], fill=color, width=width)
    return torso_bottom

# 1. STICKMAN KING (Crown, Red Royal Robe, Scepter)
def make_stickman_king():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 150
    # Royal Robe cape
    draw.polygon([(cx - 70, cy + 50), (cx + 70, cy + 50), (cx + 90, cy + 260), (cx - 90, cy + 260)], fill=(220, 38, 38, 255), outline=(153, 27, 27, 255))
    # Fur trim on cape
    draw.rectangle([cx - 75, cy + 45, cx + 75, cy + 65], fill=(245, 245, 245, 255), outline=(20, 20, 20, 255), width=3)
    # Body
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "neutral")
    torso_b = draw_body_and_legs(draw, cx, cy + 42)
    # Crown
    draw.polygon([(cx - 36, cy - 35), (cx - 40, cy - 65), (cx - 18, cy - 48), (cx, cy - 72), (cx + 18, cy - 48), (cx + 40, cy - 65), (cx + 36, cy - 35)], fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))
    draw.ellipse([cx - 43, cy - 68, cx - 37, cy - 62], fill=(239, 68, 68, 255))
    draw.ellipse([cx - 3, cy - 75, cx + 3, cy - 69], fill=(59, 130, 246, 255))
    draw.ellipse([cx + 37, cy - 68, cx + 43, cy - 62], fill=(239, 68, 68, 255))
    # Scepter in hand
    draw.line([cx, cy + 70, cx + 70, cy + 120], fill=(20, 20, 20, 255), width=6)
    draw.line([cx + 70, cy + 60, cx + 70, cy + 220], fill=(217, 119, 6, 255), width=7)
    draw.ellipse([cx + 62, cy + 50, cx + 78, cy + 66], fill=(245, 158, 11, 255), outline=(180, 83, 9, 255), width=3)
    # Left arm
    draw.line([cx, cy + 70, cx - 60, cy + 130], fill=(20, 20, 20, 255), width=6)
    return im

# 2. STICKMAN SOLDIER BLUE (Tricorn hat, Musket with bayonet)
def make_stickman_soldier_blue():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 150
    # Blue coat
    draw.polygon([(cx - 45, cy + 45), (cx + 45, cy + 45), (cx + 55, cy + 180), (cx - 55, cy + 180)], fill=(37, 99, 235, 255), outline=(29, 78, 216, 255))
    # White cross straps
    draw.line([cx - 40, cy + 50, cx + 40, cy + 175], fill=(255, 255, 255, 255), width=8)
    draw.line([cx + 40, cy + 50, cx - 40, cy + 175], fill=(255, 255, 255, 255), width=8)
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "angry")
    draw_body_and_legs(draw, cx, cy + 42)
    # Tricorn hat
    draw.polygon([(cx - 65, cy - 35), (cx, cy - 75), (cx + 65, cy - 35), (cx, cy - 30)], fill=(24, 24, 27, 255), outline=(217, 119, 6, 255))
    # Musket held across
    draw.line([cx - 70, cy + 230, cx + 80, cy + 50], fill=(120, 53, 15, 255), width=7)
    # Barrel & Bayonet
    draw.line([cx + 70, cy + 60, cx + 110, cy + 15], fill=(148, 163, 184, 255), width=5)
    draw.polygon([(cx + 105, cy + 18), (cx + 135, cy - 15), (cx + 112, cy + 12)], fill=(226, 232, 240, 255), outline=(71, 85, 105, 255))
    # Arms
    draw.line([cx, cy + 70, cx - 35, cy + 150], fill=(20, 20, 20, 255), width=6)
    draw.line([cx, cy + 70, cx + 45, cy + 110], fill=(20, 20, 20, 255), width=6)
    return im

# 3. STICKMAN SOLDIER RED (British Redcoat / Rival)
def make_stickman_soldier_red():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 150
    # Red coat
    draw.polygon([(cx - 45, cy + 45), (cx + 45, cy + 45), (cx + 55, cy + 180), (cx - 55, cy + 180)], fill=(220, 38, 38, 255), outline=(185, 28, 28, 255))
    draw.line([cx - 40, cy + 50, cx + 40, cy + 175], fill=(255, 255, 255, 255), width=8)
    draw.line([cx + 40, cy + 50, cx - 40, cy + 175], fill=(255, 255, 255, 255), width=8)
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "angry")
    draw_body_and_legs(draw, cx, cy + 42)
    # Tall shako hat
    draw.rectangle([cx - 30, cy - 85, cx + 30, cy - 35], fill=(24, 24, 27, 255), outline=(217, 119, 6, 255), width=3)
    draw.ellipse([cx - 8, cy - 98, cx + 8, cy - 82], fill=(255, 255, 255, 255))
    # Musket
    draw.line([cx + 70, cy + 230, cx - 80, cy + 50], fill=(120, 53, 15, 255), width=7)
    draw.line([cx - 70, cy + 60, cx - 110, cy + 15], fill=(148, 163, 184, 255), width=5)
    draw.polygon([(cx - 105, cy + 18), (cx - 135, cy - 15), (cx - 112, cy + 12)], fill=(226, 232, 240, 255), outline=(71, 85, 105, 255))
    # Arms
    draw.line([cx, cy + 70, cx + 35, cy + 150], fill=(20, 20, 20, 255), width=6)
    draw.line([cx, cy + 70, cx - 45, cy + 110], fill=(20, 20, 20, 255), width=6)
    return im

# 4. STICKMAN BATTLE (Two stickmen sword clashing with spark)
def make_stickman_battle():
    im = create_base(w=640, h=512)
    draw = ImageDraw.Draw(im)
    # Left fighter (Blue)
    cx1, cy1 = 180, 160
    draw_head(draw, cx1, cy1)
    draw_face(draw, cx1, cy1, "angry")
    draw.line([cx1, cy1 + 42, cx1, cy1 + 170], fill=(37, 99, 235, 255), width=8)
    draw.line([cx1, cy1 + 170, cx1 - 60, cy1 + 270], fill=(20, 20, 20, 255), width=7)
    draw.line([cx1, cy1 + 170, cx1 + 30, cy1 + 270], fill=(20, 20, 20, 255), width=7)
    # Left sword
    draw.line([cx1, cy1 + 70, cx1 + 120, cy1 + 60], fill=(20, 20, 20, 255), width=6)
    draw.line([cx1 + 80, cy1 + 100, cx1 + 170, cy1 + 10], fill=(203, 213, 225, 255), width=8)

    # Right fighter (Red)
    cx2, cy2 = 460, 160
    draw_head(draw, cx2, cy2)
    draw_face(draw, cx2, cy2, "angry")
    draw.line([cx2, cy2 + 42, cx2, cy2 + 170], fill=(220, 38, 38, 255), width=8)
    draw.line([cx2, cy2 + 170, cx2 + 60, cy2 + 270], fill=(20, 20, 20, 255), width=7)
    draw.line([cx2, cy2 + 170, cx2 - 30, cy2 + 270], fill=(20, 20, 20, 255), width=7)
    # Right sword
    draw.line([cx2, cy2 + 70, cx2 - 120, cy2 + 60], fill=(20, 20, 20, 255), width=6)
    draw.line([cx2 - 80, cy2 + 100, cx2 - 170, cy2 + 10], fill=(203, 213, 225, 255), width=8)

    # Clash spark impact in center
    sx, sy = 320, 130
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        draw.line([sx + math.cos(rad) * 10, sy + math.sin(rad) * 10, sx + math.cos(rad) * 35, sy + math.sin(rad) * 35], fill=(251, 191, 36, 255), width=4)
    draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(254, 240, 138, 255), outline=(245, 158, 11, 255), width=3)
    return im

# 5. STICKMAN DEAD (Knocked flat on floor, X eyes, R.I.P tombstone)
def make_stickman_dead():
    im = create_base()
    draw = ImageDraw.Draw(im)
    # Horizontal body on ground
    cx, cy = 290, 330
    draw_head(draw, cx - 140, cy)
    draw_face(draw, cx - 140, cy, "dead")
    draw.line([cx - 98, cy, cx + 50, cy], fill=(20, 20, 20, 255), width=8)
    # Bent legs
    draw.line([cx + 50, cy, cx + 110, cy - 25], fill=(20, 20, 20, 255), width=7)
    draw.line([cx + 110, cy - 25, cx + 140, cy + 20], fill=(20, 20, 20, 255), width=7)
    # Arm thrown back
    draw.line([cx - 40, cy, cx - 20, cy - 60], fill=(20, 20, 20, 255), width=6)
    # Tombstone nearby
    tx, ty = 100, 330
    draw.polygon([(tx - 40, ty + 20), (tx - 40, ty - 60), (tx, ty - 90), (tx + 40, ty - 60), (tx + 40, ty + 20)], fill=(148, 163, 184, 255), outline=(71, 85, 105, 255), width=4)
    if font_bold:
        draw.text((tx, ty - 45), "R.I.P", fill=(30, 41, 59, 255), font=font_bold, anchor="mm")
    return im

# 6. STICKMAN SHOCKED (Hands on cheeks, wide mouth, exclamation mark)
def make_stickman_shocked():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 170
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "shock")
    draw_body_and_legs(draw, cx, cy + 42)
    # Hands clutching head
    draw.line([cx, cy + 70, cx - 45, cy + 20], fill=(20, 20, 20, 255), width=6)
    draw.line([cx - 45, cy + 20, cx - 40, cy], fill=(20, 20, 20, 255), width=6)
    draw.line([cx, cy + 70, cx + 45, cy + 20], fill=(20, 20, 20, 255), width=6)
    draw.line([cx + 45, cy + 20, cx + 40, cy], fill=(20, 20, 20, 255), width=6)
    # Giant floating exclamation mark !
    if font_large:
        draw.text((cx + 75, cy - 50), "!", fill=(239, 68, 68, 255), font=font_large, anchor="mm")
        draw.text((cx - 75, cy - 50), "!", fill=(239, 68, 68, 255), font=font_large, anchor="mm")
    return im

# 7. STICKMAN CONFUSED (Scratching head, floating ?)
def make_stickman_confused():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 170
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "confused")
    draw_body_and_legs(draw, cx, cy + 42)
    # Arm scratching head
    draw.line([cx, cy + 70, cx + 55, cy + 40], fill=(20, 20, 20, 255), width=6)
    draw.line([cx + 55, cy + 40, cx + 30, cy - 30], fill=(20, 20, 20, 255), width=6)
    # Left arm on hip
    draw.line([cx, cy + 70, cx - 45, cy + 100], fill=(20, 20, 20, 255), width=6)
    draw.line([cx - 45, cy + 100, cx - 15, cy + 130], fill=(20, 20, 20, 255), width=6)
    # Floating Question Mark
    if font_large:
        draw.text((cx - 70, cy - 50), "?", fill=(59, 130, 246, 255), font=font_large, anchor="mm")
    return im

# 8. STICKMAN MONEY (Bags of gold coins, dollar/pound sign)
def make_stickman_money():
    im = create_base()
    draw = ImageDraw.Draw(im)
    cx, cy = 256, 160
    draw_head(draw, cx, cy)
    draw_face(draw, cx, cy, "neutral")
    draw_body_and_legs(draw, cx, cy + 42)
    # Money bag left
    bx1, by1 = cx - 80, cy + 130
    draw.ellipse([bx1 - 35, by1 - 10, bx1 + 35, by1 + 60], fill=(245, 158, 11, 255), outline=(180, 83, 9, 255), width=4)
    draw.polygon([(bx1 - 15, by1 - 10), (bx1 - 25, by1 - 30), (bx1 + 25, by1 - 30), (bx1 + 15, by1 - 10)], fill=(217, 119, 6, 255))
    if font_bold:
        draw.text((bx1, by1 + 25), "$", fill=(120, 53, 15, 255), font=font_bold, anchor="mm")
    draw.line([cx, cy + 70, bx1, by1 - 10], fill=(20, 20, 20, 255), width=6)

    # Money bag right
    bx2, by2 = cx + 80, cy + 130
    draw.ellipse([bx2 - 35, by2 - 10, bx2 + 35, by2 + 60], fill=(245, 158, 11, 255), outline=(180, 83, 9, 255), width=4)
    draw.polygon([(bx2 - 15, by2 - 10), (bx2 - 25, by2 - 30), (bx2 + 25, by2 - 30), (bx2 + 15, by2 - 10)], fill=(217, 119, 6, 255))
    if font_bold:
        draw.text((bx2, by2 + 25), "£", fill=(120, 53, 15, 255), font=font_bold, anchor="mm")
    draw.line([cx, cy + 70, bx2, by2 - 10], fill=(20, 20, 20, 255), width=6)
    return im

# 9. MAP INVASION ARROW (Curved with motion dots)
def make_map_arrow(color=(220, 38, 38, 255)):
    im = create_base(w=512, h=300)
    draw = ImageDraw.Draw(im)
    # Curved arrow path with thick outline
    points = [(60, 220), (160, 200), (280, 140), (400, 100)]
    # Dotted movement trail
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=22)
    # Arrow head
    draw.polygon([(380, 50), (470, 95), (380, 150), (400, 95)], fill=color)
    return im

# 10. SPEECH BUBBLE
def make_speech_bubble():
    im = create_base(w=512, h=350)
    draw = ImageDraw.Draw(im)
    # Comic bubble with tail
    draw.rounded_rectangle([30, 30, 480, 260], radius=35, fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=6)
    draw.polygon([(160, 258), (120, 330), (210, 258)], fill=(255, 255, 255, 255))
    draw.line([(160, 258), (120, 330)], fill=(20, 20, 20, 255), width=6)
    draw.line([(120, 330), (210, 258)], fill=(20, 20, 20, 255), width=6)
    return im

generators = {
    "stickman_king.png": make_stickman_king,
    "stickman_soldier_blue.png": make_stickman_soldier_blue,
    "stickman_soldier_red.png": make_stickman_soldier_red,
    "stickman_battle.png": make_stickman_battle,
    "stickman_dead.png": make_stickman_dead,
    "stickman_shocked.png": make_stickman_shocked,
    "stickman_confused.png": make_stickman_confused,
    "stickman_money.png": make_stickman_money,
    "map_arrow_red.png": lambda: make_map_arrow((220, 38, 38, 255)),
    "map_arrow_blue.png": lambda: make_map_arrow((37, 99, 235, 255)),
    "speech_bubble.png": make_speech_bubble,
}

print("Generating Stickman History asset suite...")
for name, func in generators.items():
    img = func()
    # Save in stickmen/
    img.save(STICKMEN_DIR / name, "PNG")
    # Save in popups/ for direct engine lookup
    img.save(POPUPS_DIR / name, "PNG")
    # Also register short stem aliases (e.g. king, battle, soldier)
    alias = name.replace("stickman_", "").replace("map_", "")
    img.save(POPUPS_DIR / alias, "PNG")
    print(f"Generated {name} and {alias}")

print("All Stickman assets generated successfully!")
