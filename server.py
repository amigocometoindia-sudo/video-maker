import asyncio
import shutil
import zipfile
import re
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pydantic import BaseModel
from uuid import uuid4
import io
from PIL import Image

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import starlette.formparsers

_original_multipart_init = starlette.formparsers.MultiPartParser.__init__

def _patched_multipart_init(self, headers, stream, **kwargs):
    kwargs["max_files"] = 100000
    kwargs["max_fields"] = 100000
    try:
        _original_multipart_init(self, headers, stream, **kwargs)
    except TypeError:
        kwargs.pop("max_part_size", None)
        _original_multipart_init(self, headers, stream, **kwargs)

starlette.formparsers.MultiPartParser.__init__ = _patched_multipart_init
starlette.formparsers.MultiPartParser.spool_max_size = 1024 * 1024 * 1024

from app_config import APP_DESCRIPTION, APP_NAME, APP_VERSION
from srt_parser import parse_srt, Cue, TIMESTAMP_PATTERN, _timestamp_to_ms
from video_generator import GenerationCanceled, SUPPORTED_IMAGE_EXTENSIONS, create_video
from auto_generator import CURATED_VOICES, generate_script_with_ai, generate_voice_and_srt, generate_thematic_slides, split_grid_images, breakdown_dialogue_scenes, generate_auto_grid_scenes

ROOT_DIR = Path(__file__).resolve().parent
FFMPEG_PATH = ROOT_DIR / "ffmpeg" / "ffmpeg.exe"
SFX_DIR = ROOT_DIR / "sfx"
OUTPUT_DIR = ROOT_DIR / "output"
INTENSITY_SFX_DIR = ROOT_DIR / "intensity_sfx"
INTENSITY_SFX_DIR.mkdir(exist_ok=True)
POPUPS_DIR = ROOT_DIR / "popups"
POPUPS_DIR.mkdir(exist_ok=True)
STICKMEN_DIR = ROOT_DIR / "stickmen"
STICKMEN_DIR.mkdir(exist_ok=True)
CUSTOM_CHANNEL_ASSETS_DIR = ROOT_DIR / "custom_channel_assets"
CUSTOM_CHANNEL_ASSETS_DIR.mkdir(exist_ok=True)
CHARACTERS_DIR = ROOT_DIR / "characters"
CHARACTERS_DIR.mkdir(exist_ok=True)
WEB_DIR = ROOT_DIR / "web"

def get_channel_character_assets() -> dict[str, Path]:
    """
    Gathers character & motion assets in order of priority:
    1. Base popups/
    2. Stickmen library (kings, soldiers, battles, arrows, tombstones)
    3. Custom user assets from custom_channel_assets/
    4. Custom character action PNGs from characters/ (highest priority override)
    """
    assets = {}
    for folder in [POPUPS_DIR, STICKMEN_DIR, CUSTOM_CHANNEL_ASSETS_DIR, CHARACTERS_DIR]:
        if folder.exists():
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    assets[path.stem] = path
    return assets

app = FastAPI(title="SRT Slideshow Generator")
OUTPUT_DIR.mkdir(exist_ok=True)


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-App-Version"] = APP_VERSION
        return response


app.add_middleware(NoCacheMiddleware)
JOBS = {}
JOB_CANCEL_EVENTS = {}
JOBS_LOCK = threading.Lock()
JOB_EXECUTOR = ThreadPoolExecutor(max_workers=1)
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}


def natural_image_order(image: UploadFile):
    filename = Path(image.filename or "").as_posix()
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", filename)]


def _update_job(job_id: str, **updates) -> None:
    with JOBS_LOCK:
        JOBS[job_id].update(updates)


def _remove_previous_videos() -> None:
    for video_path in OUTPUT_DIR.glob("*.mp4"):
        try:
            video_path.unlink()
        except OSError:
            pass


def _safe_video_stem(filename: str) -> str:
    stem = Path(filename).stem
    safe_stem = re.sub(r"[^A-Za-z0-9._ -]+", "_", stem).strip(" .")
    return safe_stem or "generated_video"


