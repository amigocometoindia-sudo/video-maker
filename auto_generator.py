import asyncio
import io
import math
import os
import re
import time
import json
import zipfile
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

import edge_tts
from srt_parser import Cue

DEFAULT_VOICE = "en-US-ChristopherNeural"

CURATED_VOICES = [
    {"id": "en-US-ChristopherNeural", "name": "Christopher (US)", "desc": "Authoritative Documentary (Recommended)", "gender": "Male"},
    {"id": "en-US-GuyNeural", "name": "Guy (US)", "desc": "Energetic & Modern Storyteller", "gender": "Male"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (UK)", "desc": "British Classic Narrator", "gender": "Male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US)", "desc": "Clear & Engaging Presenter", "gender": "Female"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (UK)", "desc": "Sophisticated Documentary", "gender": "Female"},
    {"id": "en-AU-WilliamNeural", "name": "William (AU)", "desc": "Deep & Dramatic Accent", "gender": "Male"},
]


def ms_to_srt_time(ms: int) -> str:
    h = ms // 3_600_000
    m = (ms % 3_600_000) // 60_000
    s = (ms % 60_000) // 1_000
    ml = ms % 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ml:03d}"


def _smart_crop_to_aspect(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Smart crops and resizes an image to fill target dimensions with center anchor."""
    target_ratio = target_w / target_h
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))

    resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    return img.resize((target_w, target_h), resample_filter)


def split_sentence_into_cues(start_ms: int, duration_ms: int, sentence: str, max_duration_ms: int = 4200) -> list[dict]:
    """
    Intelligent Clause-Aware Semantic Segmenter:
    Preserves complete, continuous grammatical sentences wherever possible.
    When long sentences exceed max_duration_ms, splits ONLY at logical grammatical clauses,
    punctuation pauses, or emotional contrast pivots, never mid-phrase.
    """
    sentence = sentence.strip()
    words = sentence.split()
    if not words:
        return []

    # If sentence fits naturally in a standard scene duration (up to 4.2s), keep it whole!
    if duration_ms <= max_duration_ms or len(words) <= 7:
        return [{"start_ms": start_ms, "duration_ms": duration_ms, "text": sentence}]

    # Look for logical grammatical clause split points
    delimiters = [
        r'(?<=[;:—…])\s+',
        r'(?<=--)\s+',
        r'(?<=,)\s+(?=(?:and|but|yet|so|while|until|because|however|then|or)\b)',
        r'(?<=,)\s+',
        r'\s+(?=(?:but|yet|however|suddenly|until|while|because)\b)',
    ]

    parts = []
    for pattern in delimiters:
        chunks = [c.strip() for c in re.split(pattern, sentence, flags=re.IGNORECASE) if c.strip()]
        if len(chunks) >= 2 and all(len(c.split()) >= 3 for c in chunks):
            parts = chunks
            break

    if not parts:
        conj_match = list(re.finditer(r'\s+(and|or|with|to|that)\s+', sentence, flags=re.IGNORECASE))
        if conj_match:
            mid = len(sentence) // 2
            best = min(conj_match, key=lambda m: abs(m.start() - mid))
            parts = [sentence[:best.start()].strip(), sentence[best.start():].strip()]

    if not parts or any(len(p.split()) < 3 for p in parts):
        parts = [sentence]

    # Distribute timing proportionally by character count
    total_chars = max(sum(len(p) for p in parts), 1)
    results = []
    elapsed = 0
    for idx, p in enumerate(parts):
        if idx == len(parts) - 1:
            p_dur = max(duration_ms - elapsed, 1000)
        else:
            p_dur = max(int(duration_ms * (len(p) / total_chars)), 1200)
        results.append({
            "start_ms": start_ms + elapsed,
            "duration_ms": p_dur,
            "text": p,
        })
        elapsed += p_dur

    return results


def enhance_image_visuals(
    img: Image.Image,
    target_width: int = 1920,
    target_height: int = 1080,
    enhance_colors: bool = True,
    apply_sharpening: bool = True,
) -> Image.Image:
    """
    AI-Grade Visual Upscaler & Cinematic Color Enhancer:
    1. Upscales sliced grid cells using high-precision Lanczos resampling.
    2. Enriches colors, vibrancy, and dynamic range to eliminate washed-out AI look.
    3. Restores micro-contrast and fine edge definition with unsharp masking.
    """
    w, h = img.size
    if w < target_width or h < target_height:
        scale_factor = max(target_width / w, target_height / h)
        new_w = max(int(round(w * scale_factor)), target_width)
        new_h = max(int(round(h * scale_factor)), target_height)
        resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        img = img.resize((new_w, new_h), resample=resample_filter)

    if enhance_colors:
        # Boost color vibrance and saturation (rich cinematic colors)
        img = ImageEnhance.Color(img).enhance(1.18)
        # Deepen shadows and expand dynamic range with subtle contrast
        img = ImageEnhance.Contrast(img).enhance(1.10)
        # Gentle brightness lift for shadowy details
        img = ImageEnhance.Brightness(img).enhance(1.02)

    if apply_sharpening:
        # Restore crisp edges and micro-textures
        img = img.filter(ImageFilter.UnsharpMask(radius=1.8, percent=130, threshold=2))

    return img


def split_grid_images(
    grid_images: list[Path],
    output_dir: Path,
    grid_type: str = "2x2",
    enhance: bool = True,
    target_width: int = 1920,
    target_height: int = 1080,
) -> list[Path]:
    """
    Slices 2x2 (4 panels) or 3x3 (9 panels) grid images into numbered individual scene images
    image_00000.jpg, image_00001.jpg ... in top-to-bottom, left-to-right reading order.
    Applies high-fidelity Lanczos upscaling, color grading, and edge sharpening.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cols, rows = (2, 2) if grid_type == "2x2" else (3, 3)

    sliced_paths = []
    global_idx = 0
    for g_path in sorted(grid_images):
        if not g_path.is_file():
            continue
        try:
            im = Image.open(g_path).convert("RGB")
            w, h = im.size
            cell_w = w // cols
            cell_h = h // rows
            for r in range(rows):
                for c in range(cols):
                    box = (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)
                    cell_img = im.crop(box)
                    if enhance:
                        cell_img = enhance_image_visuals(
                            cell_img,
                            target_width=target_width,
                            target_height=target_height,
                            enhance_colors=True,
                            apply_sharpening=True,
                        )
                    out_path = output_dir / f"image_{global_idx:05d}.jpg"
                    cell_img.save(out_path, "JPEG", quality=98)
                    sliced_paths.append(out_path)
                    global_idx += 1
        except Exception as e:
            print(f"[Grid Splitter Error] Failed to process {g_path}: {e}")

    return sliced_paths


def render_scene_card(
    cue_text: str,
    emotion: str,
    topic: str,
    index: int,
    w: int = 960,
    h: int = 540,
    style: str = "cinematic",
    character_img: Path | None = None,
) -> Image.Image:
    """Renders a single scene panel matching dialogue and emotion."""
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    domain = detect_topic_domain(topic or cue_text)

    palettes = {
        "stress_panic": {"top": (38, 12, 22), "bot": (18, 6, 12), "accent": (244, 63, 94), "pill": "#fda4af"},
        "thoughtful_pondering": {"top": (12, 24, 46), "bot": (6, 12, 24), "accent": (56, 189, 248), "pill": "#7dd3fc"},
        "joy_triumph": {"top": (10, 36, 26), "bot": (5, 18, 12), "accent": (16, 185, 129), "pill": "#6ee7b7"},
        "wealth_success": {"top": (42, 30, 10), "bot": (20, 14, 5), "accent": (245, 158, 11), "pill": "#fde68a"},
        "shock_surprise": {"top": (32, 16, 48), "bot": (16, 8, 24), "accent": (168, 85, 247), "pill": "#d8b4fe"},
        "battle_action": {"top": (44, 14, 14), "bot": (22, 6, 6), "accent": (239, 68, 68), "pill": "#fca5a5"},
        "defeat_sadness": {"top": (22, 26, 32), "bot": (10, 12, 16), "accent": (100, 116, 139), "pill": "#cbd5e1"},
        "focused_narrative": {"top": (15, 23, 42), "bot": (8, 12, 22), "accent": (14, 165, 233), "pill": "#93c5fd"},
    }

    pal = palettes.get(emotion, palettes["focused_narrative"])

    # Background gradient
    for y in range(h):
        ratio = y / max(h - 1, 1)
        r = int(pal["top"][0] + ratio * (pal["bot"][0] - pal["top"][0]))
        g = int(pal["top"][1] + ratio * (pal["bot"][1] - pal["top"][1]))
        b = int(pal["top"][2] + ratio * (pal["bot"][2] - pal["top"][2]))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    grid_col = (pal["accent"][0] // 5, pal["accent"][1] // 5, pal["accent"][2] // 5)
    for gx in range(40, w, 80):
        draw.line([(gx, 30), (gx, h - 30)], fill=grid_col, width=1)
    for gy in range(40, h, 60):
        draw.line([(30, gy), (w - 30, gy)], fill=grid_col, width=1)

    # Character sticker if available
    if character_img and Path(character_img).is_file():
        try:
            c_im = Image.open(character_img).convert("RGBA")
            c_h = int(h * 0.52)
            c_w = int(c_im.width * (c_h / c_im.height))
            c_im = c_im.resize((c_w, c_h), Image.Resampling.LANCZOS)
            im.paste(c_im, (w - c_w - 35, h - c_h - 40), c_im)
        except Exception:
            pass

    # Outer border
    draw.rounded_rectangle([12, 12, w - 12, h - 12], radius=16, outline=pal["accent"], width=3)

    # Top Scene Pill
    pill_text = f"SCENE {index + 1:02d} • {emotion.upper().replace('_', ' ')}"
    pill_w = len(pill_text) * 10 + 32
    draw.rounded_rectangle([28, 24, 28 + pill_w, 58], radius=8, fill=(10, 14, 23), outline=pal["accent"], width=2)

    font_small = None
    for fc in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if Path(fc).exists():
            font_small = ImageFont.truetype(fc, 16)
            break
    if font_small:
        draw.text((40, 32), pill_text, fill=pal["pill"], font=font_small)

    # Dialogue Quote Display (Middle-Bottom)
    clean_words = cue_text.strip().split()
    lines = []
    cur = []
    for wd in clean_words:
        cur.append(wd)
        if len(" ".join(cur)) > 32:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))

    font_text = None
    for fc in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if Path(fc).exists():
            font_text = ImageFont.truetype(fc, 20)
            break

    start_y = h - 50 - len(lines) * 28
    draw.rounded_rectangle([28, start_y - 10, w - 28, h - 28], radius=10, fill=(10, 14, 23))
    draw.rounded_rectangle([28, start_y - 10, w - 28, h - 28], radius=10, outline=grid_col, width=1)

    for l_idx, line in enumerate(lines):
        y_pos = start_y + l_idx * 26
        if font_text:
            draw.text((w // 2, y_pos), line, fill="#ffffff", font=font_text, anchor="mm")
        else:
            draw.text((w // 2, y_pos), line, fill="#ffffff", anchor="mm")

    return im


def generate_auto_grid_scenes(
    cues: list,
    topic: str = "",
    style: str = "cinematic",
    grid_type: str = "2x2",
    work_dir: Path = None,
) -> dict:
    """
    Automated Grid & Scene Generator:
    Takes dialogue cues, generates 2x2 or 3x3 multi-panel grid images,
    automatically slices them into numbered scene images (image_00000.jpg, etc.),
    and bundles them into a downloadable ZIP.
    """
    if not cues:
        raise ValueError("No cues provided for scene generation.")

    if work_dir is None:
        work_dir = Path("scratch") / f"auto_scenes_{int(time.time())}"
    work_dir.mkdir(parents=True, exist_ok=True)

    grids_dir = work_dir / "grids"
    slices_dir = work_dir / "slices"
    grids_dir.mkdir(parents=True, exist_ok=True)
    slices_dir.mkdir(parents=True, exist_ok=True)

    cols, rows = (2, 2) if grid_type == "2x2" else (3, 3)
    panels_per_grid = cols * rows

    norm_cues = []
    for idx, c in enumerate(cues):
        if hasattr(c, "text"):
            c_text = c.text
            c_start = getattr(c, "start_ms", 0)
            c_end = getattr(c, "end_ms", 0)
        elif isinstance(c, dict):
            c_text = c.get("text", "")
            c_start = c.get("start_ms", 0)
            c_end = c.get("end_ms", 0)
        else:
            c_text = str(c)
            c_start, c_end = 0, 0
        norm_cues.append({"index": idx, "text": c_text, "start_ms": c_start, "end_ms": c_end})

    breakdown = breakdown_dialogue_scenes(
        [Cue(start_ms=c["start_ms"], end_ms=c["end_ms"], text=c["text"]) for c in norm_cues],
        topic=topic,
        style=style,
    )
    emotions = [b["emotion"] for b in breakdown]

    char_stickers = []
    for d in [Path("characters"), Path("popups"), Path("custom_channel_assets")]:
        if d.is_dir():
            char_stickers.extend(list(d.glob("*.png")))

    panels = []
    for idx, c in enumerate(norm_cues):
        emo = emotions[idx] if idx < len(emotions) else "focused_narrative"
        matched_char = None
        for ch in char_stickers:
            stem_low = ch.stem.lower()
            if any(k in stem_low for k in emo.split("_")):
                matched_char = ch
                break
        if not matched_char and char_stickers:
            matched_char = char_stickers[idx % len(char_stickers)]

        p_img = render_scene_card(
            cue_text=c["text"],
            emotion=emo,
            topic=topic,
            index=idx,
            w=640,
            h=640 if grid_type == "2x2" else 420,
            style=style,
            character_img=matched_char,
        )
        panels.append(p_img)

    grid_paths = []
    total_grids = math.ceil(len(panels) / panels_per_grid)

    panel_w = panels[0].width
    panel_h = panels[0].height
    grid_w = panel_w * cols
    grid_h = panel_h * rows

    for g_idx in range(total_grids):
        g_img = Image.new("RGB", (grid_w, grid_h), (10, 14, 23))
        batch = panels[g_idx * panels_per_grid : (g_idx + 1) * panels_per_grid]
        for p_idx, p in enumerate(batch):
            r = p_idx // cols
            c = p_idx % cols
            g_img.paste(p, (c * panel_w, r * panel_h))
        g_path = grids_dir / f"grid_{g_idx:05d}.jpg"
        g_img.save(g_path, "JPEG", quality=95)
        grid_paths.append(g_path)

    sliced_paths = split_grid_images(grid_paths, slices_dir, grid_type=grid_type)

    zip_path = work_dir / "scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sliced_paths:
            zf.write(p, arcname=p.name)

    return {
        "grid_paths": grid_paths,
        "sliced_paths": sliced_paths,
        "zip_path": zip_path,
        "total_scenes": len(sliced_paths),
        "emotions": emotions,
        "work_dir": work_dir,
    }


async def generate_voice_and_srt(
    script_text: str,
    voice: str = DEFAULT_VOICE,
    output_audio_path: Path = None,
    output_srt_path: Path = None,
) -> tuple[Path, Path, list[Cue]]:
    """
    Converts narrative script text into MP3 audio and synchronized SRT cues using Edge-TTS.
    Guarantees strictly increasing, valid timestamps suitable for video rendering.
    """
    cleaned_text = re.sub(r"\s+", " ", script_text.strip())
    if not cleaned_text:
        raise ValueError("Script text cannot be empty.")

    raw_cues = []
    try:
        communicate = edge_tts.Communicate(cleaned_text, voice)
        with open(output_audio_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    start_ms = int(chunk["offset"] / 10_000)
                    duration_ms = int(chunk["duration"] / 10_000)
                    sub_cues = split_sentence_into_cues(start_ms, duration_ms, chunk["text"].strip(), max_duration_ms=2200)
                    raw_cues.extend(sub_cues)
    except Exception as e:
        print(f"[EdgeTTS Warning] {e}. Falling back to gTTS synthesis...", flush=True)
        try:
            from gtts import gTTS
            tts = gTTS(text=cleaned_text, lang="en")
            tts.save(str(output_audio_path))
            words = cleaned_text.split()
            tot_ms = max(int(len(words) * 330), 2500)
            raw_cues = split_sentence_into_cues(0, tot_ms, cleaned_text, max_duration_ms=2200)
        except Exception as e2:
            print(f"[gTTS Fallback Error] {e2}", flush=True)
            raise e

    if not raw_cues:
        # Fallback if no sentence boundaries detected (e.g. single short phrase)
        raw_cues.append({
            "start_ms": 100,
            "duration_ms": 3000,
            "text": cleaned_text,
        })

    # Normalize timestamps to guarantee valid, strictly increasing cues
    validated_cues: list[Cue] = []
    srt_lines: list[str] = []
    prev_start_ms = -1

    for i, item in enumerate(raw_cues):
        cur_start_ms = max(item["start_ms"], prev_start_ms + 100)
        cur_end_ms = max(cur_start_ms + item["duration_ms"], cur_start_ms + 400)
        prev_start_ms = cur_start_ms

        cue_obj = Cue(start_ms=cur_start_ms, end_ms=cur_end_ms, text=item["text"])
        validated_cues.append(cue_obj)

        cue_index = i + 1
        srt_lines.append(
            f"{cue_index}\n{ms_to_srt_time(cur_start_ms)} --> {ms_to_srt_time(cur_end_ms)}\n{item['text']}\n"
        )

    srt_content = "\n".join(srt_lines)
    output_srt_path.write_text(srt_content, encoding="utf-8")

    return output_audio_path, output_srt_path, validated_cues


def detect_topic_domain(topic: str) -> str:
    """
    Detects whether the topic is:
    - 'tech_business': Elon Musk, money, wealth, business, crypto, finance, tech, startup, stocks
    - 'psychology_mind': overthinking, brain, anxiety, psychology, habits, sleep, depression, focus
    - 'science_nature': ancient humans, evolution, universe, biology, physics, dinosaurs, space
    - 'history_war': battles, empires, kings, ancient civilizations, world war, Rome
    - 'general_explainer': default modern explainer
    """
    t = (topic or "").lower()
    if any(w in t for w in ["elon", "musk", "money", "rich", "wealth", "billionaire", "millionaire", "business", "crypto", "bitcoin", "startup", "stock", "invest", "finance", "apple", "steve jobs", "amazon", "bezos", "tesla", "spacex"]):
        return "tech_business"
    if any(w in t for w in ["overthink", "overthinking", "think", "brain", "anxiety", "psychology", "habit", "habits", "sleep", "mind", "mental", "dopamine", "adhd", "depression", "focus", "procrastinat"]):
        return "psychology_mind"
    if any(w in t for w in ["ancient human", "early human", "prehistoric", "caveman", "neanderthal", "evolution", "homo sapiens", "stone age", "hunter", "dinosaur", "universe", "space", "planet", "galaxy", "physics", "science", "biology"]):
        return "science_nature"
    if any(w in t for w in ["war", "battle", "empire", "king", "crusade", "rome", "roman", "viking", "norman", "1066", "revolution", "army", "general", "history", "ancient", "conquest"]):
        return "history_war"
    return "general_explainer"


def breakdown_dialogue_scenes(
    cues: list[Cue],
    topic: str = "",
    style: str = "cinematic",
    provider: str = "openai",
    api_key: str = "",
    api_model: str = None,
) -> list[dict]:
    """
    Intelligently analyzes dialogue cues to generate visual scene descriptions,
    emotional tones, and prompts for image/grid generation.
    """
    domain = detect_topic_domain(topic or (cues[0].text if cues else ""))
    
    style_prompts = {
        "cinematic": "cinematic realism, dynamic dramatic lighting, atmospheric depth, 8k documentary photograph",
        "stickman": "expressive 2D stickman cartoon, high-retention YouTube explainer style, clean bold outlines, vibrant colors, minimalist humorous props",
        "parchment_history": "vintage illuminated parchment illustration, warm textured medieval ink and wash, detailed historical cartoon",
        "anime_modern": "modern clean digital animation cel, high contrast, vibrant saturated color palette, clean vector lines",
    }
    style_suffix = style_prompts.get(style, style_prompts["cinematic"])

    results = []
    for idx, cue in enumerate(cues):
        text = (cue.text or "").strip()
        dur_s = round((cue.end_ms - cue.start_ms) / 1000.0, 2)
        
        t_low = text.lower()
        if any(w in t_low for w in ["stress", "anxiety", "panic", "worry", "fear", "terrified", "overwhelm"]):
            emotion = "stress_panic"
        elif any(w in t_low for w in ["think", "mind", "brain", "wonder", "ponder", "question", "doubt"]):
            emotion = "thoughtful_pondering"
        elif any(w in t_low for w in ["smile", "happy", "joy", "laugh", "relief", "victory", "won", "triumph", "breakthrough"]):
            emotion = "joy_triumph"
        elif any(w in t_low for w in ["money", "cash", "wealth", "rich", "billionaire", "gold", "profit", "fortune"]):
            emotion = "wealth_success"
        elif any(w in t_low for w in ["shock", "sudden", "unexpected", "surprise", "betray", "twist"]):
            emotion = "shock_surprise"
        elif any(w in t_low for w in ["dead", "defeat", "died", "ruin", "fall", "collapse", "loss"]):
            emotion = "defeat_sadness"
        elif any(w in t_low for w in ["battle", "fight", "attack", "strike", "war", "swords", "clash"]):
            emotion = "battle_action"
        else:
            emotion = "focused_narrative"

        clean_text_prompt = re.sub(r'[^a-zA-Z0-9\s,.-]', '', text).strip()
        scene_prompt = f"Visual scene illustrating: {clean_text_prompt}, {emotion.replace('_', ' ')} atmosphere, {style_suffix}"

        results.append({
            "cue_index": idx,
            "start_ms": cue.start_ms,
            "end_ms": cue.end_ms,
            "duration_s": dur_s,
            "text": text,
            "emotion": emotion,
            "scene_prompt": scene_prompt,
        })

    return results


def generate_script_with_ai(
    topic: str,
    duration_minutes: float = 1.0,
    provider: str = "openai",
    api_key: str = "",
    api_model: str = "",
) -> str:
    """
    Generates a high-retention, engaging YouTube explainer script via LLM across ANY genre:
    business/tech, human psychology, prehistoric science, history, or everyday dilemmas.
    """
    word_count_target = int(duration_minutes * 140)
    domain = detect_topic_domain(topic)

    domain_instructions = {
        "tech_business": (
            "Focus on high-stakes ambitions, bold gambles, extreme wealth, innovations, and the pivotal turning points "
            "that built a financial empire. Keep the tone sharp, energetic, and revealing."
        ),
        "psychology_mind": (
            "Focus on relatable human struggles, why our brains trick us into cognitive loops, vivid relatable scenarios, "
            "evolutionary survival mechanisms, and powerful breakthrough revelations."
        ),
        "science_nature": (
            "Focus on primal survival, mind-bending discoveries, daily existence against brutal elements, astonishing evolutionary leaps, "
            "and deep curiosity about how humans or nature actually worked."
        ),
        "history_war": (
            "Focus on dramatic clashes, larger-than-life historical figures, high-stakes military tactics, and decisive moments that altered history."
        ),
        "general_explainer": (
            "Hook the viewer with an intriguing question or counter-intuitive paradox, explain the underlying mechanics with clarity, "
            "and conclude with an eye-opening takeaway."
        ),
    }

    prompt = (
        f"You are the world's best YouTube explainer writer and visual storyteller, blending the viral engagement of "
        f"'Kurzgesagt', 'Vox', 'MagnatesMedia', and 'OverSimplified'.\n"
        f"Write a viral, high-retention narration script about: '{topic}'.\n\n"
        f"Genre Directives:\n{domain_instructions.get(domain, domain_instructions['general_explainer'])}\n\n"
        f"Rules for Maximum Retention:\n"
        f"1. Target length: approximately {word_count_target} words.\n"
        f"2. Hook the viewer immediately in the opening 5 seconds with an urgent question, shocking paradox, or high stakes.\n"
        f"3. Write in short, punchy sentences with vivid verbs suitable for voiceover narration.\n"
        f"4. Include direct character quotes or inner thoughts (e.g., Elon thought, 'We might go bankrupt tomorrow!', or Your brain whispers, 'What if everything goes wrong?') to trigger animated character lipsync and reactions.\n"
        f"5. Build to a decisive turning point, insight, or climax.\n"
        f"6. End with a memorable, punchy takeaway.\n"
        f"7. Do NOT include stage directions, bracketed cues, music notes, speaker labels, or scene numbers.\n"
        f"8. Output ONLY the raw spoken narration text so it can be fed directly into text-to-speech."
    )

    if api_key:
        try:
            from llm_analyzer import _call_llm_api
            result = _call_llm_api(prompt, provider, api_key, api_model)
            if result and len(result.strip()) > 50:
                clean = re.sub(r"\[.*?\]|\(.*?\)", "", result)
                clean = clean.replace('"', '').strip()
                return clean
        except Exception as e:
            print(f"[AutoScript AI Error] {e}. Falling back to curated script engine.", flush=True)

    # Built-in studio-grade fallback scripts tailored across all major domains
    tl = topic.lower()
    if any(w in tl for w in ["elon", "musk", "billionaire", "money", "rich", "wealth", "tesla", "spacex"]):
        return (
            "How did one awkward kid from South Africa become the richest human being in recorded history? "
            "It wasn't luck—it was an insane appetite for risk that nearly broke him multiple times. "
            "After selling PayPal in 2002, Elon Musk walked away with one hundred and eighty million dollars. "
            "Instead of retiring to a private island, he poured every single cent into two impossible dreams: electric cars with Tesla, and reusable rockets with SpaceX. "
            "By late 2008, both companies were literally hours away from total bankruptcy. "
            "Musk risked his last remaining dollars, sleeping on the factory floor, and personally working eighty-hour weeks. "
            "The gamble paid off. SpaceX successfully launched the Falcon 1, securing crucial NASA contracts, while Tesla transformed the global automotive industry. "
            "Today, his bold ventures have amassed a net worth surpassing two hundred billion dollars, proving that audacious risk-taking can reshape entire global industries."
        )
    elif any(w in tl for w in ["ancient human", "early human", "prehistoric", "caveman", "neanderthal", "stone age", "hunter gatherer"]):
        return (
            "Two hundred thousand years ago, what did an ordinary human do all day? "
            "Long before alarms, offices, or electricity, ancient Homo sapiens lived in a world where every single sunrise was a battle for survival. "
            "Mornings began with foraging: men tracked mammoth herds across freezing tundras, while women gathered edible roots, berries, and medicinal plants. "
            "The greatest invention wasn't a wheel—it was fire. "
            "Sitting around the glowing flames at night, tribes cooked tough meats, shared stories, painted cave walls, and developed complex spoken languages. "
            "They didn't just survive; they innovated bone needles, flint spears, and social cooperation that outperformed every other predator on Earth. "
            "Those primal survival instincts forged thousands of years ago are still hardwired into our modern brains today."
        )
    elif any(w in tl for w in ["overthink", "overthinking", "anxiety", "brain", "mind", "psychology", "worry"]):
        return (
            "Why do you lie awake at 3 AM overthinking an awkward comment you made five years ago? "
            "The truth is, your brain isn't broken—it is running an ancient survival program designed to keep you alive. "
            "To primitive humans, social rejection meant being kicked out of the tribe, which literally meant death. "
            "So your amygdala treats social embarrassment like a life-or-death emergency, replaying worst-case scenarios on an endless mental loop. "
            "Psychologists call this the negativity bias. Your brain generates thousands of hypothetical disasters, trying to protect you from future threats. "
            "The secret to breaking the cycle isn't fighting your thoughts; it is recognizing that thoughts are just mental suggestions, not reality. "
            "Once you name the loop, breathe deeply, and ground yourself in the present moment, the mental chaos immediately loses its power."
        )
    elif any(w in tl for w in ["hastings", "1066", "norman", "william", "harold"]):
        return (
            "In October 1066, England stood on the brink of an epic clash. "
            "King Harold Godwinson had just seized the throne, but across the English Channel, William Duke of Normandy claimed the crown was rightfully his. "
            "William assembled a massive invasion fleet and landed his knights on the southern coast. "
            "Near the town of Hastings, King Harold formed a formidable Anglo-Saxon shield wall atop Senlac Hill. "
            "The battle erupted with a roar as Norman cavalry charged the Saxon lines. "
            "Swords clashed and arrows darkened the sky, yet neither side would break. "
            "Then, William ordered a cunning feigned retreat, baiting Harold's defenders out of position. "
            "In the savage brawl that followed, an arrow struck King Harold, shattering Saxon resistance. "
            "William marched on London, was crowned King on Christmas Day, and changed the course of world history forever."
        )
    elif any(w in tl for w in ["french", "bastille", "louis xvi", "guillotine", "marie antoinette", "robespierre"]):
        return (
            "By 1789, France was completely broke, deeply in debt, and starving. "
            "King Louis the Sixteenth lived in golden palaces while ordinary peasants couldn't even afford bread. "
            "Furious crowds marched on Paris and stormed the dreaded Bastille fortress, tearing it down brick by brick. "
            "The revolutionaries abolished the old monarchy and proclaimed equality for all citizens. "
            "Yet paranoia quickly gripped Paris as the Reign of Terror began. "
            "The guillotine fell without mercy, claiming thousands of heads including the King himself. "
            "Out of the revolutionary chaos, an ambitious young artillery officer named Napoleon Bonaparte seized power, and France would never be the same."
        )
    elif any(w in tl for w in ["american", "independence", "washington", "tea party", "1776", "revolution"]):
        return (
            "In 1775, Britain thought governing thirteen American colonies would be simple. They were wrong. "
            "When King George imposed taxes on tea and paper without representation, the colonists dumped three hundred crates of tea into Boston harbor. "
            "Tensions exploded at Lexington and Concord with the shot heard around the world. "
            "General George Washington took command of a ragtag colonial militia facing the greatest military empire on Earth. "
            "Through freezing winters at Valley Forge and daring midnight crossings across the icy Delaware River, the Continental Army persevered. "
            "With French naval support, Washington trapped the British army at Yorktown, forcing a complete surrender. "
            "Against impossible odds, a new nation was born on the foundation of liberty and democracy."
        )
    elif any(w in tl for w in ["viking", "vikings", "ragnar", "norse", "lindisfarne"]):
        return (
            "In 793 AD, strange dragon-headed longships appeared off the windswept coast of northern England. "
            "Without warning, fierce Norse warriors stormed the monastery of Lindisfarne, plundering silver treasures and striking terror across Europe. "
            "The Viking Age had begun. "
            "Navigating stormy seas with extraordinary longships, Norse explorers raided from Ireland to Constantinople, and even crossed the Atlantic to North America. "
            "Yet they were more than raiders; they were master traders, lawgivers, and settlers who founded dynamic cities like Dublin and Kiev. "
            "Though medieval chroniclers feared them as merciless demons, their courage and seafaring genius fundamentally reshaped the medieval world."
        )
    elif any(w in tl for w in ["alexander", "macedon", "gaugamela", "persia"]):
        return (
            "At just twenty years old, Alexander the Great inherited the throne of Macedon and set his sights on the largest empire in human history: Persia. "
            "Leading an unstoppable army of Greek phalanxes and companion cavalry, Alexander marched into Asia. "
            "At the Battle of Gaugamela, facing overwhelming Persian numbers and scythed chariots, Alexander charged straight toward Emperor Darius. "
            "The Persian lines collapsed in panic, and the Great King fled into the dust. "
            "Alexander conquered from Egypt all the way to the Indus River, founding dozens of cities and never losing a single battle. "
            "Though he died mysteriously at thirty-two, his legendary ambition spread Hellenistic civilization across the ancient world."
        )
    elif any(w in tl for w in ["israel", "judea", "jewish", "jerusalem"]):
        return (
            "For over two thousand years, the history of Israel has been a relentless saga of faith, conflict, and survival. "
            "It began under the iron grip of Rome, where heavy imperial taxes sparked the Great Jewish Revolt in 66 AD. "
            "Roman legions laid siege to Jerusalem, leaving the Second Temple in burning ruins and scattering the population into global exile. "
            "Centuries rolled on as Byzantine emperors, Islamic Caliphates, and Crusader knights battled for dominion over the sacred lands. "
            "Then, in 1948, following the devastation of World War Two, the United Nations voted to establish a modern Jewish state. "
            "Neighboring armies invaded from all borders, igniting a war of survival across the desert dunes. "
            "Against fierce odds, Israel held its territory, establishing borders that still shape geopolitical headlines today."
        )
    elif any(w in tl for w in ["rome", "roman", "caesar", "empire"]):
        return (
            "From a humble muddy settlement on the Tiber River, Rome forged the greatest empire the ancient world had ever seen. "
            "Disciplined legions conquered the Mediterranean, while ambitious generals vied for supreme political power in the Senate. "
            "When Julius Caesar crossed the Rubicon, the old Republic crumbled, giving birth to imperial rule and mighty Caesars. "
            "Yet wealth bred corruption, borders grew too vast to defend, and barbarian migrations pressed relentlessly against the frontier. "
            "In 476 AD, the Western Roman Empire collapsed in flames, leaving behind laws, language, and monuments that echo through modern civilization."
        )
    else:
        clean_topic = topic.strip().title()
        return (
            f"Have you ever wondered what really drives {clean_topic}? "
            f"Beneath the surface lies a fascinating story of ambition, psychology, and hidden mechanics that few people truly understand. "
            f"It begins with a crucial challenge: how did this unexpected phenomenon change everything we thought we knew? "
            f"At every step, bold innovators and ordinary people faced high-stakes dilemmas, forcing them to adapt and push past conventional limits. "
            f"A decisive breakthrough shattered the old paradigm, turning quiet curiosity into a revolutionary realization. "
            f"When we look closer, {clean_topic} isn't just an interesting topic—it is a powerful lens revealing how our modern world actually works."
        )


def render_parchment_map(topic: str, cue_text: str, index: int, target_w: int = 1920, target_h: int = 1080) -> Image.Image:
    """Renders authentic Animated History vintage parchment map canvas with compass rose and antique borders."""
    im = Image.new("RGB", (target_w, target_h), "#ede1cb")
    draw = ImageDraw.Draw(im)

    # Aged paper vignette edges
    for i in range(16):
        margin = i * 4
        alpha_tint = (160 - i * 5, 130 - i * 4, 90 - i * 3)
        draw.rounded_rectangle([margin, margin, target_w - margin, target_h - margin], radius=24, outline=alpha_tint, width=4)

    # Outer antique double map frame
    draw.rounded_rectangle([60, 60, target_w - 60, target_h - 60], radius=16, outline="#785938", width=5)
    draw.rounded_rectangle([72, 72, target_w - 72, target_h - 72], radius=12, outline="#b8935c", width=2)

    # Vintage navigation grid lines (faint 30-degree lines across map)
    grid_color = "#e0d0b4"
    for x in range(150, target_w - 100, 240):
        draw.line([x, 80, x, target_h - 80], fill=grid_color, width=2)
    for y in range(150, target_h - 100, 200):
        draw.line([80, y, target_w - 80, y], fill=grid_color, width=2)

    # Ornamental Compass Rose (Top-Right)
    cx, cy, r = target_w - 180, 180, 75
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#a88554", width=3)
    draw.ellipse([cx - r + 15, cy - r + 15, cx + r - 15, cy + r - 15], outline="#c4a572", width=1)
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        tip_x = cx + math.sin(rad) * (r - 8)
        tip_y = cy - math.cos(rad) * (r - 8)
        draw.polygon([(cx, cy), (tip_x, tip_y), (cx + math.sin(rad + 0.3)*25, cy - math.cos(rad + 0.3)*25)], fill="#785938")
        draw.polygon([(cx, cy), (tip_x, tip_y), (cx + math.sin(rad - 0.3)*25, cy - math.cos(rad - 0.3)*25)], fill="#d4af72")

    font_title = None
    for fc in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if Path(fc).exists():
            font_title = ImageFont.truetype(fc, 38)
            break

    # Chapter Title Banner (Top-Center)
    title_text = f"— {topic.upper()} —"
    if font_title:
        draw.text((target_w // 2, 120), title_text, fill="#45321c", font=font_title, anchor="mm")

    # Ground terrain line for stickmen to stand on
    ground_y = target_h - 150
    draw.line([90, ground_y, target_w - 90, ground_y], fill="#b8935c", width=4)
    for gx in range(120, target_w - 120, 35):
        draw.line([gx, ground_y + 4, gx - 15, ground_y + 22], fill="#d4ba8a", width=2)

    return im


def render_thematic_canvas(topic: str, cue_text: str, index: int, target_w: int = 1920, target_h: int = 1080) -> Image.Image:
    """
    Renders high-retention procedural animated explainer background canvases tailored to the topic domain:
    - Tech & Business (e.g. Elon Musk, money, wealth) -> Sleek dark cyber slate with financial grid & cyan accent
    - Psychology & Mind (e.g. overthinking, anxiety, brain) -> Deep cerebral indigo with neural wave lines
    - Science & Prehistory (e.g. ancient humans, nature) -> Earthy stone/savanna with warm campfire horizon
    - History & War -> Authentic vintage parchment map
    - General Explainer -> Modern minimalist YouTube explainer backdrop
    """
    domain = detect_topic_domain(topic)
    if domain == "history_war":
        return render_parchment_map(topic, cue_text, index, target_w, target_h)

    im = Image.new("RGB", (target_w, target_h))
    draw = ImageDraw.Draw(im)

    font_title = None
    for fc in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/tahomabd.ttf"]:
        if Path(fc).exists():
            font_title = ImageFont.truetype(fc, 34)
            break

    if domain == "tech_business":
        for y in range(target_h):
            ratio = y / max(target_h, 1)
            r = int(11 + ratio * 14)
            g = int(15 + ratio * 20)
            b = int(26 + ratio * 34)
            draw.line([(0, y), (target_w, y)], fill=(r, g, b))

        grid_col = (25, 42, 68)
        for x in range(120, target_w, 180):
            draw.line([(x, 80), (x, target_h - 100)], fill=grid_col, width=1)
        for y in range(120, target_h - 100, 140):
            draw.line([(80, y), (target_w - 80, y)], fill=grid_col, width=1)

        ground_y = target_h - 150
        draw.line([80, ground_y, target_w - 80, ground_y], fill="#0284c7", width=3)
        draw.line([80, ground_y + 3, target_w - 80, ground_y + 3], fill="#0369a1", width=1)
        pill_text = f"— {topic.upper()} —"
        pill_col = "#38bdf8"

    elif domain == "psychology_mind":
        for y in range(target_h):
            ratio = y / max(target_h, 1)
            r = int(14 + ratio * 20)
            g = int(10 + ratio * 14)
            b = int(32 + ratio * 42)
            draw.line([(0, y), (target_w, y)], fill=(r, g, b))

        neural_nodes = [(320, 240), (520, 190), (740, 260), (1200, 210), (1420, 280), (1640, 220)]
        for i in range(len(neural_nodes) - 1):
            draw.line([neural_nodes[i], neural_nodes[i+1]], fill=(60, 45, 105), width=2)
        for nx, ny in neural_nodes:
            draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill="#c084fc", outline="#7e22ce")

        ground_y = target_h - 150
        draw.line([80, ground_y, target_w - 80, ground_y], fill="#a855f7", width=3)
        pill_text = f"— THE HUMAN MIND: {topic.upper()} —"
        pill_col = "#e9d5ff"

    elif domain == "science_nature":
        for y in range(target_h):
            ratio = y / max(target_h, 1)
            r = int(24 + ratio * 32)
            g = int(18 + ratio * 20)
            b = int(16 + ratio * 12)
            draw.line([(0, y), (target_w, y)], fill=(r, g, b))

        ground_y = target_h - 150
        draw.line([80, ground_y, target_w - 80, ground_y], fill="#b45309", width=4)
        for gx in range(120, target_w - 120, 40):
            draw.line([gx, ground_y + 4, gx - 12, ground_y + 20], fill="#78350f", width=2)

        pill_text = f"— {topic.upper()} —"
        pill_col = "#fbbf24"

    else:
        for y in range(target_h):
            ratio = y / max(target_h, 1)
            r = int(15 + ratio * 18)
            g = int(23 + ratio * 24)
            b = int(42 + ratio * 32)
            draw.line([(0, y), (target_w, y)], fill=(r, g, b))

        ground_y = target_h - 150
        draw.line([80, ground_y, target_w - 80, ground_y], fill="#f59e0b", width=3)
        pill_text = f"— {topic.upper()} —"
        pill_col = "#fde68a"

    if font_title:
        draw.text((target_w // 2, 95), pill_text, fill=pill_col, font=font_title, anchor="mm")

    return im


def fetch_topic_historical_archive(topic: str, max_images: int = 15) -> list[tuple[str, Image.Image]]:
    """
    Harvests authentic, high-res encyclopedic images, portraits, diagrams, or illustrations
    from English Wikipedia and Wikimedia Commons tailored to the topic domain.
    """
    import json
    images: list[tuple[str, Image.Image]] = []
    seen_urls = set()
    headers = {"User-Agent": "BahaaAI-ExplainerVideo/2.0 (contact@bahaa-ai.com)"}

    domain = detect_topic_domain(topic)
    clean_topic = re.sub(r"[^a-zA-Z0-9\s]", " ", topic).strip()

    if domain == "tech_business":
        blacklist_words = {"census", "postcode", "district", "constituency", "locator_map", "flag", "coat of arms"}
        query_variants = [
            f"{clean_topic}",
            f"{clean_topic} business",
            f"{clean_topic} technology",
            f"{clean_topic} net worth",
        ]
    elif domain == "psychology_mind":
        blacklist_words = {"census", "postcode", "district", "constituency", "locator_map"}
        query_variants = [
            f"{clean_topic}",
            f"{clean_topic} brain",
            f"{clean_topic} psychology",
            f"{clean_topic} neuroscience",
        ]
    elif domain == "science_nature":
        blacklist_words = {"census", "postcode", "district", "constituency"}
        query_variants = [
            f"{clean_topic}",
            f"{clean_topic} evolution",
            f"{clean_topic} archaeology",
            f"{clean_topic} science",
        ]
    elif domain == "history_war":
        blacklist_words = {
            "street", "town", "village", "railway", "station", "sign", "car", "modern", "road",
            "council", "district", "constituency", "parish", "borough", "hotel", "bus", "shop",
            "county", "census", "postcode"
        }
        query_variants = [
            f"{clean_topic} painting OR portrait",
            f"{clean_topic} tapestry OR artwork",
            f"{clean_topic} battle art OR engraving",
            f"{clean_topic} historical map",
        ]
    else:
        blacklist_words = {"census", "postcode", "district"}
        query_variants = [
            f"{clean_topic}",
            f"{clean_topic} concept",
            f"{clean_topic} diagram",
        ]

    for q_text in query_variants:
        if len(images) >= max_images:
            break
        try:
            q_enc = urllib.parse.quote(q_text)
            wiki_url = (
                f"https://en.wikipedia.org/w/api.php?action=query&generator=search"
                f"&gsrsearch={q_enc}&gsrlimit=12&prop=pageimages&pithumbsize=1280&format=json"
            )
            req = urllib.request.Request(wiki_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                title = p.get("title", "")
                t_words = set(re.findall(r'[a-zA-Z]+', title.lower()))
                if t_words.intersection(blacklist_words):
                    continue

                thumb = p.get("thumbnail", {}).get("source")
                if thumb and not thumb.lower().endswith(".svg") and thumb not in seen_urls:
                    thumb_lower = urllib.parse.unquote(thumb.lower())
                    if any(bw in thumb_lower for bw in blacklist_words):
                        continue
                    seen_urls.add(thumb)
                    try:
                        i_req = urllib.request.Request(thumb, headers=headers)
                        with urllib.request.urlopen(i_req, timeout=9) as i_resp:
                            raw = i_resp.read()
                        im = Image.open(io.BytesIO(raw))
                        if im.width >= 280 and im.height >= 240:
                            images.append((title, im.convert("RGB")))
                            if len(images) >= max_images:
                                break
                    except Exception:
                        pass
        except Exception as e:
            print(f"[Archive Search Query Note] {e}", flush=True)

    print(f"[Historical Archive] Successfully loaded {len(images)} authentic historical paintings for '{topic}'", flush=True)
    return images


def generate_ai_scene_images(
    cues: list[Cue],
    topic: str = "World History",
    output_dir: Path = Path("slides"),
    aspect_ratio: str = "16:9",
    progress_callback = None,
    puppets_dir: Path | None = None,
) -> tuple[list[Path], dict[int, Path]] | list[Path]:
    """
    Generates authentic Animated History full-screen illustrations and maps
    for every cue, directly matching the spoken dialogue via the AI Scene Director.
    If puppets_dir is provided, also renders bespoke transparent 60 FPS character puppets.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from animated_history_engine import direct_dialogue_scenes, compose_animated_scene, render_scene_puppet, render_scene_animated_sequence

    output_dir.mkdir(parents=True, exist_ok=True)
    if puppets_dir:
        puppets_dir.mkdir(parents=True, exist_ok=True)

    target_width, target_height = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)

    domain = detect_topic_domain(topic)

    # 1. Load authentic historical archive paintings & maps ONLY IF topic domain is history_war
    archive_images = []
    if domain == "history_war":
        try:
            archive_images = fetch_topic_historical_archive(topic, max_images=max(len(cues), 12))
        except Exception as e:
            print(f"[Archive Fetch Note] {e}", flush=True)

    # 2. AI Scene Director analyzes every dialogue cue to establish setting, characters, and action
    scene_plans = direct_dialogue_scenes(cues, topic=topic)
    auto_puppets: dict[int, Path] = {}

    def _render_one_scene(i: int, cue: Cue) -> tuple[int, Path, Path | None]:
        img_path = output_dir / f"image_{i:05d}.jpg"
        plan = scene_plans[i] if i < len(scene_plans) else None
        puppet_path = None

        if domain == "history_war" and archive_images and (i % 3 == 1 or i % 5 == 0):
            # Use authentic high-res historical artwork
            _, raw_art = archive_images[i % len(archive_images)]
            canvas = _smart_crop_to_aspect(raw_art, target_width, target_height)
        else:
            # Generate Real High-Resolution Cinematic AI Image via Pollinations Flux Engine
            import sys
            if "." not in sys.path:
                sys.path.insert(0, ".")
            from ai_image_engine import get_or_generate_ai_scene
            
            era_val = getattr(plan, "era", "") if plan else ""
            try:
                canvas = get_or_generate_ai_scene(
                    sentence=cue.text or "",
                    topic=topic,
                    era_badge=era_val,
                    style="cinematic_oil",
                    provider="flux",
                    target_w=target_width,
                    target_h=target_height,
                    stamp_date=bool(era_val),
                    seed=(i * 23) + 7,
                )
            except Exception as e:
                print(f"[Auto Generator AI Image Note] {e}, using thematic canvas fallback", flush=True)
                canvas = render_thematic_canvas(topic, cue.text or "", i, target_width, target_height)

        if plan and puppets_dir:
            cue_dur = getattr(cue, "duration", 2.5) or 2.5
            p_tag, p_frames = render_scene_animated_sequence(
                plan,
                duration=cue_dur,
                fps=8,
                target_h=int(target_height * 0.52),
                target_w=target_width,
            )
            if p_frames:
                anim_dir = puppets_dir / f"anim_{i:05d}"
                anim_dir.mkdir(parents=True, exist_ok=True)
                for f_idx, frm in enumerate(p_frames):
                    frm.save(anim_dir / f"frame_{f_idx:03d}.png", "PNG")
                puppet_path = puppets_dir / f"puppet_{i:05d}_{p_tag}.png"
                p_frames[0].save(puppet_path, "PNG")

        canvas.save(img_path, "JPEG", quality=95)
        return i, img_path, puppet_path

    # Parallelize scene rendering across worker threads
    results: list[tuple[int, Path, Path | None]] = []
    completed_scenes = 0
    with ThreadPoolExecutor(max_workers=min(len(cues), 6)) as pool:
        futures = [pool.submit(_render_one_scene, idx, cue) for idx, cue in enumerate(cues)]
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            completed_scenes += 1
            if progress_callback:
                progress_callback(completed_scenes, len(cues))

    results.sort(key=lambda x: x[0])
    image_paths = [path for _, path, _ in results]
    if puppets_dir:
        for idx, _, p_path in results:
            if p_path and p_path.is_file():
                auto_puppets[idx] = p_path
        return image_paths, auto_puppets

    return image_paths


def generate_thematic_slides(
    cues: list[Cue],
    output_dir: Path,
    aspect_ratio: str = "16:9",
    topic: str = "World History",
    puppets_dir: Path | None = None,
) -> tuple[list[Path], dict[int, Path]] | list[Path]:
    """Backwards-compatible alias for generate_ai_scene_images"""
    return generate_ai_scene_images(
        cues,
        topic=topic,
        output_dir=output_dir,
        aspect_ratio=aspect_ratio,
        puppets_dir=puppets_dir,
    )



