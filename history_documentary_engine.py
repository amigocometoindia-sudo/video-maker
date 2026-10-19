"""
History Documentary Engine — Animated History & Countryballs System
===================================================================
1-Click Automated Long-Form Documentary Engine inspired by @animatedhistoryy:
- Full-screen 16:9 illustrated cartoon backgrounds:
  1. Ancient Desert Adobe Village (houses, parapets, carts, amphoras)
  2. Royal Arched Stone Throne Room (stone throne, velvet, flaming wall torches)
  3. Roman Military Command Tent (draped canvas folds, sentry outside, command desk, scrolls)
  4. Desert Plateau Mountain Fortress (Masada cliffs, zigzag snake trail, citadel, Roman camps)
  5. Stone Cathedral / Town Square (rose window, cross, twin bell towers, arcades)
  6. Timber Family Cabin Interior (night window, dinner table with bowls, warm oil lamps)
  7. Ancient Coastal Harbor (Caesarea breakwater pier, stone lighthouse, temple, galleys, sea)
  8. Sacked Burning Ruins (crumbled towers, roaring flames, billowing smoke plumes)
  9. Geopolitical Maps & Countryballs (Israel, Egypt, Jordan, Syria, Rome, France, Britain, etc.)
  10. Bastille Stone Fortress (8 medieval towers, drawbridge, moat, French tricolor, Paris smoke)
  11. Guillotine Square (Place de la Révolution, wooden scaffold, angled steel blade, basket)
  12. Versailles Palace (golden gilded gates, neoclassical facade, green parterre box hedges)
  13. French National Assembly (neoclassical hall, tiered wooden benches, speaker rostrum, tricolor)
  14. Imperial Roman Forum (marble temple, Corinthian columns, SPQR standards, travertine plaza)
  15. Roman Colosseum (monumental stone arches, sandy gladiator arena, velarium awnings)
  16. Senlac Hill Shield Wall (rolling English hills, Saxon round shields & spears, Norman pennants)
  17. Western Front Trenches (sandbag parapets, barbed wire, shell craters, wooden duckboards)
  18. Prehistoric Mammoth Steppe (glaciated peaks, woolly mammoth silhouettes, cave campfire)
- Dynamic Museum Historical Archive integration (Wikimedia master paintings & portraits)
- Zero stickmen: clean full-screen panoramic art and historical archive paintings
- Minimalist top-left date pill badge (e.g. '1789 • PARIS', '70 AD • JERUSALEM', '1066 • HASTINGS')
- Deep AI Documentary Researcher & Multi-Chapter Script Engine (supporting 1m, 3m, 5m, 10m, 15m, 30m)
- Synchronized Edge-TTS Neural Voiceover & Clause-Aware SRT generator
- Restrained, subtle sound effects with 25-second cooldown (no annoying spam or camera clicks)
- High-performance multi-threaded NVENC / CPU FFmpeg video rendering with Ken Burns camera motion
"""

import asyncio
import math
import os
import random
import re
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import edge_tts
from srt_parser import Cue
from video_generator import (
    ASPECT_RATIOS,
    GenerationCanceled,
    build_dialogue_motion_expressions,
    _duration_seconds,
    _run_ffmpeg,
    _escape_drawtext,
    VIDEO_FPS,
)
from auto_generator import split_sentence_into_cues, ms_to_srt_time, fetch_topic_historical_archive
from history_chronicles import build_chronicle_script, get_topic_chronicle, ChronicleAct


# =====================================================================
# 1. Font Helpers & Badge Stamping
# =====================================================================

