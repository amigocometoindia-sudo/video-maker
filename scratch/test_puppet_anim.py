import os, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw

def render_cartoon_puppet_frame(
    role: str = "knight",
    expression: str = "angry",
    prop: str = "sword",
    target_h: int = 560,
    facing: str = "right",
    mouth_state: str = "closed", # "closed", "mid", "open", "shout"
    blink: bool = False,
    head_tilt: float = 0.0, # degrees
    arm_phase: float = 0.0, # 0.0 to 1.0 (for weapon swing/gesture)
    hop_offset: int = 0,
) -> Image.Image:
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
    leg_w = 5
    leg_col = "#111827"

    # Legs (squash/stretch with hop)
    left_foot_y = ground_y - hop_offset // 2
    right_foot_y = ground_y - hop_offset // 2
    draw.line([mid_x - 22, body_bottom - 10, mid_x - 35, left_foot_y], fill=leg_col, width=leg_w)
    draw.ellipse([mid_x - 45, left_foot_y - 6, mid_x - 25, left_foot_y + 4], fill=leg_col)
    draw.line([mid_x + 22, body_bottom - 10, mid_x + 35, right_foot_y], fill=leg_col, width=leg_w)
    draw.ellipse([mid_x + 25, right_foot_y - 6, mid_x + 45, right_foot_y + 4], fill=leg_col)

    # Costume
    if "knight" in role:
        draw.polygon([(mid_x - 48, body_top), (mid_x + 48, body_top), (mid_x + 55, body_bottom + 12), (mid_x - 55, body_bottom + 12)], fill="#475569", outline="#0f172a", width=4)
        draw.polygon([(mid_x - 42, body_top + 10), (mid_x + 42, body_top + 10), (mid_x + 48, body_bottom), (mid_x - 48, body_bottom)], fill="#1e40af")
        draw.line([mid_x, body_top + 10, mid_x, body_bottom], fill="#dc2626", width=10)
    elif "king" in role:
        draw.polygon([(mid_x - 55, body_top), (mid_x + 55, body_top), (mid_x + 68, body_bottom + 15), (mid_x - 68, body_bottom + 15)], fill="#831843", outline="#330b1b", width=4)
        draw.arc([mid_x - 40, body_top - 10, mid_x + 40, body_top + 45], 0, 180, fill="#facc15", width=6)
    else: # Peasant
        draw.polygon([(mid_x - 45, body_top), (mid_x + 45, body_top), (mid_x + 55, body_bottom), (mid_x - 55, body_bottom)], fill="#8c7355", outline="#2b2319", width=4)

    # Head (rotated with head_tilt)
    skin_col = "#f5c69b"
    head_im = Image.new("RGBA", (head_r * 4, head_r * 4), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(head_im)
    hc_x = head_im.width // 2
    hc_y = head_im.height // 2

    # Draw head circle
    hdraw.ellipse([hc_x - head_r, hc_y - head_r, hc_x + head_r, hc_y + head_r], fill=skin_col, outline="#2c1a0e", width=4)

    # Headgear
    if "knight" in role:
        hdraw.polygon([(hc_x - head_r - 6, hc_y), (hc_x + head_r + 6, hc_y), (hc_x, hc_y - head_r - 35)], fill="#64748b", outline="#1e293b", width=4)
        hdraw.line([hc_x, hc_y - 20, hc_x, hc_y + 12], fill="#334155", width=6)
    elif "king" in role:
        crown_y = hc_y - head_r - 5
        hdraw.polygon([
            (hc_x - 48, crown_y + 15), (hc_x - 48, crown_y - 25), (hc_x - 24, crown_y - 10),
            (hc_x, crown_y - 35), (hc_x + 24, crown_y - 10), (hc_x + 48, crown_y - 25), (hc_x + 48, crown_y + 15)
        ], fill="#facc15", outline="#713f12", width=3)
        for rx in [hc_x - 30, hc_x, hc_x + 30]:
            hdraw.ellipse([rx - 4, crown_y + 2, rx + 4, crown_y + 10], fill="#dc2626")
    else: # Hair
        hdraw.polygon([(hc_x - head_r - 4, hc_y - 10), (hc_x + head_r + 4, hc_y - 10), (hc_x + head_r - 10, hc_y - head_r - 12), (hc_x - head_r + 10, hc_y - head_r - 12)], fill="#452a17", outline="#24140a", width=3)

    # Eyes & Eyebrows
    eye_y = hc_y - 6
    eye_r = 16
    left_eye_x = hc_x - 22
    right_eye_x = hc_x + 22

    if blink:
        # Blink slit - -
        hdraw.line([left_eye_x - 14, eye_y, left_eye_x + 14, eye_y], fill="#111827", width=5)
        hdraw.line([right_eye_x - 14, eye_y, right_eye_x + 14, eye_y], fill="#111827", width=5)
    else:
        hdraw.ellipse([left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r], fill="#ffffff", outline="#111827", width=3)
        hdraw.ellipse([right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r], fill="#ffffff", outline="#111827", width=3)
        pupil_ox = 3 if not flip else -3
        hdraw.ellipse([left_eye_x + pupil_ox - 6, eye_y - 6, left_eye_x + pupil_ox + 6, eye_y + 6], fill="#111827")
        hdraw.ellipse([right_eye_x + pupil_ox - 6, eye_y - 6, right_eye_x + pupil_ox + 6, eye_y + 6], fill="#111827")

    # Eyebrows
    if expression == "angry":
        hdraw.line([left_eye_x - 16, eye_y - 24, left_eye_x + 14, eye_y - 16], fill="#111827", width=5)
        hdraw.line([right_eye_x + 16, eye_y - 24, right_eye_x - 14, eye_y - 16], fill="#111827", width=5)
    else:
        hdraw.line([left_eye_x - 14, eye_y - 20, left_eye_x + 14, eye_y - 20], fill="#111827", width=4)
        hdraw.line([right_eye_x - 14, eye_y - 20, right_eye_x + 14, eye_y - 20], fill="#111827", width=4)

    # Animated Mouth (Viseme flaps!)
    mouth_y = hc_y + 24
    if mouth_state == "open" or mouth_state == "shout":
        hdraw.polygon([(hc_x - 22, mouth_y - 5), (hc_x + 22, mouth_y - 5), (hc_x + 16, mouth_y + 24), (hc_x - 16, mouth_y + 24)], fill="#1f130b", outline="#111827", width=3)
        hdraw.rectangle([hc_x - 16, mouth_y - 4, hc_x + 16, mouth_y + 3], fill="#ffffff") # teeth
        hdraw.ellipse([hc_x - 10, mouth_y + 10, hc_x + 10, mouth_y + 22], fill="#f43f5e") # tongue
    elif mouth_state == "mid":
        hdraw.ellipse([hc_x - 16, mouth_y - 4, hc_x + 16, mouth_y + 14], fill="#1f130b", outline="#111827", width=3)
        hdraw.rectangle([hc_x - 12, mouth_y - 3, hc_x + 12, mouth_y + 2], fill="#ffffff")
    else: # closed
        hdraw.arc([hc_x - 18, mouth_y - 8, hc_x + 18, mouth_y + 14], 10, 170, fill="#111827", width=4)

    # Paste rotated head onto canvas
    if abs(head_tilt) > 0.1:
        head_rotated = head_im.rotate(head_tilt, resample=Image.BICUBIC)
    else:
        head_rotated = head_im
    im.paste(head_rotated, (mid_x - hc_x, head_y - hc_y), head_rotated)

    # Animated Arms & Weapon Swing
    arm_w = 5
    arm_col = "#111827"
    hand_y = body_top + 70

    if prop == "sword":
        # Arm & Sword swing based on arm_phase
        # arm_phase from 0.0 (raised) to 0.5 (slashing forward) to 1.0 (recovery)
        swing_angle = -0.4 + 1.2 * math.sin(arm_phase * math.pi)
        hand_x = int(mid_x + (70 + 35 * math.cos(swing_angle)) * (1 if not flip else -1))
        hy = int(hand_y + 40 * math.sin(swing_angle))
        draw.line([mid_x + (30 if not flip else -30), body_top + 15, hand_x, hy], fill=arm_col, width=arm_w)

        # Sword Blade
        sw_len = 90
        sw_x = int(hand_x + sw_len * math.cos(swing_angle - 0.5) * (1 if not flip else -1))
        sw_y = int(hy - sw_len * math.sin(swing_angle + 0.3))
        draw.line([hand_x, hy, sw_x, sw_y], fill="#cbd5e1", width=7)
        draw.line([hand_x, hy, sw_x, sw_y], fill="#ffffff", width=3)

        # Motion slash streak when swinging fast
        if 0.2 < arm_phase < 0.6:
            draw.arc([hand_x - 50, hy - 80, hand_x + 100, hy + 60], 280, 360, fill="#ffffff", width=4)
    else:
        # Gesturing arm
        gesture_offset = int(18 * math.sin(arm_phase * 2 * math.pi))
        draw.line([mid_x - 35, body_top + 15, mid_x - 65, hand_y + gesture_offset], fill=arm_col, width=arm_w)
        draw.line([mid_x + 35, body_top + 15, mid_x + 65, hand_y - gesture_offset], fill=arm_col, width=arm_w)

    return im

if __name__ == "__main__":
    out_dir = Path("scratch/test_anim_frames")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Generate 16 frames of authentic knight talking & swinging sword
    for i in range(16):
        t = i / 16.0
        mouth = ["closed", "mid", "open", "mid", "closed", "open", "mid", "closed", "open", "shout", "open", "mid", "closed", "open", "mid", "closed"][i]
        blink = (i in (7, 8)) # blink in the middle
        tilt = 4.0 * math.sin(t * 4 * math.pi) # head nod
        hop = int(12 * abs(math.sin(t * 2 * math.pi)))
        frame = render_cartoon_puppet_frame(role="knight", expression="angry", prop="sword", mouth_state=mouth, blink=blink, head_tilt=tilt, arm_phase=t, hop_offset=hop)
        frame.save(out_dir / f"knight_{i:03d}.png")
    print("Rendered 16 puppet animation frames successfully!")
