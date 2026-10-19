import wave
import struct
import math
import random
from pathlib import Path

SFX_POPUPS_DIR = Path("sfx/popups")
SFX_POPUPS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_RATE = 48000

def save_wav_stereo(filename: str, left_samples: list[float], right_samples: list[float] = None):
    if right_samples is None:
        right_samples = left_samples
    out_path = SFX_POPUPS_DIR / filename
    
    # Normalize peak if clipping
    max_peak = max(
        max(abs(s) for s in left_samples) if left_samples else 0.001,
        max(abs(s) for s in right_samples) if right_samples else 0.001
    )
    scale = 0.95 / max_peak if max_peak > 0.95 else 1.0

    int_samples = []
    for l, r in zip(left_samples, right_samples):
        sl = max(-32767, min(32767, int(l * scale * 32767)))
        sr = max(-32767, min(32767, int(r * scale * 32767)))
        int_samples.extend([sl, sr])

    with wave.open(str(out_path), "wb") as wav:
        wav.setnchannels(2)  # Stereo
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)
        raw_data = struct.pack(f"<{len(int_samples)}h", *int_samples)
        wav.writeframes(raw_data)
    print(f"Generated {filename} ({len(left_samples)/SAMPLE_RATE:.2f}s)")

# 1. CORK POP (Realistic champagne / cork bottle pop)
def make_cork_pop():
    duration = 0.22
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Vacuum snap transient (first 3ms)
        transient = (random.random() * 2 - 1) * math.exp(-t * 900) * 0.9 if t < 0.015 else 0.0
        # Cavity resonance drop from 380Hz to 180Hz
        freq = 180 + 200 * math.exp(-t * 45)
        phase = 2 * math.pi * (180 * t - (200 / 45) * math.exp(-t * 45))
        pop = math.sin(phase) * math.exp(-t * 32) * 0.95
        # Sub-body punch
        sub = math.sin(2 * math.pi * 95 * t) * math.exp(-t * 50) * 0.4
        # Subtle air hiss
        air = (random.random() * 2 - 1) * math.exp(-t * 22) * 0.12
        sample = transient + pop + sub + air
        left.append(sample)
        right.append(sample)
    save_wav_stereo("cork_pop.wav", left, right)

# 2. DING BELL (Pristine High-Frequency Notification / Service Bell Ding)
def make_ding_bell():
    duration = 0.85
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    f0 = 2637.0  # E7
    f1 = 5274.0  # Harmonic octave
    f2 = 7911.0  # High shimmer
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Strike transient
        strike = (random.random() * 2 - 1) * math.exp(-t * 600) * 0.3
        # Bell chime
        bell = (
            math.sin(2 * math.pi * f0 * t) * 0.65 * math.exp(-t * 4.5) +
            math.sin(2 * math.pi * f1 * t) * 0.25 * math.exp(-t * 7.0) +
            math.sin(2 * math.pi * f2 * t) * 0.15 * math.exp(-t * 11.0)
        )
        sample = strike + bell
        left.append(sample)
        # Slight stereo chorus on right channel
        bell_r = (
            math.sin(2 * math.pi * (f0 + 1.8) * t) * 0.65 * math.exp(-t * 4.5) +
            math.sin(2 * math.pi * (f1 - 1.2) * t) * 0.25 * math.exp(-t * 7.0) +
            math.sin(2 * math.pi * f2 * t) * 0.15 * math.exp(-t * 11.0)
        )
        right.append(strike + bell_r)
    save_wav_stereo("ding_bell.wav", left, right)

# 3. WOODEN BLOCK (Satisfying tactile hollow wood block tap)
def make_wooden_block():
    duration = 0.15
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Sharp click transient
        click = (random.random() * 2 - 1) * math.exp(-t * 800) * 0.5 if t < 0.01 else 0.0
        # Hollow wood resonance around 780 Hz decaying very fast
        f = 780 + 150 * math.exp(-t * 70)
        wood = (
            math.sin(2 * math.pi * f * t) * 0.75 +
            math.sin(2 * math.pi * f * 2.1 * t) * 0.25
        ) * math.exp(-t * 48)
        sample = click + wood
        left.append(sample)
        right.append(sample)
    save_wav_stereo("wooden_block.wav", left, right)

