import asyncio
from llm_analyzer import analyze_cues_intensity
from srt_parser import Cue
import json

cues = [
    Cue(1, 0, 1000, "I am so angry right now!"),
    Cue(2, 1000, 2000, "Just kidding, I am actually laughing."),
    Cue(3, 2000, 3000, "Wow, this is amazing!"),
    Cue(4, 3000, 4000, "I'm so sad it's over.")
]

api_key = "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"
labels = ["angry", "laugh", "sad"]

try:
    result = analyze_cues_intensity(cues, labels, api_key, "nvidia", "meta/llama-3.2-11b-vision-instruct")
    print("Result:", result)
except Exception as e:
    print("Error:", e)
