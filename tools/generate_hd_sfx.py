"""
HD Studio SFX Generator (48kHz Stereo/Mono)
===========================================
Synthesizes professional, high-fidelity sound effects for documentary & cartoon motion design:
- cinematic_whoosh: resonant smooth air sweep
- dramatic_impact: deep 40Hz sub-bass punch with acoustic decay
- war_horn: rich medieval brass carnyx/horn with harmonics and natural vibrato
- taiko_drum: deep resonating military war drum
- sword_clash: razor-sharp metallic blade strike with ringing brass overtones
- arrow_fly_hit: swift high-frequency whistle followed by sharp wooden impact
- cannon_boom: authentic deep concussive field artillery blast
- royal_fanfare: triumphant brass herald trumpet chord
- comic_boing: punchy cartoon pitch-bouncing spring
- tension_hit: dark cinematic trailer braam / brass accent
"""

import math
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav

SR = 48000
SFX_DIR = Path("sfx")
SFX_DIR.mkdir(parents=True, exist_ok=True)


def save_wav(name: str, audio: np.ndarray):
    # Normalize peak to -1.5 dB (0.84)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = (audio / peak) * 0.84
    int_audio = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    out_path = SFX_DIR / f"{name}.wav"
    wav.write(out_path, SR, int_audio)
    print(f"Generated {out_path} ({len(audio)/SR:.2f}s, peak {peak:.3f})")


def make_cinematic_whoosh():
    dur = 0.55
    t = np.linspace(0, dur, int(SR * dur))
    noise = np.random.normal(0, 1, len(t))
    # Smooth resonant band sweep from 250Hz up to 2800Hz and back down
    freq = 280 + 2600 * (np.sin(np.pi * t / dur) ** 2)
    carrier = np.sin(2 * np.pi * freq * t)
    # Bell curve volume envelope
    env = (np.sin(np.pi * t / dur) ** 2.5)
    sig = (noise * 0.7 + carrier * 0.3) * env
    # Low-pass smoothing
    kernel = np.ones(15) / 15
    sig = np.convolve(sig, kernel, mode="same")
    save_wav("cinematic_whoosh", sig)


def make_dramatic_impact():
    dur = 1.6
    t = np.linspace(0, dur, int(SR * dur))
    # Sub-bass punch dropping from 90Hz to 38Hz
    freq = 38 + 52 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * freq * t) * np.exp(-t * 3.5)
    # High transient click for attack
    t_click = t[: int(SR * 0.04)]
    click = np.sin(2 * np.pi * 320 * t_click) * np.exp(-t_click * 180)
    # Low frequency rumble
    rumble = np.random.normal(0, 0.4, len(t)) * np.exp(-t * 2.8)
    # Combine
    sig = sub * 0.75 + rumble * 0.25
    sig[: len(click)] += click * 0.5
    save_wav("dramatic_impact", sig)


def make_war_horn():
    dur = 1.8
    t = np.linspace(0, dur, int(SR * dur))
    # Fundamental: D3 (146.83 Hz) with medieval brass harmonics
    f0 = 146.83
    # Slight brass vibrato starting after attack
    vib = 1.0 + 0.015 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.2) / 0.4, 0, 1)
    pitch = f0 * vib
    # Natural brass harmonic series (1st, 2nd, 3rd, 4th, 5th, 6th)
    sig = (
        1.00 * np.sin(2 * np.pi * pitch * t) +
        0.75 * np.sin(2 * np.pi * pitch * 2 * t) +
        0.55 * np.sin(2 * np.pi * pitch * 3 * t) +
        0.35 * np.sin(2 * np.pi * pitch * 4 * t) +
        0.20 * np.sin(2 * np.pi * pitch * 5 * t) +
        0.10 * np.sin(2 * np.pi * pitch * 6 * t)
    )
    # Swell envelope (crescendo into sustained call, then gentle release)
    env = np.where(t < 0.25, t / 0.25, np.where(t < 1.3, 1.0, np.exp(-(t - 1.3) * 4.5)))
    sig = sig * env
    save_wav("war_horn", sig)