# 4. MOUTH POP (Vocal / cheek plop sound)
def make_mouth_pop():
    duration = 0.18
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Fast upward chirp from 240Hz to 820Hz in 15ms, then resonance at 520Hz decaying
        if t < 0.02:
            freq = 240 + (t / 0.02) * 580
        else:
            freq = 820 * math.exp(-(t - 0.02) * 35) + 300 * (1 - math.exp(-(t - 0.02) * 35))
        pop = math.sin(2 * math.pi * freq * t) * math.exp(-t * 36) * 0.95
        # Round 2nd harmonic
        harm = math.sin(2 * math.pi * freq * 1.85 * t) * math.exp(-t * 50) * 0.2
        sample = pop + harm
        left.append(sample)
        right.append(sample)
    save_wav_stereo("mouth_pop.wav", left, right)

# 5. MAGIC CHIME (Sparkling upward star shimmer)
def make_magic_chime():
    duration = 0.70
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    notes = [1046.5, 1318.5, 1567.98, 2093.0, 2637.0]  # C6, E6, G6, C7, E7
    delays = [0.0, 0.035, 0.070, 0.105, 0.140]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        sample_l, sample_r = 0.0, 0.0
        for idx, (note, delay) in enumerate(zip(notes, delays)):
            if t >= delay:
                dt = t - delay
                amp = math.exp(-dt * 6.5) * 0.35
                chime_l = (math.sin(2 * math.pi * note * dt) + 0.3 * math.sin(2 * math.pi * note * 2 * dt)) * amp
                chime_r = (math.sin(2 * math.pi * (note + 2.0) * dt) + 0.3 * math.sin(2 * math.pi * note * 2 * dt)) * amp
                # Pan notes across stereo field
                pan = idx / (len(notes) - 1)  # 0 to 1
                sample_l += chime_l * (1 - pan * 0.5)
                sample_r += chime_r * (0.5 + pan * 0.5)
        left.append(sample_l)
        right.append(sample_r)
    save_wav_stereo("magic_chime.wav", left, right)

# 6. RETRO BLIP (8-bit arcade jump chirp)
def make_retro_blip():
    duration = 0.14
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Fast upward sweep 350Hz -> 1450Hz
        freq = 350 + (t / duration) * 1100
        # Pseudo square/triangle wave for retro feel
        phase = (t * freq) % 1.0
        wave_val = (phase * 2 - 1) if phase < 0.5 else ((1 - phase) * 2 - 1)
        amp = (1.0 - t / duration) ** 0.8 * 0.8
        sample = wave_val * amp
        left.append(sample)
        right.append(sample)
    save_wav_stereo("retro_blip.wav", left, right)

# 7. RUBBER TWANG (Elastic spring snap)
def make_rubber_twang():
    duration = 0.42
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        base_f = 190 + (t / duration) * 260
        vibrato = math.sin(2 * math.pi * 38 * t) * 45 * math.exp(-t * 6)
        freq = base_f + vibrato
        twang = math.sin(2 * math.pi * freq * t) * math.exp(-t * 7.5) * 0.85
        # Transient snap
        snap = (random.random() * 2 - 1) * math.exp(-t * 300) * 0.35 if t < 0.02 else 0.0
        sample = twang + snap
        left.append(sample)
        right.append(sample)
    save_wav_stereo("rubber_twang.wav", left, right)

# 8. CAMERA CLICK (Snappy modern camera shutter)
def make_camera_click():
    duration = 0.16
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # First click (shutter blade open)
        click1 = (random.random() * 2 - 1) * math.exp(-t * 500) * 0.6 if t < 0.03 else 0.0
        # Second sharper click (shutter blade close at 35ms)
        click2 = 0.0
        if t >= 0.035:
            dt2 = t - 0.035
            click2 = (random.random() * 2 - 1) * math.exp(-dt2 * 600) * 0.85
            # Mechanical resonance
            mech = math.sin(2 * math.pi * 1850 * dt2) * math.exp(-dt2 * 60) * 0.3
            click2 += mech
        sample = click1 + click2
        left.append(sample)
        right.append(sample)
    save_wav_stereo("camera_click.wav", left, right)

