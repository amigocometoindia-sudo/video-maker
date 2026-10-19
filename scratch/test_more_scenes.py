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

# 5. FRENCH NATIONAL ASSEMBLY / TENNIS COURT
def render_french_assembly(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#2b2a27")
    draw = ImageDraw.Draw(im)

    # High Neoclassical Hall Coffered Ceiling
    ceil_h = int(h * 0.32)
    for y in range(0, ceil_h, 45):
        draw.line([(0, y), (w, y)], fill="#3d3b36", width=2)
    for x in range(0, w, 90):
        draw.line([(x, 0), (x, ceil_h)], fill="#3d3b36", width=2)

    # Classical Doric Columns across the back wall
    col_bot = int(h * 0.70)
    for cx in range(80, w, 160):
        draw.rectangle([cx - 20, ceil_h, cx + 20, col_bot], fill="#c7baa3", outline="#423b30", width=3)
        draw.rectangle([cx - 30, ceil_h, cx + 30, ceil_h + 30], fill="#ab9d87", outline="#423b30", width=2)

    # Tricolor French Banners draped between columns
    for bx in range(160, w - 160, 320):
        bw = 100
        by = ceil_h + 50
        draw.rectangle([bx, by, bx + bw//3, by + 120], fill="#1d4ed8")
        draw.rectangle([bx + bw//3, by, bx + (2*bw)//3, by + 120], fill="#ffffff")
        draw.rectangle([bx + (2*bw)//3, by, bx + bw, by + 120], fill="#dc2626")

    # Tiered Curved Wooden Amphitheater Benches
    for tier_i in range(4):
        ty = col_bot - 110 + tier_i * 65
        tw_left = 60 + tier_i * 50
        tw_right = w - 60 - tier_i * 50
        draw.polygon([(tw_left, ty), (tw_right, ty), (tw_right + 30, ty + 50), (tw_left - 30, ty + 50)], fill="#663c1a", outline="#291607", width=4)
        for seat_x in range(tw_left + 40, tw_right - 20, 95):
            draw.rectangle([seat_x, ty - 18, seat_x + 35, ty], fill="#854d22", outline="#291607", width=2)

    # Center Speaker Rostrum / Wooden Tribune
    pod_w = 420
    pod_h = 240
    pod_cx = w // 2
    pod_top = int(h * 0.72)
    draw.polygon([
        (pod_cx - pod_w//2 + 30, pod_top),
        (pod_cx + pod_w//2 - 30, pod_top),
        (pod_cx + pod_w//2, pod_top + pod_h),
        (pod_cx - pod_w//2, pod_top + pod_h)
    ], fill="#4f2d12", outline="#1c0f05", width=5)
    # Declaration of Rights of Man Parchment Scroll on podium
    draw.polygon([(pod_cx - 90, pod_top + 10), (pod_cx + 90, pod_top + 10), (pod_cx + 105, pod_top + 60), (pod_cx - 75, pod_top + 60)], fill="#fef3c7", outline="#92400e", width=3)
    # Revolutionary Tricolor Cockade on podium face
    draw.ellipse([pod_cx - 35, pod_top + 100, pod_cx + 35, pod_top + 170], fill="#1d4ed8")
    draw.ellipse([pod_cx - 24, pod_top + 111, pod_cx + 24, pod_top + 159], fill="#ffffff")
    draw.ellipse([pod_cx - 12, pod_top + 123, pod_cx + 12, pod_top + 147], fill="#dc2626")

    return im

# 6. ROMAN COLOSSEUM
def render_roman_colosseum(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#60a5fa")
    draw = ImageDraw.Draw(im)

    # Bright Mediterranean Blue Sky
    sky_h = int(h * 0.38)
    for y in range(sky_h):
        draw.line([(0, y), (w, y)], fill=(int(110 + (y/sky_h)*80), int(175 + (y/sky_h)*50), 245))

    # Sandy Roman Arena Ground
    ground_y = int(h * 0.62)
    draw.rectangle([0, ground_y, w, h], fill="#d8b98b")
    # Arena Sand texture
    rnd = random.Random(44)
    for _ in range(80):
        sx = rnd.randint(10, w - 10)
        sy = rnd.randint(ground_y + 10, h - 10)
        draw.ellipse([sx, sy, sx + rnd.randint(12, 35), sy + rnd.randint(4, 12)], fill="#c2a070")

    # Colosseum Exterior Monumental Curve
    c_l = 80
    c_r = w - 80
    c_top = int(h * 0.16)

    # 3 Monumental Tiers of Roman Stone Arches
    tier_height = 80
    for ti in range(3):
        t_y = c_top + ti * (tier_height + 35)
        # Tier wall
        draw.rectangle([c_l, t_y, c_r, t_y + tier_height + 35], fill="#ded3be", outline="#3b3224", width=4)
        # Arches along this tier
        for ax in range(c_l + 45, c_r - 45, 95):
            draw.rounded_rectangle([ax, t_y + 15, ax + 55, t_y + tier_height + 25], radius=25, fill="#2b2318", outline="#1c160e", width=3)
            # Classical column flanking arch
            draw.rectangle([ax - 12, t_y + 8, ax - 2, t_y + tier_height + 35], fill="#ede4d3", outline="#3b3224", width=2)
            draw.rectangle([ax + 57, t_y + 8, ax + 67, t_y + tier_height + 35], fill="#ede4d3", outline="#3b3224", width=2)

    # Top Attic Storey with Corinthian Pilasters
    attic_h = 55
    draw.rectangle([c_l - 15, c_top - attic_h, c_r + 15, c_top], fill="#cbbfa9", outline="#3b3224", width=4)
    # Velarium Mast Poles for canvas shading
    for mx in range(c_l + 30, c_r, 120):
        draw.line([mx, c_top - attic_h - 40, mx, c_top - attic_h], fill="#78350f", width=5)
        # Crimson awning flags
        draw.polygon([(mx, c_top - attic_h - 40), (mx + 35, c_top - attic_h - 25), (mx, c_top - attic_h - 10)], fill="#b91c1c")

    return im

# 7. BATTLE OF HASTINGS — SENLAC HILL SHIELD WALL
def render_hastings_battlefield(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#4b6584")
    draw = ImageDraw.Draw(im)

    # Stormy October English Channel Sky
    sky_h = int(h * 0.40)
    for y in range(sky_h):
        r = int(95 + (y/sky_h) * 45)
        g = int(120 + (y/sky_h) * 40)
        b = int(145 + (y/sky_h) * 35)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Rolling Green English Hills (Senlac Hill Ridge)
    ridge_y = int(h * 0.46)
    draw.polygon([(0, sky_h), (w, sky_h), (w, ridge_y + 40), (0, ridge_y - 20)], fill="#3e633d")
    draw.polygon([(0, ridge_y - 20), (w, ridge_y + 40), (w, h), (0, h)], fill="#4d7c49")

    # ATOP THE RIDGE: Anglo-Saxon Shield Wall
    # Dense overlapping round wooden shields with painted cross patterns
    shield_colors = ["#dc2626", "#2563eb", "#eab308", "#16a34a", "#ffffff"]
    shield_y = ridge_y - 10
    for sx in range(120, w - 120, 48):
        s_clr = shield_colors[(sx // 48) % len(shield_colors)]
        sr = 44
        # Shield circle with iron rim and boss
        draw.ellipse([sx - sr, shield_y - sr, sx + sr, shield_y + sr], fill=s_clr, outline="#1f2937", width=4)
        draw.ellipse([sx - 12, shield_y - 12, sx + 12, shield_y + 12], fill="#9ca3af", outline="#111827", width=3)
        # Painted cross on shield
        draw.line([sx - sr + 6, shield_y, sx + sr - 6, shield_y], fill="#111827", width=4)
        draw.line([sx, shield_y - sr + 6, sx, shield_y + sr - 6], fill="#111827", width=4)
        # Bristling Saxon Spears poking over the shield wall
        draw.line([sx, shield_y - sr, sx + 15, shield_y - sr - 75], fill="#78350f", width=4)
        draw.polygon([(sx + 15, shield_y - sr - 75), (sx + 20, shield_y - sr - 100), (sx + 10, shield_y - sr - 80)], fill="#cbd5e1", outline="#1e293b", width=2)

    # Golden Dragon of Wessex Royal Banner flying over King Harold's position
    flag_x = w // 2
    flag_top = ridge_y - 200
    draw.line([flag_x, shield_y, flag_x, flag_top], fill="#451a03", width=6)
    draw.polygon([(flag_x, flag_top), (flag_x + 130, flag_top + 35), (flag_x, flag_top + 70)], fill="#eab308", outline="#854d0e", width=3)
    font_dragon = get_best_font(20, bold=True)
    draw.text((flag_x + 15, flag_top + 22), "WESSEX", fill="#78350f", font=font_dragon)

    # Norman Cavalry Pennants at the foot of the hill
    for nx in [200, 380, 560, w - 560, w - 380]:
        ny = int(h * 0.78)
        draw.line([nx, ny, nx - 20, ny - 110], fill="#451a03", width=5)
        # Norman kite shield
        draw.polygon([(nx - 35, ny - 40), (nx + 10, ny - 40), (nx - 12, ny + 35)], fill="#b91c1c", outline="#1e293b", width=3)
        # Swallowtail Norman cavalry pennant
        draw.polygon([(nx - 20, ny - 110), (nx + 65, ny - 125), (nx + 40, ny - 100), (nx + 65, ny - 75), (nx - 20, ny - 90)], fill="#1e3a8a", outline="#0f172a", width=2)

    return im

# 8. WORLD WAR 1 — TRENCH BATTLEFIELD
def render_trench_battlefield(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#333533")
    draw = ImageDraw.Draw(im)

    # Leaden Gray Artillery Sky with distant fiery shellbursts
    sky_h = int(h * 0.38)
    for y in range(sky_h):
        r = int(50 + (y/sky_h) * 25)
        g = int(52 + (y/sky_h) * 22)
        b = int(58 + (y/sky_h) * 20)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Distant Shell Burst flashes
    for fx, fy, fr in [(480, sky_h - 40, 70), (1350, sky_h - 60, 90)]:
        draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill="#f97316")
        draw.ellipse([fx - fr//2, fy - fr//2, fx + fr//2, fy + fr//2], fill="#fde047")

    # Skeletal Shattered Trees stripped bare by artillery fire
    for tx in [220, 680, 1200, 1640]:
        th = 140 + (tx % 80)
        draw.line([tx, sky_h + 20, tx, sky_h - th], fill="#1c1917", width=8)
        draw.line([tx, sky_h - th//2, tx - 25, sky_h - th - 10], fill="#1c1917", width=5)
        draw.line([tx, sky_h - th//3, tx + 30, sky_h - th + 20], fill="#1c1917", width=5)

    # No Man's Land Muddy Wasteland & Shell Craters
    trench_top = int(h * 0.52)
    draw.rectangle([0, sky_h, w, trench_top], fill="#44403c")
    # Shell craters filled with murky water
    for cx, cy, cw, ch in [(360, sky_h + 50, 110, 40), (880, sky_h + 70, 150, 55), (1500, sky_h + 45, 120, 45)]:
        draw.ellipse([cx - cw//2, cy - ch//2, cx + cw//2, cy + ch//2], fill="#292524", outline="#1c1917", width=4)
        draw.ellipse([cx - cw//3, cy - ch//3, cx + cw//3, cy + ch//3], fill="#3f3f46")

    # Barbed Wire Coils across No Man's Land
    for wy in [sky_h + 30, sky_h + 85]:
        for bx in range(40, w - 40, 60):
            # Wooden post stake
            draw.line([bx, wy - 35, bx, wy + 25], fill="#292524", width=5)
            # Twisted wire loops
            draw.ellipse([bx - 20, wy - 20, bx + 20, wy + 20], outline="#78716c", width=2)
            draw.line([bx - 30, wy, bx + 30, wy], fill="#78716c", width=2)

    # Deep Zig-Zag Allied Trench in Foreground
    draw.polygon([(0, trench_top), (w, trench_top), (w, h), (0, h)], fill="#2d2822")

    # Sandbag Parapet Wall
    for sby in range(trench_top, trench_top + 90, 28):
        offset = ((sby // 28) % 2) * 35
        for sbx in range(-35, w + 70, 70):
            bx = sbx + offset
            draw.rounded_rectangle([bx, sby, bx + 65, sby + 25], radius=6, fill="#78716c", outline="#292524", width=3)

    # Corrugated Iron Trench Revetments & Duckboard Walkways
    duck_y = int(h * 0.78)
    draw.rectangle([0, duck_y, w, h], fill="#3e3223")
    # Wooden duckboard slats
    for dx in range(0, w, 32):
        draw.rectangle([dx, duck_y + 10, dx + 24, h - 20], fill="#5c442b", outline="#1c140c", width=3)

    return im

# 9. PREHISTORIC ICE AGE SAVANNA / CAVE
def render_prehistoric_savanna(w: int = 1920, h: int = 1080) -> Image.Image:
    im = Image.new("RGB", (w, h), "#c26d38")
    draw = ImageDraw.Draw(im)

    # Cold Sunset Orange / Violet Sky
    sky_h = int(h * 0.42)
    for y in range(sky_h):
        r = int(195 + (y/sky_h) * 45)
        g = int(100 + (y/sky_h) * 60)
        b = int(75 + (y/sky_h) * 55)
        draw.line([(0, y), (w, y)], fill=(min(255, r), min(255, g), min(255, b)))

    # Distant Glaciated Snow Peaks
    peak_pts = [(0, sky_h)]
    for px in range(0, w + 120, 140):
        py = sky_h - 80 - int(math.sin(px * 0.01) * 60)
        peak_pts.append((px, py))
    peak_pts.extend([(w, sky_h), (0, sky_h)])
    draw.polygon(peak_pts, fill="#ffffff", outline="#7c2d12", width=3)

    # Steppe Tundra Plains
    draw.rectangle([0, sky_h, w, h], fill="#a16207")
    rnd = random.Random(20000)
    for _ in range(70):
        gx = rnd.randint(10, w - 10)
        gy = rnd.randint(sky_h + 20, int(h * 0.75))
        draw.line([gx, gy, gx + rnd.randint(-15, 15), gy - rnd.randint(15, 35)], fill="#78350f", width=3)

    # Woolly Mammoth Herd Silhouette in the distance
    for mx, my, m_sc in [(int(w * 0.38), sky_h + 60, 0.7), (int(w * 0.48), sky_h + 45, 0.85), (int(w * 0.58), sky_h + 70, 0.65)]:
        # Mammoth body
        draw.ellipse([mx - int(55*m_sc), my - int(45*m_sc), mx + int(55*m_sc), my + int(35*m_sc)], fill="#292524")
        # Mammoth head
        draw.ellipse([mx - int(75*m_sc), my - int(40*m_sc), mx - int(25*m_sc), my + int(10*m_sc)], fill="#292524")
        # Curved Tusk
        draw.arc([mx - int(95*m_sc), my - int(35*m_sc), mx - int(35*m_sc), my + int(35*m_sc)], start=90, end=270, fill="#fef08a", width=int(4*m_sc))
        # Trunk
        draw.line([mx - int(65*m_sc), my, mx - int(75*m_sc), my + int(35*m_sc)], fill="#292524", width=int(8*m_sc))

    # Foreground Cave Overhang & Primitive Campfire
    # Massive cave rock framing top & left
    draw.polygon([(0, 0), (int(w * 0.42), 0), (int(w * 0.28), int(h * 0.45)), (0, int(h * 0.85))], fill="#1c1917")
    # Primitive ochre cave painting of running bison
    draw.ellipse([80, 160, 180, 220], fill="#991b1b")
    draw.ellipse([60, 180, 95, 210], fill="#991b1b")
    draw.line([90, 220, 85, 255], fill="#991b1b", width=4)
    draw.line([165, 220, 170, 255], fill="#991b1b", width=4)

    # Crackling Campfire in foreground
    fire_x, fire_y = int(w * 0.28), int(h * 0.84)
    # Fire glow radius
    for gr in range(160, 30, -30):
        draw.ellipse([fire_x - gr, fire_y - gr//2, fire_x + gr, fire_y + gr//2], outline=(255, 165, 0, 20), width=15)
    # Campfire logs
    draw.line([fire_x - 50, fire_y + 15, fire_x + 50, fire_y - 15], fill="#451a03", width=10)
    draw.line([fire_x - 50, fire_y - 15, fire_x + 50, fire_y + 15], fill="#451a03", width=10)
    # Flames
    draw.polygon([(fire_x, fire_y - 75), (fire_x + 35, fire_y), (fire_x - 35, fire_y)], fill="#ea580c")
    draw.polygon([(fire_x, fire_y - 50), (fire_x + 20, fire_y), (fire_x - 20, fire_y)], fill="#fde047")

    return im

def main():
    test_dir = Path("scratch/new_scenes")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = [
        ("05_assembly.jpg", render_french_assembly, "1789 • NATIONAL ASSEMBLY"),
        ("06_colosseum.jpg", render_roman_colosseum, "80 AD • COLOSSEUM"),
        ("07_hastings.jpg", render_hastings_battlefield, "1066 • SENLAC HILL"),
        ("08_trench.jpg", render_trench_battlefield, "1916 • WESTERN FRONT"),
        ("09_prehistoric.jpg", render_prehistoric_savanna, "20,000 BC • ICE AGE"),
    ]
    for name, func, badge in scenes:
        im = func(1920, 1080)
        stamp_date_pill(im, badge)
        p = test_dir / name
        im.save(p, "JPEG", quality=95)
        print(f"Rendered {name} -> {p}")

if __name__ == "__main__":
    main()
