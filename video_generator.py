import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import random

from srt_parser import Cue

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VIDEO_FPS = 30
MAX_ZOOM = 1.05
MAX_ZOOM_DURATION_SECONDS = 1.0
MOTION_WIDTH = 2560
MOTION_HEIGHT = 1440
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080
ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
}


class GenerationCanceled(Exception):
    pass


def _escape_drawtext(s: str) -> str:
    # Escape characters that have special meaning in FFmpeg drawtext
    return s.replace('\\', '\\\\').replace("'", "’").replace(':', r'\:').replace('%', r'\%')



def _duration_seconds(cues: list[Cue], index: int) -> float:
    if index + 1 < len(cues):
        duration_ms = cues[index + 1].start_ms - cues[index].start_ms
    else:
        duration_ms = max(cues[index].end_ms - cues[index].start_ms, 1_000)
    return max(duration_ms / 1_000, 0.1)


def build_dialogue_motion_expressions(
    cue_text: str,
    duration: float,
    popup_stem: str,
    aspect_ratio: str,
    index: int,
    has_battle_sfx: bool = False,
) -> tuple[str, int, str]:
    """
    Dialogue-Driven 2D Motion Design & Puppet Engine:
    Constructs bespoke, non-repeating mathematical movement expressions for character
    puppets, tactical map movements, battle lunges, shocks, and natural speech pauses.
    Returns: (overlay_anim_expr, pop_size, camera_shake_fragment)
    """
    text_lower = (cue_text or "").lower()
    words = text_lower.split()
    stem_lower = (popup_stem or "").lower()

    is_16_9 = aspect_ratio == "16:9"
    is_right_side = (index % 2 != 0 and is_16_9)
    base_x = "W-w-180" if is_right_side else 180
    base_y = "H-h-50"

    is_arrow = "arrow" in stem_lower
    is_battle = ("battle" in stem_lower or "attack" in stem_lower or "fight" in stem_lower or "war" in stem_lower or has_battle_sfx or any(w in text_lower for w in ["clash", "swords", "attack", "strike", "charge", "battle", "fight", "hit", "brawl", "slashed", "war", "cannon", "fired", "assault", "invade", "conquer"])) and not is_arrow
    is_defeat = ("dead" in stem_lower or "defeat" in stem_lower or "sad" in stem_lower or any(w in text_lower for w in ["dead", "died", "defeat", "defeated", "fallen", "casualty", "fell", "collapse", "collapsed", "slain", "crushed", "destroyed", "executed", "grief", "loss", "tears"])) and not is_arrow
    is_shock = ("shock" in stem_lower or "surprise" in stem_lower or "confused" in stem_lower or any(w in text_lower for w in ["suddenly", "surprise", "surprised", "shock", "shocked", "unexpected", "betray", "twist", "gasp", "disaster", "ambush"])) and not is_arrow
    is_march = ("march" in stem_lower or "walk" in stem_lower or "ride" in stem_lower or any(w in text_lower for w in ["march", "marched", "marching", "advance", "advanced", "journey", "ride", "cavalry", "travel", "fleet"])) and not is_arrow
    is_cheer = ("cheer" in stem_lower or "victory" in stem_lower or "celebrate" in stem_lower or any(w in text_lower for w in ["victory", "cheer", "cheered", "celebrate", "triumph", "won", "glory"])) and not is_arrow
    is_speech = ("speech" in stem_lower or "king" in stem_lower or "pope" in stem_lower or "priest" in stem_lower or any(w in text_lower for w in ["said", "declared", "announced", "speech", "demanded", "proclaimed", "shouted", "decreed", "crowned", "king", "pope", "priest", "preached"])) and not is_arrow

    # Modern Explainer Categories: Thinking, Stress, Idea, Money, Rocket
    is_thinking = ("think" in stem_lower or "brain" in stem_lower or "mind" in stem_lower or any(w in text_lower for w in ["overthink", "overthinking", "think", "thinking", "thoughts", "ponder", "wonder", "wondering", "mind", "contemplate", "doubt", "brain", "question", "curious"])) and not is_arrow
    is_stress = ("stress" in stem_lower or "anxiety" in stem_lower or "panic" in stem_lower or any(w in text_lower for w in ["stress", "stressed", "anxiety", "anxious", "panic", "panicking", "overwhelmed", "nervous", "fear", "afraid", "insomnia", "worry", "worried"])) and not is_arrow
    is_idea = ("idea" in stem_lower or "eureka" in stem_lower or "lightbulb" in stem_lower or any(w in text_lower for w in ["idea", "eureka", "solution", "realized", "realization", "breakthrough", "genius", "invented", "smart", "discovered"])) and not is_arrow
    is_money = ("money" in stem_lower or "gold" in stem_lower or "rich" in stem_lower or "wealth" in stem_lower or any(w in text_lower for w in ["billionaire", "millionaire", "wealth", "wealthy", "rich", "money", "cash", "dollars", "fortune", "profit", "stocks", "invest", "crypto", "bitcoin", "elon"])) and not is_arrow
    is_rocket = ("rocket" in stem_lower or "space" in stem_lower or "launch" in stem_lower or any(w in text_lower for w in ["rocket", "launch", "spacex", "mars", "space", "orbit"])) and not is_arrow

    camera_shake = ""
    dir_mult = -1 if is_right_side else 1

    if is_arrow:
        pop_size = 560 if is_16_9 else 440
        anim_expr = (
            "x='min(60 + (W-w-120)*(1 - exp(-t*4.2))\\, W-w-60)':"
            "y='(H-h)/2 - 40 + 20*sin(min((1 - exp(-t*4.2))*PI\\, PI))'"
        )
    elif is_battle:
        pop_size = 580 if is_16_9 else 460
        camera_shake = "+ if(between(time, 0.32, 0.62), 22*sin((time-0.32)*80)*exp(-(time-0.32)*9), 0)"
        anim_expr = (
            f"x='{base_x} + if(lt(t,0.18), {dir_mult} * (-60*(t/0.18)), "
            f"if(lt(t,0.38), {dir_mult} * (-60 + 260*((t-0.18)/0.20)), "
            f"if(lt(t,0.65), {dir_mult} * (200 + 16*sin((t-0.38)*60)*exp(-(t-0.38)*8)), "
            f"{dir_mult} * (200 - 90*min(1.0\\, (t-0.65)/0.35)))))':"
            f"y='{base_y} + if(lt(t,0.18), 18*(t/0.18), "
            f"if(lt(t,0.38), 24, "
            f"if(lt(t,0.65), 18 - 8*(t-0.38)/0.27, "
            f"10 - 10*min(1.0\\, (t-0.65)/0.35))))'"
        )
    elif is_defeat:
        pop_size = 520 if is_16_9 else 400
        anim_expr = (
            f"x='{base_x} - if(lt(t,0.18), {dir_mult} * 40*(t/0.18), {dir_mult} * 40)':"
            f"y='{base_y} + if(lt(t,0.18), 0, "
            f"if(lt(t,0.45), 85*((t-0.18)/0.27), "
            f"if(lt(t,0.7), 85 - 18*exp(-(t-0.45)*12)*abs(sin((t-0.45)*25)), 85)))'"
        )
    elif is_shock:
        pop_size = 540 if is_16_9 else 420
        anim_expr = (
            f"x='{base_x} + if(between(t,0.25,0.85), 12*sin((t-0.25)*48)*exp(-(t-0.25)*5), 0)':"
            f"y='{base_y} - if(lt(t,0.06), 0, "
            f"if(lt(t,0.36), 180*sin((t-0.06)/0.30 * PI), "
            f"if(lt(t,0.75), -30*exp(-(t-0.36)*9)*cos((t-0.36)*24), 0)))'"
        )
    elif is_march:
        pop_size = 540 if is_16_9 else 420
        anim_expr = (
            f"x='{base_x} + {dir_mult} * 18*sin(t*5)':"
            f"y='{base_y} - 28*abs(sin(t*8))'"
        )
    elif is_cheer:
        pop_size = 540 if is_16_9 else 420
        anim_expr = (
            f"x='{base_x} + 12*sin(t*6)':"
            f"y='{base_y} - 45*abs(sin(t*7.5))'"
        )
    elif is_thinking:
        pop_size = 540 if is_16_9 else 420
        anim_expr = (
            f"x='{base_x} + 12*sin(t*3.2)':"
            f"y='{base_y} - 15*sin(t*3.8) - if(lt(t,0.3), 35*(1-exp(-t*8)), 35)'"
        )
    elif is_stress:
        pop_size = 530 if is_16_9 else 410
        anim_expr = (
            f"x='{base_x} + 8*sin(t*40)*exp(-min(1.0\\, t*0.15))':"
            f"y='{base_y} - 14*abs(sin(t*12))'"
        )
    elif is_idea:
        pop_size = 550 if is_16_9 else 430
        anim_expr = (
            f"x='{base_x} + 6*sin(t*5)':"
            f"y='{base_y} - if(lt(t,0.12), 0, if(lt(t,0.38), 120*sin((t-0.12)/0.26 * PI), 20*exp(-(t-0.38)*8)*abs(cos((t-0.38)*18))))'"
        )
    elif is_money:
        pop_size = 560 if is_16_9 else 440
        anim_expr = (
            f"x='{base_x} + 10*sin(t*4.5)':"
            f"y='{base_y} - 32*abs(sin(t*6.5))'"
        )
    elif is_rocket:
        pop_size = 560 if is_16_9 else 440
        anim_expr = (
            f"x='{base_x} + 4*sin(t*30)':"
            f"y='{base_y} - min(260.0\\, 190.0*(t/max(0.6\\, {duration:.2f}*0.7))^2)'"
        )
    elif is_speech:
        pop_size = 550 if is_16_9 else 430
        speech_time = min(duration * 0.90, max(1.2, len(words) * 0.35 + 0.3))
        anim_expr = (
            f"x='{base_x} + if(lt(t,{speech_time:.3f}), 16*sin(t*6), 0)':"
            f"y='{base_y} + if(lt(t,0.35), 110*exp(-t*8)*cos(t*20), if(lt(t,{speech_time:.3f}), 20*abs(sin(t*10)), 4*sin(t*2)))'"
        )
    else:
        # Dialogue-synchronized expressive speaking cadence
        pop_size = 540 if is_16_9 else 420
        speech_time = min(duration * 0.88, max(1.1, len(words) * 0.34 + 0.3))
        anim_expr = (
            f"x='{base_x} + if(lt(t,{speech_time:.3f}), 18*sin(t*7.5), 0)':"
            f"y='{base_y} + if(lt(t,0.35), 110*exp(-t*8)*cos(t*20), "
            f"if(lt(t,{speech_time:.3f}), 18*sin(t*11)*(0.65 + 0.35*cos(t*4.5)), 4*sin(t*2)))'"
        )

    return anim_expr, pop_size, camera_shake


