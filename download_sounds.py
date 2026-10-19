import urllib.request
import os

sounds = {
    "pop1.mp3": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_2d4d7a8d8e.mp3?filename=pop-39222.mp3",
    "pop2.mp3": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_3d1982b5fb.mp3?filename=bubble-sound-43207.mp3",
    "pop3.mp3": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_510a26e857.mp3?filename=pop-94319.mp3",
    "whoosh.mp3": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_27dccfe9de.mp3?filename=whoosh-6316.mp3"
}

os.makedirs("sfx/popups", exist_ok=True)
for name, url in sounds.items():
    try:
        urllib.request.urlretrieve(url, os.path.join("sfx/popups", name))
        print(f"Downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
