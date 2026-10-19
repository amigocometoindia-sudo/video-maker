import re

with open('video_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

sfx_new = """def _create_sfx_track(
    ffmpeg_path: Path,
    sfx_paths: list[Path],
    cues: list[Cue],
    output_path: Path,
    cancel_event: threading.Event | None = None,
) -> None:
    import random

    total_duration = sum(_duration_seconds(cues, index) for index in range(len(cues)))
    elapsed_ms = 0
    cue_sfx_mapping = []

    for index, cue in enumerate(cues):
        sfx_index = random.choice(range(len(sfx_paths)))
        cue_sfx_mapping.append((sfx_index, elapsed_ms))
        elapsed_ms += round(_duration_seconds(cues, index) * 1_000)

    if not cue_sfx_mapping:
        return

    BATCH_SIZE = 150
    batches = [cue_sfx_mapping[i:i+BATCH_SIZE] for i in range(0, len(cue_sfx_mapping), BATCH_SIZE)]
    batch_files = []

    for b_idx, batch in enumerate(batches):
        usage_counts = {i: 0 for i in range(len(sfx_paths))}
        for sfx_idx, delay in batch:
            usage_counts[sfx_idx] += 1
            
        filter_parts = []
        current_split_idx = {i: 0 for i in range(len(sfx_paths))}
        
        for i in range(len(sfx_paths)):
            count = usage_counts[i]
            if count == 1:
                filter_parts.append(f"[{i}:a]anull[s{i}_0];")
            elif count > 1:
                splits = "".join(f"[s{i}_{j}]" for j in range(count))
                filter_parts.append(f"[{i}:a]asplit={count}{splits};")

        delayed_labels = []
        for index, (sfx_idx, delay) in enumerate(batch):
            split_idx = current_split_idx[sfx_idx]
            current_split_idx[sfx_idx] += 1
            
            in_label = f"[s{sfx_idx}_{split_idx}]"
            out_label = f"[d{index}]"
            delayed_labels.append(out_label)
            filter_parts.append(f"{in_label}adelay={delay}|{delay}{out_label};")
            
        filter_parts.append(
            f"{''.join(delayed_labels)}amix=inputs={len(delayed_labels)}:duration=longest:dropout_transition=0:normalize=0,volume=0.15[aout]"
        )
        
        batch_out = output_path.with_name(f"temp_sfx_{b_idx}.wav")
        batch_files.append(batch_out)
        
        command = [str(ffmpeg_path), "-y"]
        for path in sfx_paths:
            command.extend(["-i", str(path)])
            
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
"""

content = re.sub(r'def _create_sfx_track\(.*?(?=def _create_intensity_track)', sfx_new + '\n', content, flags=re.DOTALL)

intensity_new = """def _create_intensity_track(
    ffmpeg_path: Path,
    intensity_sfx_paths: dict[str, Path],
    intensity_mapping: dict[int, str],
    cues: list[Cue],
    output_path: Path,
    cancel_event: threading.Event | None = None,
) -> bool:
    total_duration = sum(_duration_seconds(cues, index) for index in range(len(cues)))
    elapsed_ms = 0
    cue_audio_mapping = []
    
    unique_paths = list(intensity_sfx_paths.values())
    path_to_idx = {p: i for i, p in enumerate(unique_paths)}
    
    for index, cue in enumerate(cues):
        label = intensity_mapping.get(index)
        if label and label in intensity_sfx_paths:
            path = intensity_sfx_paths[label]
            idx = path_to_idx[path]
            cue_audio_mapping.append((idx, elapsed_ms))
            
        elapsed_ms += round(_duration_seconds(cues, index) * 1_000)

    if not cue_audio_mapping:
        return False

    BATCH_SIZE = 150
    batches = [cue_audio_mapping[i:i+BATCH_SIZE] for i in range(0, len(cue_audio_mapping), BATCH_SIZE)]
    batch_files = []

    for b_idx, batch in enumerate(batches):
        usage_counts = {i: 0 for i in range(len(unique_paths))}
        for idx, delay in batch:
            usage_counts[idx] += 1
            
        filter_parts = []
        current_split_idx = {i: 0 for i in range(len(unique_paths))}
        
        for i in range(len(unique_paths)):
            count = usage_counts[i]
            if count == 1:
                filter_parts.append(f"[{i}:a]anull[i{i}_0];")
            elif count > 1:
                splits = "".join(f"[i{i}_{j}]" for j in range(count))
                filter_parts.append(f"[{i}:a]asplit={count}{splits};")

        delayed_labels = []
        for index, (idx, delay) in enumerate(batch):
            split_idx = current_split_idx[idx]
            current_split_idx[idx] += 1
            
            in_label = f"[i{idx}_{split_idx}]"
            out_label = f"[e{index}]"
            delayed_labels.append(out_label)
            filter_parts.append(f"{in_label}adelay={delay}|{delay}{out_label};")
            
        filter_parts.append(
            f"{''.join(delayed_labels)}amix=inputs={len(delayed_labels)}:duration=longest:dropout_transition=0:normalize=0,volume=0.15[aout]"
        )
        
        batch_out = output_path.with_name(f"temp_int_{b_idx}.wav")
        batch_files.append(batch_out)
        
        command = [str(ffmpeg_path), "-y"]
        for path in unique_paths:
            command.extend(["-i", str(path)])
            
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
"""

content = re.sub(r'def _create_intensity_track\(.*?(?=def _run_ffmpeg)', intensity_new + '\n', content, flags=re.DOTALL)

with open('video_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