def create_video(
    images: list[Path],
    cues: list[Cue],
    ffmpeg_path: Path,
    work_dir: Path,
    output_path: Path,
    on_image_started=None,
    cancel_event: threading.Event | None = None,
    audio_path: Path | None = None,
    apply_zoom: bool = True,
    sfx_paths: list[Path] | None = None,
    intensity_sfx_paths: dict[str, Path] | None = None,
    intensity_mapping: dict[int, str] | None = None,
    aspect_ratio: str = "16:9",
    on_stage_changed=None,
    popup_paths: dict[str, Path] | None = None,
    popup_mapping: dict[int, str] | None = None,
    popup_sfx_paths: list[Path] | None = None,
    motion_style: str = "smart_random",
    zoom_intensity: str = "subtle",
    bg_mode: str = "crop_fill",
    enable_subtitles: bool = False,
    subtitle_style: str = "hormozi_yellow",
    subtitle_position: str = "bottom",
    subtitle_font_size: int = 46,
    gpu_accel: str = "auto",
    parallel_workers: int = 4,
    transition_sfx_density: float = 0.25,
    transition_sfx_volume: float = 0.15,
    emotion_sfx_volume: float = 0.15,
    popup_sfx_density: float = 0.30,
    popup_sfx_volume: float = 0.25,
    color_saturation: float = 1.14,
) -> None:
    if len(images) < len(cues):
        raise ValueError(
            f"The SRT contains {len(cues)} cues, but only {len(images)} images were provided."
        )
    if aspect_ratio not in ASPECT_RATIOS:
        raise ValueError("Aspect ratio must be 16:9 or 9:16.")

    output_width, output_height = ASPECT_RATIOS[aspect_ratio]
    motion_width = output_width * 2
    motion_height = output_height * 2

    zoom_intensity_map = {"subtle": 1.05, "medium": 1.12, "dramatic": 1.22}
    max_zoom_val = zoom_intensity_map.get(zoom_intensity, 1.05)

    segments_dir = work_dir / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    segment_paths = [segments_dir / f"segment_{i:05d}.mp4" for i in range(len(cues))]

    def _render_one_segment(index: int):
        if cancel_event and cancel_event.is_set():
            raise GenerationCanceled()

        cue = cues[index]
        segment_path = segment_paths[index]
        duration = _duration_seconds(cues, index)
        frame_count = max(round(duration * VIDEO_FPS), 3)

        # 1. Base Framing & Background Mode (High-Precision Lanczos Scaling)
        if bg_mode == "glass_blur":
            base_prep = (
                f"split[bg_in][fg_in];"
                f"[bg_in]scale={motion_width}:{motion_height}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd,"
                f"crop={motion_width}:{motion_height},boxblur=20:5,eq=brightness=-0.12[blurred];"
                f"[fg_in]scale={motion_width}:{motion_height}:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd[sharp];"
                f"[blurred][sharp]overlay=(W-w)/2:(H-h)/2,"
            )
        else:
            base_prep = (
                f"scale={motion_width}:{motion_height}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd,"
                f"crop={motion_width}:{motion_height},"
            )

        # 2. Dialogue-Driven Motion & Character Resolution
        popup_label = popup_mapping.get(index) if popup_mapping else None
        popup_img = None
        if popup_label and popup_label.lower() != "none" and popup_paths:
            popup_img = popup_paths.get(popup_label)
            if not popup_img:
                lower_lookup = {k.lower(): v for k, v in popup_paths.items()}
                popup_img = lower_lookup.get(popup_label.lower())

        has_popup = popup_img is not None and Path(popup_img).is_file()
        img_stem = Path(popup_img).stem if has_popup else ""

        curr_intensity = (intensity_mapping.get(index) or "").lower() if intensity_mapping else ""
        has_battle = "battle" in curr_intensity or "epic" in curr_intensity or "high" in curr_intensity
        anim_expr, pop_size, cam_shake = build_dialogue_motion_expressions(
            cue.text or "",
            duration,
            img_stem,
            aspect_ratio,
            index,
            has_battle_sfx=has_battle,
        )

        # 3. Camera Motion & Screen Impact Shake with Contrast Adaptive Sharpening (CAS) & Cinematic Color
        if apply_zoom and motion_style != "static":
            total_frames = max(int(round(duration * VIDEO_FPS)), 1)
            zoom_span = max(total_frames - 1, 1)
            zoom_frame = f"min(on\\,{zoom_span})"
            eased_progress = f"(1-cos(PI*{zoom_frame}/{zoom_span}))/2"

            base_zoom = 1.05
            target_zoom = 1.11
            zoom_diff = target_zoom - base_zoom

            chosen_motion = motion_style
            if motion_style == "smart_random":
                motions = ["zoom_in", "zoom_out", "pan_left", "pan_right"]
                chosen_motion = motions[index % len(motions)]

            shake_suffix = f" {cam_shake}".strip() if cam_shake else ""
            if chosen_motion == "zoom_in":
                zoom_expression = f"{base_zoom:.4f}+{zoom_diff:.4f}*{eased_progress}"
                pan_x = f"iw/2-(iw/zoom/2) {shake_suffix}".strip()
                pan_y = f"ih/2-(ih/zoom/2) {shake_suffix}".strip()
            elif chosen_motion == "zoom_out":
                zoom_expression = f"{target_zoom:.4f}-{zoom_diff:.4f}*{eased_progress}"
                pan_x = f"iw/2-(iw/zoom/2) {shake_suffix}".strip()
                pan_y = f"ih/2-(ih/zoom/2) {shake_suffix}".strip()
            elif chosen_motion == "pan_left":
                zoom_expression = f"{target_zoom:.4f}"
                pan_x = f"(iw-iw/zoom)*(1-{eased_progress}) {shake_suffix}".strip()
                pan_y = f"ih/2-(ih/zoom/2) {shake_suffix}".strip()
            else:
                zoom_expression = f"{target_zoom:.4f}"
                pan_x = f"(iw-iw/zoom)*{eased_progress} {shake_suffix}".strip()
                pan_y = f"ih/2-(ih/zoom/2) {shake_suffix}".strip()

            video_filter = (
                f"{base_prep}"
                f"zoompan=z='{zoom_expression}':x='{pan_x}':"
                f"y='{pan_y}':d={frame_count}:s={motion_width}x{motion_height}:fps={VIDEO_FPS},"
                f"scale={output_width}:{output_height}:flags=lanczos+accurate_rnd,"
                f"cas=0.35,"
                f"eq=contrast=1.06:brightness=0.01:saturation={color_saturation:.2f},"
                "format=yuv420p"
            )
        else:
            if bg_mode == "glass_blur":
                video_filter = (
                    f"split[bg_in][fg_in];"
                    f"[bg_in]scale={output_width}:{output_height}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd,"
                    f"crop={output_width}:{output_height},boxblur=20:5,eq=brightness=-0.12[blurred];"
                    f"[fg_in]scale={output_width}:{output_height}:force_original_aspect_ratio=decrease:flags=lanczos+accurate_rnd[sharp];"
                    f"[blurred][sharp]overlay=(W-w)/2:(H-h)/2,"
                    f"cas=0.35,"
                    f"eq=contrast=1.06:brightness=0.01:saturation={color_saturation:.2f},"
                    "format=yuv420p"
                )
            else:
                video_filter = (
                    f"scale={output_width}:{output_height}:force_original_aspect_ratio=increase:flags=lanczos+accurate_rnd,"
                    f"crop={output_width}:{output_height},"
                    f"cas=0.35,"
                    f"eq=contrast=1.06:brightness=0.01:saturation={color_saturation:.2f},"
                    "format=yuv420p"
                )

        # 4. Dynamic Subtitles Burner
        cue_raw_text = (cue.text or "").strip()
        if enable_subtitles and cue_raw_text:
            clean_txt = _escape_drawtext(cue_raw_text)
            font_path = Path("C:/Windows/Fonts/arialbd.ttf")
            font_arg = "fontfile='C\\:/Windows/Fonts/arialbd.ttf':" if font_path.exists() else ""
            pos_y = "h-text_h-90" if aspect_ratio == "16:9" else "h-text_h-220"
            if subtitle_position == "center":
                pos_y = "(h-text_h)/2"
            elif subtitle_position == "top":
                pos_y = "90"
            pos_expr = f"x=(w-text_w)/2:y={pos_y}"

            if subtitle_style == "hormozi_yellow":
                style_expr = "fontcolor=0xFFE600:borderw=4:bordercolor=black:shadowx=2:shadowy=2:shadowcolor=black@0.9"
            elif subtitle_style == "cinematic_white":
                style_expr = "fontcolor=white:borderw=3:bordercolor=black:shadowx=2:shadowy=2:shadowcolor=black@0.8"
            elif subtitle_style == "neon_glow":
                style_expr = "fontcolor=0x00F2FE:borderw=3:bordercolor=0x003344:shadowx=0:shadowy=0:shadowcolor=0x00F2FE@0.7"
            else:
                style_expr = "fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=12"

            sub_filter = f"drawtext={font_arg}text='{clean_txt}':fontsize={subtitle_font_size}:{style_expr}:{pos_expr}"
            video_filter = f"{video_filter},{sub_filter}"

        command = [str(ffmpeg_path), "-y"]
        if not apply_zoom and motion_style == "static":
            command.extend(["-loop", "1"])
        command.extend(["-i", str(images[index])])

        if has_popup:
            # Check if this popup has a multi-frame animation sequence
            anim_dir = Path(popup_img).parent / f"anim_{index:05d}"
            is_seq = anim_dir.is_dir() and any(anim_dir.glob("frame_*.png"))
            # Only full 1920x1080 pre-baked overlays bypass scaling & animation
            is_full_canvas = img_stem.lower().startswith(("full_canvas_", "overlay_full_"))

            if is_seq:
                command.extend(["-stream_loop", "-1", "-framerate", "8", "-i", str(anim_dir / "frame_%03d.png")])
            else:
                command.extend(["-loop", "1", "-i", str(popup_img)])

            if is_full_canvas:
                complex_filter = (
                    f"[0:v]{video_filter}[bg];"
                    f"[1:v]format=yuva420p[p];"
                    f"[bg][p]overlay=0:0[outv]"
                )
            else:
                is_right_side = (index % 2 != 0 and aspect_ratio == "16:9")
                flip_filter = "hflip," if is_right_side else ""
                complex_filter = (
                    f"[0:v]{video_filter}[bg];"
                    f"[1:v]{flip_filter}scale={pop_size}:{pop_size}:force_original_aspect_ratio=decrease,format=yuva420p[p];"
                    f"[bg][p]overlay={anim_expr}:enable='gte(t,0.04)':eval=frame[outv]"
                )
            command.extend(["-filter_complex", complex_filter, "-map", "[outv]"])
        else:
            command.extend(["-vf", video_filter])

        if not apply_zoom and motion_style == "static":
            command.extend(["-t", f"{duration:.3f}"])

        if gpu_accel in ("auto", "nvenc"):
            command.extend(["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "18", "-rc", "vbr", "-b:v", "0", "-maxrate", "28M", "-bufsize", "50M"])
        else:
            command.extend(["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"])

        command.extend([
            "-frames:v", str(frame_count),
            "-an",
            str(segment_path)
        ])
        try:
            _run_ffmpeg(command, cancel_event)
        except Exception:
            if "-c:v" in command and "h264_nvenc" in command:
                c_idx = command.index("h264_nvenc")
                fallback_cmd = []
                skip = 0
                for i, arg in enumerate(command):
                    if skip > 0:
                        skip -= 1
                        continue
                    if arg == "h264_nvenc":
                        fallback_cmd.extend(["libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"])
                        continue
                    if arg in ("-preset", "-cq", "-rc", "-b:v", "-maxrate", "-bufsize") and i > c_idx:
                        skip = 1
                        continue
                    fallback_cmd.append(arg)
                _run_ffmpeg(fallback_cmd, cancel_event)
            else:
                raise

    workers = max(1, min(int(parallel_workers), len(cues), 8))
    completed_count = 0
    completed_lock = threading.Lock()

    def _worker_wrapper(idx):
        nonlocal completed_count
        _render_one_segment(idx)
        with completed_lock:
            completed_count += 1
            if on_image_started:
                on_image_started(completed_count - 1, images[idx].name)

    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_worker_wrapper, i) for i in range(len(cues))]
            for future in futures:
                future.result()
    else:
        for i in range(len(cues)):
            _worker_wrapper(i)

    concat_file = work_dir / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve().as_posix().replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n" for path in segment_paths),
        encoding="utf-8",
    )
    sfx_audio_path = None
    t_density = transition_sfx_density / 100.0 if transition_sfx_density > 1.0 else transition_sfx_density
    t_volume = transition_sfx_volume / 100.0 if transition_sfx_volume > 1.0 else transition_sfx_volume
    if sfx_paths and t_density > 0.01 and t_volume > 0.005:
        if on_stage_changed:
            on_stage_changed("Preparing image-change sounds...", 89)
        sfx_audio_path = work_dir / "image_change_sfx.wav"
        has_sfx = _create_sfx_track(
            ffmpeg_path,
            sfx_paths,
            cues,
            sfx_audio_path,
            cancel_event,
            transition_sfx_density=t_density,
            transition_sfx_volume=t_volume,
        )
        if not has_sfx:
            sfx_audio_path = None

    intensity_audio_path = None
    e_volume = emotion_sfx_volume / 100.0 if emotion_sfx_volume > 1.0 else emotion_sfx_volume
    if intensity_sfx_paths and intensity_mapping and e_volume > 0.005:
        if on_stage_changed:
            on_stage_changed("Preparing dialogue intensity sounds...", 88)
        intensity_audio_path = work_dir / "intensity_sfx.wav"
        has_intensity = _create_intensity_track(
            ffmpeg_path,
            intensity_sfx_paths,
            intensity_mapping,
            cues,
            intensity_audio_path,
            cancel_event,
            emotion_sfx_volume=e_volume,
        )
        if not has_intensity:
            intensity_audio_path = None

    popup_audio_path = None
    p_density = popup_sfx_density / 100.0 if popup_sfx_density > 1.0 else popup_sfx_density
    p_volume = popup_sfx_volume / 100.0 if popup_sfx_volume > 1.0 else popup_sfx_volume
    if popup_sfx_paths and popup_mapping and p_density > 0.01 and p_volume > 0.005:
        if on_stage_changed:
            on_stage_changed("Preparing popup sounds...", 89)
        popup_audio_path = work_dir / "popup_sfx.wav"
        has_popups = _create_popup_track(
            ffmpeg_path,
            popup_sfx_paths,
            popup_mapping,
            cues,
            popup_audio_path,
            cancel_event,
            popup_sfx_density=p_density,
            popup_sfx_volume=p_volume,
        )
        if not has_popups:
            popup_audio_path = None

    if on_stage_changed:
        on_stage_changed("Combining video segments...", 90)
    final_input_path = output_path if audio_path is None and sfx_audio_path is None and intensity_audio_path is None and popup_audio_path is None else work_dir / "slideshow_silent.mp4"
    _run_ffmpeg(
        [
            str(ffmpeg_path),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(final_input_path),
        ],
        cancel_event,
    )

    if audio_path is not None or sfx_audio_path is not None or intensity_audio_path is not None or popup_audio_path is not None:
        if on_stage_changed:
            on_stage_changed("Adding audio track...", 96)
        mux_command = [str(ffmpeg_path), "-y", "-i", str(final_input_path)]
        audio_inputs = []
        if audio_path is not None:
            mux_command.extend(["-stream_loop", "-1", "-i", str(audio_path)])
            audio_inputs.append((f"{len(audio_inputs)+1}:a", "voice"))
        if sfx_audio_path is not None:
            mux_command.extend(["-i", str(sfx_audio_path)])
            audio_inputs.append((f"{len(audio_inputs)+1}:a", "transition"))
        if intensity_audio_path is not None:
            mux_command.extend(["-i", str(intensity_audio_path)])
            audio_inputs.append((f"{len(audio_inputs)+1}:a", "intensity"))
        if popup_audio_path is not None:
            mux_command.extend(["-i", str(popup_audio_path)])
            audio_inputs.append((f"{len(audio_inputs)+1}:a", "popup"))
            
        if len(audio_inputs) > 1:
            filter_str = ""
            mix_inputs = []
            for i, (a_label, a_type) in enumerate(audio_inputs):
                vol = 1.0
                if a_type == "transition":
                    vol = max(0.0, float(t_volume))
                elif a_type == "intensity":
                    vol = max(0.0, float(e_volume))
                elif a_type == "popup":
                    vol = max(0.0, float(p_volume))
                filter_str += f"[{a_label}]aresample=48000,volume={vol:.3f}[a{i}];"
                mix_inputs.append(f"[a{i}]")
                
            filter_str += f"{''.join(mix_inputs)}amix=inputs={len(audio_inputs)}:duration=first:dropout_transition=0:normalize=0[aout]"
            mux_command.extend([
                "-filter_complex", filter_str,
                "-map", "0:v:0",
                "-map", "[aout]",
            ])
        else:
            a_label, a_type = audio_inputs[0]
            vol = 1.0
            if a_type == "transition":
                vol = max(0.0, float(t_volume))
            elif a_type == "intensity":
                vol = max(0.0, float(e_volume))
            elif a_type == "popup":
                vol = max(0.0, float(p_volume))
            if vol != 1.0:
                mux_command.extend([
                    "-filter_complex", f"[{a_label}]aresample=48000,volume={vol:.3f}[aout]",
                    "-map", "0:v:0",
                    "-map", "[aout]",
                ])
            else:
                mux_command.extend(["-map", "0:v:0", "-map", a_label])
            
        mux_command.extend([
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path),
        ])
        _run_ffmpeg(mux_command, cancel_event)


