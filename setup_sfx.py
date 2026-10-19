import wave
import struct
import math
import random
from pathlib import Path

SFX_DIR = Path("sfx")
SFX_DIR.mkdir(exist_ok=True)
SAMPLE_RATE = 44100

def save_wav(filename: str, samples: list[float]):
    out_path = SFX_DIR / filename
    with wave.open(str(out_path), "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)
        int_samples = [max(-32767, min(32767, int(s * 32767))) for s in samples]
        raw_data = struct.pack(f"<{len(int_samples)}h", *int_samples)
        wav.writeframes(raw_data)
    print(f"Generated {filename} ({len(samples)/SAMPLE_RATE:.2f}s)")

# 1. SWORD CLASH (Sharp metallic strike + resonant ringing)
def make_sword_clash():
    duration = 0.8
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    freq1, freq2, freq3 = 2800, 3400, 4200
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Initial noise burst for sharp impact
        noise = (random.random() * 2 - 1) * math.exp(-t * 60) * 0.7
        # Resonant metallic ring
        ring = (
            math.sin(2 * math.pi * freq1 * t) * 0.4 +
            math.sin(2 * math.pi * freq2 * t) * 0.3 +
            math.sin(2 * math.pi * freq3 * t) * 0.2
        ) * math.exp(-t * 8)
        sample = noise + ring
        samples.append(sample)
    save_wav("sword_clash.wav", samples)

# 2. CANNON BOOM / EXPLOSION (Deep punch + decaying rumble)
def make_cannon_boom():
    duration = 1.2
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Deep sub-bass punch
        sub = math.sin(2 * math.pi * (80 - t * 40) * t) * math.exp(-t * 5) * 0.8
        # Filtered low noise rumble
        noise = (random.random() * 2 - 1) * math.exp(-t * 4) * 0.5
        sample = sub + noise
        samples.append(sample)
    save_wav("cannon_boom.wav", samples)

# 3. COIN DING (High bell chime for money/wealth)
def make_coin_ding():
    duration = 0.9
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    f1, f2 = 2093, 3136  # C7 and G7 notes
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        bell = (
            math.sin(2 * math.pi * f1 * t) * 0.6 +
            math.sin(2 * math.pi * f2 * t) * 0.35
        ) * math.exp(-t * 5)
        samples.append(bell)
    save_wav("coin_ding.wav", samples)

# 4. CARTOON BOING (Spring frequency glide for funny moments)
def make_cartoon_boing():
    duration = 0.6
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Frequency glides up from 180 Hz to 450 Hz with vibrato
        base_freq = 180 + (t / duration) * 270
        vibrato = math.sin(2 * math.pi * 32 * t) * 35
        freq = base_freq + vibrato
        sample = math.sin(2 * math.pi * freq * t) * math.exp(-t * 4) * 0.85
        samples.append(sample)
    save_wav("cartoon_boing.wav", samples)

# 5. BODY THUD (Dull low impact for knocked-out stickman)
def make_thud():
    duration = 0.45
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Low frequency sudden drop
        freq = max(35, 140 - t * 300)
        sample = math.sin(2 * math.pi * freq * t) * math.exp(-t * 18) * 0.9
        samples.append(sample)
    save_wav("thud.wav", samples)

print("Synthesizing cartoon and history SFX...")
make_sword_clash()
make_cannon_boom()
make_coin_ding()
make_cartoon_boing()
make_thud()

try:
    from scratch.generate_popup_sounds import (
        make_cork_pop, make_ding_bell, make_wooden_block, make_mouth_pop,
        make_magic_chime, make_retro_blip, make_rubber_twang, make_camera_click,
        make_suction_pop, make_game_coin, make_subtle_tick, make_whip_whoosh,
        make_paper_snap, make_bubble_plop
    )
    print("Synthesizing popup sound effects suite...")
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
except Exception as e:
    pass

print("All sound effects created successfully!")