# 9. SUCTION POP (Deep rubber plunger pop)
def make_suction_pop():
    duration = 0.20
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Deep downward plunge 550Hz -> 110Hz
        freq = 110 + 440 * math.exp(-t * 38)
        phase = 2 * math.pi * (110 * t - (440 / 38) * math.exp(-t * 38))
        pop = math.sin(phase) * math.exp(-t * 26) * 0.95
        # Low boom body
        boom = math.sin(2 * math.pi * 75 * t) * math.exp(-t * 28) * 0.5
        sample = pop + boom
        left.append(sample)
        right.append(sample)
    save_wav_stereo("suction_pop.wav", left, right)

# 10. GAME COIN (Two-tone arcade star pickup chime)
def make_game_coin():
    duration = 0.45
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    n1, n2 = 987.77, 1318.51  # B5, E6
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        if t < 0.075:
            tone = math.sin(2 * math.pi * n1 * t) * 0.8
        else:
            dt = t - 0.075
            tone = math.sin(2 * math.pi * n2 * dt) * math.exp(-dt * 6.0) * 0.9
            tone += math.sin(2 * math.pi * (n2 * 2) * dt) * math.exp(-dt * 9.0) * 0.2
        left.append(tone)
        right.append(tone)
    save_wav_stereo("game_coin.wav", left, right)

# 11. SUBTLE TICK (Minimalist clean UI pop / tick for sleek explainer videos)
def make_subtle_tick():
    duration = 0.07
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Gentle rounded pop at 1200 Hz decaying in 25ms
        pop = math.sin(2 * math.pi * 1250 * t) * math.exp(-t * 90) * 0.85
        click = (random.random() * 2 - 1) * math.exp(-t * 700) * 0.25 if t < 0.008 else 0.0
        sample = pop + click
        left.append(sample)
        right.append(sample)
    save_wav_stereo("subtle_tick.wav", left, right)

# 12. WHIP WHOOSH (Crisp fast air whip)
def make_whip_whoosh():
    duration = 0.24
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope rises to peak at 0.08s then quickly falls
        env = math.exp(-((t - 0.08) ** 2) / (2 * (0.035 ** 2)))
        noise = (random.random() * 2 - 1)
        # Resonant high-pass sweep
        center_f = 1200 + 3200 * math.sin(min(1.0, t / 0.16) * math.pi)
        swish = noise * math.sin(2 * math.pi * center_f * t) * env * 0.85
        # Stereo panning left to right
        pan = t / duration
        left.append(swish * (1.1 - pan * 0.8))
        right.append(swish * (0.3 + pan * 0.8))
    save_wav_stereo("whip_whoosh.wav", left, right)

# 13. PAPER SNAP (Snappy card flick / whip snap)
def make_paper_snap():
    duration = 0.12
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # High impact transient
        snap = (random.random() * 2 - 1) * math.exp(-t * 400) * 0.95 if t < 0.02 else 0.0
        # Paper flutter high frequency ring
        flutter = math.sin(2 * math.pi * 3100 * t) * math.exp(-t * 80) * 0.35
        air = (random.random() * 2 - 1) * math.exp(-t * 50) * 0.2
        sample = snap + flutter + air
        left.append(sample)
        right.append(sample)
    save_wav_stereo("paper_snap.wav", left, right)

# 14. BUBBLE PLOP (Bubbly liquid water drop pop)
def make_bubble_plop():
    duration = 0.16
    total_samples = int(SAMPLE_RATE * duration)
    left, right = [], []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Rising bubble frequency 420Hz -> 1180Hz
        freq = 420 + 760 * (1 - math.exp(-t * 40))
        plop = math.sin(2 * math.pi * freq * t) * math.exp(-t * 32) * 0.95
        left.append(plop)
        right.append(plop)
    save_wav_stereo("bubble_plop.wav", left, right)

if __name__ == "__main__":
    print("Synthesizing expanded suite of popup & sticker sound effects...")
    make_cork_pop()
    make_ding_bell()
    make_wooden_block()
    make_mouth_pop()
    make_magic_chime()
    make_retro_blip()
    make_rubber_twang()
    make_camera_click()
    make_suction_pop()
    make_game_coin()
    make_subtle_tick()
    make_whip_whoosh()
    make_paper_snap()
    make_bubble_plop()
    print("Done! All additional popup sound effects synthesized successfully.")