def _create_sfx_track(
    ffmpeg_path: Path,
    sfx_paths: list[Path],
    cues: list[Cue],
    output_path: Path,
    cancel_event: threading.Event | None = None,
    transition_sfx_density: float = 0.25,
    transition_sfx_volume: float = 0.15,
) -> bool:
    density = transition_sfx_density / 100.0 if transition_sfx_density > 1.0 else transition_sfx_density
    volume = transition_sfx_volume / 100.0 if transition_sfx_volume > 1.0 else transition_sfx_volume
    if density <= 0.01 or volume <= 0.005 or not sfx_paths or not cues:
        return False

    import random

    total_duration = sum(_duration_seconds(cues, index) for index in range(len(cues)))
    elapsed_ms = 0
    cue_sfx_mapping = []

    step = max(1, round(1.0 / max(density, 0.01)))
    last_sfx_index = None

    for index, cue in enumerate(cues):
        if index % step == 0:
            candidates = [i for i in range(len(sfx_paths)) if i != last_sfx_index] if (len(sfx_paths) > 1 and last_sfx_index is not None) else list(range(len(sfx_paths)))
            sfx_index = random.choice(candidates)
            last_sfx_index = sfx_index
            cue_sfx_mapping.append((sfx_index, elapsed_ms))
        elapsed_ms += round(_duration_seconds(cues, index) * 1_000)

    if not cue_sfx_mapping:
        return False

    BATCH_SIZE = 150
    batches = [cue_sfx_mapping[i:i+BATCH_SIZE] for i in range(0, len(cue_sfx_mapping), BATCH_SIZE)]
    batch_files = []

    for b_idx, batch in enumerate(batches):
        usage_counts = {}
        for sfx_idx, delay in batch:
            usage_counts[sfx_idx] = usage_counts.get(sfx_idx, 0) + 1
            
        filter_parts = []
        current_split_idx = {i: 0 for i in usage_counts.keys()}
        
        # We only pass paths that are actually used in this batch to keep command short!
        used_sfx_indices = sorted(list(usage_counts.keys()))
        sfx_input_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_sfx_indices)}
        
        for old_idx in used_sfx_indices:
            count = usage_counts[old_idx]
            new_idx = sfx_input_map[old_idx]
            if count == 1:
                filter_parts.append(f"[{new_idx}:a]anull[s{new_idx}_0];")
            elif count > 1:
                splits = "".join(f"[s{new_idx}_{j}]" for j in range(count))
                filter_parts.append(f"[{new_idx}:a]asplit={count}{splits};")

        delayed_labels = []
        for index, (sfx_idx, delay) in enumerate(batch):
            new_idx = sfx_input_map[sfx_idx]
            split_idx = current_split_idx[sfx_idx]
            current_split_idx[sfx_idx] += 1
            
            in_label = f"[s{new_idx}_{split_idx}]"
            out_label = f"[d{index}]"
            delayed_labels.append(out_label)
            filter_parts.append(f"{in_label}adelay={delay}|{delay}{out_label};")
            
        filter_parts.append(
            f"{''.join(delayed_labels)}amix=inputs={len(delayed_labels)}:duration=longest:dropout_transition=0:normalize=0,volume={volume:.3f}[aout]"
        )
        
        batch_out = output_path.with_name(f"temp_sfx_{b_idx}.wav")
        batch_files.append(batch_out)
        
        command = [str(ffmpeg_path), "-y"]
        for old_idx in used_sfx_indices:
            command.extend(["-i", str(sfx_paths[old_idx])])
            
        command.extend([
            "-filter_complex", "".join(filter_parts),
            "-map", "[aout]",
            "-t", f"{total_duration:.3f}",
            "-ar", "48000", "-ac", "2",
            str(batch_out)
        ])
        _run_ffmpeg(command, cancel_event)

    if len(batch_files) == 1:
        batch_files[0].replace(output_path)
    else:
        mix_cmd = [str(ffmpeg_path), "-y"]
        for bf in batch_files:
            mix_cmd.extend(["-i", str(bf)])
        mix_cmd.extend([
            "-filter_complex",
            f"amix=inputs={len(batch_files)}:duration=longest:dropout_transition=0:normalize=0",
            "-ar", "48000", "-ac", "2",
            str(output_path)
        ])
        _run_ffmpeg(mix_cmd, cancel_event)
        for bf in batch_files:
            try: bf.unlink()
            except: pass
    return True

