# SRT Slideshow Generator

Current version: `1.0.03`. App name, description, and version are centralized in `app_config.py`.

Portable Windows app that runs from `SRT_Video_Generator.bat`. It expects:

- `python\python.exe`: the embeddable Python distribution
- `ffmpeg\ffmpeg.exe`: the Windows FFmpeg executable
- Python packages from `requirements.txt`

## First run

Run `setup_portable_python.bat` once. It downloads the official Windows embeddable Python distribution into `python\` and installs the requirements there. No system-wide Python installation or virtual environment is used.

After setup completes, run `SRT_Video_Generator.bat`. The browser UI opens at `http://127.0.0.1:8765`.

## Manual setup

Install the requirements into the portable interpreter itself:

```bat
python\python.exe -m pip install -r requirements.txt
```

Then run `SRT_Video_Generator.bat`. The browser UI opens at `http://127.0.0.1:8765`.

Images are sorted by natural filename order before rendering, so names such as `1-001`, `1-002`, `1-010`, and `1-011` are placed in the expected numeric order. Each image begins at one SRT cue start time, and the final image remains visible for the final cue duration. An optional audio track can be added in MP3, WAV, M4A, AAC, FLAC, or OGG format. Shorter audio loops until the video ends; longer audio is trimmed to the video duration.

The video aspect ratio can be set to `16:9` landscape (`1920x1080` Full HD) or `9:16` portrait (`1080x1920`) before generation. The default is `16:9`.

Each image uses a subtle animated zoom between 100% and 105%. The zoom takes up to one second; images shown for less than one second use their full display time, while longer images hold the final zoom level afterward. The direction alternates between images so neighboring images zoom in and out.

The bundled `sfx\click.wav` sound can be enabled or disabled in the UI. When enabled, it plays whenever a new image begins. It can be mixed with the optional music or narration track.

The generated video uses the uploaded SRT filename, for example `captions.srt` becomes `captions.mp4`. When a new video generation starts, previous MP4 videos are removed from the `output` folder so only the latest generated video remains.
