import sys
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_best_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/tahomabd.ttf",
    ] if bold else [
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

def stamp_date_pill(im: Image.Image, text: str) -> None:
    if not text:
        return
    draw = ImageDraw.Draw(im)
    clean_txt = str(text).strip().upper()
    font = get_best_font(34, bold=True)
    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    px, py = 50, 42
    pw, ph = tw + 40, th + 22
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=12, fill=(15, 23, 42), outline=(148, 163, 184), width=3)
    draw.text((px + 20, py + 9), clean_txt, fill="#ffffff", font=font)

# 1. BASTILLE FORTRESS
def render_bastille_fortress(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#1e2430")
    draw = ImageDraw.Draw(im)
    
    # Stormy Parisian sky gradient
    sky_h = int(h * 0.40)
    for y in range(sky_h):
        ratio = y / max(sky_h, 1)
        r = int(55 + ratio * 35)
        g = int(70 + ratio * 35)
        b = int(95 + ratio * 30)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    
    # Distant Paris mansard rooftops on left and right
    for bx in range(0, 420, 70):
        bh = 120 + ((bx * 7) % 60)
        draw.rectangle([bx, sky_h - bh + 60, bx + 65, sky_h + 80], fill="#333b4d", outline="#1a1e28", width=2)
        draw.polygon([(bx - 5, sky_h - bh + 60), (bx + 32, sky_h - bh + 15), (bx + 70, sky_h - bh + 60)], fill="#222938", outline="#1a1e28", width=2)
    for bx in range(w - 420, w, 70):
        bh = 120 + ((bx * 11) % 60)
        draw.rectangle([bx, sky_h - bh + 60, bx + 65, sky_h + 80], fill="#333b4d", outline="#1a1e28", width=2)
        draw.polygon([(bx - 5, sky_h - bh + 60), (bx + 32, sky_h - bh + 15), (bx + 70, sky_h - bh + 60)], fill="#222938", outline="#1a1e28", width=2)

    # Smoke billowing from revolutionary fire
    for sx, sy_base, count in [(320, sky_h - 40, 6), (1580, sky_h - 50, 6)]:
        for si in range(count):
            sm_y = sy_base - si * 50
            sm_r = 55 + si * 18
            sm_x = sx + int(math.sin(si * 1.3) * 35)
            shade = max(40, 95 - si * 9)
            draw.ellipse([sm_x - sm_r, sm_y - sm_r // 2, sm_x + sm_r, sm_y + sm_r // 2], fill=(shade + 10, shade, shade - 5))

    # The Bastille Fortress Center Wall & Massive Towers
    fort_l = 360
    fort_r = w - 360
    wall_top = int(h * 0.24)
    wall_bot = int(h * 0.72)

    # Main Curtain Wall
    draw.rectangle([fort_l, wall_top, fort_r, wall_bot], fill="#474b57", outline="#1f2229", width=5)
    # Wall stone courses / lines
    for ly in range(wall_top + 40, wall_bot, 45):
        draw.line([fort_l, ly, fort_r, ly], fill="#3a3d47", width=2)

    # 4 Monumental Round Towers (Left-Outer, Left-Inner, Right-Inner, Right-Outer)
    towers = [
        (fort_l + 40, int(h * 0.16), 170),
        (fort_l + 310, int(h * 0.18), 160),
        (fort_r - 310, int(h * 0.18), 160),
        (fort_r - 40, int(h * 0.16), 170),
    ]
    for tx, t_top, tw in towers:
        # Tower body with 3D cylindrical shading
        t_left = tx - tw // 2
        t_right = tx + tw // 2
        # Base shadow and highlight
        draw.rectangle([t_left, t_top, t_right, wall_bot], fill="#505563", outline="#1c1f26", width=5)
        draw.rectangle([t_left + 15, t_top, t_left + tw // 3, wall_bot], fill="#5f6575")
        draw.rectangle([t_right - tw // 3, t_top, t_right - 10, wall_bot], fill="#3b3e48")
        # Crenellations at tower top
        for cbx in range(t_left, t_right, 32):
            draw.rectangle([cbx, t_top - 24, cbx + 18, t_top], fill="#444955", outline="#1c1f26", width=3)
        # Narrow vertical arrow slits
        for slit_y in [t_top + 100, t_top + 220, t_top + 340]:
            draw.rectangle([tx - 6, slit_y, tx + 6, slit_y + 40], fill="#15171c", outline="#2b2e38", width=2)

    # Central Grand Iron Gateway & Drawbridge
    gate_cx = w // 2
    gate_w = 260
    gate_h = 320
    draw.rounded_rectangle([gate_cx - gate_w // 2, wall_bot - gate_h, gate_cx + gate_w // 2, wall_bot], radius=130, fill="#13151a", outline="#0a0c0f", width=6)
    
    # Wooden Drawbridge lowered across the moat
    db_l = gate_cx - 150
    db_r = gate_cx + 150
    db_top = wall_bot - 40
    db_bot = int(h * 0.85)
    draw.polygon([(db_l, db_top), (db_r, db_top), (db_r + 40, db_bot), (db_l - 40, db_bot)], fill="#66462c", outline="#281a10", width=5)
    # Heavy wooden planks on drawbridge
    for py in range(db_top + 20, db_bot, 22):
        draw.line([(db_l - 20, py), (db_r + 20, py)], fill="#4a321e", width=3)
    # Heavy iron suspension chains
    draw.line([gate_cx - 120, wall_bot - gate_h + 30, db_l - 30, db_bot - 10], fill="#94a3b8", width=5)
    draw.line([gate_cx + 120, wall_bot - gate_h + 30, db_r + 30, db_bot - 10], fill="#94a3b8", width=5)

    # Water Moat
    moat_bot = int(h * 0.88)
    draw.polygon([(0, wall_bot - 10), (w, wall_bot - 10), (w, moat_bot), (0, moat_bot)], fill="#1f3644", outline="#0e1a22", width=4)
    # Cobblestone Foreground Quai
    draw.rectangle([0, moat_bot, w, h], fill="#383d47")
    rnd = random.Random(89)
    for _ in range(70):
        cx = rnd.randint(20, w - 20)
        cy = rnd.randint(moat_bot + 15, h - 15)
        draw.ellipse([cx, cy, cx + rnd.randint(18, 45), cy + rnd.randint(8, 20)], fill="#2b2f38", outline="#1c1f26", width=2)

    # French Tricolor Flag waving on the tallest Bastille tower
    flag_x = towers[1][0]
    flag_top_y = towers[1][1] - 120
    draw.line([flag_x, towers[1][1] - 24, flag_x, flag_top_y], fill="#0f172a", width=5)
    # Blue, White, Red stripes
    fw = 90
    fh = 55
    draw.rectangle([flag_x, flag_top_y, flag_x + fw // 3, flag_top_y + fh], fill="#1d4ed8")
    draw.rectangle([flag_x + fw // 3, flag_top_y, flag_x + (2 * fw) // 3, flag_top_y + fh], fill="#ffffff")
    draw.rectangle([flag_x + (2 * fw) // 3, flag_top_y, flag_x + fw, flag_top_y + fh], fill="#dc2626")
    draw.polygon([(flag_x, flag_top_y), (flag_x + fw, flag_top_y), (flag_x + fw - 15, flag_top_y + fh // 2), (flag_x + fw, flag_top_y + fh), (flag_x, flag_top_y + fh)], fill=None, outline="#1e293b", width=2)

    return im

# 2. GUILLOTINE SQUARE
def render_guillotine_square(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#3d4450")
    draw = ImageDraw.Draw(im)

    # Parisian gloomy overcast sky
    sky_h = int(h * 0.45)
    for y in range(sky_h):
        r = int(90 + (y / sky_h) * 45)
        g = int(105 + (y / sky_h) * 40)
        b = int(125 + (y / sky_h) * 35)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Classical Paris buildings in background (Place de la Révolution / Hôtel de Crillon style)
    bldg_top = int(h * 0.22)
    bldg_bot = int(h * 0.58)
    draw.rectangle([0, bldg_top, w, bldg_bot], fill="#787f8d", outline="#2b303c", width=4)
    # Mansard slate roofs
    draw.polygon([(0, bldg_top), (w, bldg_top), (w, bldg_top - 90), (0, bldg_top - 90)], fill="#3e4552", outline="#1e2229", width=3)
    # Classical colonnade arches
    for col_x in range(60, w - 60, 110):
        draw.rectangle([col_x, bldg_top + 40, col_x + 35, bldg_bot], fill="#9199a8", outline="#2b303c", width=2)
        draw.rounded_rectangle([col_x - 10, bldg_top + 90, col_x + 45, bldg_bot - 40], radius=15, fill="#232731", outline="#1a1c22", width=2)

    # Cobblestone Plaza ground
    draw.rectangle([0, bldg_bot, w, h], fill="#4f5460")
    rnd = random.Random(1793)
    for _ in range(90):
        cx = rnd.randint(10, w - 10)
        cy = rnd.randint(bldg_bot + 10, h - 10)
        draw.ellipse([cx, cy, cx + rnd.randint(15, 35), cy + rnd.randint(6, 15)], fill="#3c404a", outline="#202329", width=1)

    # Wooden Scaffold / Platform in Center
    scaf_w = 640
    scaf_h = 160
    scaf_cx = w // 2
    scaf_top = int(h * 0.56)
    scaf_bot = scaf_top + scaf_h
    scaf_l = scaf_cx - scaf_w // 2
    scaf_r = scaf_cx + scaf_w // 2

    # Raised timber scaffold base
    draw.polygon([(scaf_l - 40, scaf_bot), (scaf_r + 40, scaf_bot), (scaf_r, scaf_top), (scaf_l, scaf_top)], fill="#854d27", outline="#381e0d", width=5)
    # Steps on right side
    for si in range(6):
        sy = scaf_top + si * 26
        draw.rectangle([scaf_r + 15 - si * 6, sy, scaf_r + 110 - si * 6, sy + 24], fill="#6b3d1c", outline="#2e190b", width=3)

    # Red wooden safety railing around scaffold
    draw.rectangle([scaf_l, scaf_top - 45, scaf_r, scaf_top], fill="#991b1b", outline="#450a0a", width=3)
    for rx in range(scaf_l + 30, scaf_r, 55):
        draw.line([rx, scaf_top - 45, rx, scaf_top], fill="#450a0a", width=3)

    # THE GUILLOTINE
    g_cx = scaf_cx
    g_base_y = scaf_top - 20
    g_h = 360
    g_top_y = g_base_y - g_h
    post_dist = 60

    # Two tall vertical timber upright beams
    draw.rectangle([g_cx - post_dist - 14, g_top_y, g_cx - post_dist + 14, g_base_y], fill="#451a03", outline="#1c0701", width=4)
    draw.rectangle([g_cx + post_dist - 14, g_top_y, g_cx + post_dist + 14, g_base_y], fill="#451a03", outline="#1c0701", width=4)
    # Top Crossbeam & Pulley
    draw.rectangle([g_cx - post_dist - 28, g_top_y - 20, g_cx + post_dist + 28, g_top_y], fill="#3d1401", outline="#1c0701", width=4)
    draw.ellipse([g_cx - 16, g_top_y - 12, g_cx + 16, g_top_y + 16], fill="#78716c", outline="#1c0701", width=3)

    # The Heavy Angled Steel Blade (Gleaming metallic diagonal edge)
    blade_y = g_top_y + 70
    draw.polygon([
        (g_cx - post_dist + 14, blade_y),
        (g_cx + post_dist - 14, blade_y),
        (g_cx + post_dist - 14, blade_y + 65),
        (g_cx - post_dist + 14, blade_y + 115),
    ], fill="#e2e8f0", outline="#334155", width=4)
    # Metallic reflection stripe
    draw.line([g_cx - post_dist + 24, blade_y + 10, g_cx + post_dist - 24, blade_y + 10], fill="#ffffff", width=3)

    # Bascule (Tilting wooden board) & Lunette (Neck hole)
    draw.rounded_rectangle([g_cx - 40, g_base_y - 75, g_cx + 40, g_base_y], radius=8, fill="#5c2c0d", outline="#1c0701", width=3)
    draw.ellipse([g_cx - 18, g_base_y - 55, g_cx + 18, g_base_y - 22], fill="#0a0502", outline="#2b1104", width=3)

    # Wicker Basket for the head
    draw.rounded_rectangle([g_cx - 85, g_base_y - 45, g_cx - 45, g_base_y + 10], radius=6, fill="#b45309", outline="#451a03", width=3)
    for wy in range(g_base_y - 40, g_base_y + 10, 8):
        draw.line([g_cx - 85, wy, g_cx - 45, wy], fill="#78350f", width=2)

    # French Revolutionary Tricolor Ribbon draped on railing
    rw = 120
    rh = 30
    draw.rectangle([scaf_l + 40, scaf_top - 40, scaf_l + 40 + rw // 3, scaf_top - 10], fill="#1d4ed8")
    draw.rectangle([scaf_l + 40 + rw // 3, scaf_top - 40, scaf_l + 40 + (2*rw)//3, scaf_top - 10], fill="#ffffff")
    draw.rectangle([scaf_l + 40 + (2*rw)//3, scaf_top - 40, scaf_l + 40 + rw, scaf_top - 10], fill="#dc2626")

    return im

# 3. VERSAILLES PALACE
def render_versailles_palace(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#7ec8f2")
    draw = ImageDraw.Draw(im)

    # Royal Blue Summer Sky
    sky_h = int(h * 0.36)
    for y in range(sky_h):
        r = int(110 + (y / sky_h) * 70)
        g = int(185 + (y / sky_h) * 45)
        b = int(245)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    # Fluffy white clouds
    for cx, cy in [(320, 110), (980, 80), (1600, 120)]:
        draw.ellipse([cx - 100, cy - 35, cx + 100, cy + 35], fill="#ffffff")

    # The Grand Neoclassical Palace of Versailles Facade
    palace_top = int(h * 0.22)
    palace_bot = int(h * 0.58)
    draw.rectangle([0, palace_top, w, palace_bot], fill="#e8d5b5", outline="#4a3721", width=5)

    # Roof Attic & Balustrade with Classical Urns / Statues
    draw.rectangle([0, palace_top - 35, w, palace_top], fill="#cfbe9e", outline="#4a3721", width=3)
    for ux in range(40, w, 75):
        draw.rectangle([ux, palace_top - 55, ux + 18, palace_top - 35], fill="#b8a584", outline="#3d2d1b", width=2)
        draw.ellipse([ux - 4, palace_top - 68, ux + 22, palace_top - 50], fill="#b8a584", outline="#3d2d1b", width=2)

    # Rhythmic Classical French Windows (Two Tiers)
    for wx in range(60, w - 60, 115):
        # Upper tier
        draw.rounded_rectangle([wx, palace_top + 25, wx + 45, palace_top + 95], radius=20, fill="#1e3a5f", outline="#3b2b1a", width=3)
        # Lower grand French arched doors
        draw.rounded_rectangle([wx, palace_top + 125, wx + 45, palace_bot - 15], radius=22, fill="#1e3a5f", outline="#3b2b1a", width=3)
        # Gold framing
        draw.rectangle([wx - 6, palace_top + 18, wx + 51, palace_top + 24], fill="#ca8a04")

    # Palace Central Pavilion Pediment
    p_cx = w // 2
    draw.polygon([(p_cx - 220, palace_top - 35), (p_cx, palace_top - 120), (p_cx + 220, palace_top - 35)], fill="#dccab0", outline="#4a3721", width=5)
    # Royal French Bourbon Coat of Arms (Gold Shield with 3 Fleurs-de-lis)
    draw.rounded_rectangle([p_cx - 35, palace_top - 95, p_cx + 35, palace_top - 45], radius=10, fill="#1e3a8a", outline="#ca8a04", width=3)
    draw.ellipse([p_cx - 10, palace_top - 85, p_cx + 10, palace_top - 60], fill="#eab308")

    # Courtyard (Cour d'Honneur) Ground with marble paving lines
    draw.rectangle([0, palace_bot, w, h], fill="#dfceb1")
    for ly in range(palace_bot + 40, h, 65):
        draw.line([0, ly, w, ly], fill="#c7b494", width=2)

    # Symmetrical Green Parterre Box Hedges on Left and Right
    for hedge_l, hedge_r in [(80, 480), (w - 480, w - 80)]:
        draw.rounded_rectangle([hedge_l, int(h * 0.64), hedge_r, int(h * 0.88)], radius=25, fill="#2d6a4f", outline="#1b4332", width=4)
        draw.rounded_rectangle([hedge_l + 35, int(h * 0.68), hedge_r - 35, int(h * 0.84)], radius=18, fill="#52b788", outline="#1b4332", width=3)
        draw.ellipse([(hedge_l + hedge_r)//2 - 25, int(h * 0.76) - 25, (hedge_l + hedge_r)//2 + 25, int(h * 0.76) + 25], fill="#1b4332")

    # The Gilded Golden Gates of Versailles (Grille Royale) in Foreground
    gate_top = int(h * 0.60)
    gate_bot = h
    # Wrought iron gilded spear pales
    for gx in range(380, w - 380, 26):
        draw.line([gx, gate_top, gx, gate_bot], fill="#ca8a04", width=6)
        # Gold spear finial tip
        draw.polygon([(gx - 8, gate_top), (gx, gate_top - 24), (gx + 8, gate_top)], fill="#eab308", outline="#854d0e", width=2)
    # Horizontal gilded rails
    for ry in [gate_top + 45, gate_top + 160, int(h * 0.88)]:
        draw.rectangle([360, ry - 6, w - 360, ry + 6], fill="#a16207", outline="#713f12", width=2)

    return im

# 4. ROMAN FORUM
def render_roman_forum(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#5ba2d6")
    draw = ImageDraw.Draw(im)

    # Azure Mediterranean Sky
    sky_h = int(h * 0.42)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(90 + (y / sky_h) * 90), int(160 + (y / sky_h) * 55), 235))

    # Roman Umbrella Pine / Cypress Trees on background hills
    draw.polygon([(0, sky_h), (w, sky_h), (w, int(h * 0.52)), (0, int(h * 0.52))], fill="#8a9e73")
    for px in [120, 280, 1620, 1780]:
        # Tall Italian Cypress
        draw.polygon([(px - 22, sky_h + 10), (px, sky_h - 130), (px + 22, sky_h + 10)], fill="#1f4124", outline="#0f2413", width=2)
        draw.line([px, sky_h + 10, px, sky_h + 40], fill="#3d2817", width=6)

    # Travertine Marble Plaza Ground
    plaza_top = int(h * 0.52)
    draw.rectangle([0, plaza_top, w, h], fill="#e8dfce")
    for py in range(plaza_top + 50, h, 75):
        draw.line([0, py, w, py], fill="#cfc2ad", width=2)

    # Triumphal Arch of Septimius Severus on Left Side
    arch_l = 80
    arch_w = 420
    arch_top = int(h * 0.22)
    arch_bot = plaza_top + 60
    draw.rectangle([arch_l, arch_top, arch_l + arch_w, arch_bot], fill="#ded5c4", outline="#403628", width=5)
    # Attic inscription panel
    draw.rectangle([arch_l + 25, arch_top + 18, arch_l + arch_w - 25, arch_top + 70], fill="#c7bbaa", outline="#403628", width=3)
    # Grand Central Archway
    draw.rounded_rectangle([arch_l + 130, arch_top + 130, arch_l + arch_w - 130, arch_bot], radius=75, fill="#3b3225", outline="#211b13", width=5)

    # Temple of Jupiter / Saturn in Center-Right
    t_cx = int(w * 0.65)
    t_w = 860
    t_top = int(h * 0.18)
    t_podium_top = int(h * 0.58)

    # Triangular Marble Pediment
    draw.polygon([(t_cx - t_w//2, t_top), (t_cx, t_top - 140), (t_cx + t_w//2, t_top)], fill="#f0ebe0", outline="#3a3227", width=6)
    # Pediment relief sculpture
    draw.ellipse([t_cx - 45, t_top - 75, t_cx + 45, t_top - 20], fill="#baa892", outline="#3a3227", width=3)
    # Entablature with SPQR Gold Inscription
    draw.rectangle([t_cx - t_w//2 - 15, t_top, t_cx + t_w//2 + 15, t_top + 45], fill="#e4dbcc", outline="#3a3227", width=4)
    font_spqr = get_best_font(26, bold=True)
    draw.text((t_cx - 160, t_top + 8), "SENATVS POPVLVSQVE ROMANVS", fill="#ca8a04", font=font_spqr)

    # 6 Monumental Fluted Corinthian Columns
    col_spacing = t_w // 7
    for ci in range(1, 7):
        col_x = (t_cx - t_w // 2) + ci * col_spacing
        col_w = 40
        # Column shaft with fluting lines
        draw.rectangle([col_x - col_w//2, t_top + 45, col_x + col_w//2, t_podium_top], fill="#f5f0e6", outline="#3a3227", width=3)
        draw.line([col_x - 8, t_top + 45, col_x - 8, t_podium_top], fill="#ded3c1", width=2)
        draw.line([col_x + 8, t_top + 45, col_x + 8, t_podium_top], fill="#ded3c1", width=2)
        # Ornate Capital
        draw.rectangle([col_x - col_w//2 - 12, t_top + 45, col_x + col_w//2 + 12, t_top + 70], fill="#baa892", outline="#3a3227", width=2)

    # Marble Podium Steps
    draw.polygon([(t_cx - t_w//2 - 40, t_podium_top), (t_cx + t_w//2 + 40, t_podium_top), (t_cx + t_w//2 + 90, plaza_top + 160), (t_cx - t_w//2 - 90, plaza_top + 160)], fill="#ded5c4", outline="#3a3227", width=5)
    for stp_y in range(t_podium_top + 25, plaza_top + 160, 25):
        draw.line([(t_cx - t_w//2 - 60, stp_y), (t_cx + t_w//2 + 60, stp_y)], fill="#baa892", width=3)

    # Roman SPQR Legionary Standard Banner (Red & Gold Eagle)
    std_x = int(w * 0.22)
    std_top = int(h * 0.38)
    # Gold spear staff
    draw.line([std_x, std_top - 50, std_x, plaza_top + 180], fill="#ca8a04", width=8)
    # Golden Aquila Eagle
    draw.polygon([(std_x - 30, std_top - 65), (std_x, std_top - 95), (std_x + 30, std_top - 65), (std_x, std_top - 45)], fill="#eab308", outline="#713f12", width=3)
    # Crimson Vexillum Cloth Banner
    draw.rectangle([std_x - 55, std_top - 40, std_x + 55, std_top + 95], fill="#991b1b", outline="#450a0a", width=3)
    font_std = get_best_font(28, bold=True)
    draw.text((std_x - 42, std_top - 10), "SPQR", fill="#fde047", font=font_std)

    return im

def main():
    test_dir = Path("scratch/new_scenes")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = [
        ("01_bastille.jpg", render_bastille_fortress, "1789 • PARIS"),
        ("02_guillotine.jpg", render_guillotine_square, "1793 • PLACE DE LA RÉVOLUTION"),
        ("03_versailles.jpg", render_versailles_palace, "1789 • VERSAILLES"),
        ("04_forum.jpg", render_roman_forum, "44 BC • ROME"),
    ]
    for name, func, badge in scenes:
        im = func(1920, 1080)
        stamp_date_pill(im, badge)
        p = test_dir / name
        im.save(p, "JPEG", quality=95)
        print(f"Rendered {name} -> {p}")

if __name__ == "__main__":
    main()