def _create_intensity_track(
    ffmpeg_path: Path,
    intensity_sfx_paths: dict[str, Path],
    intensity_mapping: dict[int, str],
    cues: list[Cue],
    output_path: Path,
    cancel_event: threading.Event | None = None,
    emotion_sfx_volume: float = 0.15,
) -> bool:
    vol = emotion_sfx_volume / 100.0 if emotion_sfx_volume > 1.0 else emotion_sfx_volume
    if vol <= 0.005 or not intensity_sfx_paths or not intensity_mapping:
        return False

    total_duration = sum(_duration_seconds(cues, index) for index in range(len(cues)))
    elapsed_ms = 0
    cue_audio_mapping = []
    
    unique_paths = list(intensity_sfx_paths.values())
    path_to_idx = {p: i for i, p in enumerate(unique_paths)}
    
    lower_sfx_map = {k.lower(): v for k, v in intensity_sfx_paths.items()}
    stem_map = {Path(k).stem.lower(): v for k, v in intensity_sfx_paths.items()}
    for index, cue in enumerate(cues):
        label = intensity_mapping.get(index) or intensity_mapping.get(str(index))
        if label and str(label).lower() != "none":
            lbl_str = str(label).strip()
            path = (
                intensity_sfx_paths.get(lbl_str) or
                lower_sfx_map.get(lbl_str.lower()) or
                stem_map.get(Path(lbl_str).stem.lower())
            )
            if not path:
                import re
                clean_lbl = re.sub(r'[^a-zA-Z0-9]', '', lbl_str).lower()
                for k, p in lower_sfx_map.items():
                    clean_k = re.sub(r'[^a-zA-Z0-9]', '', k).lower()
                    if clean_lbl and (clean_lbl in clean_k or clean_k in clean_lbl):
                        path = p
                        break
            if path:
                idx = path_to_idx[path]
                cue_audio_mapping.append((idx, elapsed_ms))
                print(f"[SFX] Scheduled dialogue sound '{label}' ({path.name}) at {elapsed_ms}ms (cue {index})", flush=True)
            
        elapsed_ms += round(_duration_seconds(cues, index) * 1_000)

    if not cue_audio_mapping:
        print("[SFX] No dialogue sounds scheduled.", flush=True)
        return False

    print(f"[SFX] Building intensity audio track with {len(cue_audio_mapping)} triggers...", flush=True)

    BATCH_SIZE = 150
    batches = [cue_audio_mapping[i:i+BATCH_SIZE] for i in range(0, len(cue_audio_mapping), BATCH_SIZE)]
    batch_files = []

    for b_idx, batch in enumerate(batches):
        usage_counts = {}
        for idx, delay in batch:
            usage_counts[idx] = usage_counts.get(idx, 0) + 1
            
        filter_parts = []
        current_split_idx = {i: 0 for i in usage_counts.keys()}
        
        used_indices = sorted(list(usage_counts.keys()))
        input_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_indices)}
        
        for old_idx in used_indices:
            count = usage_counts[old_idx]
            new_idx = input_map[old_idx]
            if count == 1:
                filter_parts.append(f"[{new_idx}:a]anull[i{new_idx}_0];")
            elif count > 1:
                splits = "".join(f"[i{new_idx}_{j}]" for j in range(count))
                filter_parts.append(f"[{new_idx}:a]asplit={count}{splits};")

        delayed_labels = []
        for index, (idx, delay) in enumerate(batch):
            new_idx = input_map[idx]
            split_idx = current_split_idx[idx]
            current_split_idx[idx] += 1
            
            in_label = f"[i{new_idx}_{split_idx}]"
            out_label = f"[e{index}]"
            delayed_labels.append(out_label)
            filter_parts.append(f"{in_label}adelay={delay}|{delay}{out_label};")
            
        filter_parts.append(
            f"{''.join(delayed_labels)}amix=inputs={len(delayed_labels)}:duration=longest:dropout_transition=0:normalize=0,volume={vol:.3f}[aout]"
        )
        
        batch_out = output_path.with_name(f"temp_int_{b_idx}.wav")
        batch_files.append(batch_out)
        
        command = [str(ffmpeg_path), "-y"]
        for old_idx in used_indices:
            command.extend(["-i", str(unique_paths[old_idx])])
            
        command.extend([
            "-filter_complex", "".join(filter_parts),
            "-map", "[aout]",
            "-t", f"{total_duration:.3f}",
            "-ar", "48000", "-ac", "2",
            str(batch_out)
        ])
        _run_ffmpeg(command, cancel_event)

    if len(batch_files) == 1:
        batch_files[0].replace(output_path)
    else:
        mix_cmd = [str(ffmpeg_path), "-y"]
        for bf in batch_files:
            mix_cmd.extend(["-i", str(bf)])
        mix_cmd.extend([
            "-filter_complex",
            f"amix=inputs={len(batch_files)}:duration=longest:dropout_transition=0:normalize=0",
            "-ar", "48000", "-ac", "2",
            str(output_path)
        ])
        _run_ffmpeg(mix_cmd, cancel_event)
        for bf in batch_files:
            try: bf.unlink()
            except: pass
    return True