def _run_generation(
    job_id,
    image_paths,
    cues,
    work_dir,
    output_path,
    cancel_event,
    audio_path,
    apply_zoom,
    sfx_paths,
    aspect_ratio,
    intensity_sfx_paths=None,
    popup_paths=None,
    popup_sfx_paths=None,
    api_key=None,
    ai_provider=None,
    popup_prompt=None,
    api_model=None,
    motion_style="smart_random",
    zoom_intensity="subtle",
    bg_mode="crop_fill",
    enable_subtitles=False,
    subtitle_style="hormozi_yellow",
    subtitle_position="bottom",
    subtitle_font_size=46,
    gpu_accel="auto",
    parallel_workers=4,
    initial_popup_mapping=None,
    emotion_sfx_volume=0.15,
    color_saturation=1.14,
    popup_sfx_volume=0.25,
    transition_sfx_density=25.0,
    transition_sfx_volume=0.15,
    emotion_sfx_density=25.0,
    popup_sfx_density=30.0,
):
    total_images = len(cues)

    # Normalize densities and volumes (support both 0-100 and 0.0-1.0)
    t_density = transition_sfx_density / 100.0 if transition_sfx_density > 1.0 else transition_sfx_density
    t_vol = transition_sfx_volume / 100.0 if transition_sfx_volume > 1.0 else transition_sfx_volume
    e_density = emotion_sfx_density / 100.0 if emotion_sfx_density > 1.0 else emotion_sfx_density
    e_vol = emotion_sfx_volume / 100.0 if emotion_sfx_volume > 1.0 else emotion_sfx_volume
    p_density = popup_sfx_density / 100.0 if popup_sfx_density > 1.0 else popup_sfx_density
    p_vol = popup_sfx_volume / 100.0 if popup_sfx_volume > 1.0 else popup_sfx_volume

    def image_started(index, filename):
        _update_job(
            job_id,
            current_image=index + 1,
            current_filename=filename,
            progress=round((index / total_images) * 90),
            phase=f"Rendering image {index + 1} of {total_images}",
        )

    def stage_changed(message, progress):
        _update_job(job_id, current_filename="", phase=message, progress=progress)

    try:
        intensity_mapping = {}
        if intensity_sfx_paths:
            stage_changed("Analyzing dialogue sound effects...", 5)
            from llm_analyzer import analyze_cues_intensity
            def intensity_progress(current_chunk, total_chunks):
                prog = 5 + int((current_chunk / total_chunks) * 4)
                stage_changed(f"Analyzing dialogue sound effects - Chunk {current_chunk+1}/{total_chunks}...", prog)
            intensity_mapping = analyze_cues_intensity(cues, list(intensity_sfx_paths.keys()), api_key, ai_provider, api_model, progress_callback=intensity_progress, sfx_density=e_density)
            active_sfx = [v for v in intensity_mapping.values() if v and v.lower() != 'none']
            print(f"[SFX] Mapped {len(active_sfx)} sound triggers across {len(cues)} cues (density={e_density:.2f}): {active_sfx}", flush=True)
            
        if initial_popup_mapping:
            popup_mapping = dict(initial_popup_mapping)
        elif popup_paths:
            stage_changed("Analyzing dialogue for 2D character animation...", 10)
            from llm_analyzer import analyze_cues_popups
            def popup_progress(current_chunk, total_chunks):
                prog = 10 + int((current_chunk / total_chunks) * 4)
                stage_changed(f"Analyzing dialogue for 2D character animation - Chunk {current_chunk+1}/{total_chunks}...", prog)
            popup_mapping = analyze_cues_popups(cues, popup_paths, api_key, ai_provider, popup_prompt, api_model, progress_callback=popup_progress)
        else:
            popup_mapping = {}

        active_puppets = [v for v in popup_mapping.values() if v and v.lower() != 'none']
        print(f"[Character Puppets] Intelligently placed {len(active_puppets)}/{len(cues)} dialogue-matched animations: {active_puppets[:6]}...", flush=True)

        create_video(
            image_paths,
            cues,
            FFMPEG_PATH,
            work_dir,
            output_path,
            on_image_started=image_started,
            cancel_event=cancel_event,
            audio_path=audio_path,
            apply_zoom=apply_zoom,
            sfx_paths=sfx_paths,
            intensity_sfx_paths=intensity_sfx_paths,
            intensity_mapping=intensity_mapping,
            aspect_ratio=aspect_ratio,
            on_stage_changed=stage_changed,
            popup_paths=popup_paths,
            popup_mapping=popup_mapping,
            popup_sfx_paths=popup_sfx_paths,
            motion_style=motion_style,
            zoom_intensity=zoom_intensity,
            bg_mode=bg_mode,
            enable_subtitles=enable_subtitles,
            subtitle_style=subtitle_style,
            subtitle_position=subtitle_position,
            subtitle_font_size=subtitle_font_size,
            gpu_accel=gpu_accel,
            parallel_workers=parallel_workers,
            transition_sfx_density=t_density,
            transition_sfx_volume=t_vol,
            emotion_sfx_volume=e_vol,
            popup_sfx_density=p_density,
            popup_sfx_volume=p_vol,
            color_saturation=color_saturation,
        )
        _update_job(
            job_id,
            state="complete",
            progress=100,
            current_image=total_images,
            current_filename="",
            phase="Complete",
            output_name=output_path.name,
        )
    except GenerationCanceled:
        _update_job(job_id, state="canceled", current_filename="", phase="Canceled", error="Generation canceled.")
    except Exception as error:
        _update_job(job_id, state="error", error=str(error))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        with JOBS_LOCK:
            JOB_CANCEL_EVENTS.pop(job_id, None)


