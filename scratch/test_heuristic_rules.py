import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
import re
from srt_parser import parse_srt

cues = parse_srt(Path("scratch/quentin.srt"))

# User's uploaded sounds
user_sfx = [
    '01 Boom', 'punch', 'Bruh Sound Effect', 'Disappointed', 'Minecraft Hurt',
    'Pop', 'Swoosh', 'Whoosh', 'OMG meme', 'kids yeyy', 'Cash Register',
    'crowd shocked', 'Wrong Answer', 'Confused Reverb', 'Clock Ticking Sound Effect',
    'Apple Notification', 'Applause', 'Ding Sound Effect', 'Awkward Pause',
    'Sudden suspense Sound effect', 'Heavy object Hit and body thud sound effect',
    'hmmm', 'good-idea', 'Nope sound effect', 'Glitch Sound Effect'
]

EMOTION_AND_SFX_RULES = [
    {
        "name": "guilt_sadness",
        "sound_keys": ["disappointed", "awww", "sad", "hurt", "thud"],
        "words": ["guilt", "guilty", "sad", "sadness", "cry", "crying", "tears", "sorrow", "grief", "pain", "loss", "tragic", "sob", "shame", "regret", "disappointed", "depressed"],
    },
    {
        "name": "failure_wrong",
        "sound_keys": ["wrong answer", "nope", "reboot failure", "disappointed", "hurt", "glitch"],
        "words": ["wrong", "fail", "failing", "failure", "failed", "mistake", "error", "blunder", "useless", "worthless", "loser", "ruined", "flaw", "defeat", "defeated"],
    },
    {
        "name": "confusion_question",
        "sound_keys": ["confused", "hmmm", "what", "mystery", "reverb"],
        "words": ["strange", "strangely", "curious", "mystery", "mysterious", "wonder", "wondering", "puzzling", "puzzle", "odd", "weird", "question", "questions", "secret", "secrets", "voice in your head", "inside your head"],
    },
    {
        "name": "awkward_pause",
        "sound_keys": ["awkward", "pause", "bruh", "cricket"],
        "words": ["awkward", "silence", "stare", "hesitate", "hesitation", "uncomfortable"],
    },
    {
        "name": "lazy_absurd",
        "sound_keys": ["bruh", "goofy", "bloop", "fart", "boing", "pop"],
        "words": ["lazy", "laziness", "slacker", "procrastinate", "procrastinating", "ridiculous", "absurd", "foolish", "joke", "funny"],
    },
    {
        "name": "phone_tech",
        "sound_keys": ["apple notification", "message sound", "iphone", "notification", "discord"],
        "words": ["phone", "screen", "scrolling", "notification", "message", "text", "app", "online", "internet"],
    },
    {
        "name": "time_pressure",
        "sound_keys": ["clock tick", "clock ticking", "tick", "ticking"],
        "words": ["wasting time", "wasting right now", "deadlines", "deadline", "hours", "minutes", "seconds", "clock", "ticking", "running out", "schedule", "too late", "hurry"],
    },
    {
        "name": "shock_surprise",
        "sound_keys": ["crowd shocked", "omg", "suspense", "shock", "surprise"],
        "words": ["suddenly", "sudden", "shock", "shocked", "shocking", "surprise", "surprised", "gasp", "unexpected", "unbelievable", "astonished", "whoa", "wow", "omg", "twist", "betray"],
    },
    {
        "name": "reward_success",
        "sound_keys": ["ding", "applause", "kids yeyy", "cash register", "cheer", "good-idea"],
        "words": ["praise", "praised", "reward", "rewarded", "achieve", "achievement", "achievements", "good grades", "success", "successful", "win", "winning", "earned", "responsible", "useful"],
    },
    {
        "name": "work_productivity",
        "sound_keys": ["keyboard", "typewriter", "paper", "data"],
        "words": ["working", "grind", "hustle", "productive", "productivity", "effort", "goals"],
    },
    {
        "name": "worry_anxiety",
        "sound_keys": ["sudden suspense", "tension", "drop disto", "dark drop", "upset pulses"],
        "words": ["worry", "worrying", "worried", "anxious", "anxiety", "fear", "scared", "stress", "stressed", "pressure", "panic", "dread", "nervous"],
    },
    {
        "name": "idea_realization",
        "sound_keys": ["good-idea", "ding", "bell", "pop"],
        "words": ["realize", "realized", "idea", "epiphany", "truth", "discover", "discovered", "understand", "learned", "explanation"],
    },
    {
        "name": "impact_hit",
        "sound_keys": ["punch", "hit", "thud", "impact", "slam", "boom"],
        "words": ["punch", "hit", "struck", "strike", "slam", "slapped", "crushed", "shattered", "collapsed", "died", "dead", "casualty", "heavy"],
    },
    {
        "name": "whoosh_motion",
        "sound_keys": ["whoosh", "swoosh", "swish", "swing"],
        "words": ["fast", "speed", "rush", "quick", "swift", "dash", "jump", "escape"],
    }
]

lower_sfx = {s.lower(): s for s in user_sfx}

def find_sound_by_keys(keys):
    for k in keys:
        k_lower = k.lower()
        for sfx_key, orig in lower_sfx.items():
            if k_lower in sfx_key or sfx_key in k_lower:
                return orig
    return None

rule_sound_map = []
for rule in EMOTION_AND_SFX_RULES:
    snd = find_sound_by_keys(rule["sound_keys"])
    if snd:
        rule_sound_map.append((rule["words"], snd))

mapping = {}
last_idx = -999
for idx, cue in enumerate(cues):
    if idx - last_idx < 2:
        continue
    cue_text = (cue.text or "").lower()
    for words, sound in rule_sound_map:
        if any(re.search(r'\b' + re.escape(w) + r'\b', cue_text) for w in words):
            mapping[idx] = sound
            last_idx = idx
            break

print(f"Total cues: {len(cues)}, Mapped triggers: {len(mapping)}")
for idx in sorted(mapping.keys()):
    print(f"Cue {idx} ({cues[idx].start_ms/1000:.1f}s): [{mapping[idx]}] -> {cues[idx].text}")