def _run_ffmpeg(command: list[str], cancel_event: threading.Event | None = None) -> None:
    import tempfile
    import os
    fd, log_path = tempfile.mkstemp(suffix=".log")
    with open(fd, 'w', encoding='utf-8') as log_file:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        while process.poll() is None:
            if cancel_event and cancel_event.is_set():
                process.terminate()
                process.wait()
                raise GenerationCanceled()
            try:
                process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                continue

    if process.returncode != 0:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            err = f.read()
        try:
            os.remove(log_path)
        except:
            pass
        raise RuntimeError(f"FFmpeg could not render this image or combine the video segments. Error: {err}")
    else:
        try:
            os.remove(log_path)
        except:
            pass


def _create_popup_track(
    ffmpeg_path: Path,
    popup_sfx_paths: list[Path],
    popup_mapping: dict[int, str],
    cues: list[Cue],
    output_path: Path,
    cancel_event: threading.Event | None = None,
    popup_sfx_density: float = 0.30,
    popup_sfx_volume: float = 0.25,
) -> bool:
    density = popup_sfx_density / 100.0 if popup_sfx_density > 1.0 else popup_sfx_density
    volume = popup_sfx_volume / 100.0 if popup_sfx_volume > 1.0 else popup_sfx_volume
    if density <= 0.01 or volume <= 0.005 or not popup_sfx_paths or not popup_mapping or not cues:
        return False

    total_duration = sum(_duration_seconds(cues, index) for index in range(len(cues)))
    elapsed_ms = 0
    cue_audio_mapping = []
    
    import random
    unique_paths = popup_sfx_paths
    step = max(1, round(1.0 / max(density, 0.01)))
    popup_count = 0
    last_popup_idx = None
    
    for index, cue in enumerate(cues):
        label = popup_mapping.get(index)
        if label and label != "none" and unique_paths:
            if popup_count % step == 0:
                candidates = [i for i in range(len(unique_paths)) if i != last_popup_idx] if (len(unique_paths) > 1 and last_popup_idx is not None) else list(range(len(unique_paths)))
                idx = random.choice(candidates)
                last_popup_idx = idx
                cue_audio_mapping.append((idx, elapsed_ms))
            popup_count += 1
            
        elapsed_ms += round(_duration_seconds(cues, index) * 1_000)

    if not cue_audio_mapping:
        return False

    BATCH_SIZE = 150
    batches = [cue_audio_mapping[i:i+BATCH_SIZE] for i in range(0, len(cue_audio_mapping), BATCH_SIZE)]
    batch_files = []

    for b_idx, batch in enumerate(batches):
        usage_counts = {}
        for idx, delay in batch:
            usage_counts[idx] = usage_counts.get(idx, 0) + 1
            
        filter_parts = []
        current_split_idx = {i: 0 for i in usage_counts.keys()}
        
        used_indices = sorted(list(usage_counts.keys()))
        input_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_indices)}
        
        for old_idx in used_indices:
            count = usage_counts[old_idx]
            new_idx = input_map[old_idx]
            if count == 1:
                filter_parts.append(f"[{new_idx}:a]anull[i{new_idx}_0];")
            elif count > 1:
                splits = "".join(f"[i{new_idx}_{j}]" for j in range(count))
                filter_parts.append(f"[{new_idx}:a]asplit={count}{splits};")

        delayed_labels = []
        for index, (idx, delay) in enumerate(batch):
            new_idx = input_map[idx]
            split_idx = current_split_idx[idx]
            current_split_idx[idx] += 1
            
            in_label = f"[i{new_idx}_{split_idx}]"
            out_label = f"[e{index}]"
            delayed_labels.append(out_label)
            filter_parts.append(f"{in_label}adelay={delay}|{delay}{out_label};")
            
        filter_parts.append(
            f"{''.join(delayed_labels)}amix=inputs={len(delayed_labels)}:duration=longest:dropout_transition=0:normalize=0,volume={volume:.3f}[aout]"
        )
        
        batch_out = output_path.with_name(f"temp_pop_{b_idx}.wav")
        batch_files.append(batch_out)
        
        command = [str(ffmpeg_path), "-y"]
        for old_idx in used_indices:
            command.extend(["-i", str(unique_paths[old_idx])])
            
        command.extend([
            "-filter_complex", "".join(filter_parts),
            "-map", "[aout]",
            "-t", f"{total_duration:.3f}",
            "-ar", "48000", "-ac", "2",
            str(batch_out)
        ])
        _run_ffmpeg(command, cancel_event)

    if len(batch_files) == 1:
        batch_files[0].replace(output_path)
    else:
        mix_cmd = [str(ffmpeg_path), "-y"]
        for bf in batch_files:
            mix_cmd.extend(["-i", str(bf)])
        mix_cmd.extend([
            "-filter_complex",
            f"amix=inputs={len(batch_files)}:duration=longest:dropout_transition=0:normalize=0",
            "-ar", "48000", "-ac", "2",
            str(output_path)
        ])
        _run_ffmpeg(mix_cmd, cancel_event)
        for bf in batch_files:
            try: bf.unlink()
            except: pass
    return True
