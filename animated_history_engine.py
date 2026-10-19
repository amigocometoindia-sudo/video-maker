"""
Animated History Engine
=======================
Implements the exact full-screen visual and animation style of @animatedhistoryy:
1. Full-screen 16:9 illustrated cartoon backgrounds (ancient villages, throne rooms, burning ruins, caves, camps).
2. Geopolitical regional maps with color-coded national borders, comic labels, and sweeping tactical arrows.
3. Authentic expressive characters (expressive heads, big cartoon eyes, open screaming/grinning mouths, period outfits, stick limbs, props).
4. Countryballs (Polandball style) with flag textures, expressive eyes, and weapons for modern geopolitics.
5. Minimalist translucent top-left date pill (e.g. '26 AD', '1066', '1948').
6. AI Scene Director linking every dialogue cue to the precise historical setting, characters, and SFX.
"""

import math
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# =====================================================================
# Font Helpers
# =====================================================================

def get_best_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Finds the best available cartoon / clean sans font on Windows."""
    candidates = []
    if bold:
        candidates = [
            "C:/Windows/Fonts/comicbd.ttf",      # Comic Sans Bold (signature history cartoon style)
            "C:/Windows/Fonts/segoeuib.ttf",     # Segoe UI Bold
            "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
            "C:/Windows/Fonts/tahomabd.ttf",     # Tahoma Bold
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/comic.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
        ]

    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


# =====================================================================
# 1. Procedural Background Illustrators (Full-Screen 16:9)
# =====================================================================

def render_ancient_village(w: int = 1920, h: int = 1080) -> Image.Image:
    """Renders the authentic Animated History ancient desert/adobe village with wooden carts and pots."""
    im = Image.new("RGB", (w, h), "#dfd1b8")
    draw = ImageDraw.Draw(im)

    # Sky gradient (soft cartoon blue fading to warm horizon)
    sky_h = int(h * 0.42)
    for y in range(sky_h):
        ratio = y / max(sky_h, 1)
        r = int(120 + ratio * 85)
        g = int(185 + ratio * 45)
        b = int(220 + ratio * 15)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Fluffy cartoon clouds
    for cx, cy, cr in [(300, 110, 70), (370, 95, 85), (450, 115, 65), (1450, 90, 80), (1540, 75, 95), (1630, 95, 75)]:
        draw.ellipse([cx - cr, cy - cr // 2, cx + cr, cy + cr // 2], fill="#ffffff")
    for cx, cy, cr in [(350, 125, 90), (1520, 105, 100)]:
        draw.ellipse([cx - cr, cy - cr // 3, cx + cr, cy + cr // 3], fill="#ffffff")

    # Distant mountain ridge
    ridge_pts = [(0, sky_h)]
    for rx in range(0, w + 100, 120):
        ry = sky_h - 20 - int(math.sin(rx * 0.008) * 35 + math.cos(rx * 0.015) * 20)
        ridge_pts.append((rx, ry))
    ridge_pts.extend([(w, sky_h), (0, sky_h)])
    draw.polygon(ridge_pts, fill="#cbb793")

    # Ground terrain (sandy desert earth)
    ground_y = sky_h
    draw.rectangle([0, ground_y, w, h], fill="#dfd1b8")
    # Ground texture specks / terrain cracks
    rnd = random.Random(42)
    for _ in range(60):
        gx = rnd.randint(50, w - 50)
        gy = rnd.randint(ground_y + 80, h - 30)
        gw = rnd.randint(15, 60)
        draw.line([gx, gy, gx + gw, gy + rnd.randint(-4, 4)], fill="#c4b294", width=2)

    # Adobe Houses - Left Wing
    # House 1 (Far Left foreground building)
    draw.polygon([(0, 220), (380, 260), (380, 720), (0, 720)], fill="#d6c3a3", outline="#3b2b1a", width=4)
    # Roof parapet crenellations
    for bx in [40, 140, 240, 320]:
        draw.rectangle([bx, 215, bx + 45, 260], fill="#c2ae8e", outline="#3b2b1a", width=3)
    # Doorway
    draw.rounded_rectangle([130, 430, 250, 715], radius=50, fill="#2c2217", outline="#3b2b1a", width=4)
    # Window
    draw.rectangle([260, 310, 310, 370], fill="#38291a", outline="#3b2b1a", width=3)

    # Adobe Houses - Right Wing
    # House 2 (Far Right foreground building)
    draw.polygon([(w - 420, 290), (w, 240), (w, 740), (w - 420, 740)], fill="#d1bd9d", outline="#3b2b1a", width=4)
    # Parapet
    for bx in [w - 380, w - 280, w - 180, w - 80]:
        draw.rectangle([bx, 240, bx + 45, 290], fill="#bdab8b", outline="#3b2b1a", width=3)
    # Doorway Right
    draw.rounded_rectangle([w - 300, 450, w - 180, 735], radius=50, fill="#281f15", outline="#3b2b1a", width=4)
    # Window Right
    draw.rectangle([w - 380, 340, w - 330, 400], fill="#38291a", outline="#3b2b1a", width=3)

    # Middle Background Buildings
    draw.rectangle([680, 340, 880, 560], fill="#c9b595", outline="#3b2b1a", width=3)
    draw.rectangle([730, 370, 770, 420], fill="#2f2316", outline="#3b2b1a", width=2)
    draw.rectangle([1040, 320, 1260, 560], fill="#c4b090", outline="#3b2b1a", width=3)
    draw.rectangle([1120, 360, 1160, 410], fill="#2f2316", outline="#3b2b1a", width=2)

    # Props: Wooden Cart on Left
    cart_x, cart_y = 70, 680
    draw.polygon([(cart_x, cart_y - 60), (cart_x + 160, cart_y - 40), (cart_x + 150, cart_y + 10), (cart_x - 10, cart_y - 10)], fill="#8b5a2b", outline="#2b1a0e", width=4)
    # Wheel with spokes
    wx, wy, wr = cart_x + 90, cart_y + 35, 65
    draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill="#6a3e1b", outline="#2b1a0e", width=5)
    draw.ellipse([wx - 14, wy - 14, wx + 14, wy + 14], fill="#2b1a0e")
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        draw.line([wx, wy, wx + math.cos(rad) * wr, wy + math.sin(rad) * wr], fill="#2b1a0e", width=3)

    # Props: Clay Pots / Jars
    for px, py, pw, ph, clr in [(420, 720, 45, 60, "#a05a2c"), (465, 730, 40, 50, "#8b4513"), (440, 750, 35, 40, "#cd853f")]:
        draw.ellipse([px, py, px + pw, py + ph], fill=clr, outline="#2c1709", width=3)
        draw.ellipse([px + pw // 4, py - 6, px + 3 * pw // 4, py + 4], fill=clr, outline="#2c1709", width=2)

    return im


def render_throne_room(w: int = 1920, h: int = 1080) -> Image.Image:
    """Renders authentic Animated History royal/emperor throne room with stone blocks, wall torches, and throne."""
    im = Image.new("RGB", (w, h), "#1e1815")
    draw = ImageDraw.Draw(im)

    # Stone masonry wall background
    brick_h = 75
    for row, y in enumerate(range(0, h, brick_h)):
        offset = (row % 2) * 90
        for x in range(-90, w + 180, 180):
            bx = x + offset
            shade = 32 + (row * 3 + (bx // 180) * 7) % 18
            draw.rectangle([bx, y, bx + 175, y + brick_h - 5], fill=(shade, shade - 6, shade - 10), outline="#110d0a", width=2)

    # Arched Vault in Background Center
    arch_cx, arch_w, arch_h = w // 2, 600, 700
    draw.rounded_rectangle([arch_cx - arch_w // 2, 100, arch_cx + arch_w // 2, 800], radius=180, fill="#130e0b", outline="#0a0705", width=6)

    # Raised Dais / Platform Steps for Throne
    draw.polygon([(arch_cx - 420, 780), (arch_cx + 420, 780), (arch_cx + 520, 920), (arch_cx - 520, 920)], fill="#3a2e24", outline="#150f0b", width=4)
    draw.rectangle([arch_cx - 550, 920, arch_cx + 550, h], fill="#2d2218", outline="#150f0b", width=4)

    # The Stone Throne
    tx, ty = arch_cx, 440
    # Throne Backrest
    draw.polygon([(tx - 160, ty - 220), (tx + 160, ty - 220), (tx + 190, ty + 240), (tx - 190, ty + 240)], fill="#4a3e35", outline="#1a140f", width=5)
    # Throne Peak Crown / Crest
    draw.polygon([(tx - 160, ty - 220), (tx, ty - 290), (tx + 160, ty - 220)], fill="#5c4d42", outline="#1a140f", width=5)
    # Throne Armrests
    draw.rectangle([tx - 230, ty + 60, tx - 170, ty + 260], fill="#55463b", outline="#1a140f", width=4)
    draw.rectangle([tx + 170, ty + 60, tx + 230, ty + 260], fill="#55463b", outline="#1a140f", width=4)
    # Throne Velvet Cushion (Royal Crimson)
    draw.rounded_rectangle([tx - 150, ty + 120, tx + 150, ty + 240], radius=15, fill="#7f1d1d", outline="#450a0a", width=3)

    # Wall Torches with warm glow on both sides
    for torch_x in [280, w - 280]:
        # Sconce iron bracket
        draw.line([torch_x, 340, torch_x, 460], fill="#1c1612", width=10)
        draw.polygon([(torch_x - 16, 340), (torch_x + 16, 340), (torch_x + 24, 300), (torch_x - 24, 300)], fill="#403227", outline="#150f0b", width=3)
        # Torch Flame Glow
        glow_r = 160
        glow_box = [torch_x - glow_r, 260 - glow_r, torch_x + glow_r, 260 + glow_r]
        # Radial gradient approximation
        for r_step in range(glow_r, 20, -25):
            alpha = int(40 * (1 - r_step / glow_r))
            draw.ellipse([torch_x - r_step, 260 - r_step, torch_x + r_step, 260 + r_step], outline=(255, 170, 40, alpha), width=18)
        # Flame Petals
        draw.polygon([(torch_x, 180), (torch_x + 35, 270), (torch_x + 20, 310), (torch_x - 20, 310), (torch_x - 35, 270)], fill="#f97316")
        draw.polygon([(torch_x, 210), (torch_x + 18, 280), (torch_x - 18, 280)], fill="#fde047")

    return im


def render_burning_ruins(w: int = 1920, h: int = 1080) -> Image.Image:
    """Renders authentic Animated History sacked/destroyed battlefield with fire, smoke, and crumbled walls."""
    im = Image.new("RGB", (w, h), "#24252a")
    draw = ImageDraw.Draw(im)

    # Dark stormy smoke sky
    for y in range(int(h * 0.5)):
        ratio = y / (h * 0.5)
        r = int(55 - ratio * 15)
        g = int(60 - ratio * 18)
        b = int(70 - ratio * 20)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Dark billowing smoke plumes
    rnd = random.Random(88)
    for sx in [220, 460, 920, 1420, 1700]:
        for si in range(8):
            sm_y = int(h * 0.55) - si * 65
            sm_r = 60 + si * 18
            sm_x = sx + int(math.sin(si + sx) * 45)
            shade = max(25, 65 - si * 6)
            draw.ellipse([sm_x - sm_r, sm_y - sm_r // 2, sm_x + sm_r, sm_y + sm_r // 2], fill=(shade, shade, shade + 4))

    # Crumbled Stone Walls & Towers
    # Left Ruined Tower
    draw.polygon([(60, 720), (60, 380), (120, 340), (190, 410), (280, 360), (360, 430), (360, 720)], fill="#3d3f47", outline="#1c1d22", width=5)
    # Right Ruined Tower
    draw.polygon([(w - 420, 720), (w - 420, 400), (w - 340, 350), (w - 270, 420), (w - 180, 370), (w - 80, 430), (w - 80, 720)], fill="#383940", outline="#1c1d22", width=5)

    # Roaring fire flames on ruins
    for fx, fy, fw, fh in [(100, 370, 90, 140), (260, 390, 110, 160), (w - 360, 380, 120, 170), (w - 220, 390, 90, 130)]:
        draw.polygon([(fx + fw // 2, fy - fh), (fx + fw, fy), (fx + fw * 0.7, fy - fh * 0.3), (fx, fy)], fill="#ea580c")
        draw.polygon([(fx + fw // 2, fy - fh * 0.7), (fx + fw * 0.8, fy), (fx + fw * 0.2, fy)], fill="#facc15")

    # Dark ash ground
    ground_y = int(h * 0.65)
    draw.rectangle([0, ground_y, w, h], fill="#27272a")
    for _ in range(50):
        rx = rnd.randint(30, w - 30)
        ry = rnd.randint(ground_y + 40, h - 30)
        draw.ellipse([rx, ry, rx + rnd.randint(12, 35), ry + rnd.randint(6, 18)], fill="#18181b", outline="#09090b", width=2)

    return im


def render_geopolitical_map(
    w: int = 1920,
    h: int = 1080,
    topic: str = "",
    region: str = "auto",
    highlight_name: str = "",
    arrows: list[dict] | None = None,
    labels: list[tuple[str, int, int]] | None = None,
) -> Image.Image:
    """
    Renders authentic Animated History geopolitical colored terrain map
    with highlighted territories, white borders, comic labels, and tactical arrows.
    """
    im = Image.new("RGB", (w, h), "#e8d8be")
    draw = ImageDraw.Draw(im)

    topic_lower = (topic or "").lower()
    is_british = any(k in topic_lower for k in ["hastings", "1066", "norman", "england", "britain", "william", "harold", "channel", "saxon", "london"]) or region == "british_isles"

    font_large = get_best_font(54, bold=True)
    font_med = get_best_font(40, bold=True)
    font_small = get_best_font(30, bold=True)

    if is_british:
        # British Isles / English Channel Map
        draw.rectangle([0, 0, w, h], fill="#2b82a2")

        # England Landmass (North / Left) - Rich green with crisp white border
        england_polygon = [
            (0, 0),
            (int(w * 0.75), 0),
            (int(w * 0.70), int(h * 0.32)),
            (int(w * 0.62), int(h * 0.48)),
            (int(w * 0.45), int(h * 0.52)),
            (int(w * 0.28), int(h * 0.58)),
            (0, int(h * 0.45)),
        ]
        draw.polygon(england_polygon, fill="#65a30d", outline="#ffffff", width=5)

        # Highlight Hastings Landing Site in Crimson Red
        hastings_polygon = [
            (int(w * 0.58), int(h * 0.42)),
            (int(w * 0.64), int(h * 0.44)),
            (int(w * 0.62), int(h * 0.50)),
            (int(w * 0.56), int(h * 0.47)),
        ]
        draw.polygon(hastings_polygon, fill="#dc2626", outline="#ffffff", width=3)

        # Normandy / France Landmass (South / Right) - Amber Gold with crisp white border
        france_polygon = [
            (int(w * 0.20), h),
            (int(w * 0.38), int(h * 0.72)),
            (int(w * 0.58), int(h * 0.68)),
            (int(w * 0.78), int(h * 0.62)),
            (w, int(h * 0.58)),
            (w, h),
        ]
        draw.polygon(france_polygon, fill="#d97706", outline="#ffffff", width=5)

        map_labels = [
            ("ENGLAND", int(w * 0.35), int(h * 0.25), font_large, "#ffffff"),
            ("HASTINGS", int(w * 0.62), int(h * 0.38), font_small, "#fef08a"),
            ("ENGLISH CHANNEL", int(w * 0.42), int(h * 0.62), font_med, "#ffffff"),
            ("NORMANDY", int(w * 0.52), int(h * 0.82), font_large, "#ffffff"),
            ("FRANCE", int(w * 0.82), int(h * 0.85), font_large, "#ffffff"),
        ]

        if not arrows:
            arrows = [
                {"from": (int(w * 0.46), int(h * 0.74)), "to": (int(w * 0.58), int(h * 0.49)), "color": "#000000", "width": 16},
                {"from": (int(w * 0.55), int(h * 0.70)), "to": (int(w * 0.62), int(h * 0.46)), "color": "#dc2626", "width": 14},
            ]
    else:
        # Mediterranean / Levant / Middle East Map (Animated History standard)
        sea_polygon = [(0, 0), (int(w * 0.52), 0), (int(w * 0.48), int(h * 0.65)), (int(w * 0.42), int(h * 0.75)), (0, int(h * 0.62))]
        draw.polygon(sea_polygon, fill="#2b82a2")

        draw.polygon([(int(w * 0.45), int(h * 0.72)), (int(w * 0.52), h), (int(w * 0.48), h), (int(w * 0.43), int(h * 0.78))], fill="#2b82a2")

        # North Africa / Egypt
        draw.polygon([(0, int(h * 0.62)), (int(w * 0.45), int(h * 0.68)), (int(w * 0.48), h), (0, h)], fill="#b4cf44", outline="#ffffff", width=4)

        # Anatolia / Turkey
        draw.polygon([(int(w * 0.25), 0), (int(w * 0.75), 0), (int(w * 0.65), int(h * 0.35)), (int(w * 0.38), int(h * 0.32))], fill="#d9994c", outline="#ffffff", width=4)

        # Greater Middle East
        draw.polygon([(int(w * 0.50), int(h * 0.32)), (w, int(h * 0.28)), (w, h), (int(w * 0.52), h), (int(w * 0.48), int(h * 0.48))], fill="#7d7365", outline="#ffffff", width=4)

        # Highlighted Centerpiece
        hl_label = highlight_name or "JUDEA"
        judea_polygon = [
            (int(w * 0.46), int(h * 0.44)),
            (int(w * 0.49), int(h * 0.42)),
            (int(w * 0.50), int(h * 0.56)),
            (int(w * 0.46), int(h * 0.68)),
            (int(w * 0.44), int(h * 0.58)),
        ]
        draw.polygon(judea_polygon, fill="#a81c24", outline="#ffffff", width=4)

        map_labels = [
            ("Africa", int(w * 0.16), int(h * 0.78), font_large, "#ffffff"),
            ("Middle East", int(w * 0.72), int(h * 0.52), font_large, "#ffffff"),
            ("Mediterranean", int(w * 0.24), int(h * 0.34), font_med, "#ffffff"),
            (hl_label, int(w * 0.475), int(h * 0.53), font_small, "#fef08a"),
        ]

        if not arrows:
            arrows = [
                {"from": (int(w * 0.48), int(h * 0.48)), "to": (int(w * 0.38), int(h * 0.38)), "color": "#000000", "width": 14},
                {"from": (int(w * 0.48), int(h * 0.50)), "to": (int(w * 0.53), int(h * 0.28)), "color": "#000000", "width": 14},
                {"from": (int(w * 0.48), int(h * 0.52)), "to": (int(w * 0.58), int(h * 0.48)), "color": "#000000", "width": 14},
            ]

    # Draw Text Labels
    for item in map_labels:
        text, lx, ly, fnt, text_color = item[0], item[1], item[2], item[3], item[4]
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
            draw.text((lx + dx, ly + dy), text, fill="#000000", font=fnt, anchor="mm")
        draw.text((lx, ly), text, fill=text_color, font=fnt, anchor="mm")

    # Draw Curved Tactical Arrows
    for arr in arrows:
        fx, fy = arr.get("from", (int(w * 0.48), int(h * 0.48)))
        tx, ty = arr.get("to", (int(w * 0.38), int(h * 0.38)))
        clr = arr.get("color", "#000000")
        aw = arr.get("width", 14)

        ctrl_x = (fx + tx) // 2 + (fy - ty) // 4
        ctrl_y = (fy + ty) // 2 + (tx - fx) // 4

        curve_pts = []
        for t_step in range(16):
            t = t_step / 15.0
            cx = (1 - t)**2 * fx + 2 * (1 - t) * t * ctrl_x + t**2 * tx
            cy = (1 - t)**2 * fy + 2 * (1 - t) * t * ctrl_y + t**2 * ty
            curve_pts.append((cx, cy))

        for pi in range(len(curve_pts) - 1):
            draw.line([curve_pts[pi], curve_pts[pi + 1]], fill=clr, width=aw)

        tip_x, tip_y = tx, ty
        prev_x, prev_y = curve_pts[-2]
        angle = math.atan2(tip_y - prev_y, tip_x - prev_x)
        head_len = aw * 2.8
        p1 = (tip_x - head_len * math.cos(angle - 0.5), tip_y - head_len * math.sin(angle - 0.5))
        p2 = (tip_x - head_len * math.cos(angle + 0.5), tip_y - head_len * math.sin(angle + 0.5))
        draw.polygon([(tip_x, tip_y), p1, p2], fill=clr)

    return im


# =====================================================================
# 2. Authentic Animated History Character Renderer
# =====================================================================

def render_cartoon_character(
    role: str = "roman_soldier",
    expression: str = "angry",
    prop: str = "sword",
    target_h: int = 560,
    facing: str = "right",
    mouth_state: str = "auto",
    blink: bool = False,
    head_tilt: float = 0.0,
    arm_phase: float = 0.0,
    hop_offset: int = 0,
) -> Image.Image:
    """
    Renders high-definition Animated History character with:
    - Expressive cartoon head, hair, big cartoon eyes, open mouth.
    - Authentic period clothing / armor / robes.
    - Stick limbs with hands holding weapons/props.
    - Parametric animation support: mouth flaps, eye blinks, head nod, weapon swings.
    - Transparent background.
    """
    cw, ch = 480, target_h
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    mid_x = cw // 2
    head_y = 110 - hop_offset
    head_r = 55
    body_top = head_y + head_r - 10
    body_bottom = body_top + 160
    ground_y = ch - 25

    flip = facing == "left"

    # Stick Legs (Thin black strokes with oval feet)
    leg_w = 5
    leg_col = "#111827"
    left_foot_y = ground_y - hop_offset // 2
    right_foot_y = ground_y - hop_offset // 2
    draw.line([mid_x - 22, body_bottom - 10, mid_x - 35, left_foot_y], fill=leg_col, width=leg_w)
    draw.ellipse([mid_x - 45, left_foot_y - 6, mid_x - 25, left_foot_y + 4], fill=leg_col)
    draw.line([mid_x + 22, body_bottom - 10, mid_x + 35, right_foot_y], fill=leg_col, width=leg_w)
    draw.ellipse([mid_x + 25, right_foot_y - 6, mid_x + 45, right_foot_y + 4], fill=leg_col)

    # Costume / Tunic on Body
    if "roman" in role or "centurion" in role:
        # Roman segmented cuirass + pteruges
        draw.polygon([(mid_x - 45, body_top), (mid_x + 45, body_top), (mid_x + 52, body_bottom), (mid_x - 52, body_bottom)], fill="#858994", outline="#22272e", width=4)
        for strip_y in range(body_top + 25, body_bottom - 20, 28):
            draw.line([mid_x - 46, strip_y, mid_x + 46, strip_y], fill="#b4b9c4", width=3)
        # Red tunic sash
        draw.polygon([(mid_x - 30, body_top), (mid_x - 10, body_top), (mid_x + 40, body_bottom), (mid_x + 20, body_bottom)], fill="#991b1b")
    elif "king" in role or "emperor" in role:
        # Royal velvet robe (Crimson with gold ermine chain)
        draw.polygon([(mid_x - 55, body_top), (mid_x + 55, body_top), (mid_x + 68, body_bottom + 15), (mid_x - 68, body_bottom + 15)], fill="#831843", outline="#330b1b", width=4)
        # Gold collar chain
        draw.arc([mid_x - 40, body_top - 10, mid_x + 40, body_top + 45], 0, 180, fill="#facc15", width=6)
    elif "monk" in role or "priest" in role:
        # Dark monk habit / brown robe
        draw.polygon([(mid_x - 50, body_top), (mid_x + 50, body_top), (mid_x + 65, body_bottom + 25), (mid_x - 65, body_bottom + 25)], fill="#3f2e22", outline="#1c140d", width=4)
        # White cord belt
        draw.line([mid_x - 50, body_bottom - 20, mid_x + 50, body_bottom - 20], fill="#f5f5f4", width=4)
    elif "general" in role or "officer" in role:
        # Khaki officer uniform
        draw.polygon([(mid_x - 46, body_top), (mid_x + 46, body_top), (mid_x + 52, body_bottom), (mid_x - 52, body_bottom)], fill="#85754e", outline="#292416", width=4)
        # Crossbelt
        draw.line([mid_x - 35, body_top, mid_x + 35, body_bottom], fill="#453a23", width=7)
    elif "businessman" in role or "tech" in role or "founder" in role or "elon" in role:
        # Sleek modern navy suit + white shirt + red tie
        draw.polygon([(mid_x - 48, body_top), (mid_x + 48, body_top), (mid_x + 54, body_bottom), (mid_x - 54, body_bottom)], fill="#1e293b", outline="#0f172a", width=4)
        draw.polygon([(mid_x - 16, body_top), (mid_x + 16, body_top), (mid_x, body_top + 34)], fill="#ffffff")
        draw.polygon([(mid_x - 7, body_top + 10), (mid_x + 7, body_top + 10), (mid_x + 10, body_bottom - 22), (mid_x, body_bottom - 10), (mid_x - 10, body_bottom - 22)], fill="#ef4444")
    elif "thinker" in role or "psychology" in role or "overthink" in role:
        # Modern cerebral indigo knit sweater / hoodie
        draw.polygon([(mid_x - 50, body_top), (mid_x + 50, body_top), (mid_x + 58, body_bottom), (mid_x - 58, body_bottom)], fill="#312e81", outline="#1e1b4b", width=4)
        draw.arc([mid_x - 26, body_top - 6, mid_x + 26, body_top + 20], 0, 180, fill="#4338ca", width=5)
    elif "caveman" in role or "hunter" in role or "primal" in role:
        # Prehistoric animal pelt tunic with ragged hem
        draw.polygon([(mid_x - 48, body_top), (mid_x + 48, body_top), (mid_x + 56, body_bottom + 10), (mid_x - 56, body_bottom + 10)], fill="#78350f", outline="#451a03", width=4)
        for hx in range(mid_x - 56, mid_x + 46, 16):
            draw.polygon([(hx, body_bottom + 10), (hx + 8, body_bottom + 24), (hx + 16, body_bottom + 10)], fill="#78350f")
    elif "knight" in role or "norman" in role or "saxon" in role:
        # Chainmail hauberk with heraldic surcoat
        draw.polygon([(mid_x - 48, body_top), (mid_x + 48, body_top), (mid_x + 55, body_bottom + 12), (mid_x - 55, body_bottom + 12)], fill="#475569", outline="#0f172a", width=4)
        # Heraldic blue/red tunic
        draw.polygon([(mid_x - 42, body_top + 10), (mid_x + 42, body_top + 10), (mid_x + 48, body_bottom), (mid_x - 48, body_bottom)], fill="#1e40af")
        draw.line([mid_x, body_top + 10, mid_x, body_bottom], fill="#dc2626", width=10)
    else:
        # Peasant / Rebel ragged tunic
        draw.polygon([(mid_x - 45, body_top), (mid_x + 45, body_top), (mid_x + 55, body_bottom), (mid_x - 55, body_bottom)], fill="#8c7355", outline="#2b2319", width=4)
        # Ragged jagged hem
        for hx in range(mid_x - 55, mid_x + 45, 18):
            draw.polygon([(hx, body_bottom), (hx + 9, body_bottom + 10), (hx + 18, body_bottom)], fill="#8c7355")

    # Animated Head on Dedicated Rotatable Surface
    skin_col = "#f5c69b"
    head_pad = head_r * 4
    head_im = Image.new("RGBA", (head_pad, head_pad), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(head_im)
    hc_x = head_pad // 2
    hc_y = head_pad // 2

    # Draw Cartoon Head Base
    hdraw.ellipse([hc_x - head_r, hc_y - head_r, hc_x + head_r, hc_y + head_r], fill=skin_col, outline="#2c1a0e", width=4)

    # Headgear / Hair
    if "roman" in role or "centurion" in role:
        hdraw.polygon([(hc_x - head_r - 6, hc_y), (hc_x + head_r + 6, hc_y), (hc_x + head_r, hc_y - head_r - 10), (hc_x - head_r, hc_y - head_r - 10)], fill="#8492a6", outline="#1f2937", width=4)
        hdraw.polygon([(hc_x - 20, hc_y - head_r - 10), (hc_x + 20, hc_y - head_r - 10), (hc_x + 28, hc_y - head_r - 45), (hc_x - 28, hc_y - head_r - 45)], fill="#dc2626", outline="#7f1d1d", width=3)
        hdraw.polygon([(hc_x - head_r, hc_y), (hc_x - head_r + 18, hc_y + 40), (hc_x - head_r + 28, hc_y)], fill="#8492a6", outline="#1f2937", width=3)
        hdraw.polygon([(hc_x + head_r, hc_y), (hc_x + head_r - 18, hc_y + 40), (hc_x + head_r - 28, hc_y)], fill="#8492a6", outline="#1f2937", width=3)
    elif "knight" in role or "norman" in role or "saxon" in role:
        hdraw.polygon([(hc_x - head_r - 6, hc_y), (hc_x + head_r + 6, hc_y), (hc_x, hc_y - head_r - 35)], fill="#64748b", outline="#1e293b", width=4)
        hdraw.line([hc_x, hc_y - 20, hc_x, hc_y + 12], fill="#334155", width=6)
    elif "king" in role:
        crown_y = hc_y - head_r - 5
        hdraw.polygon([
            (hc_x - 48, crown_y + 15),
            (hc_x - 48, crown_y - 25),
            (hc_x - 24, crown_y - 10),
            (hc_x, crown_y - 35),
            (hc_x + 24, crown_y - 10),
            (hc_x + 48, crown_y - 25),
            (hc_x + 48, crown_y + 15),
        ], fill="#facc15", outline="#713f12", width=3)
        for rx in [hc_x - 30, hc_x, hc_x + 30]:
            hdraw.ellipse([rx - 4, crown_y + 2, rx + 4, crown_y + 10], fill="#dc2626")
    elif "general" in role:
        cap_y = hc_y - head_r + 10
        hdraw.polygon([(hc_x - 55, cap_y), (hc_x + 55, cap_y), (hc_x + 65, cap_y - 30), (hc_x - 65, cap_y - 30)], fill="#334155", outline="#0f172a", width=3)
        hdraw.polygon([(hc_x - 58, cap_y), (hc_x + 58, cap_y), (hc_x + 48, cap_y + 12), (hc_x - 48, cap_y + 12)], fill="#0f172a")
    else:
        hdraw.polygon([(hc_x - head_r - 4, hc_y - 10), (hc_x + head_r + 4, hc_y - 10), (hc_x + head_r - 10, hc_y - head_r - 12), (hc_x - head_r + 10, hc_y - head_r - 12)], fill="#452a17", outline="#24140a", width=3)
        for hx in [hc_x - 35, hc_x, hc_x + 35]:
            hdraw.ellipse([hx - 15, hc_y - head_r - 15, hx + 15, hc_y - head_r + 8], fill="#452a17")

    # Big Cartoon Eyes with Eye Blink Support
    eye_y = hc_y - 6
    eye_r = 16
    left_eye_x = hc_x - 22
    right_eye_x = hc_x + 22

    if expression == "dead":
        for ex in [left_eye_x, right_eye_x]:
            hdraw.line([ex - 12, eye_y - 12, ex + 12, eye_y + 12], fill="#111827", width=5)
            hdraw.line([ex + 12, eye_y - 12, ex - 12, eye_y + 12], fill="#111827", width=5)
    elif blink:
        # Cartoon Eye Blink Slit: - -
        hdraw.line([left_eye_x - 14, eye_y, left_eye_x + 14, eye_y], fill="#111827", width=5)
        hdraw.line([right_eye_x - 14, eye_y, right_eye_x + 14, eye_y], fill="#111827", width=5)
    else:
        hdraw.ellipse([left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r], fill="#ffffff", outline="#111827", width=3)
        hdraw.ellipse([right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r], fill="#ffffff", outline="#111827", width=3)
        pupil_ox = 3 if not flip else -3
        pupil_r = 6
        hdraw.ellipse([left_eye_x + pupil_ox - pupil_r, eye_y - pupil_r, left_eye_x + pupil_ox + pupil_r, eye_y + pupil_r], fill="#111827")
        hdraw.ellipse([right_eye_x + pupil_ox - pupil_r, eye_y - pupil_r, right_eye_x + pupil_ox + pupil_r, eye_y + pupil_r], fill="#111827")

        if expression == "angry":
            hdraw.line([left_eye_x - 16, eye_y - 24, left_eye_x + 14, eye_y - 16], fill="#111827", width=5)
            hdraw.line([right_eye_x + 16, eye_y - 24, right_eye_x - 14, eye_y - 16], fill="#111827", width=5)
        elif expression == "shocked":
            hdraw.arc([left_eye_x - 14, eye_y - 32, left_eye_x + 14, eye_y - 18], 180, 360, fill="#111827", width=4)
            hdraw.arc([right_eye_x - 14, eye_y - 32, right_eye_x + 14, eye_y - 18], 180, 360, fill="#111827", width=4)
        else:
            hdraw.line([left_eye_x - 14, eye_y - 20, left_eye_x + 14, eye_y - 20], fill="#111827", width=4)
            hdraw.line([right_eye_x - 14, eye_y - 20, right_eye_x + 14, eye_y - 20], fill="#111827", width=4)

    # Cartoon Mouth with Talking Viseme States
    mouth_y = hc_y + 24
    cur_mouth = mouth_state
    if cur_mouth == "auto":
        if expression in ("screaming", "angry"):
            cur_mouth = "shout"
        elif expression == "evil_grin":
            cur_mouth = "evil_grin"
        elif expression == "dead":
            cur_mouth = "dead"
        else:
            cur_mouth = "closed"

    if cur_mouth in ("shout", "open"):
        # Wide open shouting / speaking mouth with red tongue and teeth
        hdraw.polygon([(hc_x - 24, mouth_y - 6), (hc_x + 24, mouth_y - 6), (hc_x + 16, mouth_y + 24), (hc_x - 16, mouth_y + 24)], fill="#1f130b", outline="#111827", width=3)
        hdraw.rectangle([hc_x - 18, mouth_y - 5, hc_x + 18, mouth_y + 3], fill="#ffffff")
        hdraw.ellipse([hc_x - 12, mouth_y + 10, hc_x + 12, mouth_y + 22], fill="#f43f5e")
    elif cur_mouth == "mid":
        # Mid-open conversational mouth
        hdraw.ellipse([hc_x - 16, mouth_y - 4, hc_x + 16, mouth_y + 14], fill="#1f130b", outline="#111827", width=3)
        hdraw.rectangle([hc_x - 12, mouth_y - 3, hc_x + 12, mouth_y + 2], fill="#ffffff")
    elif cur_mouth == "evil_grin":
        hdraw.polygon([(hc_x - 28, mouth_y), (hc_x + 28, mouth_y), (hc_x + 20, mouth_y + 18), (hc_x - 20, mouth_y + 18)], fill="#ffffff", outline="#111827", width=3)
        for tx in range(hc_x - 20, hc_x + 22, 10):
            hdraw.line([tx, mouth_y, tx, mouth_y + 18], fill="#111827", width=2)
    elif cur_mouth == "dead":
        hdraw.line([hc_x - 14, mouth_y + 10, hc_x + 14, mouth_y + 2], fill="#111827", width=4)
    else:
        # Closed mouth smirk
        hdraw.arc([hc_x - 18, mouth_y - 8, hc_x + 18, mouth_y + 14], 10, 170, fill="#111827", width=4)

    # Rotate head by head_tilt and composite onto body
    if abs(head_tilt) > 0.1:
        head_rotated = head_im.rotate(head_tilt, resample=Image.BICUBIC)
    else:
        head_rotated = head_im
    im.paste(head_rotated, (mid_x - hc_x, head_y - hc_y), head_rotated)

    # Stick Arms & Props with Animation Phase
    arm_w = 5
    arm_col = "#111827"
    hand_y = body_top + 70

    if prop == "sword":
        # Dynamic sword slash and gleam based on arm_phase
        swing_angle = -0.4 + 1.2 * math.sin(arm_phase * math.pi)
        hand_x = int(mid_x + (70 + 35 * math.cos(swing_angle)) * (1 if not flip else -1))
        hy = int(hand_y + 40 * math.sin(swing_angle))
        draw.line([mid_x + (30 if not flip else -30), body_top + 15, hand_x, hy], fill=arm_col, width=arm_w)

        sw_len = 90
        sw_x = int(hand_x + sw_len * math.cos(swing_angle - 0.5) * (1 if not flip else -1))
        sw_y = int(hy - sw_len * math.sin(swing_angle + 0.3))
        draw.line([hand_x - 8, hy, hand_x + 8, hy], fill="#ca8a04", width=6)
        draw.line([hand_x, hy, sw_x, sw_y], fill="#cbd5e1", width=7)
        draw.line([hand_x, hy, sw_x, sw_y], fill="#ffffff", width=3)

        # White speed blur streak during strike
        if 0.2 < arm_phase < 0.65:
            streak_box = [hand_x - 40, hy - 70, hand_x + 90, hy + 50]
            draw.arc(streak_box, 270, 360, fill="#ffffff", width=4)
    elif prop == "spear":
        # Spear thrust forward
        thrust = int(45 * math.sin(arm_phase * math.pi))
        hand_x = mid_x + (70 + thrust if not flip else -(70 + thrust))
        draw.line([mid_x + (30 if not flip else -30), body_top + 15, hand_x, hand_y], fill=arm_col, width=arm_w)
        draw.line([hand_x - 20, ground_y, hand_x + 25, head_y - head_r - 50], fill="#854d0e", width=6)
        draw.polygon([(hand_x + 25, head_y - head_r - 50), (hand_x + 35, head_y - head_r - 85), (hand_x + 15, head_y - head_r - 50)], fill="#94a3b8", outline="#334155", width=2)
    elif prop == "broom":
        sweep = int(25 * math.sin(arm_phase * 2 * math.pi))
        hand_x = mid_x + (65 if not flip else -65)
        draw.line([mid_x + (30 if not flip else -30), body_top + 15, hand_x, hand_y + sweep], fill=arm_col, width=arm_w)
        draw.line([hand_x - 15, ground_y, hand_x + 20, head_y - head_r - 40 + sweep], fill="#a16207", width=5)
        bx, by = hand_x + 20, head_y - head_r - 40 + sweep
        draw.polygon([(bx - 20, by), (bx + 20, by), (bx + 30, by - 45), (bx - 30, by - 45)], fill="#fde047", outline="#713f12", width=3)
    elif prop == "stool":
        toss_y = int(50 * math.sin(arm_phase * math.pi))
        hand_x = mid_x + (60 if not flip else -60)
        draw.line([mid_x + (30 if not flip else -30), body_top + 15, hand_x, hand_y], fill=arm_col, width=arm_w)
        sx, sy = hand_x, hand_y - 30 - toss_y
        draw.ellipse([sx - 35, sy - 14, sx + 35, sy + 14], fill="#92400e", outline="#451a03", width=3)
        draw.line([sx - 25, sy, sx - 35, sy + 50], fill="#78350f", width=4)
        draw.line([sx, sy, sx, sy + 55], fill="#78350f", width=4)
        draw.line([sx + 25, sy, sx + 35, sy + 50], fill="#78350f", width=4)
    else:
        # Conversational arm gestures
        gesture_offset = int(16 * math.sin(arm_phase * 2 * math.pi))
        draw.line([mid_x - 35, body_top + 15, mid_x - 65, hand_y + gesture_offset], fill=arm_col, width=arm_w)
        draw.line([mid_x + 35, body_top + 15, mid_x + 65, hand_y - gesture_offset], fill=arm_col, width=arm_w)

    return im


def render_countryball(
    country: str = "israel",
    expression: str = "angry",
    weapon: str = "ak47",
    size: int = 240,
) -> Image.Image:
    """Renders authentic Polandball / Countryball with national flag texture, comic eyes, and weapon."""
    im = Image.new("RGBA", (size + 140, size + 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    bx, by, br = size // 2 + 30, size // 2 + 30, size // 2 - 10

    # Base sphere with black stroke
    # Draw flag inside ball
    mask = Image.new("L", (size + 140, size + 80), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.ellipse([bx - br, by - br, bx + br, by + br], fill=255)

    flag_layer = Image.new("RGBA", (size + 140, size + 80), "#ffffff")
    f_draw = ImageDraw.Draw(flag_layer)

    c_norm = country.lower()
    if "israel" in c_norm:
        f_draw.rectangle([0, 0, size + 140, size + 80], fill="#ffffff")
        # Blue stripes
        f_draw.rectangle([0, by - br + 25, size + 140, by - br + 55], fill="#0038b8")
        f_draw.rectangle([0, by + br - 55, size + 140, by + br - 25], fill="#0038b8")
        # Star of David (two overlapping triangles)
        st_r = 30
        f_draw.polygon([(bx, by - st_r), (bx + int(st_r * 0.86), by + st_r // 2), (bx - int(st_r * 0.86), by + st_r // 2)], outline="#0038b8", width=4)
        f_draw.polygon([(bx, by + st_r), (bx + int(st_r * 0.86), by - st_r // 2), (bx - int(st_r * 0.86), by - st_r // 2)], outline="#0038b8", width=4)
    elif "egypt" in c_norm:
        div1 = by - int(br / 3)
        div2 = by + int(br / 3)
        f_draw.rectangle([0, 0, size + 140, div1], fill="#ce1126")
        f_draw.rectangle([0, div1, size + 140, div2], fill="#ffffff")
        f_draw.rectangle([0, div2, size + 140, size + 80], fill="#000000")
        # Eagle of Saladin in gold
        f_draw.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill="#c09300")
    elif "syria" in c_norm:
        div1 = by - int(br / 3)
        div2 = by + int(br / 3)
        f_draw.rectangle([0, 0, size + 140, div1], fill="#ce1126")
        f_draw.rectangle([0, div1, size + 140, div2], fill="#ffffff")
        f_draw.rectangle([0, div2, size + 140, size + 80], fill="#000000")
        # Two green stars
        f_draw.ellipse([bx - 26, by - 9, bx - 10, by + 7], fill="#007a3d")
        f_draw.ellipse([bx + 10, by - 9, bx + 26, by + 7], fill="#007a3d")
    elif "jordan" in c_norm:
        div1 = by - int(br / 3)
        div2 = by + int(br / 3)
        f_draw.rectangle([0, 0, size + 140, div1], fill="#000000")
        f_draw.rectangle([0, div1, size + 140, div2], fill="#ffffff")
        f_draw.rectangle([0, div2, size + 140, size + 80], fill="#007a3d")
        f_draw.polygon([(bx - br, by - br), (bx - br, by + br), (bx - int(br * 0.1), by)], fill="#ce1126")
        f_draw.ellipse([bx - int(br * 0.6) - 5, by - 5, bx - int(br * 0.6) + 5, by + 5], fill="#ffffff")
    else:
        # Default neutral blue/gold
        f_draw.rectangle([0, 0, size + 140, size + 80], fill="#1e3a8a")

    im.paste(flag_layer, (0, 0), mask)
    # Re-draw clean black ball border
    draw.ellipse([bx - br, by - br, bx + br, by + br], outline="#000000", width=6)

    # Expressive Comic Eyes (Polandball style)
    eye_y = by - 8
    ew, eh = 28, 38
    # Left eye
    draw.ellipse([bx - 38, eye_y - eh // 2, bx - 10, eye_y + eh // 2], fill="#ffffff", outline="#000000", width=4)
    # Right eye
    draw.ellipse([bx + 10, eye_y - eh // 2, bx + 38, eye_y + eh // 2], fill="#ffffff", outline="#000000", width=4)
    # Angry slant lids
    if expression == "angry":
        draw.line([bx - 44, eye_y - eh // 2 - 4, bx - 6, eye_y], fill="#000000", width=6)
        draw.line([bx + 44, eye_y - eh // 2 - 4, bx + 6, eye_y], fill="#000000", width=6)

    # AK-47 / Rifle held on side
    if weapon == "ak47":
        gx, gy = bx + br - 10, by + 10
        # Barrel
        draw.line([gx - 40, gy + 15, gx + 65, gy - 20], fill="#1e293b", width=7)
        # Wooden stock
        draw.polygon([(gx - 40, gy + 15), (gx - 75, gy + 30), (gx - 65, gy + 45), (gx - 35, gy + 25)], fill="#854d0e", outline="#1e293b", width=2)
        # Curved magazine
        draw.arc([gx - 10, gy + 10, gx + 25, gy + 45], 40, 180, fill="#0f172a", width=6)

    return im


# =====================================================================
# 3. Top-Left Minimalist Date Pill Badge
# =====================================================================

def stamp_date_pill(im: Image.Image, text: str) -> None:
    """Stamps the authentic Animated History minimalist dark translucent date pill in top-left."""
    if not text:
        return
    draw = ImageDraw.Draw(im)
    clean_txt = str(text).strip().upper()

    font = get_best_font(38, bold=True)
    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x, pad_y = 26, 14
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    bx, by = 45, 45

    # Dark translucent background (#1e1e1ecc)
    pill = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(pill)
    p_draw.rounded_rectangle([0, 0, bw, bh], radius=16, fill=(15, 20, 28, 205), outline=(255, 255, 255, 60), width=2)
    im.paste(pill, (bx, by), pill)

    # Crisp white casual text
    draw.text((bx + bw // 2, by + bh // 2 - 2), clean_txt, fill="#ffffff", font=font, anchor="mm")


# =====================================================================
# 4. AI Scene Director: Dialogue Parsing to Scene Sheet
# =====================================================================

@dataclass
class ScenePlan:
    index: int
    text: str
    era_badge: str
    scene_type: str        # "village", "throne_room", "burning_ruins", "map", "countryballs", "caves"
    characters: list[dict] # [{"role": "roman", "expression": "angry", "prop": "sword", "pos": 0.25}]
    arrows: list[dict] = field(default_factory=list)
    sfx: str = "whoosh"
    topic: str = ""


def direct_dialogue_scenes(cues: list[Any], topic: str = "History") -> list[ScenePlan]:
    """
    The AI Scene Director:
    Analyzes every dialogue cue and deterministically maps it to the exact
    authentic Animated History visual setting, character configuration, and SFX.
    """
    plans: list[ScenePlan] = []
    topic_lower = topic.lower()

    is_medieval = any(w in topic_lower for w in ["hastings", "1066", "norman", "england", "william", "harold", "knight", "saxon", "britain"])
    is_rome = any(w in topic_lower for w in ["rome", "roman", "caesar", "gladiator"])
    warrior_role = "knight" if is_medieval else "roman"

    # Track current era throughout narrative progression
    current_era = "1066" if is_medieval else "66 AD"
    m_topic = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", topic, re.IGNORECASE)
    if m_topic:
        current_era = m_topic.group(0).upper()

    for idx, cue in enumerate(cues):
        t = cue.text.lower()

        # 1. Detect era dates in cue
        m_date = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", cue.text, re.IGNORECASE)
        if m_date:
            current_era = m_date.group(0).upper()

        # 2. Determine Scene Type from Dialogue Context
        era_year = int(re.sub(r'\D', '', current_era) or 0)
        is_modern_era = era_year >= 1900

        is_map = any(w in t for w in ["territory", "border", "borders", "marched", "expand", "invade", "invasion", "map", "land", "fled", "empire", "across", "middle east", "africa", "europe", "channel", "fleet", "normandy", "england", "alliances", "state", "partition"])
        is_fire_ruins = any(w in t for w in ["fire", "burn", "burned", "ruin", "destroy", "destroyed", "sacked", "clash", "bloody", "defeat", "killed", "casualty", "massacre", "shield wall", "cavalry", "brawl", "siege", "legion", "legions", "temple", "revolt", "war", "exile"])
        is_throne = any(w in t for w in ["king", "emperor", "throne", "ruler", "palace", "decree", "court", "council", "crowned", "caesar", "harold", "william", "duke", "coronation", "caliphate", "pope", "sovereign", "byzantine"])
        is_cave = any(w in t for w in ["cave", "scroll", "scrolls", "dead sea", "hidden", "tomb", "secret", "desert"])

        # Decide background type
        if is_modern_era and is_map:
            stype = "countryballs"
        elif is_throne:
            stype = "throne_room"
        elif is_fire_ruins:
            stype = "burning_ruins"
        elif is_map:
            stype = "map"
        elif is_cave:
            stype = "caves"
        else:
            # Alternating narrative default: village vs map
            stype = "village" if idx % 2 == 0 else "map"

        # 3. Configure Characters & Props (True Dialogue-Matching)
        characters = []
        sfx = "cinematic_whoosh"
        is_king_cue = any(w in t for w in ["king", "queen", "emperor", "crown", "crowned", "throne", "duke", "harold", "william", "caesar", "ruler", "palace", "coronation", "monarch"])
        is_combat_cue = any(w in t for w in ["battle", "clash", "swords", "charge", "cavalry", "attack", "strike", "fight", "brawl", "shield wall", "slashed", "assault"])
        is_cavalry_cue = any(w in t for w in ["cavalry", "horse", "horses", "gallop", "charge", "mounted", "knights charged"])
        is_casualty_cue = any(w in t for w in ["arrow struck", "slain", "fell", "dead", "died", "defeat", "defeated", "collapse", "collapsed", "shattered", "crushed"])
        is_shock_cue = any(w in t for w in ["surprise", "shock", "shocked", "unexpected", "betray", "betrayal", "twist", "ambush", "trapped"])
        is_victory_cue = any(w in t for w in ["victory", "victorious", "won", "triumph", "triumphant", "conquered", "celebrated", "rejoice"])
        is_riot_cue = any(w in t for w in ["riot", "rebel", "tax", "anger", "trouble", "dispute", "protest"])
        is_speech_cue = any(w in t for w in ["said", "claimed", "declared", "announced", "speech", "proclaimed", "shouted", "decreed", "demanded"]) or ('"' in cue.text or "'" in cue.text)
        is_monk_cue = any(w in t for w in ["church", "faith", "pope", "monk", "priest", "bishop"])

        is_psychology_cue = any(w in t for w in ["overthink", "overthinking", "think", "thinking", "brain", "anxiety", "stress", "worry", "loop", "thoughts", "mind", "fear", "dopamine", "awake", "panic", "negativity"])
        is_wealth_tech_cue = any(w in t for w in ["money", "rich", "wealth", "billion", "million", "dollar", "elon", "musk", "tesla", "spacex", "startup", "invest", "risk", "gamble", "profit", "broke", "bankrupt"])
        is_prehistory_cue = any(w in t for w in ["ancient", "human", "primal", "tribe", "fire", "cave", "hunter", "gatherer", "mammoth", "neanderthal", "predator", "survival", "survive"])

        pos_slot = 0.38 if idx % 2 == 0 else 0.62

        if is_psychology_cue:
            expr = "shocked" if is_shock_cue else ("screaming" if is_speech_cue else ("dead" if is_casualty_cue else "angry"))
            characters = [
                {"role": "thinker", "expression": expr, "prop": "idle", "pos": pos_slot}
            ]
        elif is_wealth_tech_cue:
            expr = "evil_grin" if (is_victory_cue or "billion" in t or "profit" in t) else ("shocked" if ("broke" in t or "bankrupt" in t) else ("screaming" if is_speech_cue else "angry"))
            characters = [
                {"role": "businessman", "expression": expr, "prop": "idle", "pos": pos_slot}
            ]
        elif is_prehistory_cue:
            expr = "screaming" if is_speech_cue else "angry"
            characters = [
                {"role": "caveman", "expression": expr, "prop": "spear" if is_combat_cue else "idle", "pos": pos_slot}
            ]
        elif is_modern_era and is_map:
            characters = [
                {"role": "countryball", "country": "israel", "expression": "angry", "weapon": "ak47", "pos": 0.48},
            ]
        elif is_casualty_cue:
            characters = [
                {"role": "king" if is_king_cue else warrior_role, "expression": "dead", "prop": "idle", "pos": 0.50}
            ]
        elif is_shock_cue:
            characters = [
                {"role": "king" if is_king_cue else warrior_role, "expression": "shocked", "prop": "idle", "pos": 0.50}
            ]
        elif is_victory_cue:
            characters = [
                {"role": "king" if is_king_cue else warrior_role, "expression": "screaming", "prop": "sword" if is_combat_cue else "idle", "pos": 0.50}
            ]
        elif is_cavalry_cue:
            characters = [
                {"role": warrior_role, "expression": "screaming", "prop": "spear", "pos": 0.36}
            ]
        elif is_combat_cue:
            characters = [
                {"role": warrior_role, "expression": "screaming" if is_speech_cue else "angry", "prop": "sword", "pos": pos_slot}
            ]
        elif is_king_cue or (is_speech_cue and any(k in t for k in ["william", "harold", "caesar", "king", "ruler"])):
            expr = "evil_grin" if ("claim" in t or "plot" in t or "rightfully" in t) else ("screaming" if is_speech_cue else "angry")
            characters = [
                {"role": "king", "expression": expr, "prop": "idle", "pos": 0.50}
            ]
        elif is_riot_cue:
            characters = [
                {"role": "peasant", "expression": "screaming", "prop": "broom" if idx % 2 == 0 else "stool", "pos": 0.50}
            ]
        elif is_monk_cue:
            characters = [
                {"role": "monk", "expression": "screaming", "prop": "idle", "pos": 0.50}
            ]
        elif is_speech_cue:
            characters = [
                {"role": warrior_role if is_medieval else "peasant", "expression": "screaming", "prop": "idle", "pos": pos_slot}
            ]
        # Otherwise: characters remains empty (clean scenic/landscape presentation)

        plans.append(ScenePlan(
            index=idx,
            text=cue.text,
            era_badge=current_era if current_era else f"SCENE {idx + 1:02d}",
            scene_type=stype,
            characters=characters,
            sfx=sfx,
            topic=topic,
        ))

    return plans


# =====================================================================
# 5. Master Scene Compositor
# =====================================================================

def compose_animated_scene(plan: ScenePlan, w: int = 1920, h: int = 1080, include_characters: bool = True) -> Image.Image:
    """Renders the complete 16:9 scene background according to the AI Scene Plan."""
    # 1. Base Background Layer
    if plan.scene_type == "throne_room":
        canvas = render_throne_room(w, h)
    elif plan.scene_type == "burning_ruins":
        canvas = render_burning_ruins(w, h)
    elif plan.scene_type in ("map", "countryballs"):
        canvas = render_geopolitical_map(
            w, h,
            topic=plan.topic,
            highlight_name="HASTINGS" if "hastings" in plan.topic.lower() else "JUDEA"
        )
    else:
        canvas = render_ancient_village(w, h)

    # 2. Composite Characters on Stage if static baking requested
    if include_characters:
        for ch in plan.characters:
            pos_ratio = ch.get("pos", 0.5)
            role = ch.get("role", "peasant")
            expr = ch.get("expression", "angry")
            prop = ch.get("prop", "sword")

            if role == "countryball":
                c_ball = render_countryball(country=ch.get("country", "israel"), expression=expr, weapon=ch.get("weapon", "ak47"))
                bx = int(w * pos_ratio) - c_ball.width // 2
                by = int(h * 0.45) if pos_ratio > 0.4 else int(h * 0.65)
                canvas.paste(c_ball, (bx, by), c_ball)
            else:
                char_img = render_cartoon_character(
                    role=role,
                    expression=expr,
                    prop=prop,
                    target_h=int(h * 0.52),
                    facing="right" if pos_ratio < 0.5 else "left",
                )
                cx = int(w * pos_ratio) - char_img.width // 2
                cy = h - char_img.height - 40
                canvas.paste(char_img, (cx, cy), char_img)

    # 3. Stamp Top-Left Era/Date Pill Badge
    stamp_date_pill(canvas, plan.era_badge)

    return canvas


def render_scene_puppet(plan: ScenePlan, target_h: int = 560) -> tuple[str, Image.Image] | None:
    """
    Renders an isolated transparent RGBA character puppet for 60 FPS dialogue animation.
    Returns: (puppet_tag, rgba_image) or None
    """
    if not plan.characters:
        return None

    # Pick the primary character of this scene
    ch = plan.characters[0]
    role = ch.get("role", "peasant")
    expr = ch.get("expression", "angry")
    prop = ch.get("prop", "sword")

    if role == "countryball":
        img = render_countryball(
            country=ch.get("country", "israel"),
            expression=expr,
            weapon=ch.get("weapon", "ak47"),
            size=int(target_h * 0.72)
        )
        tag = f"countryball_{ch.get('country', 'generic')}_{expr}"
        return tag, img

    img = render_cartoon_character(
        role=role,
        expression=expr,
        prop=prop,
        target_h=target_h,
        facing="right"
    )
    tag = f"puppet_{role}_{expr}_{prop}"
    return tag, img


def render_tactical_arrow_animation(
    w: int = 1920,
    h: int = 1080,
    duration: float = 2.0,
    fps: int = 8,
    topic: str = "",
) -> list[Image.Image]:
    """
    Renders an animated tactical invasion arrow surging across the map frame-by-frame.
    """
    total_frames = max(int(round(duration * fps)), 4)
    fx, fy = int(w * 0.46), int(h * 0.74)
    tx, ty = int(w * 0.58), int(h * 0.49)
    ctrl_x = (fx + tx) // 2 + (fy - ty) // 4
    ctrl_y = (fy + ty) // 2 + (tx - fx) // 4
    aw = 16

    frames = []
    for f in range(total_frames):
        t = f / float(fps)
        prog = min(1.0, max(0.08, t / 1.3))

        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        # Generate curve points up to prog
        num_steps = max(4, int(20 * prog))
        curve_pts = []
        for step in range(num_steps + 1):
            s = (step / float(num_steps)) * prog
            cx = (1 - s)**2 * fx + 2 * (1 - s) * s * ctrl_x + s**2 * tx
            cy = (1 - s)**2 * fy + 2 * (1 - s) * s * ctrl_y + s**2 * ty
            curve_pts.append((cx, cy))

        # Shadow stroke
        for pi in range(len(curve_pts) - 1):
            draw.line([curve_pts[pi], curve_pts[pi + 1]], fill="#000000", width=aw + 4)
        # Red invasion stroke
        for pi in range(len(curve_pts) - 1):
            draw.line([curve_pts[pi], curve_pts[pi + 1]], fill="#dc2626", width=aw)

        # Arrowhead at current tip
        if len(curve_pts) >= 2:
            tip_x, tip_y = curve_pts[-1]
            prev_x, prev_y = curve_pts[-2]
            angle = math.atan2(tip_y - prev_y, tip_x - prev_x)
            head_len = aw * 2.8
            p1 = (tip_x - head_len * math.cos(angle - 0.5), tip_y - head_len * math.sin(angle - 0.5))
            p2 = (tip_x - head_len * math.cos(angle + 0.5), tip_y - head_len * math.sin(angle + 0.5))
            draw.polygon([(tip_x, tip_y), p1, p2], fill="#dc2626", outline="#ffffff", width=2)

        # Target Impact Flash Star when arrow arrives
        if prog >= 0.95:
            pulse = 1.0 + 0.3 * math.sin(t * 15)
            sr = int(24 * pulse)
            for a_deg in range(0, 360, 45):
                rad = math.radians(a_deg)
                draw.line([(tx, ty), (tx + int(sr * math.cos(rad)), ty + int(sr * math.sin(rad)))], fill="#fde047", width=4)
            draw.ellipse([tx - 10, ty - 10, tx + 10, ty + 10], fill="#ffffff")

        frames.append(im)

    return frames


def render_scene_animated_sequence(
    plan: ScenePlan,
    duration: float = 2.0,
    fps: int = 8,
    target_h: int = 560,
    target_w: int = 1920,
) -> tuple[str, list[Image.Image]]:
    """
    Renders an authentic Animated History multi-frame 2D animation sequence:
    - Dialogue-synced mouth flaps & head nods
    - Eye blinks
    - Weapon slashes & props
    - Dynamic arrow paths on maps
    Returns: (tag, list_of_rgba_frames)
    """
    text_lower = (plan.text or "").lower()
    total_frames = max(int(round(duration * fps)), 4)

    # 1. Map Tactical Arrow Animation
    if plan.scene_type in ("map",) and (not plan.characters or any(w in text_lower for w in ["arrow", "invade", "invasion", "channel", "fleet", "landed"])):
        frames = render_tactical_arrow_animation(
            w=target_w,
            h=int(target_w * 9 / 16) if target_w == 1920 else 1080,
            duration=duration,
            fps=fps,
            topic=plan.topic,
        )
        return "tactical_arrow_anim", frames

    # 2. Character Animation Sequence
    if not plan.characters:
        return "none", []

    ch = plan.characters[0]
    role = ch.get("role", "peasant")
    expr = ch.get("expression", "angry")
    prop = ch.get("prop", "sword")

    if role == "countryball":
        frames = []
        for f in range(total_frames):
            t = f / float(fps)
            hop = int(22 * abs(math.sin(t * 3.5 * math.pi)))
            blink = (int(t * 10) % 25 in (0, 1)) and t > 0.3
            c_img = render_countryball(
                country=ch.get("country", "israel"),
                expression=expr,
                weapon=ch.get("weapon", "ak47"),
                size=int(target_h * 0.72)
            )
            frames.append(c_img)
        tag = f"countryball_{ch.get('country', 'generic')}_{expr}"
        return tag, frames

    words = (plan.text or "").split()
    speech_duration = min(duration * 0.88, max(1.1, len(words) * 0.32 + 0.3))
    is_battle = "sword" in prop or "battle" in plan.scene_type or any(w in text_lower for w in ["clash", "fight", "strike", "attack", "battle", "war", "charge"])
    is_riot = "broom" in prop or "stool" in prop or any(w in text_lower for w in ["riot", "rebel", "tax", "trouble", "dispute"])

    frames = []
    for f in range(total_frames):
        t = f / float(fps)
        if t < speech_duration:
            # Active dialogue syllables
            mouth_idx = int(t * 7.5) % 4
            mouth = ["mid", "open", "mid", "closed"][mouth_idx]
            if is_battle or expr in ("screaming", "angry"):
                if mouth == "open":
                    mouth = "shout"
            head_nod = 3.5 * math.sin(t * 12)
            hop = int(10 * abs(math.sin(t * 6)))
        else:
            mouth = "closed"
            head_nod = 0.0
            hop = 0

        blink = (int(t * 10) % 25 in (0, 1)) and t > 0.35

        if is_battle:
            arm_ph = (t % 0.75) / 0.75
        elif is_riot:
            arm_ph = 0.5 + 0.5 * math.sin(t * 10)
        else:
            arm_ph = 0.5 + 0.5 * math.sin(t * 5)

        frm = render_cartoon_character(
            role=role,
            expression=expr,
            prop=prop,
            target_h=target_h,
            facing="right",
            mouth_state=mouth,
            blink=blink,
            head_tilt=head_nod,
            arm_phase=arm_ph,
            hop_offset=hop,
        )
        frames.append(frm)

    tag = f"puppet_{role}_{expr}_{prop}"
    return tag, frames