def make_taiko_drum():
    dur = 1.2
    t = np.linspace(0, dur, int(SR * dur))
    # Deep acoustic drum membrane pitch bend: 130Hz -> 55Hz
    freq = 55 + 75 * np.exp(-t * 22)
    drum = np.sin(2 * np.pi * freq * t) * np.exp(-t * 4.2)
    # Membrane stick slap transient
    t_slap = t[: int(SR * 0.03)]
    slap = np.random.normal(0, 1, len(t_slap)) * np.exp(-t_slap * 140)
    sig = drum * 0.85
    sig[: len(slap)] += slap * 0.4
    save_wav("taiko_drum", sig)


def make_sword_clash():
    dur = 0.95
    t = np.linspace(0, dur, int(SR * dur))
    # Metallic resonant clang frequencies (steel on steel)
    f_clash = [1240, 2480, 3720, 5100, 7850]
    amps = [0.45, 0.35, 0.25, 0.20, 0.15]
    decays = [5.5, 7.0, 9.0, 12.0, 16.0]

    clang = np.zeros_like(t)
    for f, a, d in zip(f_clash, amps, decays):
        clang += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)

    # Sharp blade strike transient
    t_hit = t[: int(SR * 0.025)]
    hit_noise = np.random.normal(0, 1, len(t_hit)) * np.exp(-t_hit * 220)
    clang[: len(hit_noise)] += hit_noise * 0.55
    save_wav("sword_clash", clang)


def make_arrow_fly_hit():
    dur = 0.75
    t = np.linspace(0, dur, int(SR * dur))
    # 1. Whoosh whistle (0.0 to 0.28s)
    t_whistle = t[t < 0.30]
    whistle_freq = 950 + 1200 * (t_whistle / 0.30)
    whistle = np.sin(2 * np.pi * whistle_freq * t_whistle) * (t_whistle / 0.30) * np.random.normal(0.8, 0.2, len(t_whistle))

    # 2. Sharp wooden thud impact at t=0.28s
    sig = np.zeros_like(t)
    sig[: len(whistle)] += whistle * 0.35

    impact_start = int(SR * 0.28)
    t_imp = t[impact_start:] - 0.28
    imp_freq = 110 * np.exp(-t_imp * 25)
    thud = np.sin(2 * np.pi * imp_freq * t_imp) * np.exp(-t_imp * 18)
    # Target crack
    t_crack = t_imp[: int(SR * 0.02)]
    crack = np.random.normal(0, 1, len(t_crack)) * np.exp(-t_crack * 260)

    imp_full = thud * 0.75
    imp_full[: len(crack)] += crack * 0.6
    sig[impact_start : impact_start + len(imp_full)] += imp_full
    save_wav("arrow_fly_hit", sig)


def make_cannon_boom():
    dur = 1.9
    t = np.linspace(0, dur, int(SR * dur))
    # Deep explosive detonation sweep (180Hz -> 32Hz)
    boom_f = 32 + 148 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * boom_f * t) * np.exp(-t * 2.8)
    # Heavy low-end rumble
    rumble = np.random.normal(0, 1, len(t)) * np.exp(-t * 3.2)
    kernel = np.ones(35) / 35
    rumble_filt = np.convolve(rumble, kernel, mode="same")
    # Concussive shockwave crack
    t_crack = t[: int(SR * 0.04)]
    shock = np.random.normal(0, 1, len(t_crack)) * np.exp(-t_crack * 110)

    sig = boom * 0.70 + rumble_filt * 0.35
    sig[: len(shock)] += shock * 0.45
    save_wav("cannon_boom", sig)


def make_royal_fanfare():
    dur = 1.6
    t = np.linspace(0, dur, int(SR * dur))
    # Triumphant Major Triad (Bb4 466Hz, D5 587Hz, F5 698Hz)
    chord = (
        0.40 * np.sin(2 * np.pi * 466.16 * t) +
        0.35 * np.sin(2 * np.pi * 587.33 * t) +
        0.30 * np.sin(2 * np.pi * 698.46 * t) +
        0.20 * np.sin(2 * np.pi * 932.33 * t)  # Octave
    )
    env = np.where(t < 0.08, t / 0.08, np.exp(-(t - 0.08) * 1.8))
    sig = chord * env
    save_wav("royal_fanfare", sig)