@app.post("/api/clear-cache")
async def clear_cache():
    try:
        from llm_analyzer import CACHE_DIR
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
        CACHE_DIR.mkdir(exist_ok=True)
        return {"status": "success", "message": "AI cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 400 and exc.detail == "There was an error parsing the body":
        import traceback
        with open("server_crash.log", "w", encoding="utf-8") as f:
            f.write(f"Cause: {exc.__cause__}\n")
            traceback.print_exception(type(exc.__cause__), exc.__cause__, getattr(exc.__cause__, '__traceback__', None), file=f)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

@app.post("/api/generate")
async def generate_video(
    srt_file: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    audio_file: UploadFile | None = File(None),
    apply_zoom: bool = Form(True),
    bundled_sfx: list[str] = Form(default=[]),
    custom_sfx: list[UploadFile] = File(default=[]),
    aspect_ratio: str = Form("16:9"),
    ai_provider: str = Form(default="openai"),
    api_key: str = Form(default=""),
    api_model: str = Form(default=""),
    bundled_intensity: list[str] = Form(default=[]),
    custom_intensity: list[UploadFile] = File(default=[]),
    enable_popups: bool = Form(default=False),
    popup_prompt: str = Form(default=""),
    custom_popups: list[UploadFile] = File(default=[]),
    custom_popup_sfx: UploadFile | None = File(None),
    bundled_popup_sfx: list[str] = Form(default=[]),
    motion_style: str = Form(default="smart_random"),
    zoom_intensity: str = Form(default="subtle"),
    bg_mode: str = Form(default="crop_fill"),
    enable_subtitles: bool = Form(default=False),
    subtitle_style: str = Form(default="hormozi_yellow"),
    subtitle_position: str = Form(default="bottom"),
    subtitle_font_size: int = Form(default=46),
    gpu_accel: str = Form(default="auto"),
    parallel_workers: int = Form(default=4),
    emotion_sfx_volume: float = Form(default=0.15),
    popup_sfx_volume: float = Form(default=0.25),
    color_boost: float = Form(default=115),
    transition_sfx_density: float = Form(default=25.0),
    transition_sfx_volume: float = Form(default=0.15),
    emotion_sfx_density: float = Form(default=25.0),
    popup_sfx_density: float = Form(default=30.0),
):
    if not srt_file.filename or not srt_file.filename.lower().endswith(".srt"):
        raise HTTPException(status_code=400, detail="Please select an SRT file.")
    if not FFMPEG_PATH.is_file():
        raise HTTPException(status_code=500, detail=f"Missing bundled FFmpeg: {FFMPEG_PATH}")
    if aspect_ratio not in {"16:9", "9:16"}:
        raise HTTPException(status_code=400, detail="Aspect ratio must be 16:9 or 9:16.")

    valid_images = [
        image for image in images
        if image.filename and Path(image.filename).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    valid_images.sort(key=natural_image_order)
    if not valid_images:
        raise HTTPException(status_code=400, detail="No supported images were selected.")

    work_dir = Path(tempfile.mkdtemp(prefix="srt_slideshow_"))
    srt_path = work_dir / "captions.srt"
    srt_path.write_bytes(await srt_file.read())

    image_paths = []
    for index, image in enumerate(valid_images):
        raw_data = await image.read()
        image_path = work_dir / f"image_{index:05d}.jpg"
        try:
            with Image.open(io.BytesIO(raw_data)) as im:
                im = im.convert("RGB")
                w, h = im.size
                im_cropped = im.crop((int(w * 0.01), int(h * 0.01), int(w * 0.96), int(h * 0.96)))
                im_cropped.save(image_path, "JPEG", quality=96)
        except Exception as e:
            print(f"[Image Crop] Warning: Could not crop image {index} with PIL ({e}), writing raw bytes", flush=True)
            fallback_path = work_dir / f"image_{index:05d}{Path(image.filename).suffix.lower()}"
            fallback_path.write_bytes(raw_data)
            image_path = fallback_path
        image_paths.append(image_path)

    audio_path = None
    if audio_file and audio_file.filename:
        audio_extension = Path(audio_file.filename).suffix.lower()
        if audio_extension not in SUPPORTED_AUDIO_EXTENSIONS:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail="Unsupported audio format.")
        audio_path = work_dir / f"audio{audio_extension}"
        audio_path.write_bytes(await audio_file.read())

    sfx_paths = []
    for sfx_name in bundled_sfx:
        sfx_path = SFX_DIR / sfx_name
        if sfx_path.is_file() and sfx_path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            sfx_paths.append(sfx_path)
            
    for index, sfx_file in enumerate(custom_sfx):
        if sfx_file.filename:
            sfx_extension = Path(sfx_file.filename).suffix.lower()
            if sfx_extension in SUPPORTED_AUDIO_EXTENSIONS:
                sfx_path = work_dir / f"custom_sfx_{index:03d}{sfx_extension}"
                sfx_path.write_bytes(await sfx_file.read())
                sfx_paths.append(sfx_path)

    intensity_sfx_paths = {}
    for path in INTENSITY_SFX_DIR.glob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            intensity_sfx_paths[path.stem] = path

    for path in SFX_DIR.glob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            if path.name.lower() not in ("popup.wav", "click.wav"):
                if path.stem not in intensity_sfx_paths:
                    intensity_sfx_paths[path.stem] = path
            
    for index, file in enumerate(custom_intensity):
        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext in SUPPORTED_AUDIO_EXTENSIONS:
                stem = Path(file.filename).stem
                path = work_dir / f"custom_intensity_{index:03d}{ext}"
                path.write_bytes(await file.read())
                intensity_sfx_paths[stem] = path

    if not intensity_sfx_paths and sfx_paths:
        for p in sfx_paths:
            if p.name.lower() not in ("popup.wav", "click.wav"):
                intensity_sfx_paths[p.stem] = p

    print(f"[SFX] Available sound effects pool: {list(intensity_sfx_paths.keys())}", flush=True)

    try:
        cues = parse_srt(srt_path)
    except ValueError as error:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(error)) from error

    if len(image_paths) < len(cues):
        cues = cues[:len(image_paths)]
        
    custom_popup_paths = {}
    for index, file in enumerate(custom_popups):
        if file.filename:
            ext = Path(file.filename).suffix.lower()
            if ext in SUPPORTED_IMAGE_EXTENSIONS:
                stem = Path(file.filename).stem
                path = work_dir / f"custom_popup_{index:03d}{ext}"
                path.write_bytes(await file.read())
                custom_popup_paths[stem] = path

    popup_paths = {}
    if custom_popup_paths:
        # User uploaded their own custom character/stickman folder!
        # Strictly use user uploaded assets so old bundled stickmen do not hijack them.
        popup_paths = custom_popup_paths
        print(f"[Popups] Exclusively using {len(popup_paths)} user-uploaded custom popups: {list(popup_paths.keys())[:6]}...", flush=True)
    elif enable_popups:
        popup_paths = get_channel_character_assets()
            
    popup_sfx_paths = []
    popups_sfx_dir = SFX_DIR / "popups"
    if bundled_popup_sfx:
        for sfx_name in bundled_popup_sfx:
            p = popups_sfx_dir / sfx_name
            if not p.is_file():
                p = SFX_DIR / sfx_name
            if p.is_file() and p.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                popup_sfx_paths.append(p)
    elif popups_sfx_dir.exists():
        for path in sorted(popups_sfx_dir.glob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS and not path.name.startswith(("-", ".")):
                popup_sfx_paths.append(path)

    if custom_popup_sfx and custom_popup_sfx.filename:
        ext = Path(custom_popup_sfx.filename).suffix.lower()
        if ext in SUPPORTED_AUDIO_EXTENSIONS:
            custom_path = work_dir / f"custom_popup_sfx_{ext}"
            custom_path.write_bytes(await custom_popup_sfx.read())
            popup_sfx_paths.append(custom_path)
            
    # Auto-remove backgrounds of uploaded popups if rembg is installed
    try:
        import rembg
        session = rembg.new_session("u2net")
        for stem, path in popup_paths.items():
            try:
                with open(path, "rb") as f:
                    input_data = f.read()
                output_data = rembg.remove(input_data, session=session)
                out_path = work_dir / f"{stem}_nobg.png"
                with open(out_path, "wb") as f:
                    f.write(output_data)
                
                # Save a debug copy to output/ so the user can verify it
                import shutil
                shutil.copy2(out_path, OUTPUT_DIR / f"DEBUG_REMBG_{stem}.png")
                
                popup_paths[stem] = out_path
                print(f"[REMBG SUCCESS] Removed background for {stem}", flush=True)
            except Exception as e:
                print(f"[REMBG ERROR] Failed to remove background for {stem}: {e}", flush=True)
    except Exception as e:
        print(f"[REMBG ERROR] Background removal failed: {e}", flush=True)

    try:
        _remove_previous_videos()
    except RuntimeError as error:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(error)) from error

    job_id = uuid4().hex
    output_path = OUTPUT_DIR / f"{_safe_video_stem(srt_file.filename)}.mp4"
    with JOBS_LOCK:
        JOBS[job_id] = {
            "state": "working",
            "progress": 0,
            "current_image": 0,
            "total_images": len(cues),
            "current_filename": "",
            "phase": "Preparing...",
            "error": "",
        }
        JOB_CANCEL_EVENTS[job_id] = threading.Event()
    JOB_EXECUTOR.submit(
        _run_generation,
        job_id,
        image_paths,
        cues,
        work_dir,
        output_path,
        JOB_CANCEL_EVENTS[job_id],
        audio_path,
        apply_zoom,
        sfx_paths,
        aspect_ratio,
        intensity_sfx_paths=intensity_sfx_paths,
        popup_paths=popup_paths,
        popup_sfx_paths=popup_sfx_paths,
        api_key=api_key,
        ai_provider=ai_provider,
        popup_prompt=popup_prompt,
        api_model=api_model,
        motion_style=motion_style,
        zoom_intensity=zoom_intensity,
        bg_mode=bg_mode,
        enable_subtitles=enable_subtitles,
        subtitle_style=subtitle_style,
        subtitle_position=subtitle_position,
        subtitle_font_size=subtitle_font_size,
        gpu_accel=gpu_accel,
        parallel_workers=parallel_workers,
        initial_popup_mapping=None,
        emotion_sfx_volume=emotion_sfx_volume,
        color_saturation=max(0.2, min(float(color_boost) / 100.0, 2.5)),
        popup_sfx_volume=popup_sfx_volume,
        transition_sfx_density=transition_sfx_density,
        transition_sfx_volume=transition_sfx_volume,
        emotion_sfx_density=emotion_sfx_density,
        popup_sfx_density=popup_sfx_density,
    )

    return {"job_id": job_id}