def get_best_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Finds best available clean sans / bold font on Windows."""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/tahomabd.ttf",
        "C:/Windows/Fonts/comicbd.ttf",
    ] if bold else [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/comic.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def stamp_date_pill(im: Image.Image, text: str) -> None:
    """Stamps authentic Animated History minimalist dark translucent date/era pill in top-left."""
    if not text:
        return
    draw = ImageDraw.Draw(im)
    clean_txt = str(text).strip().upper()

    font = get_best_font(34, bold=True)
    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Safe TV action zone margins (prevent Ken Burns zoom cropping)
    px, py = 120, 80
    pw, ph = tw + 44, th + 24

    # Dark translucent pill with border
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(15, 23, 42), outline=(148, 163, 184), width=3)
    draw.text((px + 22, py + 10), clean_txt, fill="#ffffff", font=font)


def fit_archive_image_1080p(src: Image.Image, w: int = 1920, h: int = 1080) -> Image.Image:
    """Crops and fits high-res archive painting into full-frame 16:9 canvas with subtle framing."""
    src_rgba = src.convert("RGBA")
    scale = max(w / max(src.width, 1), h / max(src.height, 1))
    nw = int(src.width * scale)
    nh = int(src.height * scale)
    scaled = src_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    cropped = scaled.crop((left, top, left + w, top + h))
    return cropped.convert("RGB")


# =====================================================================
# 2. Master Vector Scene Renderers (1080p Full-Screen 16:9)
# =====================================================================

def render_ancient_village(w: int = 1920, h: int = 1080) -> Image.Image:
    """Adobe desert village with wooden carts, clay pots, parapet roofs."""
    im = Image.new("RGB", (w, h), "#dfd1b8")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.42)
    for y in range(sky_h):
        ratio = y / max(sky_h, 1)
        r = int(120 + ratio * 85)
        g = int(185 + ratio * 45)
        b = int(220 + ratio * 15)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Fluffy clouds
    for cx, cy, cr in [(300, 110, 70), (370, 95, 85), (450, 115, 65), (1450, 90, 80), (1540, 75, 95), (1630, 95, 75)]:
        draw.ellipse([cx - cr, cy - cr // 2, cx + cr, cy + cr // 2], fill="#ffffff")

    # Distant mountain ridge
    ridge_pts = [(0, sky_h)]
    for rx in range(0, w + 100, 120):
        ry = sky_h - 20 - int(math.sin(rx * 0.008) * 35 + math.cos(rx * 0.015) * 20)
        ridge_pts.append((rx, ry))
    ridge_pts.extend([(w, sky_h), (0, sky_h)])
    draw.polygon(ridge_pts, fill="#cbb793")

    # Ground terrain
    ground_y = sky_h
    draw.rectangle([0, ground_y, w, h], fill="#dfd1b8")
    rnd = random.Random(42)
    for _ in range(50):
        gx = rnd.randint(50, w - 50)
        gy = rnd.randint(ground_y + 80, h - 30)
        gw = rnd.randint(15, 60)
        draw.line([gx, gy, gx + gw, gy + rnd.randint(-4, 4)], fill="#c4b294", width=2)

    # Adobe Houses Left Wing
    draw.polygon([(0, 220), (380, 260), (380, 720), (0, 720)], fill="#d6c3a3", outline="#3b2b1a", width=4)
    for bx in [40, 140, 240, 320]:
        draw.rectangle([bx, 215, bx + 45, 260], fill="#c2ae8e", outline="#3b2b1a", width=3)
    draw.rounded_rectangle([130, 430, 250, 715], radius=50, fill="#2c2217", outline="#3b2b1a", width=4)
    draw.rectangle([260, 310, 310, 370], fill="#38291a", outline="#3b2b1a", width=3)

    # Adobe Houses Right Wing
    draw.polygon([(w - 420, 290), (w, 240), (w, 740), (w - 420, 740)], fill="#d1bd9d", outline="#3b2b1a", width=4)
    for bx in [w - 380, w - 280, w - 180, w - 80]:
        draw.rectangle([bx, 240, bx + 45, 290], fill="#bdab8b", outline="#3b2b1a", width=3)
    draw.rounded_rectangle([w - 300, 450, w - 180, 735], radius=50, fill="#281f15", outline="#3b2b1a", width=4)
    draw.rectangle([w - 380, 340, w - 330, 400], fill="#38291a", outline="#3b2b1a", width=3)

    # Background buildings
    draw.rectangle([680, 340, 880, 560], fill="#c9b595", outline="#3b2b1a", width=3)
    draw.rectangle([1040, 320, 1260, 560], fill="#c4b090", outline="#3b2b1a", width=3)

    # Wooden Cart & Wheel on Left
    cart_x, cart_y = 70, 680
    draw.polygon([(cart_x, cart_y - 60), (cart_x + 160, cart_y - 40), (cart_x + 150, cart_y + 10), (cart_x - 10, cart_y - 10)], fill="#8b5a2b", outline="#2b1a0e", width=4)
    wx, wy, wr = cart_x + 90, cart_y + 35, 65
    draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr], fill="#6a3e1b", outline="#2b1a0e", width=5)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        draw.line([wx, wy, wx + math.cos(rad) * wr, wy + math.sin(rad) * wr], fill="#2b1a0e", width=3)

    # Clay Amphoras / Pots
    for px, py, pw, ph, clr in [(420, 720, 45, 60, "#a05a2c"), (465, 730, 40, 50, "#8b4513")]:
        draw.ellipse([px, py, px + pw, py + ph], fill=clr, outline="#2c1709", width=3)

    return im


def render_throne_room(w: int = 1920, h: int = 1080) -> Image.Image:
    """Royal stone throne room with velvet cushion, dais steps, wall torches."""
    im = Image.new("RGB", (w, h), "#1e1815")
    draw = ImageDraw.Draw(im)

    brick_h = 75
    for row, y in enumerate(range(0, h, brick_h)):
        offset = (row % 2) * 90
        for x in range(-90, w + 180, 180):
            bx = x + offset
            shade = 32 + (row * 3 + (bx // 180) * 7) % 18
            draw.rectangle([bx, y, bx + 175, y + brick_h - 5], fill=(shade, shade - 6, shade - 10), outline="#110d0a", width=2)

    arch_cx, arch_w, arch_h = w // 2, 600, 700
    draw.rounded_rectangle([arch_cx - arch_w // 2, 100, arch_cx + arch_w // 2, 800], radius=180, fill="#130e0b", outline="#0a0705", width=6)

    # Dais Steps
    draw.polygon([(arch_cx - 420, 780), (arch_cx + 420, 780), (arch_cx + 520, 920), (arch_cx - 520, 920)], fill="#3a2e24", outline="#150f0b", width=4)
    draw.rectangle([arch_cx - 550, 920, arch_cx + 550, h], fill="#2d2218", outline="#150f0b", width=4)

    # Stone Throne
    tx, ty = arch_cx, 440
    draw.polygon([(tx - 160, ty - 220), (tx + 160, ty - 220), (tx + 190, ty + 240), (tx - 190, ty + 240)], fill="#4a3e35", outline="#1a140f", width=5)
    draw.polygon([(tx - 160, ty - 220), (tx, ty - 290), (tx + 160, ty - 220)], fill="#5c4d42", outline="#1a140f", width=5)
    draw.rectangle([tx - 230, ty + 60, tx - 170, ty + 260], fill="#55463b", outline="#1a140f", width=4)
    draw.rectangle([tx + 170, ty + 60, tx + 230, ty + 260], fill="#55463b", outline="#1a140f", width=4)
    draw.rounded_rectangle([tx - 150, ty + 120, tx + 150, ty + 240], radius=15, fill="#7f1d1d", outline="#450a0a", width=3)

    # Torches on both sides
    for torch_x in [280, w - 280]:
        draw.line([torch_x, 340, torch_x, 460], fill="#1c1612", width=10)
        draw.polygon([(torch_x - 16, 340), (torch_x + 16, 340), (torch_x + 24, 300), (torch_x - 24, 300)], fill="#403227", outline="#150f0b", width=3)
        glow_r = 140
        for r_step in range(glow_r, 20, -25):
            draw.ellipse([torch_x - r_step, 260 - r_step, torch_x + r_step, 260 + r_step], outline=(255, 170, 40, 20), width=16)
        draw.polygon([(torch_x, 180), (torch_x + 35, 270), (torch_x + 20, 310), (torch_x - 20, 310), (torch_x - 35, 270)], fill="#f97316")
        draw.polygon([(torch_x, 210), (torch_x + 18, 280), (torch_x - 18, 280)], fill="#fde047")

    return im


def render_military_tent(w: int = 1920, h: int = 1080) -> Image.Image:
    """Roman military command tent with draped folds, sentry outside, command desk, scrolls."""
    im = Image.new("RGB", (w, h), "#4d3d2e")
    draw = ImageDraw.Draw(im)

    # Tent ceiling ridge & support poles
    draw.polygon([(0, 40), (w, 40), (w, 85), (0, 85)], fill="#2c2016", outline="#150e09", width=4)
    for px in [320, int(w * 0.65)]:
        draw.polygon([(px - 14, 40), (px + 14, 40), (px + 18, h), (px - 18, h)], fill="#2c2016", outline="#150e09", width=4)

    # Draped tent canvas folds with shading
    for fx in range(-60, w + 120, 240):
        draw.polygon([(fx, 80), (fx + 120, 80), (fx + 180, int(h * 0.72)), (fx - 40, int(h * 0.72))], fill="#594634", outline="#2c2016", width=3)
        draw.polygon([(fx + 120, 80), (fx + 240, 80), (fx + 280, int(h * 0.72)), (fx + 180, int(h * 0.72))], fill="#66513d", outline="#2c2016", width=3)

    # Doorway flap opening to sunny desert camp
    door_l = int(w * 0.66)
    door_r = int(w * 0.88)
    door_top = int(h * 0.26)
    door_bot = int(h * 0.75)

    draw.rectangle([door_l, door_top, door_r, door_bot], fill="#48cae4")
    draw.rectangle([door_l, int(h * 0.52), door_r, door_bot], fill="#e0d0b4")
    draw.polygon([(door_l, int(h * 0.52)), (door_r, int(h * 0.52)), (door_r, int(h * 0.48)), (door_l, int(h * 0.50))], fill="#c7b089")

    # Draped curtains at doorway
    draw.polygon([(door_l - 40, door_top - 20), (door_l + 20, door_top - 20), (door_l - 10, door_bot), (door_l - 60, door_bot)], fill="#4a392b", outline="#1f160e", width=4)
    draw.polygon([(door_r + 40, door_top - 20), (door_r - 20, door_top - 20), (door_r + 10, door_bot), (door_r + 60, door_bot)], fill="#4a392b", outline="#1f160e", width=4)
    draw.rounded_rectangle([door_l - 30, door_top - 40, door_r + 30, door_top + 10], radius=15, fill="#7d624a", outline="#2c2016", width=4)
    for bx in range(door_l - 10, door_r + 20, 35):
        draw.line([bx, door_top - 40, bx, door_top + 10], fill="#2c2016", width=3)

    # Ground floor
    draw.polygon([(0, int(h * 0.70)), (w, int(h * 0.70)), (w, h), (0, h)], fill="#9e8564")

    # Campaign Desk
    desk_cx = int(w * 0.58)
    desk_w = 480
    desk_top = int(h * 0.64)
    draw.polygon([
        (desk_cx - desk_w//2 + 30, desk_top),
        (desk_cx + desk_w//2 - 30, desk_top),
        (desk_cx + desk_w//2, desk_top + 50),
        (desk_cx - desk_w//2, desk_top + 50)
    ], fill="#3b2b1d", outline="#170f09", width=4)
    for leg_x in [desk_cx - desk_w//2 + 40, desk_cx + desk_w//2 - 40]:
        draw.rectangle([leg_x - 10, desk_top + 50, leg_x + 10, int(h * 0.89)], fill="#241912", outline="#0a0604", width=3)

    # Scrolls on table
    draw.polygon([(desk_cx - 80, desk_top + 10), (desk_cx + 80, desk_top + 10), (desk_cx + 95, desk_top + 45), (desk_cx - 65, desk_top + 45)], fill="#e8d5b5", outline="#59442b", width=2)
    draw.ellipse([desk_cx + 110, desk_top + 20, desk_cx + 155, desk_top + 38], fill="#d4be98", outline="#59442b", width=2)

    return im


def render_fortress_plateau(w: int = 1920, h: int = 1080) -> Image.Image:
    """Masada-style desert plateau mountain fortress with winding trail and surrounding camps."""
    im = Image.new("RGB", (w, h), "#dfd1b8")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.18)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(210 + y * 0.2), int(225 + y * 0.1), 240))

    # Horizon & Dead Sea
    draw.polygon([(0, sky_h), (w, sky_h), (w, int(h * 0.35)), (0, int(h * 0.35))], fill="#c7b089")
    draw.polygon([(int(w * 0.65), int(h * 0.22)), (w, int(h * 0.20)), (w, int(h * 0.28)), (int(w * 0.72), int(h * 0.30))], fill="#2b82a2")

    # Mountain Slopes
    mt_top_y = int(h * 0.28)
    mt_bot_y = int(h * 0.90)
    mt_l_top = int(w * 0.26)
    mt_r_top = int(w * 0.88)

    draw.polygon([
        (mt_l_top, mt_top_y),
        (mt_r_top, mt_top_y),
        (int(w * 0.96), mt_bot_y),
        (int(w * 0.12), mt_bot_y),
    ], fill="#cbb286", outline="#3b2b1a", width=5)

    # Striations
    for rx in range(int(w * 0.20), int(w * 0.90), 80):
        draw.line([(rx, mt_top_y + 15), (rx + int(math.sin(rx)*40), mt_bot_y - 20)], fill="#ad9368", width=4)

    # Zigzag Trail
    snake_path = [
        (int(w * 0.40), mt_bot_y - 10),
        (int(w * 0.52), mt_bot_y - 100),
        (int(w * 0.38), mt_bot_y - 220),
        (int(w * 0.55), mt_bot_y - 340),
        (int(w * 0.42), mt_bot_y - 460),
        (int(w * 0.48), mt_top_y + 40),
        (int(w * 0.39), mt_top_y),
    ]
    for spi in range(len(snake_path) - 1):
        draw.line([snake_path[spi], snake_path[spi + 1]], fill="#f3ead8", width=12)
        draw.line([snake_path[spi], snake_path[spi + 1]], fill="#a3895e", width=4)

    # Citadel Walls atop Plateau
    fw_l = mt_l_top - 15
    fw_r = mt_r_top + 15
    fw_h = 95
    draw.polygon([
        (fw_l, mt_top_y),
        (fw_r, mt_top_y),
        (fw_r, mt_top_y - fw_h),
        (fw_l, mt_top_y - fw_h)
    ], fill="#9d835e", outline="#332211", width=5)

    for cx in range(fw_l, fw_r, 40):
        draw.rectangle([cx, mt_top_y - fw_h - 18, cx + 22, mt_top_y - fw_h], fill="#9d835e", outline="#332211", width=3)

    return im


def render_church_town_square(w: int = 1920, h: int = 1080) -> Image.Image:
    """Byzantine / Medieval stone cathedral with rose window, cross, arcades."""
    im = Image.new("RGB", (w, h), "#dfd1b8")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.35)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(150 + int(y * 0.2), 200, 235))
    for cx, cy in [(350, 90), (1450, 80)]:
        draw.ellipse([cx - 90, cy - 35, cx + 90, cy + 35], fill="#ffffff")

    ground_y = int(h * 0.55)
    draw.rectangle([0, ground_y, w, h], fill="#dfd1b8")

    # City Arcades Left & Right
    for wx in [0, w - 480]:
        draw.rectangle([wx, 260, wx + 480, ground_y], fill="#c9b595", outline="#3b2b1a", width=5)
        for bx in range(wx + 30, wx + 460, 75):
            draw.rectangle([bx, 220, bx + 45, 260], fill="#b8a484", outline="#3b2b1a", width=3)
        for ax in range(wx + 50, wx + 420, 130):
            draw.rounded_rectangle([ax, 380, ax + 85, ground_y], radius=40, fill="#2c2217", outline="#3b2b1a", width=4)

    # Cathedral Facade
    cx = w // 2
    cw = 620
    ch_top = 220
    draw.rectangle([cx - cw//2, ch_top, cx + cw//2, ground_y], fill="#d6c3a3", outline="#3b2b1a", width=5)
    draw.polygon([(cx - cw//2 - 20, ch_top), (cx, ch_top - 180), (cx + cw//2 + 20, ch_top)], fill="#bdab8b", outline="#3b2b1a", width=5)

    # Rose Window
    rw_r = 75
    draw.ellipse([cx - rw_r, ch_top + 45 - rw_r, cx + rw_r, ch_top + 45 + rw_r], fill="#261d15", outline="#3b2b1a", width=6)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        draw.line([cx, ch_top + 45, cx + math.cos(rad) * rw_r, ch_top + 45 + math.sin(rad) * rw_r], fill="#3b2b1a", width=3)

    return im


def render_family_cabin(w: int = 1920, h: int = 1080) -> Image.Image:
    """Timber cabin dining room with table, bowls, glowing oil lamp."""
    im = Image.new("RGB", (w, h), "#1e1e1e")
    draw = ImageDraw.Draw(im)

    # Wall planks
    for y in range(0, int(h * 0.75), 55):
        shade = 32 + (y % 110) // 10
        draw.rectangle([0, y, w, y + 50], fill=(shade, shade - 6, shade - 12), outline="#111111", width=2)

    # Night window
    win_cx, win_cy, win_w, win_h = w // 2, 280, 260, 320
    draw.rectangle([win_cx - win_w//2, win_cy - win_h//2, win_cx + win_w//2, win_cy + win_h//2], fill="#111c2e", outline="#3d3126", width=10)
    draw.line([win_cx, win_cy - win_h//2, win_cx, win_cy + win_h//2], fill="#3d3126", width=6)
    draw.line([win_cx - win_w//2, win_cy, win_cx + win_w//2, win_cy], fill="#3d3126", width=6)

    # Dinner Table
    tbl_top = int(h * 0.62)
    tbl_left = 220
    tbl_right = w - 220
    draw.polygon([
        (tbl_left + 60, tbl_top),
        (tbl_right - 60, tbl_top),
        (tbl_right, tbl_top + 90),
        (tbl_left, tbl_top + 90)
    ], fill="#42352b", outline="#1a140f", width=5)

    # Oil Lamps with soft glow
    for lamp_x, lamp_y in [(120, int(h * 0.65)), (w - 120, int(h * 0.65))]:
        glow_r = 120
        for r_step in range(glow_r, 20, -25):
            draw.ellipse([lamp_x - r_step, lamp_y - r_step, lamp_x + r_step, lamp_y + r_step], outline=(255, 200, 80, 25), width=16)
        draw.ellipse([lamp_x - 22, lamp_y + 10, lamp_x + 22, lamp_y + 35], fill="#92400e", outline="#451a03", width=3)

    return im


def render_coastal_harbor(w: int = 1920, h: int = 1080) -> Image.Image:
    """Ancient harbor with breakwater pier, lighthouse, galleys, sea."""
    im = Image.new("RGB", (w, h), "#5294b8")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.22)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(140 + y * 0.3), int(200 + y * 0.2), int(235 + y * 0.1)))

    # Blue sea
    draw.polygon([(int(w * 0.30), sky_h), (w, sky_h), (w, h), (int(w * 0.20), h)], fill="#2b7aa1")

    # Coastline
    draw.polygon([(0, sky_h), (int(w * 0.35), sky_h), (int(w * 0.28), int(h * 0.55)), (int(w * 0.20), h), (0, h)], fill="#c9b990")

    # Stone Breakwater Pier
    pier_points = [
        (int(w * 0.25), int(h * 0.58)),
        (int(w * 0.55), int(h * 0.74)),
        (int(w * 0.65), int(h * 0.72)),
        (int(w * 0.70), int(h * 0.58)),
        (int(w * 0.62), int(h * 0.40)),
        (int(w * 0.50), int(h * 0.40)),
        (int(w * 0.48), int(h * 0.44)),
        (int(w * 0.58), int(h * 0.44)),
        (int(w * 0.64), int(h * 0.56)),
        (int(w * 0.60), int(h * 0.68)),
        (int(w * 0.54), int(h * 0.70)),
        (int(w * 0.26), int(h * 0.55)),
    ]
    draw.polygon(pier_points, fill="#8ea2aa", outline="#222e33", width=4)

    # Stone Lighthouse
    lh_x, lh_y = int(w * 0.63), int(h * 0.66)
    draw.polygon([(lh_x - 30, lh_y + 45), (lh_x + 30, lh_y + 45), (lh_x + 20, lh_y - 75), (lh_x - 20, lh_y - 75)], fill="#a2b3bb", outline="#1c2428", width=4)

    return im


def render_burning_ruins(w: int = 1920, h: int = 1080) -> Image.Image:
    """Sacked ruined battlefield with billowing smoke, fire, crumbled walls."""
    im = Image.new("RGB", (w, h), "#24252a")
    draw = ImageDraw.Draw(im)

    for y in range(int(h * 0.5)):
        ratio = y / (h * 0.5)
        draw.line([(0, y), (w, y)], fill=(int(55 - ratio * 15), int(60 - ratio * 18), int(70 - ratio * 20)))

    # Billowing smoke
    for sx in [220, 460, 920, 1420, 1700]:
        for si in range(7):
            sm_y = int(h * 0.55) - si * 65
            sm_r = 60 + si * 18
            sm_x = sx + int(math.sin(si + sx) * 45)
            shade = max(25, 65 - si * 6)
            draw.ellipse([sm_x - sm_r, sm_y - sm_r // 2, sm_x + sm_r, sm_y + sm_r // 2], fill=(shade, shade, shade + 4))

    # Crumbled stone walls
    draw.polygon([(60, 720), (60, 380), (120, 340), (190, 410), (280, 360), (360, 430), (360, 720)], fill="#3d3f47", outline="#1c1d22", width=5)
    draw.polygon([(w - 420, 720), (w - 420, 400), (w - 340, 350), (w - 270, 420), (w - 180, 370), (w - 80, 430), (w - 80, 720)], fill="#383940", outline="#1c1d22", width=5)

    # Flames
    for fx, fy, fw, fh in [(100, 370, 90, 140), (260, 390, 110, 160), (w - 360, 380, 120, 170)]:
        draw.polygon([(fx + fw // 2, fy - fh), (fx + fw, fy), (fx + fw * 0.7, fy - fh * 0.3), (fx, fy)], fill="#ea580c")
        draw.polygon([(fx + fw // 2, fy - fh * 0.7), (fx + fw * 0.8, fy), (fx + fw * 0.2, fy)], fill="#facc15")

    ground_y = int(h * 0.65)
    draw.rectangle([0, ground_y, w, h], fill="#27272a")

    return im


def render_countryballs_war_scene(w: int = 1920, h: int = 1080, topic: str = "") -> Image.Image:
    """Geopolitical regional map with multiple Countryballs facing each other with weapons."""
    from animated_history_engine import render_geopolitical_map, render_countryball
    canvas = render_geopolitical_map(w, h, topic=topic, highlight_name="FRONTLINE")

    # Add appropriate Countryballs on map
    top_low = topic.lower()
    if "israel" in top_low:
        israel_ball = render_countryball("israel", expression="angry", weapon="ak47", size=220)
        canvas.paste(israel_ball, (int(w * 0.44), int(h * 0.38)), israel_ball)
        egypt_ball = render_countryball("egypt", expression="angry", weapon="ak47", size=180)
        canvas.paste(egypt_ball, (int(w * 0.22), int(h * 0.65)), egypt_ball)
        jordan_ball = render_countryball("jordan", expression="angry", weapon="ak47", size=180)
        canvas.paste(jordan_ball, (int(w * 0.64), int(h * 0.42)), jordan_ball)
    elif "france" in top_low or "french" in top_low or "napoleon" in top_low:
        france_ball = render_countryball("france", expression="angry", weapon="sword", size=220)
        canvas.paste(france_ball, (int(w * 0.42), int(h * 0.40)), france_ball)
        britain_ball = render_countryball("britain", expression="angry", weapon="musket", size=190)
        canvas.paste(britain_ball, (int(w * 0.30), int(h * 0.18)), britain_ball)
    else:
        ball1 = render_countryball("rome", expression="angry", weapon="sword", size=200)
        canvas.paste(ball1, (int(w * 0.45), int(h * 0.45)), ball1)

    return canvas


# =====================================================================
# 3. New Topic-Specific Vector Renderers (French, Rome, Hastings, WW1, etc.)
# =====================================================================

def render_bastille_fortress(w: int = 1920, h: int = 1080) -> Image.Image:
    """Massive 8-tower stone Bastille fortress with drawbridge, moat, French tricolor, Paris smoke."""
    im = Image.new("RGB", (w, h), "#1e2430")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.40)
    for y in range(sky_h):
        ratio = y / max(sky_h, 1)
        draw.line([(0, y), (w, y)], fill=(int(55 + ratio * 35), int(70 + ratio * 35), int(95 + ratio * 30)))

    # Mansard roofs in background
    for bx in range(0, 420, 70):
        bh = 120 + ((bx * 7) % 60)
        draw.rectangle([bx, sky_h - bh + 60, bx + 65, sky_h + 80], fill="#333b4d", outline="#1a1e28", width=2)
    for bx in range(w - 420, w, 70):
        bh = 120 + ((bx * 11) % 60)
        draw.rectangle([bx, sky_h - bh + 60, bx + 65, sky_h + 80], fill="#333b4d", outline="#1a1e28", width=2)

    # Smoke plumes
    for sx, sy_base, count in [(320, sky_h - 40, 6), (1580, sky_h - 50, 6)]:
        for si in range(count):
            sm_y = sy_base - si * 50
            sm_r = 55 + si * 18
            sm_x = sx + int(math.sin(si * 1.3) * 35)
            shade = max(40, 95 - si * 9)
            draw.ellipse([sm_x - sm_r, sm_y - sm_r // 2, sm_x + sm_r, sm_y + sm_r // 2], fill=(shade + 10, shade, shade - 5))

    # Fortress Curtain Wall & Towers
    fort_l, fort_r = 360, w - 360
    wall_top, wall_bot = int(h * 0.24), int(h * 0.72)
    draw.rectangle([fort_l, wall_top, fort_r, wall_bot], fill="#474b57", outline="#1f2229", width=5)

    towers = [
        (fort_l + 40, int(h * 0.16), 170),
        (fort_l + 310, int(h * 0.18), 160),
        (fort_r - 310, int(h * 0.18), 160),
        (fort_r - 40, int(h * 0.16), 170),
    ]
    for tx, t_top, tw in towers:
        t_left, t_right = tx - tw // 2, tx + tw // 2
        draw.rectangle([t_left, t_top, t_right, wall_bot], fill="#505563", outline="#1c1f26", width=5)
        draw.rectangle([t_left + 15, t_top, t_left + tw // 3, wall_bot], fill="#5f6575")
        draw.rectangle([t_right - tw // 3, t_top, t_right - 10, wall_bot], fill="#3b3e48")
        for cbx in range(t_left, t_right, 32):
            draw.rectangle([cbx, t_top - 24, cbx + 18, t_top], fill="#444955", outline="#1c1f26", width=3)
        for slit_y in [t_top + 100, t_top + 220, t_top + 340]:
            draw.rectangle([tx - 6, slit_y, tx + 6, slit_y + 40], fill="#15171c", outline="#2b2e38", width=2)

    # Gateway & Drawbridge
    gate_cx, gate_w, gate_h = w // 2, 260, 320
    draw.rounded_rectangle([gate_cx - gate_w // 2, wall_bot - gate_h, gate_cx + gate_w // 2, wall_bot], radius=130, fill="#13151a", outline="#0a0c0f", width=6)

    db_l, db_r = gate_cx - 150, gate_cx + 150
    db_top, db_bot = wall_bot - 40, int(h * 0.85)
    draw.polygon([(db_l, db_top), (db_r, db_top), (db_r + 40, db_bot), (db_l - 40, db_bot)], fill="#66462c", outline="#281a10", width=5)
    for py in range(db_top + 20, db_bot, 22):
        draw.line([(db_l - 20, py), (db_r + 20, py)], fill="#4a321e", width=3)
    draw.line([gate_cx - 120, wall_bot - gate_h + 30, db_l - 30, db_bot - 10], fill="#94a3b8", width=5)
    draw.line([gate_cx + 120, wall_bot - gate_h + 30, db_r + 30, db_bot - 10], fill="#94a3b8", width=5)

    # Moat & Cobblestone
    moat_bot = int(h * 0.88)
    draw.polygon([(0, wall_bot - 10), (w, wall_bot - 10), (w, moat_bot), (0, moat_bot)], fill="#1f3644", outline="#0e1a22", width=4)
    draw.rectangle([0, moat_bot, w, h], fill="#383d47")

    # French Tricolor Flag
    flag_x = towers[1][0]
    flag_top_y = towers[1][1] - 120
    draw.line([flag_x, towers[1][1] - 24, flag_x, flag_top_y], fill="#0f172a", width=5)
    fw, fh = 90, 55
    draw.rectangle([flag_x, flag_top_y, flag_x + fw // 3, flag_top_y + fh], fill="#1d4ed8")
    draw.rectangle([flag_x + fw // 3, flag_top_y, flag_x + (2 * fw) // 3, flag_top_y + fh], fill="#ffffff")
    draw.rectangle([flag_x + (2 * fw) // 3, flag_top_y, flag_x + fw, flag_top_y + fh], fill="#dc2626")

    return im


def render_guillotine_square(w: int = 1920, h: int = 1080) -> Image.Image:
    """Place de la Révolution: wooden scaffold platform, angled steel blade, wicker basket, Paris plaza."""
    im = Image.new("RGB", (w, h), "#3d4450")
    draw = ImageDraw.Draw(im)

    # Gloomy Paris overcast sky
    sky_h = int(h * 0.45)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(90 + (y / sky_h) * 45), int(105 + (y / sky_h) * 40), int(125 + (y / sky_h) * 35)))

    # Neoclassical Paris background
    bldg_top, bldg_bot = int(h * 0.22), int(h * 0.58)
    draw.rectangle([0, bldg_top, w, bldg_bot], fill="#787f8d", outline="#2b303c", width=4)
    for col_x in range(60, w - 60, 110):
        draw.rectangle([col_x, bldg_top + 40, col_x + 35, bldg_bot], fill="#9199a8", outline="#2b303c", width=2)
        draw.rounded_rectangle([col_x - 10, bldg_top + 90, col_x + 45, bldg_bot - 40], radius=15, fill="#232731", outline="#1a1c22", width=2)

    # Cobblestone ground
    draw.rectangle([0, bldg_bot, w, h], fill="#4f5460")

    # Wooden Scaffold / Platform
    scaf_w, scaf_h = 640, 160
    scaf_cx = w // 2
    scaf_top = int(h * 0.56)
    scaf_bot = scaf_top + scaf_h
    scaf_l, scaf_r = scaf_cx - scaf_w // 2, scaf_cx + scaf_w // 2

    draw.polygon([(scaf_l - 40, scaf_bot), (scaf_r + 40, scaf_bot), (scaf_r, scaf_top), (scaf_l, scaf_top)], fill="#854d27", outline="#381e0d", width=5)
    for si in range(6):
        sy = scaf_top + si * 26
        draw.rectangle([scaf_r + 15 - si * 6, sy, scaf_r + 110 - si * 6, sy + 24], fill="#6b3d1c", outline="#2e190b", width=3)

    # Red railing
    draw.rectangle([scaf_l, scaf_top - 45, scaf_r, scaf_top], fill="#991b1b", outline="#450a0a", width=3)

    # THE GUILLOTINE
    g_cx = scaf_cx
    g_base_y = scaf_top - 20
    g_h = 360
    g_top_y = g_base_y - g_h
    post_dist = 60

    draw.rectangle([g_cx - post_dist - 14, g_top_y, g_cx - post_dist + 14, g_base_y], fill="#451a03", outline="#1c0701", width=4)
    draw.rectangle([g_cx + post_dist - 14, g_top_y, g_cx + post_dist + 14, g_base_y], fill="#451a03", outline="#1c0701", width=4)
    draw.rectangle([g_cx - post_dist - 28, g_top_y - 20, g_cx + post_dist + 28, g_top_y], fill="#3d1401", outline="#1c0701", width=4)

    # Angled Steel Blade
    blade_y = g_top_y + 70
    draw.polygon([
        (g_cx - post_dist + 14, blade_y),
        (g_cx + post_dist - 14, blade_y),
        (g_cx + post_dist - 14, blade_y + 65),
        (g_cx - post_dist + 14, blade_y + 115),
    ], fill="#e2e8f0", outline="#334155", width=4)

    # Lunette & Wicker Basket
    draw.rounded_rectangle([g_cx - 40, g_base_y - 75, g_cx + 40, g_base_y], radius=8, fill="#5c2c0d", outline="#1c0701", width=3)
    draw.ellipse([g_cx - 18, g_base_y - 55, g_cx + 18, g_base_y - 22], fill="#0a0502", outline="#2b1104", width=3)
    draw.rounded_rectangle([g_cx - 85, g_base_y - 45, g_cx - 45, g_base_y + 10], radius=6, fill="#b45309", outline="#451a03", width=3)

    # Tricolor ribbon
    draw.rectangle([scaf_l + 40, scaf_top - 40, scaf_l + 80, scaf_top - 10], fill="#1d4ed8")
    draw.rectangle([scaf_l + 80, scaf_top - 40, scaf_l + 120, scaf_top - 10], fill="#ffffff")
    draw.rectangle([scaf_l + 120, scaf_top - 40, scaf_l + 160, scaf_top - 10], fill="#dc2626")

    return im


def render_versailles_palace(w: int = 1920, h: int = 1080) -> Image.Image:
    """Neoclassical Palace of Versailles: golden gilded gates, classical facade, parterre gardens."""
    im = Image.new("RGB", (w, h), "#7ec8f2")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.36)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(110 + (y / sky_h) * 70), int(185 + (y / sky_h) * 45), 245))

    palace_top, palace_bot = int(h * 0.22), int(h * 0.58)
    draw.rectangle([0, palace_top, w, palace_bot], fill="#e8d5b5", outline="#4a3721", width=5)

    # Windows
    for wx in range(60, w - 60, 115):
        draw.rounded_rectangle([wx, palace_top + 25, wx + 45, palace_top + 95], radius=20, fill="#1e3a5f", outline="#3b2b1a", width=3)
        draw.rounded_rectangle([wx, palace_top + 125, wx + 45, palace_bot - 15], radius=22, fill="#1e3a5f", outline="#3b2b1a", width=3)

    # Pediment
    p_cx = w // 2
    draw.polygon([(p_cx - 220, palace_top - 35), (p_cx, palace_top - 120), (p_cx + 220, palace_top - 35)], fill="#dccab0", outline="#4a3721", width=5)

    # Courtyard
    draw.rectangle([0, palace_bot, w, h], fill="#dfceb1")

    # Parterre green box hedges
    for hedge_l, hedge_r in [(80, 480), (w - 480, w - 80)]:
        draw.rounded_rectangle([hedge_l, int(h * 0.64), hedge_r, int(h * 0.88)], radius=25, fill="#2d6a4f", outline="#1b4332", width=4)
        draw.rounded_rectangle([hedge_l + 35, int(h * 0.68), hedge_r - 35, int(h * 0.84)], radius=18, fill="#52b788", outline="#1b4332", width=3)

    # Gilded Golden Gates in Foreground
    gate_top = int(h * 0.60)
    for gx in range(380, w - 380, 26):
        draw.line([gx, gate_top, gx, h], fill="#ca8a04", width=6)
        draw.polygon([(gx - 8, gate_top), (gx, gate_top - 24), (gx + 8, gate_top)], fill="#eab308", outline="#854d0e", width=2)
    for ry in [gate_top + 45, gate_top + 160, int(h * 0.88)]:
        draw.rectangle([360, ry - 6, w - 360, ry + 6], fill="#a16207", outline="#713f12", width=2)

    return im


def render_french_assembly(w: int = 1920, h: int = 1080) -> Image.Image:
    """French National Assembly / Tennis Court Oath chamber with tiered benches, speaker rostrum."""
    im = Image.new("RGB", (w, h), "#2b2a27")
    draw = ImageDraw.Draw(im)

    ceil_h = int(h * 0.32)
    col_bot = int(h * 0.70)
    for cx in range(80, w, 160):
        draw.rectangle([cx - 20, ceil_h, cx + 20, col_bot], fill="#c7baa3", outline="#423b30", width=3)

    # Tricolor banners
    for bx in range(160, w - 160, 320):
        bw, by = 100, ceil_h + 50
        draw.rectangle([bx, by, bx + bw//3, by + 120], fill="#1d4ed8")
        draw.rectangle([bx + bw//3, by, bx + (2*bw)//3, by + 120], fill="#ffffff")
        draw.rectangle([bx + (2*bw)//3, by, bx + bw, by + 120], fill="#dc2626")

    # Tiered Benches
    for tier_i in range(4):
        ty = col_bot - 110 + tier_i * 65
        tw_left, tw_right = 60 + tier_i * 50, w - 60 - tier_i * 50
        draw.polygon([(tw_left, ty), (tw_right, ty), (tw_right + 30, ty + 50), (tw_left - 30, ty + 50)], fill="#663c1a", outline="#291607", width=4)

    # Speaker Tribune / Podium
    pod_w, pod_h, pod_cx = 420, 240, w // 2
    pod_top = int(h * 0.72)
    draw.polygon([(pod_cx - pod_w//2 + 30, pod_top), (pod_cx + pod_w//2 - 30, pod_top), (pod_cx + pod_w//2, pod_top + pod_h), (pod_cx - pod_w//2, pod_top + pod_h)], fill="#4f2d12", outline="#1c0f05", width=5)
    draw.polygon([(pod_cx - 90, pod_top + 10), (pod_cx + 90, pod_top + 10), (pod_cx + 105, pod_top + 60), (pod_cx - 75, pod_top + 60)], fill="#fef3c7", outline="#92400e", width=3)
    draw.ellipse([pod_cx - 35, pod_top + 100, pod_cx + 35, pod_top + 170], fill="#1d4ed8")
    draw.ellipse([pod_cx - 24, pod_top + 111, pod_cx + 24, pod_top + 159], fill="#ffffff")
    draw.ellipse([pod_cx - 12, pod_top + 123, pod_cx + 12, pod_top + 147], fill="#dc2626")

    return im


def render_roman_forum(w: int = 1920, h: int = 1080) -> Image.Image:
    """Imperial Roman Forum: marble Temple of Jupiter, Corinthian columns, SPQR standard."""
    im = Image.new("RGB", (w, h), "#5ba2d6")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.42)
    plaza_top = int(h * 0.52)
    draw.rectangle([0, plaza_top, w, h], fill="#e8dfce")

    # Arch on left
    arch_l, arch_w, arch_top, arch_bot = 80, 420, int(h * 0.22), plaza_top + 60
    draw.rectangle([arch_l, arch_top, arch_l + arch_w, arch_bot], fill="#ded5c4", outline="#403628", width=5)
    draw.rounded_rectangle([arch_l + 130, arch_top + 130, arch_l + arch_w - 130, arch_bot], radius=75, fill="#3b3225", outline="#211b13", width=5)

    # Temple of Saturn in Center-Right
    t_cx, t_w = int(w * 0.65), 860
    t_top, t_podium_top = int(h * 0.18), int(h * 0.58)

    draw.polygon([(t_cx - t_w//2, t_top), (t_cx, t_top - 140), (t_cx + t_w//2, t_top)], fill="#f0ebe0", outline="#3a3227", width=6)
    draw.rectangle([t_cx - t_w//2 - 15, t_top, t_cx + t_w//2 + 15, t_top + 45], fill="#e4dbcc", outline="#3a3227", width=4)
    font_spqr = get_best_font(26, bold=True)
    draw.text((t_cx - 160, t_top + 8), "SENATVS POPVLVSQVE ROMANVS", fill="#ca8a04", font=font_spqr)

    col_spacing = t_w // 7
    for ci in range(1, 7):
        col_x = (t_cx - t_w // 2) + ci * col_spacing
        draw.rectangle([col_x - 20, t_top + 45, col_x + 20, t_podium_top], fill="#f5f0e6", outline="#3a3227", width=3)

    draw.polygon([(t_cx - t_w//2 - 40, t_podium_top), (t_cx + t_w//2 + 40, t_podium_top), (t_cx + t_w//2 + 90, plaza_top + 160), (t_cx - t_w//2 - 90, plaza_top + 160)], fill="#ded5c4", outline="#3a3227", width=5)

    # Red & Gold SPQR Standard
    std_x, std_top = int(w * 0.22), int(h * 0.38)
    draw.line([std_x, std_top - 50, std_x, plaza_top + 180], fill="#ca8a04", width=8)
    draw.polygon([(std_x - 30, std_top - 65), (std_x, std_top - 95), (std_x + 30, std_top - 65), (std_x, std_top - 45)], fill="#eab308", outline="#713f12", width=3)
    draw.rectangle([std_x - 55, std_top - 40, std_x + 55, std_top + 95], fill="#991b1b", outline="#450a0a", width=3)
    font_std = get_best_font(28, bold=True)
    draw.text((std_x - 42, std_top - 10), "SPQR", fill="#fde047", font=font_std)

    return im


def render_roman_colosseum(w: int = 1920, h: int = 1080) -> Image.Image:
    """The Roman Colosseum: monumental stone arches, arena sand, velarium awnings."""
    im = Image.new("RGB", (w, h), "#60a5fa")
    draw = ImageDraw.Draw(im)

    ground_y = int(h * 0.62)
    draw.rectangle([0, ground_y, w, h], fill="#d8b98b")

    c_l, c_r, c_top = 80, w - 80, int(h * 0.16)
    for ti in range(3):
        t_y = c_top + ti * 115
        draw.rectangle([c_l, t_y, c_r, t_y + 115], fill="#ded3be", outline="#3b3224", width=4)
        for ax in range(c_l + 45, c_r - 45, 95):
            draw.rounded_rectangle([ax, t_y + 15, ax + 55, t_y + 105], radius=25, fill="#2b2318", outline="#1c160e", width=3)

    return im


def render_hastings_battlefield(w: int = 1920, h: int = 1080) -> Image.Image:
    """Senlac Hill 1066: rolling green English hills, Saxon round shield wall, Norman pennants."""
    im = Image.new("RGB", (w, h), "#4b6584")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.40)
    ridge_y = int(h * 0.46)
    draw.polygon([(0, sky_h), (w, sky_h), (w, ridge_y + 40), (0, ridge_y - 20)], fill="#3e633d")
    draw.polygon([(0, ridge_y - 20), (w, ridge_y + 40), (w, h), (0, h)], fill="#4d7c49")

    # Saxon Shield Wall atop the ridge
    shield_colors = ["#dc2626", "#2563eb", "#eab308", "#16a34a", "#ffffff"]
    shield_y = ridge_y - 10
    for sx in range(120, w - 120, 48):
        s_clr = shield_colors[(sx // 48) % len(shield_colors)]
        sr = 44
        draw.ellipse([sx - sr, shield_y - sr, sx + sr, shield_y + sr], fill=s_clr, outline="#1f2937", width=4)
        draw.ellipse([sx - 12, shield_y - 12, sx + 12, shield_y + 12], fill="#9ca3af", outline="#111827", width=3)
        draw.line([sx, shield_y - sr, sx + 15, shield_y - sr - 75], fill="#78350f", width=4)

    # Wessex Dragon banner
    draw.line([w // 2, shield_y, w // 2, ridge_y - 200], fill="#451a03", width=6)
    draw.polygon([(w // 2, ridge_y - 200), (w // 2 + 130, ridge_y - 165), (w // 2, ridge_y - 130)], fill="#eab308", outline="#854d0e", width=3)

    # Norman pennants
    for nx in [200, 380, 560, w - 560, w - 380]:
        ny = int(h * 0.78)
        draw.line([nx, ny, nx - 20, ny - 110], fill="#451a03", width=5)
        draw.polygon([(nx - 35, ny - 40), (nx + 10, ny - 40), (nx - 12, ny + 35)], fill="#b91c1c", outline="#1e293b", width=3)

    return im


def render_trench_battlefield(w: int = 1920, h: int = 1080) -> Image.Image:
    """Western Front WW1: muddy trench with sandbag parapets, barbed wire, shell craters, duckboards."""
    im = Image.new("RGB", (w, h), "#333533")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.38)
    trench_top = int(h * 0.52)
    draw.rectangle([0, sky_h, w, trench_top], fill="#44403c")

    # Shell bursts
    for fx, fy, fr in [(480, sky_h - 40, 70), (1350, sky_h - 60, 90)]:
        draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill="#f97316")
        draw.ellipse([fx - fr//2, fy - fr//2, fx + fr//2, fy + fr//2], fill="#fde047")

    # Barbed wire
    for wy in [sky_h + 30, sky_h + 85]:
        for bx in range(40, w - 40, 60):
            draw.line([bx, wy - 35, bx, wy + 25], fill="#292524", width=5)
            draw.ellipse([bx - 20, wy - 20, bx + 20, wy + 20], outline="#78716c", width=2)

    # Sandbags
    for sby in range(trench_top, trench_top + 90, 28):
        offset = ((sby // 28) % 2) * 35
        for sbx in range(-35, w + 70, 70):
            bx = sbx + offset
            draw.rounded_rectangle([bx, sby, bx + 65, sby + 25], radius=6, fill="#78716c", outline="#292524", width=3)

    # Duckboard planks
    duck_y = int(h * 0.78)
    draw.rectangle([0, duck_y, w, h], fill="#3e3223")
    for dx in range(0, w, 32):
        draw.rectangle([dx, duck_y + 10, dx + 24, h - 20], fill="#5c442b", outline="#1c140c", width=3)

    return im


def render_prehistoric_savanna(w: int = 1920, h: int = 1080) -> Image.Image:
    """Ice Age mammoth steppe: glaciated peaks, woolly mammoth silhouettes, cave campfire."""
    im = Image.new("RGB", (w, h), "#c26d38")
    draw = ImageDraw.Draw(im)

    sky_h = int(h * 0.42)
    draw.rectangle([0, sky_h, w, h], fill="#a16207")

    # Distant peaks
    peak_pts = [(0, sky_h)]
    for px in range(0, w + 120, 140):
        py = sky_h - 80 - int(math.sin(px * 0.01) * 60)
        peak_pts.append((px, py))
    peak_pts.extend([(w, sky_h), (0, sky_h)])
    draw.polygon(peak_pts, fill="#ffffff", outline="#7c2d12", width=3)

    # Mammoth silhouettes
    for mx, my, m_sc in [(int(w * 0.38), sky_h + 60, 0.7), (int(w * 0.48), sky_h + 45, 0.85), (int(w * 0.58), sky_h + 70, 0.65)]:
        draw.ellipse([mx - int(55*m_sc), my - int(45*m_sc), mx + int(55*m_sc), my + int(35*m_sc)], fill="#292524")
        draw.arc([mx - int(95*m_sc), my - int(35*m_sc), mx - int(35*m_sc), my + int(35*m_sc)], start=90, end=270, fill="#fef08a", width=int(4*m_sc))

    # Cave overhang & campfire
    draw.polygon([(0, 0), (int(w * 0.42), 0), (int(w * 0.28), int(h * 0.45)), (0, int(h * 0.85))], fill="#1c1917")
    fire_x, fire_y = int(w * 0.28), int(h * 0.84)
    draw.polygon([(fire_x, fire_y - 75), (fire_x + 35, fire_y), (fire_x - 35, fire_y)], fill="#ea580c")
    draw.polygon([(fire_x, fire_y - 50), (fire_x + 20, fire_y), (fire_x - 20, fire_y)], fill="#fde047")

    return im


# Backward-compatible script dictionary
DOCUMENTARY_CURATED_SCRIPTS = {
    "israel": {
        "title": "2000 Years of Israel History",
        "script": build_chronicle_script("2000 Years of Israel History", duration_minutes=3.0),
    },
    "rome": {
        "title": "1000 Years of the Roman Empire",
        "script": build_chronicle_script("1000 Years of the Roman Empire", duration_minutes=3.0),
    },
    "french_revolution": {
        "title": "The French Revolution Explained",
        "script": build_chronicle_script("The French Revolution Explained", duration_minutes=3.0),
    },
    "hastings": {
        "title": "The 1066 Battle of Hastings",
        "script": build_chronicle_script("The 1066 Battle of Hastings", duration_minutes=3.0),
    },
}


# =====================================================================
# 4. Documentary Script & Chapter Breakdown Engine
# =====================================================================

def generate_documentary_script(
    topic: str,
    duration_minutes: float = 3.0,
    api_key: str = "",
    provider: str = "openai",
    model: str = "",
) -> str:
    """Generates an engaging, high-retention multi-chapter documentary script scaled to target duration."""
    return build_chronicle_script(
        topic=topic,
        duration_minutes=duration_minutes,
        api_key=api_key,
        provider=provider,
        model=model,
    )


def breakdown_script_to_chapters(script: str, topic: str = "") -> list[dict]:
    """Parses a documentary narration script into structured visual chapters."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not sentences:
        sentences = [script]

    chapters = []
    current_era = "HISTORY"
    m_top = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", topic, re.IGNORECASE)
    if m_top:
        current_era = m_top.group(0).upper()

    topic_low = (topic or "").lower()
    is_french = any(w in topic_low for w in ["french", "bastille", "napoleon", "guillotine", "robespierre", "1789", "paris"])
    is_roman = any(w in topic_low for w in ["rome", "roman", "caesar", "colosseum", "republic", "senate", "augustus", "empire"])
    is_hastings = any(w in topic_low for w in ["hastings", "1066", "norman", "saxons", "wessex", "harold", "william"])
    is_ww1 = any(w in topic_low for w in ["ww1", "world war 1", "world war i", "trench", "sarajevo", "somme", "verdun"])
    is_prehistoric = any(w in topic_low for w in ["human", "dawn", "evolution", "mammoth", "ice age", "cave", "prehistoric"])

    for idx, sent in enumerate(sentences):
        m_date = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", sent, re.IGNORECASE)
        if m_date:
            current_era = m_date.group(0).upper()

        t = sent.lower()

        # Topic-tailored chapter scene assignment
        if is_french:
            if any(w in t for w in ["bastille", "prison", "storming"]):
                stype = "bastille_fortress"
            elif any(w in t for w in ["guillotine", "terror", "scaffold", "blade", "execution", "louis xvi", "danton", "robespierre"]):
                stype = "guillotine_square"
            elif any(w in t for w in ["versailles", "palace", "marie antoinette", "golden", "gates"]):
                stype = "versailles_palace"
            elif any(w in t for w in ["assembly", "tennis court", "rights of man", "deputies", "constitution", "convention"]):
                stype = "french_assembly"
            elif any(w in t for w in ["battle", "war", "fire", "burning", "waterloo", "tuileries"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["napoleon", "italy", "general", "campaign"]):
                stype = "military_tent"
            elif any(w in t for w in ["coronation", "emperor", "crowned", "notre-dame"]):
                stype = "church_town_square"
            elif any(w in t for w in ["map", "europe", "border", "borders", "invade", "coalition"]):
                stype = "map"
            else:
                stype = ["bastille_fortress", "guillotine_square", "versailles_palace", "french_assembly", "map"][idx % 5]

        elif is_roman:
            if any(w in t for w in ["senate", "forum", "republic", "consul", "curia", "speech", "spqr", "patrician"]):
                stype = "roman_forum"
            elif any(w in t for w in ["colosseum", "gladiator", "arena", "games", "spectacle"]):
                stype = "roman_colosseum"
            elif any(w in t for w in ["tent", "camp", "legion", "general", "marius", "sulla", "rubicon"]):
                stype = "military_tent"
            elif any(w in t for w in ["palace", "throne", "caesar", "emperor", "augustus", "nero"]):
                stype = "throne_room"
            elif any(w in t for w in ["fire", "sack", "ruin", "barbarian", "alaric", "goths", "vandals", "burn"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["church", "christian", "constantine", "basilica", "byzantium"]):
                stype = "church_town_square"
            elif any(w in t for w in ["map", "empire", "border", "provinces", "mediterranean"]):
                stype = "map"
            else:
                stype = ["roman_forum", "roman_colosseum", "military_tent", "throne_room", "map"][idx % 5]

        elif is_hastings:
            if any(w in t for w in ["shield wall", "senlac", "hill", "saxon", "charge", "cavalry", "arrow"]):
                stype = "hastings_battlefield"
            elif any(w in t for w in ["ships", "fleet", "channel", "landing", "pevensey", "harbor", "coast"]):
                stype = "coastal_harbor"
            elif any(w in t for w in ["throne", "crown", "westminster", "coronation", "edward", "godwinson", "william"]):
                stype = "throne_room"
            elif any(w in t for w in ["map", "normandy", "england", "march"]):
                stype = "map"
            else:
                stype = ["hastings_battlefield", "coastal_harbor", "throne_room", "map"][idx % 4]

        elif is_ww1:
            if any(w in t for w in ["trench", "mud", "somme", "verdun", "wire", "shell", "artillery", "ypres", "frontline"]):
                stype = "trench_battlefield"
            elif any(w in t for w in ["sarajevo", "archduke", "assassination", "franz ferdinand"]):
                stype = "church_town_square"
            elif any(w in t for w in ["alliances", "coalitions", "empires", "central powers", "allies"]):
                stype = "countryballs"
            elif any(w in t for w in ["fire", "burn", "destroyed", "ruins", "bombed"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["map", "western front", "eastern front", "europe"]):
                stype = "map"
            else:
                stype = ["trench_battlefield", "countryballs", "map"][idx % 3]

        elif is_prehistoric:
            if any(w in t for w in ["ice age", "mammoth", "cave", "camp", "fire", "hunt", "steppe", "savanna"]):
                stype = "prehistoric_savanna"
            elif any(w in t for w in ["shelter", "cabin", "table", "family"]):
                stype = "family_cabin"
            else:
                stype = "prehistoric_savanna"

        else:
            # Israel / Default
            if any(w in t for w in ["1948", "1967", "1973", "world war", "tanks", "five neighboring", "statehood"]):
                stype = "countryballs"
            elif any(w in t for w in ["masada", "fortress", "plateau", "citadel", "mountain", "dead sea"]):
                stype = "fortress_plateau"
            elif any(w in t for w in ["caesarea", "harbor", "port", "ships", "coast"]):
                stype = "coastal_harbor"
            elif any(w in t for w in ["church", "basilica", "cathedral", "holy sepulchre", "dome of the rock", "caliph"]):
                stype = "church_town_square"
            elif any(w in t for w in ["tent", "camp", "general", "vespasian", "titus"]):
                stype = "military_tent"
            elif any(w in t for w in ["fire", "burn", "ruin", "destroy", "temple was consumed"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["border", "map", "territory", "mediterranean"]):
                stype = "map"
            else:
                stype = "ancient_village" if idx % 2 == 0 else "map"

        title_words = re.sub(r"[^\w\s]", "", sent).split()[:5]
        title = " ".join(title_words).title() if title_words else f"Chapter {idx+1}"

        chapters.append({
            "index": idx + 1,
            "title": title,
            "era": current_era,
            "scene_type": stype,
            "narration": sent,
        })
    return chapters


# =====================================================================
# 5. Scene Director & Dialogue-to-Visual Mapper
# =====================================================================

@dataclass
class DocumentaryScene:
    index: int
    text: str
    era_badge: str
    scene_type: str
    characters: list[dict]
    sfx: str | None
    duration_s: float


def direct_documentary_scenes(cues: list[Cue], topic: str = "") -> list[DocumentaryScene]:
    """
    Intelligently analyzes each dialogue line in the documentary to determine:
    1. Exact historical setting / backdrop matching topic
    2. Zero stickmen (no popup characters)
    3. Minimalist top-left era/date badge
    4. Restrained, non-annoying sound effects with strict 25-second cooldown
    """
    scenes = []
    current_era = "HISTORY"
    m_topic = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", topic, re.IGNORECASE)
    if m_topic:
        current_era = m_topic.group(0).upper()

    topic_low = (topic or "").lower()
    is_french = any(w in topic_low for w in ["french", "bastille", "napoleon", "guillotine", "robespierre", "1789", "paris"])
    is_roman = any(w in topic_low for w in ["rome", "roman", "caesar", "colosseum", "republic", "senate", "augustus", "empire"])
    is_hastings = any(w in topic_low for w in ["hastings", "1066", "norman", "saxons", "wessex", "harold", "william"])
    is_ww1 = any(w in topic_low for w in ["ww1", "world war 1", "world war i", "trench", "sarajevo", "somme", "verdun"])
    is_prehistoric = any(w in topic_low for w in ["human", "dawn", "evolution", "mammoth", "ice age", "cave", "prehistoric"])

    last_sfx_time = -100.0

    for idx, cue in enumerate(cues):
        t = (cue.text or "").lower()
        dur_s = round((cue.end_ms - cue.start_ms) / 1000.0, 2)
        cue_time_s = cue.start_ms / 1000.0

        # Extract chronological dates
        m_date = re.search(r"\b(1\d{3}|20\d{2}|\d{1,3}\s*(?:BC|AD|BCE|CE))\b", cue.text, re.IGNORECASE)
        if m_date:
            current_era = m_date.group(0).upper()

        location_badge = None
        for loc in ["PARIS", "VERSAILLES", "BASTILLE", "ROME", "JERUSALEM", "MASADA", "HASTINGS", "LONDON", "NORMANDY", "CAESAREA", "VERDUN", "SOMME"]:
            if loc.lower() in t:
                location_badge = loc
                break

        active_badge = f"{current_era} • {location_badge}" if location_badge else current_era

        # Topic-tailored Scene Backdrop Selection
        if is_french:
            if any(w in t for w in ["bastille", "prison", "storming"]):
                stype = "bastille_fortress"
            elif any(w in t for w in ["guillotine", "terror", "scaffold", "blade", "execution", "louis xvi", "danton", "robespierre"]):
                stype = "guillotine_square"
            elif any(w in t for w in ["versailles", "palace", "marie antoinette", "golden", "gates", "gilded"]):
                stype = "versailles_palace"
            elif any(w in t for w in ["assembly", "tennis court", "rights of man", "deputies", "constitution", "convention"]):
                stype = "french_assembly"
            elif any(w in t for w in ["battle", "war", "fire", "burning", "waterloo", "tuileries"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["napoleon", "italy", "general", "campaign"]):
                stype = "military_tent"
            elif any(w in t for w in ["coronation", "emperor", "crowned", "notre-dame"]):
                stype = "church_town_square"
            elif any(w in t for w in ["map", "europe", "border", "borders", "invade", "coalition"]):
                stype = "map"
            else:
                stype = ["bastille_fortress", "guillotine_square", "versailles_palace", "french_assembly", "map"][idx % 5]

        elif is_roman:
            if any(w in t for w in ["senate", "forum", "republic", "consul", "curia", "speech", "spqr", "patrician"]):
                stype = "roman_forum"
            elif any(w in t for w in ["colosseum", "gladiator", "arena", "games", "spectacle"]):
                stype = "roman_colosseum"
            elif any(w in t for w in ["tent", "camp", "legion", "general", "marius", "sulla", "rubicon"]):
                stype = "military_tent"
            elif any(w in t for w in ["palace", "throne", "caesar", "emperor", "augustus", "nero"]):
                stype = "throne_room"
            elif any(w in t for w in ["fire", "sack", "ruin", "barbarian", "alaric", "goths", "vandals", "burn"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["church", "christian", "constantine", "basilica", "byzantium"]):
                stype = "church_town_square"
            elif any(w in t for w in ["map", "empire", "border", "provinces", "mediterranean"]):
                stype = "map"
            else:
                stype = ["roman_forum", "roman_colosseum", "military_tent", "throne_room", "map"][idx % 5]

        elif is_hastings:
            if any(w in t for w in ["shield wall", "senlac", "hill", "saxon", "charge", "cavalry", "arrow"]):
                stype = "hastings_battlefield"
            elif any(w in t for w in ["ships", "fleet", "channel", "landing", "pevensey", "harbor", "coast"]):
                stype = "coastal_harbor"
            elif any(w in t for w in ["throne", "crown", "westminster", "coronation", "edward", "godwinson", "william"]):
                stype = "throne_room"
            elif any(w in t for w in ["map", "normandy", "england", "march"]):
                stype = "map"
            else:
                stype = ["hastings_battlefield", "coastal_harbor", "throne_room", "map"][idx % 4]

        elif is_ww1:
            if any(w in t for w in ["trench", "mud", "somme", "verdun", "wire", "shell", "artillery", "ypres", "frontline"]):
                stype = "trench_battlefield"
            elif any(w in t for w in ["sarajevo", "archduke", "assassination", "franz ferdinand"]):
                stype = "church_town_square"
            elif any(w in t for w in ["alliances", "coalitions", "empires", "central powers", "allies"]):
                stype = "countryballs"
            elif any(w in t for w in ["fire", "burn", "destroyed", "ruins", "bombed"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["map", "western front", "eastern front", "europe"]):
                stype = "map"
            else:
                stype = ["trench_battlefield", "countryballs", "map"][idx % 3]

        elif is_prehistoric:
            if any(w in t for w in ["ice age", "mammoth", "cave", "camp", "fire", "hunt", "steppe", "savanna"]):
                stype = "prehistoric_savanna"
            elif any(w in t for w in ["shelter", "cabin", "table", "family"]):
                stype = "family_cabin"
            else:
                stype = "prehistoric_savanna"

        else:
            # Israel / Default
            if any(w in t for w in ["1948", "1967", "1973", "world war", "tanks", "five neighboring", "statehood"]):
                stype = "countryballs"
            elif any(w in t for w in ["masada", "fortress", "plateau", "citadel", "mountain", "dead sea"]):
                stype = "fortress_plateau"
            elif any(w in t for w in ["caesarea", "harbor", "port", "ships", "coast"]):
                stype = "coastal_harbor"
            elif any(w in t for w in ["church", "basilica", "cathedral", "holy sepulchre", "dome of the rock", "caliph"]):
                stype = "church_town_square"
            elif any(w in t for w in ["tent", "camp", "general", "vespasian", "titus"]):
                stype = "military_tent"
            elif any(w in t for w in ["fire", "burn", "ruin", "destroy", "temple was consumed"]):
                stype = "burning_ruins"
            elif any(w in t for w in ["border", "map", "territory", "mediterranean"]):
                stype = "map"
            else:
                stype = "ancient_village" if idx % 2 == 0 else "map"

        # STRICT RESTAINED SFX ENGINE: Cooldown of at least 25 seconds between effects!
        sfx = None
        if cue_time_s - last_sfx_time >= 25.0:
            if any(w in t for w in ["cannon", "bastille fell", "breached", "explosion", "artillery barrage"]):
                sfx = "cannon_boom"
                last_sfx_time = cue_time_s
            elif any(w in t for w in ["blade", "guillotine", "fell to the scaffold", "executed"]):
                sfx = "tension_hit"
                last_sfx_time = cue_time_s
            elif any(w in t for w in ["clash", "swords", "shield wall", "hand-to-hand"]):
                sfx = "sword_clash"
                last_sfx_time = cue_time_s
            elif any(w in t for w in ["crowned", "coronation", "emperor", "proclaimed"]):
                sfx = "royal_fanfare"
                last_sfx_time = cue_time_s

        scenes.append(DocumentaryScene(
            index=idx,
            text=cue.text,
            era_badge=active_badge,
            scene_type=stype,
            characters=[],  # ZERO STICKMEN
            sfx=sfx,
            duration_s=dur_s,
        ))

    return scenes


def compose_documentary_frame(scene: DocumentaryScene, topic: str = "", include_characters: bool = False) -> Image.Image:
    """Renders the full 1080p illustrated scene background matching the documentary moment."""
    w, h = 1920, 1080
    stype = scene.scene_type

    if stype == "bastille_fortress":
        canvas = render_bastille_fortress(w, h)
    elif stype == "guillotine_square":
        canvas = render_guillotine_square(w, h)
    elif stype == "versailles_palace":
        canvas = render_versailles_palace(w, h)
    elif stype == "french_assembly":
        canvas = render_french_assembly(w, h)
    elif stype == "roman_forum":
        canvas = render_roman_forum(w, h)
    elif stype == "roman_colosseum":
        canvas = render_roman_colosseum(w, h)
    elif stype == "hastings_battlefield":
        canvas = render_hastings_battlefield(w, h)
    elif stype == "trench_battlefield":
        canvas = render_trench_battlefield(w, h)
    elif stype == "prehistoric_savanna":
        canvas = render_prehistoric_savanna(w, h)
    elif stype == "family_cabin":
        canvas = render_family_cabin(w, h)
    elif stype == "coastal_harbor":
        canvas = render_coastal_harbor(w, h)
    elif stype == "military_tent":
        canvas = render_military_tent(w, h)
    elif stype == "fortress_plateau":
        canvas = render_fortress_plateau(w, h)
    elif stype == "church_town_square":
        canvas = render_church_town_square(w, h)
    elif stype == "throne_room":
        canvas = render_throne_room(w, h)
    elif stype == "burning_ruins":
        canvas = render_burning_ruins(w, h)
    elif stype == "countryballs":
        canvas = render_countryballs_war_scene(w, h, topic=topic)
    elif stype == "map":
        from animated_history_engine import render_geopolitical_map
        canvas = render_geopolitical_map(w, h, topic=topic, highlight_name="FRONTLINE")
    else:
        # Fallback tailored to topic
        top_low = topic.lower()
        if "french" in top_low or "bastille" in top_low:
            canvas = render_bastille_fortress(w, h)
        elif "rome" in top_low or "roman" in top_low:
            canvas = render_roman_forum(w, h)
        elif "hastings" in top_low or "1066" in top_low:
            canvas = render_hastings_battlefield(w, h)
        elif "ww1" in top_low or "trench" in top_low:
            canvas = render_trench_battlefield(w, h)
        elif "human" in top_low or "prehistoric" in top_low:
            canvas = render_prehistoric_savanna(w, h)
        else:
            canvas = render_ancient_village(w, h)

    # Stamp Top-Left Era/Date Pill
    stamp_date_pill(canvas, scene.era_badge)
    return canvas


# =====================================================================
# 6. Master End-to-End Documentary Pipeline
# =====================================================================

def run_documentary_pipeline(
    job_id: str,
    topic: str,
    duration_minutes: float,
    voice: str,
    aspect_ratio: str,
    subtitle_style: str,
    sfx_volume: float,
    gpu_accel: str,
    parallel_workers: int,
    output_path: Path,
    cancel_event,
    update_job_callback,
    api_key: str = "",
    provider: str = "openai",
    model: str = "",
    custom_script: str = "",
    include_archive_art: bool = True,
    ai_image_provider: str = "flux",
    image_style: str = "cinematic_oil",
    stamp_dates: bool = True,
) -> None:
    """
    Executes the 1-Click Long-Form Animated History Video Generator.
    Produces high-retention, documentary video end-to-end.
    """
    work_dir = Path(tempfile.mkdtemp(prefix="doc_studio_"))

    try:
        def update_stage(msg: str, progress: int, current_img: int = 0, total_imgs: int = 0):
            if update_job_callback:
                update_job_callback(
                    job_id,
                    phase=msg,
                    progress=progress,
                    current_image=current_img,
                    total_images=total_imgs,
                )

        # -------------------------------------------------------------
        # STEP 1: Deep Research & Multi-Chapter Scripting (0 - 10%)
        # -------------------------------------------------------------
        update_stage(f"Deep Researching documentary on '{topic}' ({duration_minutes}m target)...", 5)
        if custom_script and custom_script.strip():
            script_text = custom_script.strip()
            print(f"[Documentary Researcher] Using user-provided custom script ({len(script_text.split())} words)", flush=True)
        else:
            script_text = generate_documentary_script(
                topic=topic,
                duration_minutes=duration_minutes,
                api_key=api_key,
                provider=provider,
                model=model,
            )
            print(f"[Documentary Researcher] Script generated ({len(script_text.split())} words for {duration_minutes} min)", flush=True)

        if cancel_event and cancel_event.is_set():
            raise GenerationCanceled()

        # -------------------------------------------------------------
        # STEP 2: Neural Voiceover & Clause-Aware Timings (10 - 20%)
        # -------------------------------------------------------------
        update_stage("Synthesizing studio voiceover & clause-aware subtitles...", 12)
        audio_path = work_dir / "narration.mp3"
        srt_path = work_dir / "captions.srt"

        from auto_generator import generate_voice_and_srt
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            _, _, cues = loop.run_until_complete(
                generate_voice_and_srt(script_text, voice, audio_path, srt_path)
            )
        finally:
            loop.close()

        total_cues = len(cues)
        print(f"[Documentary Voiceover] Synthesized {total_cues} synchronized cues", flush=True)

        if cancel_event and cancel_event.is_set():
            raise GenerationCanceled()

        # -------------------------------------------------------------
        # STEP 3: High-End Cinematic AI Scene Imagery & Museum Art (20 - 55%)
        # -------------------------------------------------------------
        update_stage(f"Directing {total_cues} scenes and generating cinematic AI imagery...", 20)
        scene_plans = direct_documentary_scenes(cues, topic=topic)

        # Harvest real historical museum paintings from Wikipedia / Commons if enabled
        archive_artworks = []
        if include_archive_art:
            try:
                archive_artworks = fetch_topic_historical_archive(topic, max_images=min(total_cues // 2, 25))
                print(f"[Documentary Pipeline] Harvested {len(archive_artworks)} historical museum paintings for '{topic}'", flush=True)
            except Exception as e:
                print(f"[Documentary Pipeline] Archive fetch note: {e}", flush=True)

        frames_dir = work_dir / "scenes"
        frames_dir.mkdir(parents=True, exist_ok=True)

        def img_progress(cur, total, msg):
            p = 20 + int((cur / max(total, 1)) * 34)
            update_stage(f"Generating cinematic AI Scene {cur}/{total}...", p, cur, total)

        import sys
        if "." not in sys.path:
            sys.path.insert(0, ".")
        from ai_image_engine import batch_generate_scene_images

        # Dispatch parallel AI image generation with smart caching & zero stickmen
        scene_images = batch_generate_scene_images(
            scenes=scene_plans,
            topic=topic,
            output_dir=frames_dir,
            aspect_ratio=aspect_ratio,
            provider=ai_image_provider or "flux",
            api_key=api_key,
            style=image_style or "cinematic_oil",
            stamp_dates=stamp_dates,
            max_workers=min(parallel_workers or 4, 6),
            progress_callback=img_progress,
            archive_artworks=archive_artworks if include_archive_art else [],
            use_archive_hybrid=include_archive_art,
        )

        # -------------------------------------------------------------
        # STEP 4: Build Restrained Dialogue SFX (45 - 55%)
        # -------------------------------------------------------------
        update_stage("Aligning subtle sound effects suite...", 48)
        sfx_dir = Path("sfx")
        intensity_sfx_paths = {}
        intensity_mapping = {}

        if sfx_volume > 0.02:
            for idx, plan in enumerate(scene_plans):
                if plan.sfx:
                    sfx_key = plan.sfx
                    sfx_file = sfx_dir / f"{sfx_key}.wav"
                    if not sfx_file.is_file():
                        sfx_file = sfx_dir / f"{sfx_key}.mp3"
                    if sfx_file.is_file():
                        intensity_sfx_paths[sfx_key] = sfx_file
                        intensity_mapping[idx] = sfx_key

        print(f"[Documentary SFX] Mapped {len(intensity_mapping)} subtle action sound triggers (volume: {sfx_volume:.2f})", flush=True)

        # -------------------------------------------------------------
        # STEP 5: High-Speed GPU/CPU Video Rendering (55 - 95%)
        # -------------------------------------------------------------
        update_stage("Rendering documentary video with camera motion...", 55)

        from video_generator import create_video
        from server import FFMPEG_PATH

        def render_progress(current_img, filename):
            prog = 55 + int((current_img / total_cues) * 35)
            update_stage(f"Rendering scene {current_img+1}/{total_cues}...", prog, current_img+1, total_cues)

        def stage_change(msg, prog):
            update_stage(msg, prog)

        create_video(
            images=scene_images,
            cues=cues,
            ffmpeg_path=FFMPEG_PATH,
            work_dir=work_dir,
            output_path=output_path,
            on_image_started=render_progress,
            cancel_event=cancel_event,
            audio_path=audio_path,
            apply_zoom=True,
            sfx_paths=[],  # ZERO camera shutter clicks
            intensity_sfx_paths=intensity_sfx_paths,
            intensity_mapping=intensity_mapping,
            aspect_ratio=aspect_ratio,
            on_stage_changed=stage_change,
            popup_paths={},  # ZERO STICKMEN
            popup_mapping={},  # ZERO STICKMEN
            popup_sfx_paths=[],
            motion_style="smart_random",
            zoom_intensity="subtle",
            bg_mode="crop_fill",
            enable_subtitles=True if subtitle_style != "none" else False,
            subtitle_style=subtitle_style if subtitle_style != "none" else "hormozi_yellow",
            subtitle_position="bottom",
            subtitle_font_size=46,
            gpu_accel=gpu_accel,
            parallel_workers=parallel_workers,
            emotion_sfx_volume=sfx_volume,
        )

        update_stage("Documentary production complete!", 100, total_cues, total_cues)
        if update_job_callback:
            update_job_callback(
                job_id,
                state="complete",
                progress=100,
                output_name=output_path.name,
                phase="Complete",
            )
        print(f"[Documentary Pipeline] SUCCESS! Generated: {output_path.name}", flush=True)

    except GenerationCanceled:
        if update_job_callback:
            update_job_callback(job_id, state="canceled", phase="Canceled", error="Generation canceled.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        if update_job_callback:
            update_job_callback(job_id, state="error", phase="Failed", error=str(e))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