def make_comic_boing():
    dur = 0.65
    t = np.linspace(0, dur, int(SR * dur))
    # Classic cartoon spring bounce: rapidly vibrating frequency
    pitch = 240 + 380 * t + 80 * np.sin(2 * np.pi * 28 * t)
    sig = np.sin(2 * np.pi * pitch * t) * np.exp(-t * 3.6)
    save_wav("comic_boing", sig)


def make_tension_hit():
    dur = 1.5
    t = np.linspace(0, dur, int(SR * dur))
    # Dark cinematic trailer brass hit
    f0 = 65.4  # C2
    drone = (
        0.50 * np.sin(2 * np.pi * f0 * t) +
        0.40 * np.sin(2 * np.pi * f0 * 1.5 * t) +  # Minor third dissonance
        0.30 * np.sin(2 * np.pi * f0 * 2.0 * t) +
        0.25 * np.sin(2 * np.pi * f0 * 2.8 * t)
    )
    env = np.where(t < 0.06, t / 0.06, np.exp(-(t - 0.06) * 2.2))
    sig = drone * env
    save_wav("tension_hit", sig)


def make_cavalry_gallop():
    dur = 1.6
    t = np.linspace(0, dur, int(SR * dur))
    sig = np.zeros_like(t)
    # Horse hoof clatter rhythm: ta-ta-dum ... ta-ta-dum
    hoof_times = [0.08, 0.22, 0.38, 0.58, 0.72, 0.88, 1.08, 1.22, 1.38]
    for ht in hoof_times:
        idx = int(SR * ht)
        h_len = int(SR * 0.07)
        if idx + h_len < len(t):
            sub_t = np.linspace(0, 0.07, h_len)
            f_clop = 160 + 60 * np.exp(-sub_t * 60)
            clop = np.sin(2 * np.pi * f_clop * sub_t) * np.exp(-sub_t * 55)
            # Gravel/dirt scatter texture
            dirt = np.random.normal(0, 0.3, h_len) * np.exp(-sub_t * 70)
            sig[idx : idx + h_len] += clop * 0.7 + dirt * 0.3
    save_wav("cavalry_gallop", sig)


def make_victory_cheer():
    dur = 2.0
    t = np.linspace(0, dur, int(SR * dur))
    # Triumphant fanfare + roaring ambient crowd swell
    fanfare = (
        0.35 * np.sin(2 * np.pi * 523.25 * t) +  # C5
        0.30 * np.sin(2 * np.pi * 659.25 * t) +  # E5
        0.35 * np.sin(2 * np.pi * 783.99 * t)    # G5
    )
    env_f = np.where(t < 0.1, t / 0.1, np.exp(-(t - 0.1) * 2.5))
    # Crowd roar swell
    crowd = np.random.normal(0, 0.4, len(t))
    kernel = np.ones(80) / 80
    crowd_filt = np.convolve(crowd, kernel, mode="same")
    env_c = np.where(t < 0.4, t / 0.4, np.where(t < 1.4, 1.0, np.exp(-(t - 1.4) * 3.0)))
    sig = fanfare * env_f * 0.55 + crowd_filt * env_c * 0.45
    save_wav("victory_cheer", sig)


if __name__ == "__main__":
    print("Synthesizing HD Studio Sound Effects into sfx/...")
    make_cinematic_whoosh()
    make_dramatic_impact()
    make_war_horn()
    make_taiko_drum()
    make_sword_clash()
    make_arrow_fly_hit()
    make_cannon_boom()
    make_royal_fanfare()
    make_comic_boing()
    make_tension_hit()
    make_cavalry_gallop()
    make_victory_cheer()
    print("Done! All HD SFX ready.")
