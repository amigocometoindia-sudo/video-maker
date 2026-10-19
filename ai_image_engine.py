"""
AI Image Generation Engine — Cinematic Documentary & History Visuals
====================================================================
Generates hyper-realistic, high-resolution 1080p AI scene images
using Pollinations Flux, OpenAI DALL-E 3, and Wikimedia Archives.
- Zero stickmen, zero ugly gradient boxes
- 100% Free Pollinations Flux AI out of the box (no API key required)
- Parallel thread-pool generation with local disk caching
- Bottom-edge watermark stripping and TV-safe date badge stamping
"""

import io
import math
import os
import re
import time
import hashlib
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

CACHE_DIR = Path("ai_cache/doc_images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================================
# 1. Font & Safe Date Pill Stamping
# =====================================================================

def get_best_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Finds best available sans / bold font on Windows."""
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
    """Stamps authentic Animated History minimalist dark translucent date/era pill with TV-safe margin."""
    if not text:
        return
    draw = ImageDraw.Draw(im)
    clean_txt = str(text).strip().upper()

    font = get_best_font(34, bold=True)
    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # TV-safe broadcast margin to protect against Ken Burns zoom-in
    px, py = 120, 80
    pw, ph = tw + 44, th + 24

    draw.rounded_rectangle(
        [px, py, px + pw, py + ph],
        radius=14,
        fill=(15, 23, 42),
        outline=(148, 163, 184),
        width=3,
    )
    draw.text((px + 22, py + 10), clean_txt, fill="#ffffff", font=font)


# =====================================================================
# 2. Visual Prompt Synthesizer
# =====================================================================

def synthesize_visual_prompt(
    sentence: str,
    topic: str = "",
    era: str = "",
    style: str = "cinematic_oil",
) -> str:
    """
    Transforms a narration sentence into an ultra-evocative cinematic visual prompt
    specifically tuned for Flux and DALL-E 3 image generators.
    """
    # Clean dialogue
    clean = re.sub(r"[^A-Za-z0-9 ,.'-]", "", sentence).strip()
    
    # Topic domain context
    t_low = (topic or "").lower()
    domain_hint = ""
    if any(w in t_low for w in ["french", "bastille", "napoleon", "guillotine", "paris", "1789"]):
        domain_hint = "18th century French Revolution, Paris, authentic neoclassical architecture, tricoteuses, tricolor standards"
    elif any(w in t_low for w in ["rome", "roman", "caesar", "colosseum", "empire", "senate"]):
        domain_hint = "Ancient Imperial Rome, marble temples, Corinthian columns, Roman legionaries, SPQR crimson standards"
    elif any(w in t_low for w in ["israel", "jerusalem", "masada", "judea", "temple"]):
        domain_hint = "Ancient Levant, Judean desert cliffs, limestone fortress, ancient Jerusalem stone walls, Roman siege"
    elif any(w in t_low for w in ["hastings", "1066", "norman", "saxon", "william", "harold"]):
        domain_hint = "Medieval 1066 Battle of Hastings, Saxon round shield wall, Norman cavalry, chainmail armour, rolling green hills"
    elif any(w in t_low for w in ["ww1", "world war 1", "world war i", "trench", "somme", "verdun"]):
        domain_hint = "World War 1 Western Front, muddy trench parapets, barbed wire entanglements, artillery smoke, steel helmets"
    elif any(w in t_low for w in ["human", "dawn", "evolution", "mammoth", "ice age", "prehistoric"]):
        domain_hint = "Prehistoric Ice Age, glaciated mountain peaks, woolly mammoths, hunter-gatherer campfire, ancient cave"
    else:
        domain_hint = f"Historical documentary, authentic period setting for '{topic}'"

    era_part = f", era {era}" if era and era != "HISTORY" else ""

    style_presets = {
        "cinematic_oil": "epic cinematic historical oil painting, dramatic chiaroscuro volumetric lighting, photorealistic, rich vibrant color palette, deep shadows, 8k resolution, award-winning cinematography, highly detailed textures, masterpiece",
        "hyper_realistic": "ultra-realistic 35mm film photography, Kodak Portra 400 color science, rich jewel tones, dynamic range, historical documentary still, National Geographic style, cinematic lighting, 8k uhd, photorealistic, atmospheric depth",
        "vintage_archival": "vintage historical archival photograph, warm amber and rich sepia tones, dramatic lighting, authentic period details, museum collection quality, 8k",
        "graphic_illustrated": "detailed graphic novel historical illustration, punchy vibrant colors, high contrast, cinematic composition, trending on ArtStation, crisp lines, 8k",
    }
    style_desc = style_presets.get(style, style_presets["cinematic_oil"])

    prompt = (
        f"{style_desc}. Subject: {clean}. "
        f"Setting and context: {domain_hint}{era_part}. "
        f"Wide angle panoramic shot, dramatic composition, cinematic atmosphere, no text, no captions, no words, no watermarks, no frames, no modern elements."
    )
    return prompt[:480]


# =====================================================================
# 3. Pollinations Flux Engine (100% Free, Zero Key)
# =====================================================================

def fetch_pollinations_flux_image(
    prompt: str,
    target_w: int = 1920,
    target_h: int = 1080,
    timeout: int = 35,
    seed: int | None = None,
) -> Image.Image:
    """
    Fetches a high-resolution cinematic AI image from Pollinations Flux API.
    Renders oversized and crops bottom edge to guarantee zero watermark logos.
    """
    if seed is None:
        seed = int(hashlib.md5(prompt.encode("utf-8")).hexdigest()[:6], 16) % 100000

    encoded_prompt = urllib.parse.quote(prompt.strip())
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nofeed=true"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()

    img = Image.open(io.BytesIO(data)).convert("RGB")

    # Crop off bottom 40px to completely eliminate any watermark logo
    crop_bottom = max(img.height - 40, int(img.height * 0.94))
    img_cropped = img.crop((0, 0, img.width, crop_bottom))

    # Center-fill / smart crop to exact target aspect ratio
    target_ratio = target_w / target_h
    current_ratio = img_cropped.width / img_cropped.height

    if current_ratio > target_ratio:
        new_w = int(img_cropped.height * target_ratio)
        offset = (img_cropped.width - new_w) // 2
        img_cropped = img_cropped.crop((offset, 0, offset + new_w, img_cropped.height))
    else:
        new_h = int(img_cropped.width / target_ratio)
        offset = (img_cropped.height - new_h) // 2
        img_cropped = img_cropped.crop((0, offset, img_cropped.width, offset + new_h))

    # Resize to full target resolution with Lanczos
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    final_img = img_cropped.resize((target_w, target_h), resample_filter)

    # Cinematic AI Color Grading & Edge Detail Restoration
    final_img = ImageEnhance.Color(final_img).enhance(1.15)
    final_img = ImageEnhance.Contrast(final_img).enhance(1.10)
    final_img = ImageEnhance.Brightness(final_img).enhance(1.02)
    final_img = final_img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=125, threshold=2))

    return final_img


# =====================================================================
# 4. OpenAI DALL-E 3 Engine (When API Key is provided)
# =====================================================================

def fetch_dalle3_image(
    prompt: str,
    api_key: str,
    target_w: int = 1920,
    target_h: int = 1080,
    timeout: int = 40,
) -> Image.Image:
    """Fetches high-res cinematic image via OpenAI DALL-E 3 API."""
    import openai
    client = openai.OpenAI(api_key=api_key)

    size = "1792x1024" if target_w >= target_h else "1024x1792"
    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt[:950],
        size=size,
        quality="standard",
        n=1,
    )
    img_url = resp.data[0].url

    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw_data = r.read()

    img = Image.open(io.BytesIO(raw_data)).convert("RGB")
    resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    return img.resize((target_w, target_h), resample_filter)


def fetch_nvidia_nim_image(
    prompt: str,
    api_key: str,
    model: str = "flux.1-dev",
    target_w: int = 1920,
    target_h: int = 1080,
    timeout: int = 45,
) -> Image.Image:
    """
    Generates ultra-high fidelity 1080p AI imagery via NVIDIA NIM API.
    Supports FLUX.1-dev, FLUX.1-schnell, and Stable Diffusion 3.5 Large on NVIDIA's cloud tensor infrastructure.
    """
    import json
    import base64

    url = "https://integrate.api.nvidia.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "NIM-Studio-Client/1.0",
    }

    candidate_models = [
        model or "flux.1-dev",
        "flux.1-schnell",
        "black-forest-labs/flux.1-dev",
        "black-forest-labs/flux.1-schnell",
        "stabilityai/stable-diffusion-3.5-large",
    ]

    last_err = None
    for m in candidate_models:
        payload = {
            "model": m,
            "prompt": prompt[:950],
            "num_images": 1,
            "response_format": "b64_json",
            "width": 1024,
            "height": 1024,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                item = data.get("data", [{}])[0]
                raw_bytes = None
                if "b64_json" in item and item["b64_json"]:
                    raw_bytes = base64.b64decode(item["b64_json"])
                elif "url" in item and item["url"]:
                    u_req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(u_req, timeout=timeout) as u_resp:
                        raw_bytes = u_resp.read()

                if raw_bytes:
                    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                    scale = max(target_w / img.width, target_h / img.height)
                    nw, nh = int(img.width * scale), int(img.height * scale)
                    resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                    scaled = img.resize((nw, nh), resample_filter)
                    left = (nw - target_w) // 2
                    top = (nh - target_h) // 2
                    cropped = scaled.crop((left, top, left + target_w, top + target_h))
                    print(f"[AI Image Engine] Successfully generated image via NVIDIA NIM ({m})!", flush=True)
                    return cropped
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {he.code}: {err_body}"
            print(f"[AI Image Engine] NVIDIA NIM model {m} failed: {last_err}", flush=True)
            continue
        except Exception as e:
            last_err = str(e)
            print(f"[AI Image Engine] NVIDIA NIM model {m} error: {last_err}", flush=True)
            continue

    raise RuntimeError(f"All NVIDIA NIM models failed: {last_err}")


# =====================================================================
# 5. Dynamic Wikimedia Commons Museum Artwork Engine
# =====================================================================


def fetch_wikimedia_scene_artwork(
    sentence: str,
    topic: str,
    target_w: int = 1920,
    target_h: int = 1080,
    timeout: int = 14,
) -> Image.Image | None:
    """
    Dynamically searches and downloads authentic museum masterworks & engravings
    from Wikimedia Commons matching the scene's historical context.
    """
    import json
    t_low = (sentence + " " + topic).lower()
    search_term = None
    historical_keywords = [
        "bastille", "versailles", "guillotine", "robespierre", "napoleon", "louis xvi",
        "julius caesar", "colosseum", "roman forum", "senate", "augustus", "pompeii", "rubicon",
        "masada", "jerusalem temple", "caesarea", "crusades", "saladin",
        "battle of hastings", "bayeux tapestry", "william the conqueror", "harold godwinson",
        "western front", "battle of verdun", "battle of the somme", "archduke franz ferdinand",
        "woolly mammoth", "ice age", "cave painting", "stone age",
    ]
    for kw in historical_keywords:
        if kw in t_low:
            search_term = kw
            break

    if not search_term:
        clean_words = [w for w in re.sub(r"[^a-zA-Z0-9\s]", "", sentence).split() if len(w) > 3 and w.lower() not in {"this", "that", "with", "from", "they", "their", "when", "into", "over", "after", "before", "where"}]
        search_term = " ".join(clean_words[:3]) or topic

    search_q = f"{search_term} painting"
    url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
        f"&gsrsearch={urllib.parse.quote(search_q)}&gsrnamespace=6&gsrlimit=3"
        f"&prop=imageinfo&iiprop=url&format=json"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "BahaaAI-HistoryDoc/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                info = p.get("imageinfo", [{}])[0]
                img_url = info.get("url", "")
                if img_url and any(img_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                    img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(img_req, timeout=timeout) as ir:
                        raw = ir.read()
                        im = Image.open(io.BytesIO(raw)).convert("RGB")
                        tr = target_w / target_h
                        ir_ratio = im.width / im.height
                        if ir_ratio > tr:
                            nw = int(im.height * tr)
                            left = (im.width - nw) // 2
                            im = im.crop((left, 0, left + nw, im.height))
                        else:
                            nh = int(im.width / tr)
                            top = (im.height - nh) // 2
                            im = im.crop((0, top, im.width, top + nh))
                        resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                        return im.resize((target_w, target_h), resample_filter)
    except Exception:
        pass
    return None


# =====================================================================
# 6. Smart Caching & Multi-Provider Dispatcher
# =====================================================================

def get_or_generate_ai_scene(
    sentence: str,
    topic: str = "",
    era_badge: str = "",
    style: str = "cinematic_oil",
    provider: str = "flux",
    api_key: str = "",
    target_w: int = 1920,
    target_h: int = 1080,
    output_path: Path | None = None,
    stamp_date: bool = True,
    seed: int | None = None,
) -> Image.Image:
    """
    Smart cached dispatcher:
    1. Checks if already generated on disk.
    2. Calls Pollinations Flux, DALL-E 3, or fallback.
    3. Stamps date badge and saves.
    """
    prompt = synthesize_visual_prompt(sentence=sentence, topic=topic, era=era_badge, style=style)
    
    # Hash key for disk caching
    cache_key = hashlib.md5(f"{prompt}_{target_w}x{target_h}_{provider}".encode("utf-8")).hexdigest()
    cached_file = CACHE_DIR / f"{cache_key}.jpg"

    img = None
    if cached_file.is_file():
        try:
            img = Image.open(cached_file).convert("RGB")
        except Exception:
            img = None

    if img is None:
        # Check NVIDIA NIM (nvapi-...)
        is_nvidia = provider == "nvidia" or (api_key and api_key.strip().startswith("nvapi-"))
        if is_nvidia and api_key and api_key.strip():
            try:
                img = fetch_nvidia_nim_image(
                    prompt=prompt,
                    api_key=api_key,
                    target_w=target_w,
                    target_h=target_h,
                )
            except Exception as e:
                print(f"[AI Image Engine] NVIDIA NIM error ({e}), falling back to Pollinations Flux...", flush=True)
                img = None

        # Check OpenAI DALL-E 3
        if img is None and provider == "openai" and api_key and api_key.strip():
            try:
                img = fetch_dalle3_image(prompt=prompt, api_key=api_key, target_w=target_w, target_h=target_h)
            except Exception as e:
                print(f"[AI Image Engine] DALL-E 3 error ({e}), falling back to Pollinations Flux...", flush=True)
                img = None

        if img is None:
            # Pollinations Flux (Free, zero key, reliable)
            try:
                img = fetch_pollinations_flux_image(
                    prompt=prompt,
                    target_w=target_w,
                    target_h=target_h,
                    seed=seed,
                )
            except Exception as e:
                print(f"[AI Image Engine] Flux error on '{prompt[:50]}...': {e}", flush=True)
                img = None

    if img is None:
        # Tier 3: Query Wikimedia Commons for authentic museum artwork matching this scene
        try:
            img = fetch_wikimedia_scene_artwork(sentence, topic, target_w=target_w, target_h=target_h)
            if img:
                print(f"[AI Image Engine] Loaded authentic historical museum artwork for '{sentence[:40]}...'", flush=True)
        except Exception as e:
            print(f"[AI Image Engine] Wikimedia fallback note: {e}", flush=True)

    # Fallback if all failed (generate rich atmospheric cinematic gradient backdrop)
    if img is None:
        img = create_cinematic_fallback_backdrop(sentence, topic, era_badge, target_w, target_h)

    # Save to cache
    try:
        img.save(cached_file, "JPEG", quality=95)
    except Exception:
        pass

    # Clone for return so cache stays pristine
    final_img = img.copy()

    # Stamp TV-safe date badge if requested
    if stamp_date and era_badge:
        stamp_date_pill(final_img, era_badge)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        final_img.save(output_path, "JPEG", quality=95)

    return final_img


def create_cinematic_fallback_backdrop(
    sentence: str,
    topic: str,
    era_badge: str,
    w: int = 1920,
    h: int = 1080,
) -> Image.Image:
    """Atmospheric dark cinematic backdrop with vignette when network is unavailable."""
    im = Image.new("RGB", (w, h), "#0a0e17")
    draw = ImageDraw.Draw(im)

    # Deep radial / linear lighting
    for y in range(h):
        ratio = y / max(h - 1, 1)
        r = int(14 + ratio * 18)
        g = int(20 + ratio * 24)
        b = int(36 + ratio * 42)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Center glow
    glow_box = [int(w * 0.2), int(h * 0.15), int(w * 0.8), int(h * 0.85)]
    draw.ellipse(glow_box, fill=(28, 42, 70))
    im = im.filter(ImageFilter.GaussianBlur(radius=80))
    return im


# =====================================================================
# 6. High-Performance Parallel Batch Image Generator
# =====================================================================

def batch_generate_scene_images(
    scenes: list[Any],
    topic: str,
    output_dir: Path,
    aspect_ratio: str = "16:9",
    provider: str = "flux",
    api_key: str = "",
    style: str = "cinematic_oil",
    stamp_dates: bool = True,
    max_workers: int = 4,
    progress_callback: Callable[[int, int, str], None] | None = None,
    archive_artworks: list[tuple[str, Image.Image]] | None = None,
    use_archive_hybrid: bool = True,
) -> list[Path]:
    """
    Renders all documentary scene images concurrently:
    - High-speed parallel fetching via ThreadPoolExecutor.
    - Interleaves real museum archive paintings when enabled for authentic documentary texture.
    - Yields real-time progress callbacks to the UI.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    target_w, target_h = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
    total_scenes = len(scenes)

    image_paths: list[Path | None] = [None] * total_scenes
    tasks = []

    archive_idx = 0
    archive_count = len(archive_artworks) if archive_artworks else 0

    print(f"[AI Image Engine] Starting parallel generation for {total_scenes} scenes (provider: {provider}, workers: {max_workers})...", flush=True)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, sc in enumerate(scenes):
            out_file = output_dir / f"scene_{idx:05d}.jpg"
            text = getattr(sc, "text", str(sc))
            era = getattr(sc, "era_badge", "")

            # Check if this scene should be an authentic museum archive painting
            should_use_archive = (
                use_archive_hybrid
                and archive_count > 0
                and (idx % 3 == 1 or idx % 5 == 0)
                and archive_idx < archive_count
            )

            if should_use_archive:
                try:
                    _, raw_img = archive_artworks[archive_idx % archive_count]
                    archive_idx += 1
                    
                    # Fit archive painting into target 16:9 / 9:16
                    src_rgba = raw_img.convert("RGBA")
                    scale = max(target_w / max(src_rgba.width, 1), target_h / max(src_rgba.height, 1))
                    nw, nh = int(src_rgba.width * scale), int(src_rgba.height * scale)
                    resample_filter = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                    scaled = src_rgba.resize((nw, nh), resample_filter)
                    left = (nw - target_w) // 2
                    top = (nh - target_h) // 2
                    art_frame = scaled.crop((left, top, left + target_w, top + target_h)).convert("RGB")
                    
                    if stamp_dates and era:
                        stamp_date_pill(art_frame, era)
                        
                    art_frame.save(out_file, "JPEG", quality=95)
                    image_paths[idx] = out_file
                    continue
                except Exception as e:
                    print(f"[AI Image Engine] Archive interleaving error on scene {idx}: {e}", flush=True)

            # Generate via AI
            future = executor.submit(
                get_or_generate_ai_scene,
                sentence=text,
                topic=topic,
                era_badge=era,
                style=style,
                provider=provider,
                api_key=api_key,
                target_w=target_w,
                target_h=target_h,
                output_path=out_file,
                stamp_date=stamp_dates,
                seed=(idx * 17) + 42,
            )
            tasks.append((idx, future))

        # Await AI parallel generations
        completed_count = sum(1 for p in image_paths if p is not None)
        for idx, future in tasks:
            try:
                future.result()
                image_paths[idx] = output_dir / f"scene_{idx:05d}.jpg"
            except Exception as e:
                print(f"[AI Image Engine] Failed to generate scene {idx}: {e}", flush=True)
                # Fallback to local atmospheric frame
                fallback_path = output_dir / f"scene_{idx:05d}.jpg"
                sc_text = getattr(scenes[idx], "text", "")
                sc_era = getattr(scenes[idx], "era_badge", "")
                fallback_img = create_cinematic_fallback_backdrop(sc_text, topic, sc_era, target_w, target_h)
                if stamp_dates and sc_era:
                    stamp_date_pill(fallback_img, sc_era)
                fallback_img.save(fallback_path, "JPEG", quality=95)
                image_paths[idx] = fallback_path

            completed_count += 1
            if progress_callback:
                progress_callback(completed_count, total_scenes, f"Generated AI scene {completed_count}/{total_scenes}")

    # Ensure all slots are filled
    final_paths = []
    for idx, p in enumerate(image_paths):
        if p and p.is_file():
            final_paths.append(p)
        else:
            fallback_p = output_dir / f"scene_{idx:05d}.jpg"
            fallback_im = create_cinematic_fallback_backdrop("", topic, "", target_w, target_h)
            fallback_im.save(fallback_p, "JPEG", quality=95)
            final_paths.append(fallback_p)

    print(f"[AI Image Engine] Finished generating {len(final_paths)} AI scene images!", flush=True)
    return final_paths