@app.get("/api/version")
async def get_version():
    return {"name": APP_NAME, "description": APP_DESCRIPTION, "version": APP_VERSION}

@app.get("/api/voices")
async def get_voices():
    return CURATED_VOICES

class AutoScriptRequest(BaseModel):
    topic: str
    duration_minutes: float = 1.0
    provider: str = "openai"
    api_key: str = ""
    api_model: str = ""

@app.post("/api/auto-script")
async def create_auto_script(req: AutoScriptRequest):
    if not (req.topic or "").strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        script = generate_script_with_ai(
            topic=req.topic,
            duration_minutes=req.duration_minutes,
            provider=req.provider,
            api_key=req.api_key,
            api_model=req.api_model,
        )
        return {"status": "success", "script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/split-grids")
async def api_split_grids(
    grid_files: list[UploadFile] = File(...),
    grid_type: str = Form("2x2"),
):
    """
    Slices uploaded 2x2 or 3x3 grid images into individual numbered scene images:
    image_00000.jpg, image_00001.jpg... and packages them into a ZIP for 1-click use.
    """
    if not grid_files:
        raise HTTPException(status_code=400, detail="No grid images uploaded.")
    
    work_dir = Path(tempfile.mkdtemp(prefix="srt_gridsplit_"))
    upload_dir = work_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    sliced_dir = work_dir / "sliced"
    sliced_dir.mkdir(parents=True, exist_ok=True)

    input_paths = []
    for idx, f in enumerate(grid_files):
        if f.filename:
            ext = Path(f.filename).suffix.lower()
            if ext in SUPPORTED_IMAGE_EXTENSIONS:
                dest = upload_dir / f"grid_{idx:04d}{ext}"
                dest.write_bytes(await f.read())
                input_paths.append(dest)

    if not input_paths:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="No valid image files found in upload.")

    sliced_paths = split_grid_images(input_paths, sliced_dir, grid_type=grid_type)
    
    zip_stem = f"sliced_scenes_{uuid4().hex[:8]}"
    zip_path = OUTPUT_DIR / f"{zip_stem}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for p in sliced_paths:
            zipf.write(p, arcname=p.name)

    shutil.rmtree(work_dir, ignore_errors=True)
    return {
        "status": "success",
        "grid_type": grid_type,
        "input_grid_count": len(input_paths),
        "total_sliced_scenes": len(sliced_paths),
        "zip_url": f"/api/download-grid-zip/{zip_path.name}",
        "zip_name": zip_path.name,
    }

@app.get("/api/download-grid-zip/{filename}")
async def download_grid_zip(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, filename=filename, media_type="application/zip")


class AutoGenerateScenesRequest(BaseModel):
    cues: list[dict]
    topic: str = ""
    style: str = "cinematic"
    grid_type: str = "2x2"


