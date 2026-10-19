import sys
sys.path.insert(0, ".")
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from animated_history_engine import (
    render_cartoon_character,
    stamp_date_pill,
)

# Test tent composite with characters
def create_tent_scene():
    w, h = 1920, 1080
    im = Image.new("RGB", (w, h), "#4d3d2e")
    draw = ImageDraw.Draw(im)

    # Rich draped canvas tent interior with curved bezier folds
    # Tent ceiling ridge pole
    draw.polygon([(0, 40), (w, 40), (w, 85), (0, 85)], fill="#2c2016", outline="#150e09", width=4)
    # Support poles
    for px in [320, int(w * 0.65)]:
        draw.polygon([(px - 14, 40), (px + 14, 40), (px + 18, h), (px - 18, h)], fill="#2c2016", outline="#150e09", width=4)

    # Draped tent canvas folds with shading
    for fx in range(-60, w + 120, 240):
        # Shaded fold
        draw.polygon([(fx, 80), (fx + 120, 80), (fx + 180, int(h * 0.72)), (fx - 40, int(h * 0.72))], fill="#594634", outline="#2c2016", width=3)
        draw.polygon([(fx + 120, 80), (fx + 240, 80), (fx + 280, int(h * 0.72)), (fx + 180, int(h * 0.72))], fill="#66513d", outline="#2c2016", width=3)

    # Tent Doorway opening out to sunny camp on right
    door_l = int(w * 0.66)
    door_r = int(w * 0.88)
    door_top = int(h * 0.26)
    door_bot = int(h * 0.75)

    # Bright sunny desert sky outside
    draw.rectangle([door_l, door_top, door_r, door_bot], fill="#48cae4")
    draw.rectangle([door_l, int(h * 0.52), door_r, door_bot], fill="#e0d0b4")
    # Distant mountains
    draw.polygon([(door_l, int(h * 0.52)), (door_r, int(h * 0.52)), (door_r, int(h * 0.48)), (door_l, int(h * 0.50))], fill="#c7b089")

    # Draped tent curtains tied back at doorway
    draw.polygon([(door_l - 40, door_top - 20), (door_l + 20, door_top - 20), (door_l - 10, door_bot), (door_l - 60, door_bot)], fill="#4a392b", outline="#1f160e", width=4)
    draw.polygon([(door_r + 40, door_top - 20), (door_r - 20, door_top - 20), (door_r + 10, door_bot), (door_r + 60, door_bot)], fill="#4a392b", outline="#1f160e", width=4)
    # Rolled top bundle
    draw.rounded_rectangle([door_l - 30, door_top - 40, door_r + 30, door_top + 10], radius=15, fill="#7d624a", outline="#2c2016", width=4)
    for bx in range(door_l - 10, door_r + 20, 35):
        draw.line([bx, door_top - 40, bx, door_top + 10], fill="#2c2016", width=3)

    # Sentry outside guarding tent entrance
    sentry = render_cartoon_character(role="roman_soldier", expression="angry", prop="spear", target_h=380, facing="left")
    im.paste(sentry, (door_r - 180, door_bot - 380 + 30), sentry)

    # Dirt Ground inside tent
    draw.polygon([(0, int(h * 0.70)), (w, int(h * 0.70)), (w, h), (0, h)], fill="#9e8564")

    # Wooden Bed / Cot on Left
    cot_y = int(h * 0.75)
    draw.polygon([(80, cot_y), (int(w * 0.45), cot_y), (int(w * 0.42), cot_y + 45), (60, cot_y + 45)], fill="#42220f", outline="#1c0d05", width=4)
    draw.rectangle([60, cot_y + 45, 80, int(h * 0.88)], fill="#2b1408", outline="#100602", width=3)
    draw.rectangle([int(w * 0.40), cot_y + 45, int(w * 0.42), int(h * 0.88)], fill="#2b1408", outline="#100602", width=3)
    # Bed mattress & folded blankets
    draw.rounded_rectangle([90, cot_y - 20, 240, cot_y], radius=10, fill="#786149", outline="#2b1408", width=3)
    draw.rounded_rectangle([250, cot_y - 20, 420, cot_y], radius=10, fill="#8c7358", outline="#2b1408", width=3)

    # Roman Commander's Wooden Campaign Table (Center)
    desk_cx = int(w * 0.58)
    desk_w = 480
    desk_top = int(h * 0.64)
    draw.polygon([
        (desk_cx - desk_w//2 + 30, desk_top),
        (desk_cx + desk_w//2 - 30, desk_top),
        (desk_cx + desk_w//2, desk_top + 50),
        (desk_cx - desk_w//2, desk_top + 50)
    ], fill="#3b2b1d", outline="#170f09", width=4)
    # Desk legs
    for leg_x in [desk_cx - desk_w//2 + 40, desk_cx + desk_w//2 - 40]:
        draw.rectangle([leg_x - 10, desk_top + 50, leg_x + 10, int(h * 0.89)], fill="#241912", outline="#0a0604", width=3)

    # Scrolls & maps on table
    draw.polygon([(desk_cx - 80, desk_top + 10), (desk_cx + 80, desk_top + 10), (desk_cx + 95, desk_top + 45), (desk_cx - 65, desk_top + 45)], fill="#e8d5b5", outline="#59442b", width=2)
    draw.ellipse([desk_cx + 110, desk_top + 20, desk_cx + 155, desk_top + 38], fill="#d4be98", outline="#59442b", width=2)

    # Composite Characters:
    # 1. Peasant Prisoner sitting on ground by cot on left
    peasant = render_cartoon_character(role="peasant", expression="screaming", prop="idle", target_h=460, facing="right", mouth_state="shout")
    im.paste(peasant, (int(w * 0.18), int(h * 0.48)), peasant)

    # 2. Roman Commander / Centurion sitting/standing at desk reading scroll
    centurion = render_cartoon_character(role="roman_soldier", expression="angry", prop="idle", target_h=520, facing="left", mouth_state="open")
    im.paste(centurion, (desk_cx - 100, int(h * 0.38)), centurion)

    # Top-Left Minimalist Date Pill
    stamp_date_pill(im, "66 AD • JUDEA")

    im.save("scratch/scene_test/test_tent_composite.jpg", "JPEG", quality=95)
    print("Tent composite saved!")

create_tent_scene()