@app.post("/api/auto-generate-scenes")
async def api_auto_generate_scenes(req: AutoGenerateScenesRequest):
    """
    Automated AI Grid & Scene Generation:
    1. Takes dialogue cues from the script.
    2. Builds dialogue-accurate 2x2 or 3x3 multi-panel grid images illustrating the narrative.
    3. Slices the grids into numbered scenes (image_00000.jpg, image_00001.jpg, etc.).
    4. Packages the scenes into a downloadable ZIP.
    5. Returns preview URLs for every grid and sliced scene.
    """
    if not req.cues:
        raise HTTPException(status_code=400, detail="No cues provided for scene generation.")

    work_id = f"autoscene_{uuid4().hex[:8]}"
    work_dir = OUTPUT_DIR / work_id
    try:
        res = generate_auto_grid_scenes(
            cues=req.cues,
            topic=req.topic,
            style=req.style,
            grid_type=req.grid_type,
            work_dir=work_dir,
        )

        zip_name = f"auto_scenes_{uuid4().hex[:8]}.zip"
        final_zip_path = OUTPUT_DIR / zip_name
        shutil.copy2(res["zip_path"], final_zip_path)

        grid_items = [
            {
                "filename": p.name,
                "url": f"/api/preview-image/{work_id}/grids/{p.name}",
            }
            for p in res["grid_paths"]
        ]

        scene_items = [
            {
                "cue_index": i,
                "filename": p.name,
                "url": f"/api/preview-image/{work_id}/slices/{p.name}",
                "emotion": res["emotions"][i] if i < len(res["emotions"]) else "focused_narrative",
            }
            for i, p in enumerate(res["sliced_paths"])
        ]

        return {
            "status": "success",
            "total_scenes": res["total_scenes"],
            "grid_type": req.grid_type,
            "grids": grid_items,
            "scenes": scene_items,
            "zip_url": f"/api/download-grid-zip/{zip_name}",
            "zip_name": zip_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/preview-image/{work_id}/{subdir}/{filename}")
async def preview_image(work_id: str, subdir: str, filename: str):
    clean_w = re.sub(r"[^A-Za-z0-9_-]", "", work_id)
    clean_s = re.sub(r"[^A-Za-z0-9_-]", "", subdir)
    clean_f = re.sub(r"[^A-Za-z0-9_.-]", "", filename)
    file_path = OUTPUT_DIR / clean_w / clean_s / clean_f
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Preview image not found.")
    return FileResponse(file_path, media_type="image/jpeg")

@app.post("/api/generate-semantic-srt")
async def api_generate_semantic_srt(
    script_text: str = Form(...),
    voice: str = Form("en-US-ChristopherNeural"),
    topic: str = Form(""),
):
    """
    Synthesizes voiceover audio and generates a clean, narrative-driven SRT
    using the new semantic clause-aware & emotional pivot segmenter.
    """
    clean_script = (script_text or "").strip()
    if not clean_script:
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")

    work_dir = Path(tempfile.mkdtemp(prefix="srt_semgen_"))
    audio_path = OUTPUT_DIR / f"voice_{uuid4().hex[:8]}.mp3"
    srt_path = OUTPUT_DIR / f"subtitles_{uuid4().hex[:8]}.srt"

    try:
        _, _, validated_cues = await generate_voice_and_srt(
            clean_script,
            voice=voice,
            output_audio_path=audio_path,
            output_srt_path=srt_path,
        )
        srt_content = srt_path.read_text(encoding="utf-8")
        cue_list = [
            {
                "index": i + 1,
                "start_ms": c.start_ms,
                "end_ms": c.end_ms,
                "duration_s": round((c.end_ms - c.start_ms) / 1000.0, 2),
                "text": c.text,
            }
            for i, c in enumerate(validated_cues)
        ]
        scenes = breakdown_dialogue_scenes(validated_cues, topic=topic or clean_script[:60], style="cinematic")

        grid_prompts_2x2 = []
        for g_idx in range(0, len(scenes), 4):
            batch = scenes[g_idx:g_idx+4]
            items_desc = " | ".join(f"[Panel {p+1}]: {b['scene_prompt']}" for p, b in enumerate(batch))
            grid_prompts_2x2.append({
                "grid_number": (g_idx // 4) + 1,
                "scene_range": f"{batch[0]['cue_index']+1} - {batch[-1]['cue_index']+1}",
                "prompt": f"2x2 Grid of 4 sequential panels: {items_desc}. Consistent visual style, distinct border grid.",
            })

        return {
            "status": "success",
            "cue_count": len(validated_cues),
            "srt_text": srt_content,
            "srt_url": f"/api/download-file/{srt_path.name}",
            "audio_url": f"/api/download-file/{audio_path.name}",
            "cues": cue_list,
            "scenes": scenes,
            "grid_prompts_2x2": grid_prompts_2x2,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

@app.post("/api/scene-director-breakdown")
async def api_scene_director_breakdown(
    cues_text: str = Form(""),
    topic: str = Form(""),
    style: str = Form("cinematic"),
):
    """
    Analyzes subtitle text or dialogue to produce scene visual prompts,
    emotional tones, and 2x2/3x3 grid grouping prompts.
    Robustly handles full SRT, partial timestamps, or plain dialogue sentences.
    """
    raw_text = (cues_text or "").strip()
    if not raw_text:
        raw_text = (topic or "").strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    cues = []
    matches = list(TIMESTAMP_PATTERN.finditer(raw_text))
    if matches:
        for i, match in enumerate(matches):
            try:
                start_ms = _timestamp_to_ms(match.group("start"))
                end_ms = _timestamp_to_ms(match.group("end"))
                text_start = match.end()
                text_end = matches[i+1].start() if i + 1 < len(matches) else len(raw_text)
                c_text = raw_text[text_start:text_end].strip()
                lines = [l.strip() for l in c_text.splitlines() if l.strip() and not l.strip().isdigit()]
                cues.append(Cue(start_ms=start_ms, end_ms=end_ms, text=" ".join(lines)))
            except Exception:
                pass

    if not cues:
        # Fallback: parse as natural sentences
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', raw_text) if s.strip()]
        cur_t = 0
        for s in sentences:
            dur = max(len(s.split()) * 350, 2000)
            cues.append(Cue(start_ms=cur_t, end_ms=cur_t + dur, text=s))
            cur_t += dur + 100

    if not cues:
        cues.append(Cue(start_ms=0, end_ms=3000, text=raw_text[:120]))

    scenes = breakdown_dialogue_scenes(cues, topic=topic, style=style)

    grid_prompts_2x2 = []
    for g_idx in range(0, len(scenes), 4):
        batch = scenes[g_idx:g_idx+4]
        items_desc = " | ".join(f"[Panel {p+1}]: {b['scene_prompt']}" for p, b in enumerate(batch))
        grid_prompts_2x2.append({
            "grid_number": (g_idx // 4) + 1,
            "scene_range": f"{batch[0]['cue_index']+1} - {batch[-1]['cue_index']+1}",
            "prompt": f"2x2 Grid of 4 sequential panels: {items_desc}. Consistent visual style, distinct border grid.",
        })

    return {
        "status": "success",
        "scene_count": len(scenes),
        "scenes": scenes,
        "grid_prompts_2x2": grid_prompts_2x2,
    }

@app.get("/api/download-file/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    media_type = "text/plain" if filename.endswith(".srt") else "audio/mpeg"
    return FileResponse(file_path, filename=filename, media_type=media_type)


def _run_auto_generation(
    job_id: str,
    topic: str,
    script_text: str,
    voice: str,
    duration_minutes: float,
    saved_images: list[Path],
    work_dir: Path,
    output_path: Path,
    cancel_event: threading.Event,
    aspect_ratio: str,
    motion_style: str,
    zoom_intensity: str,
    bg_mode: str,
    enable_subtitles: bool,
    subtitle_style: str,
    subtitle_position: str,
    subtitle_font_size: int,
    gpu_accel: str,
    parallel_workers: int,
    bundled_sfx: list[str],
    api_key: str,
    ai_provider: str,
    api_model: str,
    enable_popups: bool,
    emotion_sfx_volume: float = 0.15,
    popup_sfx_volume: float = 0.40,
):
    try:
        def stage(msg, prog):
            _update_job(job_id, phase=msg, progress=prog)

        if not script_text or len(script_text.strip()) < 10:
            stage("Writing documentary script with AI...", 3)
            script_text = generate_script_with_ai(topic, duration_minutes, ai_provider, api_key, api_model)

        stage("Generating studio voiceover & synchronized subtitles...", 7)
        audio_path = work_dir / "narration.mp3"
        srt_path = work_dir / "captions.srt"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            _, _, cues = loop.run_until_complete(
                generate_voice_and_srt(script_text, voice, audio_path, srt_path)
            )
        finally:
            loop.close()

        auto_puppets = {}
        if saved_images:
            stage("Preparing uploaded visuals & 2D animation...", 14)
            image_paths = list(saved_images)
            if len(image_paths) < len(cues):
                orig = list(image_paths)
                while len(image_paths) < len(cues):
                    image_paths.extend(orig)
                image_paths = image_paths[:len(cues)]
            if enable_popups:
                puppets_dir = work_dir / "puppets"
                puppets_dir.mkdir(parents=True, exist_ok=True)
                from animated_history_engine import direct_dialogue_scenes, render_scene_animated_sequence
                scene_plans = direct_dialogue_scenes(cues, topic=topic)
                target_w, target_h = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
                for idx, cue in enumerate(cues):
                    plan = scene_plans[idx] if idx < len(scene_plans) else None
                    if plan:
                        cue_dur = getattr(cue, "duration", 2.5) or 2.5
                        p_tag, p_frames = render_scene_animated_sequence(
                            plan,
                            duration=cue_dur,
                            fps=8,
                            target_h=int(target_h * 0.52),
                            target_w=target_w,
                        )
                        if p_frames:
                            anim_dir = puppets_dir / f"anim_{idx:05d}"
                            anim_dir.mkdir(parents=True, exist_ok=True)
                            for f_i, frm in enumerate(p_frames):
                                frm.save(anim_dir / f"frame_{f_i:03d}.png", "PNG")
                            p_path = puppets_dir / f"puppet_{idx:05d}_{p_tag}.png"
                            p_frames[0].save(p_path, "PNG")
                            auto_puppets[idx] = p_path
        else:
            stage("Generating visual scenes & character puppets...", 14)
            slides_dir = work_dir / "slides"
            puppets_dir = work_dir / "puppets" if enable_popups else None
            res = generate_thematic_slides(cues, slides_dir, aspect_ratio=aspect_ratio, topic=topic, puppets_dir=puppets_dir)
            if isinstance(res, tuple):
                image_paths, auto_puppets = res
            else:
                image_paths = res

        _update_job(job_id, total_images=len(cues))

        sfx_paths = []
        for sfx_name in bundled_sfx:
            sfx_file = SFX_DIR / sfx_name
            if sfx_file.is_file():
                sfx_paths.append(sfx_file)
        # Default to camera shutter transition sounds if not explicitly specified
        if not sfx_paths:
            for f in sorted(SFX_DIR.glob("*")):
                if f.is_file() and ("shutter" in f.name.lower() or "camera" in f.name.lower()):
                    sfx_paths.append(f)

        intensity_sfx_paths = {}
        for folder in (INTENSITY_SFX_DIR, SFX_DIR):
            if folder.exists():
                for path in folder.glob("*"):
                    if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                        if path.name.lower() not in ("popup.wav", "click.wav", "rake swing whoosh close.mp3"):
                            if path.stem not in intensity_sfx_paths:
                                intensity_sfx_paths[path.stem] = path

        popup_paths = {}
        initial_popups = {}
        if enable_popups:
            popup_paths = get_channel_character_assets()
            for idx, p_path in auto_puppets.items():
                popup_paths[p_path.stem] = p_path
                initial_popups[idx] = p_path.stem

        # Zero annoying popup blips - audio is strictly dialogue-driven action SFX
        popup_sfx_paths = []

        _run_generation(
            job_id=job_id,
            image_paths=image_paths,
            cues=cues,
            work_dir=work_dir,
            output_path=output_path,
            cancel_event=cancel_event,
            audio_path=audio_path,
            apply_zoom=True,
            sfx_paths=sfx_paths,
            aspect_ratio=aspect_ratio,
            intensity_sfx_paths=intensity_sfx_paths,
            popup_paths=popup_paths if enable_popups else None,
            popup_sfx_paths=popup_sfx_paths if enable_popups else None,
            api_key=api_key,
            ai_provider=ai_provider,
            popup_prompt=None,
            api_model=api_model,
            motion_style=motion_style,
            zoom_intensity=zoom_intensity,
            bg_mode=bg_mode,
            enable_subtitles=enable_subtitles,
            subtitle_style=subtitle_style,
            subtitle_position=subtitle_position,
            subtitle_font_size=subtitle_font_size,
            gpu_accel=gpu_accel,
            parallel_workers=parallel_workers,
            initial_popup_mapping=initial_popups if (enable_popups and initial_popups) else None,
            emotion_sfx_volume=emotion_sfx_volume,
            popup_sfx_volume=popup_sfx_volume,
        )
    except GenerationCanceled:
        _update_job(job_id, state="canceled", phase="Canceled", error="Generation canceled.")
    except Exception as e:
        _update_job(job_id, state="error", phase="Failed", error=str(e))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        with JOBS_LOCK:
            JOB_CANCEL_EVENTS.pop(job_id, None)

@app.post("/api/generate-auto")
async def generate_auto_video(
    topic: str = Form(""),
    script_text: str = Form(""),
    voice: str = Form("en-US-ChristopherNeural"),
    duration_minutes: float = Form(1.0),
    aspect_ratio: str = Form("16:9"),
    custom_images: list[UploadFile] = File(default=[]),
    motion_style: str = Form("smart_random"),
    zoom_intensity: str = Form("medium"),
    bg_mode: str = Form("glass_blur"),
    enable_subtitles: bool = Form(True),
    subtitle_style: str = Form("hormozi_yellow"),
    subtitle_position: str = Form("bottom"),
    subtitle_font_size: int = Form(46),
    gpu_accel: str = Form("auto"),
    parallel_workers: int = Form(4),
    bundled_sfx: list[str] = Form(default=[]),
    api_key: str = Form(""),
    ai_provider: str = Form("gemini"),
    api_model: str = Form(""),
    enable_popups: bool = Form(True),
    emotion_sfx_volume: float = Form(0.15),
    popup_sfx_volume: float = Form(0.40),
):
    if not (topic or "").strip() and not (script_text or "").strip():
        raise HTTPException(status_code=400, detail="Please enter a topic or script.")
    if aspect_ratio not in {"16:9", "9:16"}:
        raise HTTPException(status_code=400, detail="Aspect ratio must be 16:9 or 9:16.")

    work_dir = Path(tempfile.mkdtemp(prefix="srt_auto_"))
    saved_images = []
    for index, image in enumerate(custom_images):
        if image.filename and Path(image.filename).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            image_path = work_dir / f"uploaded_{index:05d}{Path(image.filename).suffix.lower()}"
            image_path.write_bytes(await image.read())
            saved_images.append(image_path)

    try:
        _remove_previous_videos()
    except RuntimeError as error:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(error)) from error

    safe_title = re.sub(r"[^A-Za-z0-9._ -]+", "_", topic.strip() or "auto_history").strip(" .") or "auto_history"
    output_path = OUTPUT_DIR / f"{safe_title}.mp4"
    job_id = uuid4().hex

    with JOBS_LOCK:
        JOBS[job_id] = {
            "state": "working",
            "progress": 0,
            "current_image": 0,
            "total_images": 0,
            "current_filename": "",
            "phase": "Starting 1-Click Auto Pipeline...",
            "error": "",
        }
        JOB_CANCEL_EVENTS[job_id] = threading.Event()

    JOB_EXECUTOR.submit(
        _run_auto_generation,
        job_id,
        topic,
        script_text,
        voice,
        duration_minutes,
        saved_images,
        work_dir,
        output_path,
        JOB_CANCEL_EVENTS[job_id],
        aspect_ratio,
        motion_style,
        zoom_intensity,
        bg_mode,
        enable_subtitles,
        subtitle_style,
        subtitle_position,
        subtitle_font_size,
        gpu_accel,
        parallel_workers,
        bundled_sfx,
        api_key,
        ai_provider,
        api_model,
        enable_popups,
        emotion_sfx_volume,
        popup_sfx_volume,
    )

    return {"job_id": job_id}

@app.get("/api/sfx")
async def get_sfx_list():
    SFX_DIR.mkdir(exist_ok=True)
    return [
        f.name for f in SFX_DIR.glob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS and not f.name.startswith(("-", "."))
    ]

@app.get("/api/popup-sfx")
async def get_popup_sfx_list():
    popups_sfx_dir = SFX_DIR / "popups"
    popups_sfx_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for f in sorted(popups_sfx_dir.glob("*")):
        if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS and not f.name.startswith(("-", ".")):
            results.append({
                "filename": f.name,
                "name": f.stem.replace("_", " ").title(),
                "url": f"/static-assets/sfx/popups/{f.name}"
            })
    return results

@app.get("/api/intensity")
async def get_intensity_list():
    INTENSITY_SFX_DIR.mkdir(exist_ok=True)
    return [f.name for f in INTENSITY_SFX_DIR.glob("*") if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS]


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Generation job not found.")
        d = dict(job)
        d["status"] = "done" if d.get("state") == "complete" else ("error" if d.get("state") == "error" else "working")
        d["stage"] = d.get("phase", "working")
        d["message"] = d.get("phase", "")
        if "output_name" in d:
            d["video_filename"] = d["output_name"]
            d["video_url"] = f"/api/jobs/{job_id}/download"
        return d


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        cancel_event = JOB_CANCEL_EVENTS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Generation job not found.")
        if not cancel_event:
            if job["state"] == "working":
                job.update(state="error", phase="Failed", error="The generation worker stopped unexpectedly.")
            return dict(job)
        if job["state"] != "working":
            return dict(job)
        job["state"] = "canceling"
        cancel_event.set()
        return dict(job)


@app.get("/api/jobs/{job_id}/download")
async def download_job(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Generation job not found.")
        if job["state"] != "complete":
            raise HTTPException(status_code=409, detail="Video generation is not complete.")
        output_name = job["output_name"]

    output_path = OUTPUT_DIR / output_name
    return FileResponse(output_path, media_type="video/mp4", filename=output_name)


app.mount("/static-assets/stickmen", StaticFiles(directory=str(STICKMEN_DIR)), name="stickmen_static")
app.mount("/static-assets/popups", StaticFiles(directory=str(POPUPS_DIR)), name="popups_static")
app.mount("/static-assets/custom_channel_assets", StaticFiles(directory=str(CUSTOM_CHANNEL_ASSETS_DIR)), name="custom_assets_static")
app.mount("/static-assets/characters", StaticFiles(directory=str(CHARACTERS_DIR)), name="characters_static")
app.mount("/static-assets/sfx", StaticFiles(directory=str(SFX_DIR)), name="sfx_static")

@app.get("/api/channel-assets")
def list_channel_assets():
    """Returns list of all available Animated History stickmen, characters, and custom assets."""
    all_assets = get_channel_character_assets()
    return {
        "count": len(all_assets),
        "assets": [
            {
                "name": stem,
                "filename": path.name,
                "is_custom": path.parent in (CUSTOM_CHANNEL_ASSETS_DIR, CHARACTERS_DIR),
                "folder": path.parent.name,
                "url": f"/static-assets/{path.parent.name}/{path.name}",
            }
            for stem, path in sorted(all_assets.items())
        ]
    }

@app.post("/api/upload-channel-asset")
async def upload_channel_asset(asset_file: UploadFile = File(...)):
    """Allows uploading custom characters or action PNGs directly into characters/"""
    if not asset_file.filename:
        raise HTTPException(status_code=400, detail="Missing file")
    ext = Path(asset_file.filename).suffix.lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, or WEBP allowed")

    clean_name = re.sub(r"[^A-Za-z0-9._-]+", "_", asset_file.filename)
    dest = CHARACTERS_DIR / clean_name
    dest.write_bytes(await asset_file.read())
    return {"status": "ok", "filename": clean_name, "saved_to": "characters"}

# =====================================================================
# Animated History Long-Form Documentary Engine Endpoints
# =====================================================================
from history_documentary_engine import (
    generate_documentary_script,
    breakdown_script_to_chapters,
    run_documentary_pipeline,
    DOCUMENTARY_CURATED_SCRIPTS,
)

class DocResearchRequest(BaseModel):
    topic: str
    duration_minutes: float = 3.0
    api_key: str = ""
    ai_provider: str = "openai"
    api_model: str = ""
    preset: str = ""

class DocGenerateRequest(BaseModel):
    topic: str
    duration_minutes: float = 3.0
    voice: str = "en-US-ChristopherNeural"
    aspect_ratio: str = "16:9"
    subtitle_style: str = "hormozi_yellow"
    sfx_volume: float = 0.20
    gpu_accel: str = "auto"
    parallel_workers: int = 4
    api_key: str = ""
    ai_provider: str = "openai"
    api_model: str = ""
    custom_script: str = ""
    preset: str = ""
    style: str = "animated_history"
    stamp_dates: bool = True
    puppet_sync: bool = True
    countryballs: bool = True
    include_archive_art: bool = True
    ai_image_provider: str = "flux"
    image_style: str = "cinematic_oil"

class TestNvidiaKeyRequest(BaseModel):
    api_key: str

@app.post("/api/documentary/test_nvidia_key")
async def api_test_nvidia_key(req: TestNvidiaKeyRequest):
    key = req.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API Key cannot be empty.")
    
    import json, urllib.request, time
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    t0 = time.time()
    try:
        chat_req = urllib.request.Request(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            data=json.dumps({
                "model": "meta/llama-3.3-70b-instruct",
                "messages": [{"role": "user", "content": "Respond with 'NVIDIA NIM ACTIVE' in 3 words only."}],
                "max_tokens": 10,
            }).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(chat_req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data["choices"][0]["message"]["content"].strip()
            elapsed = round((time.time() - t0) * 1000)
            return {
                "success": True,
                "status": "valid",
                "message": f"NVIDIA NIM Verified! ({elapsed}ms latency)",
                "sample_output": msg,
                "model": "meta/llama-3.3-70b-instruct",
                "latency_ms": elapsed,
            }
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8", errors="ignore")
        return {
            "success": False,
            "status": "error",
            "message": f"HTTP {he.code}: {body}",
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": str(e),
        }

@app.post("/api/documentary/research")
async def api_documentary_research(req: DocResearchRequest):
    if not (req.topic or "").strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        provider = req.ai_provider
        if req.api_key and req.api_key.strip().startswith("nvapi-"):
            provider = "nvidia"

        script = generate_documentary_script(
            topic=req.topic,
            duration_minutes=req.duration_minutes,
            api_key=req.api_key,
            provider=provider,
            model=req.api_model,
        )
        chapters = breakdown_script_to_chapters(script, topic=req.topic)
        return {
            "success": True,
            "status": "success",
            "topic": req.topic,
            "duration_minutes": req.duration_minutes,
            "word_count": len(script.split()),
            "script": script,
            "outline": {
                "title": req.topic,
                "chapters": chapters,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documentary/presets")
async def api_documentary_presets():
    return [
        {
            "id": "israel",
            "title": "2000 Years of Israel History in Minutes",
            "badge": "EPIC DOCUMENTARY",
            "era": "66 AD - Modern Day",
            "desc": "Roman Judea revolt, Masada siege, Caesarea harbor, Byzantine basilicas, Crusades, Ottomans, British Mandate & 1948 countryball battles.",
            "default_topic": "2000 Years of Israel History",
        },
        {
            "id": "rome",
            "title": "1000 Years of the Roman Empire",
            "badge": "CLASSICAL HISTORY",
            "era": "509 BC - 476 AD",
            "desc": "From Republic farming legions to Julius Caesar crossing the Rubicon, Pax Romana, and the dramatic fall of Western Rome.",
            "default_topic": "1000 Years of the Roman Empire",
        },
        {
            "id": "french_revolution",
            "title": "The French Revolution Explained",
            "badge": "REVOLUTIONARY WAR",
            "era": "1789 - 1804",
            "desc": "Storming of the Bastille, fall of Louis XVI, Reign of Terror, guillotine paranoia, and the rise of Emperor Napoleon.",
            "default_topic": "The French Revolution Explained",
        },
        {
            "id": "hastings",
            "title": "The 1066 Battle of Hastings",
            "badge": "MEDIEVAL CONQUEST",
            "era": "October 1066",
            "desc": "King Harold's Saxon shield wall vs William Duke of Normandy's knights, feigned retreat, arrow strike, and coronation.",
            "default_topic": "The 1066 Battle of Hastings",
        },
        {
            "id": "ww1",
            "title": "World War 1 in 15 Minutes",
            "badge": "MODERN GEOPOLITICS",
            "era": "1914 - 1918",
            "desc": "The assassination in Sarajevo, trench warfare, machine guns, Countryball alliances, and the November Armistice.",
            "default_topic": "World War 1 in 15 Minutes",
        },
        {
            "id": "ancient_human",
            "title": "What Did Ancient Humans Do All Day?",
            "badge": "PREHISTORY & EVOLUTION",
            "era": "200,000 Years Ago",
            "desc": "Daily survival in the Ice Age, mammoth hunts, cave paintings, discovery of fire, and the dawn of human language.",
            "default_topic": "What Did Ancient Humans Do All Day",
        },
    ]

@app.post("/api/documentary/generate")
async def api_generate_documentary(req: DocGenerateRequest):
    topic = (req.topic or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    if req.aspect_ratio not in {"16:9", "9:16"}:
        raise HTTPException(status_code=400, detail="Aspect ratio must be 16:9 or 9:16.")

    try:
        _remove_previous_videos()
    except Exception:
        pass

    safe_title = re.sub(r"[^A-Za-z0-9._ -]+", "_", topic or "documentary").strip(" .") or "documentary"
    output_path = OUTPUT_DIR / f"{safe_title}.mp4"
    job_id = uuid4().hex

    with JOBS_LOCK:
        JOBS[job_id] = {
            "state": "working",
            "progress": 0,
            "current_image": 0,
            "total_images": 0,
            "current_filename": "",
            "phase": "Starting 1-Click Documentary Engine...",
            "error": "",
            "topic": topic,
            "duration_minutes": req.duration_minutes,
        }
        JOB_CANCEL_EVENTS[job_id] = threading.Event()

    ai_prov = req.ai_provider
    img_prov = req.ai_image_provider
    if req.api_key and req.api_key.strip().startswith("nvapi-"):
        if ai_prov in ("openai", "default", ""):
            ai_prov = "nvidia"
        if img_prov in ("flux", "nvidia"):
            img_prov = "nvidia"

    def doc_worker():
        run_documentary_pipeline(
            job_id=job_id,
            topic=topic,
            duration_minutes=req.duration_minutes,
            voice=req.voice,
            aspect_ratio=req.aspect_ratio,
            subtitle_style=req.subtitle_style,
            sfx_volume=req.sfx_volume,
            gpu_accel=req.gpu_accel,
            parallel_workers=req.parallel_workers,
            output_path=output_path,
            cancel_event=JOB_CANCEL_EVENTS[job_id],
            update_job_callback=_update_job,
            api_key=req.api_key,
            provider=ai_prov,
            model=req.api_model,
            custom_script=req.custom_script,
            include_archive_art=req.include_archive_art,
            ai_image_provider=img_prov,
            image_style=req.image_style,
            stamp_dates=req.stamp_dates,
        )

    JOB_EXECUTOR.submit(doc_worker)
    return {
        "success": True,
        "job_id": job_id,
        "status": "started",
        "output_filename": output_path.name,
        "video_url": f"/api/jobs/{job_id}/download",
    }

app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
