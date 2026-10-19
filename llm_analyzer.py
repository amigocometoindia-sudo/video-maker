import json
import time
import re
import hashlib
import os
import io
import base64
from pathlib import Path
from PIL import Image

CACHE_DIR = Path("ai_cache")
CACHE_DIR.mkdir(exist_ok=True)

def _get_cache_path(chunk_text, prompt_type, extra_key=""):
    combined = f"{chunk_text}_{prompt_type}_{extra_key}"
    content_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
    return CACHE_DIR / f"{prompt_type}_{content_hash}.json"

def _resolve_sfx_match(val: str, available_labels: list[str]) -> str | None:
    if not val or not isinstance(val, str):
        return None
    val_clean = val.strip()
    if val_clean.lower() in ("none", "null", "false", "no", "n/a", "none.", ""):
        return None
        
    val_lower = val_clean.lower()
    
    # 1. Exact match
    for lbl in available_labels:
        if val_clean == lbl:
            return lbl
            
    # 2. Case-insensitive exact match
    for lbl in available_labels:
        if val_lower == lbl.lower():
            return lbl
            
    # 3. Cleaned alphanumeric match
    def clean_text(s):
        return re.sub(r'[^a-zA-Z0-9\s]', ' ', s).strip().lower()
        
    v_norm = clean_text(val_clean)
    for lbl in available_labels:
        if v_norm == clean_text(lbl):
            return lbl
            
    # 4. Substring containment match (e.g. 'whoosh' in 'Rake Swing Whoosh Close')
    for lbl in available_labels:
        lbl_norm = clean_text(lbl)
        if v_norm and (v_norm in lbl_norm or lbl_norm in v_norm):
            return lbl
            
    # 5. Word overlap match
    val_words = set(v_norm.split()) - {"sound", "sfx", "audio", "effect", "the", "a"}
    best_match = None
    max_overlap = 0
    for lbl in available_labels:
        lbl_words = set(clean_text(lbl).split()) - {"sound", "sfx", "audio", "effect", "the", "a"}
        overlap = len(val_words & lbl_words)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = lbl
            
    if max_overlap > 0:
        return best_match

    # 6. Semantic Category / Emotion to sound file mapping
    SEMANTIC_EMOTION_MAP = {
        'angry': ['angry', 'rage', 'mad', 'furious', 'growl', 'snarl', 'punch', 'hit', 'slam', 'boom', 'impact', 'thud', 'dramatic_impact', '01 boom'],
        'sad': ['sad', 'disappointed', 'cry', 'crying', 'tears', 'sorrow', 'grief', 'hurt', 'loss', 'awww', 'sigh', 'thud', 'tragic', 'sob', 'shame', 'regret', 'minecraft hurt', 'dramatic_impact'],
        'happy': ['happy', 'joy', 'excited', 'yay', 'yeyy', 'applause', 'cheer', 'celebrate', 'ding', 'win', 'glory', 'glad', 'kids yeyy', 'victory_cheer', 'royal_fanfare', 'good-idea'],
        'laugh': ['laugh', 'laughter', 'funny', 'joke', 'goofy', 'bruh', 'giggle', 'bloop', 'fart', 'boing', 'pop', 'chuckle', 'haha', 'meme', 'comedy', 'comic_boing', 'cartoon_boing', 'humor'],
        'shock': ['shock', 'shocked', 'surprise', 'surprised', 'omg', 'gasp', 'suspense', 'confused', 'reverb', 'whoa', 'wow', 'sudden', 'crowd shocked', 'omg meme', 'comic_boing', 'tension_hit'],
        'fear': ['fear', 'scared', 'horror', 'terrified', 'creepy', 'spooky', 'dread', 'panic', 'scream', 'screaming', 'nightmare', 'tension_hit', 'dramatic_impact', 'minecraft hurt'],
        'confused': ['confused', 'question', 'mystery', 'secret', 'strange', 'wonder', 'reverb', 'hmmm', 'what', 'curious', 'voice', 'confused reverb', '_what_'],
        'fail': ['fail', 'failing', 'failure', 'wrong', 'error', 'nope', 'reboot failure', 'defeat', 'lost', 'disappointed', 'casualty', 'wrong answer', 'nope sound effect', 'thud'],
        'guilt': ['guilt', 'guilty', 'disappointed', 'awww', 'wrong answer', 'sad', 'awkward', 'thud'],
        'awkward': ['awkward', 'pause', 'cricket', 'silence', 'disappointed', 'bruh', 'awkward pause', 'bruh sound effect'],
        'lazy': ['lazy', 'slacker', 'procrastinate', 'bruh', 'goofy', 'fart', 'boing', 'pop', 'cartoon fart'],
        'money': ['cash', 'coin', 'money', 'register', 'gold', 'ting', 'rich', 'wealth', 'tax', 'cash register', 'cash ting', 'coin_ding'],
        'tension': ['tension', 'suspense', 'heartbeat', 'dark', 'drop', 'danger', 'creepy', 'threat', 'trap', 'ambush', 'tension_hit', 'sudden suspense', 'dark drop'],
        'impact': ['punch', 'hit', 'strike', 'slap', 'smack', 'slam', 'impact', 'thud', 'bonk', 'bamboo', 'crash', 'dramatic_impact', 'sword_clash', 'bamboo hit', 'heavy object hit'],
        'explosion': ['boom', 'explosion', 'blast', 'bomb', 'cannon', 'burst', 'cannon_boom', '01 boom', 'dramatic_impact'],
        'whoosh': ['whoosh', 'swoosh', 'swish', 'rush', 'swing', 'speed', 'fast', 'dash', 'cinematic_whoosh', 'fast whoosh'],
        'success': ['success', 'ding', 'correct', 'achievement', 'win', 'notification', 'applause', 'cheer', 'ding sound effect', 'applause', 'kids yeyy'],
        'phone': ['phone', 'screen', 'notification', 'message', 'text', 'app', 'apple notification', 'message sound', 'iphone', 'discord'],
        'clock': ['clock', 'tick', 'ticking', 'time', 'waiting', 'deadlines', 'clock tick', 'clock ticking'],
        'glitch': ['glitch', 'error', 'static', 'hack', 'corrupt', 'glitch sound effect'],
        'camera': ['camera', 'shutter', 'click', 'photo', 'camera shutter', 'camera-shutter', 'click']
    }

    for cat, aliases in SEMANTIC_EMOTION_MAP.items():
        if v_norm == cat or any(a in v_norm or v_norm in a for a in aliases):
            for a in aliases:
                for lbl in available_labels:
                    if a in lbl.lower():
                        return lbl
    return None
        
def _generate_with_retry(model, prompt, max_retries=3):
    import google.generativeai as genai
    for attempt in range(max_retries):
        try:
            return model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json")
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                match = re.search(r"retry in ([\d\.]+)s", error_str)
                wait_time = float(match.group(1)) + 1 if match else 30
                time.sleep(wait_time)
            else:
                raise

def _call_llm_api(prompt, provider, api_key, api_model=None):
    print("Sending chunk to AI...", flush=True)
    import httpx
    strict_timeout = httpx.Timeout(12.0, connect=5.0, read=12.0, write=5.0)

    if provider.lower() == "openai":
        import openai
        client = openai.OpenAI(api_key=api_key, timeout=strict_timeout)
        target_model = api_model if api_model else "gpt-4o-mini"
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    elif provider.lower() == "nvidia":
        import openai
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
            timeout=strict_timeout
        )
        response = client.chat.completions.create(
            model="meta/llama-3.2-11b-vision-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    elif provider.lower() == "bytez":
        import openai
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.bytez.com/models/v2/openai/v1",
            default_headers={"Authorization": f"Key {api_key}"},
            timeout=strict_timeout
        )
        
        model_id = api_model if api_model else "meta-llama/Meta-Llama-3-8B-Instruct"
            
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    else:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = _generate_with_retry(model, prompt)
        return response.text

POPUP_SEMANTIC_KEYWORDS = {
    "stickman_king": [
        "king", "kings", "queen", "queens", "emperor", "emperors", "empire", "empires", "crown", "crowned",
        "throne", "ruler", "rulers", "rule", "ruled", "monarch", "monarchy", "prince", "dynasty", "reign",
        "leader", "leaders", "palace", "coronation", "sovereign", "caesar", "sultan", "tsar", "czar", "royal"
    ],
    "stickman_battle": [
        "battle", "battles", "fight", "fighting", "clash", "clashed", "combat", "duel", "skirmish", "swords",
        "war", "strike", "frontline", "weapon", "weapons"
    ],
    "stickman_soldier_blue": [
        "army", "armies", "soldiers", "soldier", "troops", "infantry", "marching", "patrol", "allies", "forces", "regiment"
    ],
    "stickman_soldier_red": [
        "enemy", "enemies", "rival", "rivals", "british", "foes", "redcoats", "opposition", "rebellion", "crusade"
    ],
    "stickman_dead": [
        "death", "dead", "die", "died", "dying", "kill", "killed", "kills", "casualty", "casualties",
        "plague", "famine", "disease", "poison", "poisoned", "defeat", "defeated", "loss", "lost",
        "murder", "murdered", "slain", "grave", "fatal", "perish", "perished", "fallen", "execute"
    ],
    "stickman_shocked": [
        "sudden", "suddenly", "surprise", "surprised", "shock", "shocked", "shocking", "unexpected",
        "unexpectedly", "betray", "betrayed", "betrayal", "twist", "unbelievable",
        "astonishing", "treason", "conspiracy", "plot"
    ],
    "stickman_confused": [
        "why", "how", "what", "mystery", "mysterious", "question", "questions", "secret", "secrets",
        "unknown", "wonder", "wondered", "puzzle", "puzzling", "curious", "who", "strange"
    ],
    "stickman_money": [
        "gold", "wealth", "wealthy", "rich", "riches", "treasure", "treasures", "coin", "coins", "silver",
        "money", "trade", "traded", "trading", "merchant", "merchants", "taxes", "tax", "prosper", "fortune",
        "economy", "economic", "commerce", "richer"
    ],
    "map_arrow_red": [
        "invade", "invaded", "invasion", "advance", "advanced", "conquest", "conquered", "expand",
        "expanded", "expansion", "territory", "borders", "frontier", "retreat", "flee", "fled", "direction"
    ],
    "map_arrow_blue": [
        "defend", "defense", "defended", "counterattack", "relief", "navy", "fleet", "sail", "sea", "islands"
    ],
    "speech_bubble": [
        "said", "declared", "announced", "replied", "speech", "proclaimed", "demand", "demanded", "treaty", "signed"
    ],
    "swords": [
        "war", "battle", "fight", "clash", "swords", "weapon", "arms"
    ],
    "king": [
        "king", "crown", "emperor", "throne", "ruler", "monarch"
    ],
    "fire": [
        "fire", "burn", "burned", "burning", "ruin", "ruins", "ruined", "destroy", "destroyed", "destruction",
        "sack", "sacked", "blaze", "flame", "flames", "ash", "ashes", "collapse", "collapsed", "explosion",
        "exploded", "torched", "devastated"
    ],
    "skull": [
        "death", "dead", "die", "died", "kill", "defeat", "slain"
    ],
    "gold": [
        "gold", "wealth", "rich", "treasure", "money", "tax"
    ],
}

CHARACTER_ACTION_KEYWORDS = {
    # Psychology & Mental Health (Overthinking, anxiety, brain, ideas)
    "thinking": ["thinking", "think", "thinks", "thought", "thoughts", "overthink", "overthinking", "ponder", "wonder", "wondering", "mind", "contemplate", "doubt", "doubts", "question", "questioning", "curious", "head", "reflection", "reflect"],
    "stress": ["stress", "stressed", "stressful", "anxiety", "anxious", "panic", "panicking", "panicked", "overwhelmed", "nervous", "fear", "afraid", "worry", "worried", "worrying", "scared", "insomnia", "dread", "nightmare", "crisis"],
    "idea": ["idea", "ideas", "eureka", "solution", "solutions", "realized", "realization", "discovered", "discovery", "breakthrough", "genius", "smart", "clever", "invented", "invention", "insight", "lightbulb", "inspired"],
    "brain": ["brain", "brains", "amygdala", "cortex", "neuron", "neurons", "neuroscience", "psychology", "psychologist", "dopamine", "cognitive", "mental", "habit", "habits", "memory", "subconscious"],
    "sleep": ["sleep", "sleeping", "asleep", "bed", "night", "insomnia", "tired", "exhausted", "exhaustion", "burnout", "dream", "dreams", "wake", "waking", "rest"],

    # Business, Tech & Wealth (Elon Musk, billionaire, startups, rockets)
    "money": ["gold", "money", "wealth", "wealthy", "rich", "richest", "billionaire", "billionaires", "millionaire", "cash", "dollars", "fortune", "profit", "profits", "invest", "invested", "investor", "stocks", "shares", "crypto", "bitcoin", "revenue", "bank", "capital", "fund", "funds", "tax", "taxes"],
    "business": ["business", "company", "companies", "startup", "startups", "founded", "founder", "ceo", "boss", "executive", "empire", "corporation", "deal", "deals", "contract", "hired", "work", "working", "office", "career", "industry", "trade", "merchant"],
    "tech": ["tech", "technology", "rocket", "rockets", "spacex", "space", "launch", "launched", "mars", "orbit", "tesla", "car", "cars", "electric", "code", "coding", "software", "internet", "computer", "algorithm", "ai", "robot", "factory"],

    # Anthropology & Prehistory (Ancient humans, survival, hunting, fire)
    "prehistoric": ["ancient human", "early human", "prehistoric", "caveman", "neanderthal", "homo sapiens", "stone age", "ancestor", "ancestors", "tribe", "tribal", "primal", "primitive", "hunter", "gatherer", "nomad", "mammoth", "flint", "spear"],
    "fire": ["fire", "flame", "flames", "torch", "burn", "burning", "sparks", "warmth", "cook", "cooking", "stone tool", "tools", "axe", "wheel", "craft"],

    # Classic Action & Dramatic Categories
    "attack": ["attack", "assault", "strike", "fight", "fighting", "battle", "swords", "charge", "slashed", "war", "clash", "clashed", "conquer", "hit", "invade", "invasion"],
    "speech": ["said", "spoke", "speech", "speaking", "declared", "proclaimed", "announced", "decree", "decreed", "demanded", "preached", "called", "tell", "stated", "warned"],
    "king": ["king", "queen", "emperor", "throne", "crown", "pope", "palace", "ruler", "monarch", "lord", "empire", "reign"],
    "monk": ["church", "priest", "monk", "pope", "bishop", "temple", "holy", "crusade", "crusader", "faith", "pray", "prayed", "praying", "god"],
    "shock": ["shock", "shocked", "sudden", "suddenly", "surprise", "surprised", "unexpected", "betray", "betrayal", "twist", "gasp", "disaster", "ambush"],
    "defeat": ["dead", "died", "death", "kill", "killed", "defeat", "defeated", "fallen", "slain", "casualty", "collapse", "collapsed", "sad", "tears", "cry", "crying", "ruin"],
    "march": ["march", "marched", "marching", "advance", "advanced", "walk", "walked", "journey", "ride", "cavalry", "travel", "fleet", "sail"],
    "cheer": ["victory", "victorious", "cheer", "cheered", "celebrate", "celebrated", "celebration", "triumph", "triumphant", "won", "win", "glory", "joy"],
    "confused": ["confused", "confusion", "mystery", "mysterious", "strange", "bizarre", "weird", "puzzle", "puzzled", "why", "how", "secret"],
}

ACTION_FALLBACK_LABELS = {
    "thinking": ["confused", "question", "speech_bubble", "shocked"],
    "stress": ["shocked", "confused", "dead", "fire"],
    "idea": ["gold", "king", "speech_bubble"],
    "brain": ["question", "confused", "king"],
    "sleep": ["dead", "confused"],
    "money": ["money", "gold", "king"],
    "business": ["money", "king", "speech_bubble"],
    "tech": ["gold", "fire", "arrow_blue"],
    "prehistoric": ["fire", "soldier_blue", "battle"],
    "fire": ["fire", "battle"],
    "confused": ["confused", "question", "shocked"],
    "cheer": ["gold", "king", "victory", "celebrate"],
    "monk": ["king", "priest", "speech"],
    "speech": ["king", "speech_bubble", "speech"],
    "march": ["soldier_blue", "soldier_red", "soldier"],
    "defeat": ["dead", "skull"],
    "shock": ["shocked", "confused", "surprise", "question"],
    "attack": ["battle", "swords", "soldier_red", "soldier_blue"],
}

def heuristic_popup_mapping(cues, popup_labels: list[str]) -> dict[int, str]:
    """Smart heuristic matcher for character action PNGs and popups with natural dialogue-driven pacing."""
    if not popup_labels or not cues:
        return {}

    mapping = {}
    lower_labels = {lbl.lower(): lbl for lbl in popup_labels}
    prev_match = None

    used_labels = set()

    # Pre-parse character labels into token lists
    label_tokens = {}
    for lbl in popup_labels:
        clean = re.sub(r'[^a-zA-Z0-9]', ' ', lbl).lower()
        tokens = [t for t in clean.split() if len(t) > 2 and t not in ("png", "jpg", "jpeg", "webp", "custom", "character", "stickman")]
        label_tokens[lbl] = tokens

    for idx, cue in enumerate(cues):
        cue_text = (cue.text or "").lower()
        best_match = None
        best_score = 0

        # 1. Match against Character Action rules (highest score for direct character file matches)
        for action_cat, act_words in CHARACTER_ACTION_KEYWORDS.items():
            if any(re.search(r'\b' + re.escape(w) + r'\b', cue_text) for w in act_words):
                for lbl, toks in label_tokens.items():
                    if lbl not in used_labels and (action_cat in lbl.lower() or any(t in act_words for t in toks)):
                        score = 3
                        if score > best_score:
                            best_score = score
                            best_match = lbl
                            break

        # 2. Direct token overlap match with custom character filenames
        for lbl, toks in label_tokens.items():
            if lbl not in used_labels:
                matched_toks = sum(1 for t in toks if re.search(r'\b' + re.escape(t) + r'\b', cue_text))
                if matched_toks > 0 and (matched_toks * 2) > best_score:
                    best_score = matched_toks * 2
                    best_match = lbl

        # 3. Action fallback labels (e.g. cheer -> gold/king, monk -> king/priest)
        if not best_match:
            for action_cat, act_words in CHARACTER_ACTION_KEYWORDS.items():
                if any(re.search(r'\b' + re.escape(w) + r'\b', cue_text) for w in act_words):
                    fallbacks = ACTION_FALLBACK_LABELS.get(action_cat, [])
                    for fb in fallbacks:
                        matched_fb = (
                            lower_labels.get(fb) or
                            lower_labels.get(f"stickman_{fb}") or
                            lower_labels.get(fb.replace("stickman_", ""))
                        )
                        if matched_fb and matched_fb not in used_labels:
                            best_match = matched_fb
                            break
                    if best_match:
                        break

        # 4. Fallback to existing POPUP_SEMANTIC_KEYWORDS
        if not best_match:
            for label_key, keywords in POPUP_SEMANTIC_KEYWORDS.items():
                matched_lbl = (
                    lower_labels.get(label_key) or
                    lower_labels.get(label_key.replace("stickman_", "")) or
                    lower_labels.get(f"stickman_{label_key}")
                )
                if matched_lbl and matched_lbl not in used_labels:
                    if any(re.search(r'\b' + re.escape(kw) + r'\b', cue_text) for kw in keywords):
                        best_match = matched_lbl
                        break

        if best_match and best_match not in used_labels:
            mapping[idx] = best_match
            prev_match = best_match
            used_labels.add(best_match)

    # Ensure ALL available popup assets are used AT MOST ONCE with ZERO looping:
    unused_labels = [lbl for lbl in popup_labels if lbl not in used_labels]
    if unused_labels:
        def nat_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        sorted_unused = sorted(unused_labels, key=nat_sort_key)
        
        target_indices = []
        last_added = -3
        for idx, cue in enumerate(cues):
            text = (cue.text or "").strip()
            if idx in mapping:
                last_added = idx
                continue
            # Natural dialogue pacing: animate character every 2-3 cues on substantial lines
            if idx - last_added >= 2 and len(text.split()) >= 3:
                target_indices.append(idx)
                last_added = idx

        # If not enough candidate cues with >=2 spacing, loosen to empty cues
        if len(target_indices) < len(sorted_unused):
            for idx in range(len(cues)):
                if idx not in mapping and idx not in target_indices:
                    target_indices.append(idx)
            target_indices.sort()

        # Assign each unused asset to an empty cue (strictly single-use per asset)
        for step, unassigned in enumerate(sorted_unused):
            if step < len(target_indices):
                target_cue = target_indices[step]
                mapping[target_cue] = unassigned
                used_labels.add(unassigned)

    print(f"[Dialogue Character Director] Intelligently placed {len(mapping)} single-use character actions across {len(cues)} cues (all unique, zero loops): {list(mapping.values())[:8]}...", flush=True)
    return mapping


EMOTION_AND_SFX_RULES = [
    {
        "name": "guilt_sadness",
        "sound_keys": ["disappointed", "awww", "sad", "hurt", "thud"],
        "words": ["guilt", "guilty", "sad", "sadness", "cry", "crying", "tears", "sorrow", "grief", "pain", "loss", "tragic", "sob", "shame", "regret", "disappointed", "depressed"],
        "fallback_sound_keys": ["dramatic_impact", "thud"],
    },
    {
        "name": "failure_wrong",
        "sound_keys": ["wrong answer", "nope", "reboot failure", "disappointed", "hurt", "glitch"],
        "words": ["wrong", "fail", "failing", "failure", "failed", "mistake", "error", "blunder", "useless", "worthless", "loser", "ruined", "flaw", "defeat", "defeated"],
        "fallback_sound_keys": ["dramatic_impact", "thud"],
    },
    {
        "name": "confusion_question",
        "sound_keys": ["confused", "hmmm", "what", "mystery", "reverb"],
        "words": ["strange", "strangely", "curious", "mystery", "mysterious", "wonder", "wondering", "puzzling", "puzzle", "odd", "weird", "question", "questions", "secret", "secrets", "voice in your head", "inside your head"],
        "fallback_sound_keys": ["comic_boing", "tension_hit"],
    },
    {
        "name": "awkward_pause",
        "sound_keys": ["awkward", "pause", "bruh", "cricket"],
        "words": ["awkward", "silence", "stare", "hesitate", "hesitation", "uncomfortable"],
        "fallback_sound_keys": ["thud"],
    },
    {
        "name": "lazy_absurd",
        "sound_keys": ["bruh", "goofy", "bloop", "fart", "boing", "pop"],
        "words": ["lazy", "laziness", "slacker", "procrastinate", "procrastinating", "ridiculous", "absurd", "foolish", "joke", "funny"],
        "fallback_sound_keys": ["comic_boing", "cartoon_boing"],
    },
    {
        "name": "phone_tech",
        "sound_keys": ["apple notification", "message sound", "iphone", "notification", "discord"],
        "words": ["phone", "screen", "scrolling", "notification", "message", "text", "app", "online", "internet"],
        "fallback_sound_keys": ["coin_ding"],
    },
    {
        "name": "time_pressure",
        "sound_keys": ["clock tick", "clock ticking", "tick", "ticking"],
        "words": ["wasting time", "wasting right now", "deadlines", "deadline", "hours", "minutes", "seconds", "clock", "ticking", "running out", "schedule", "too late", "hurry"],
        "fallback_sound_keys": ["taiko_drum", "tension_hit"],
    },
    {
        "name": "shock_surprise",
        "sound_keys": ["crowd shocked", "omg", "suspense", "shock", "surprise"],
        "words": ["suddenly", "sudden", "shock", "shocked", "shocking", "surprise", "surprised", "gasp", "unexpected", "unbelievable", "astonished", "whoa", "wow", "omg", "twist", "betray"],
        "fallback_sound_keys": ["comic_boing", "tension_hit", "dramatic_impact"],
    },
    {
        "name": "reward_success",
        "sound_keys": ["ding", "applause", "kids yeyy", "cash register", "cheer", "good-idea"],
        "words": ["praise", "praised", "reward", "rewarded", "achieve", "achievement", "achievements", "good grades", "success", "successful", "win", "winning", "earned", "responsible", "useful"],
        "fallback_sound_keys": ["victory_cheer", "royal_fanfare", "coin_ding"],
    },
    {
        "name": "productivity_work",
        "sound_keys": ["keyboard", "typewriter", "paper", "data"],
        "words": ["working", "grind", "hustle", "productive", "productivity", "effort", "goals"],
        "fallback_sound_keys": ["taiko_drum"],
    },
    {
        "name": "worry_anxiety",
        "sound_keys": ["sudden suspense", "tension", "drop disto", "dark drop", "upset pulses"],
        "words": ["worry", "worrying", "worried", "anxious", "anxiety", "fear", "scared", "stress", "stressed", "pressure", "panic", "dread", "nervous"],
        "fallback_sound_keys": ["tension_hit", "dramatic_impact"],
    },
    {
        "name": "idea_realization",
        "sound_keys": ["good-idea", "ding", "bell", "pop"],
        "words": ["realize", "realized", "idea", "epiphany", "truth", "discover", "discovered", "understand", "learned", "explanation"],
        "fallback_sound_keys": ["coin_ding"],
    },
    {
        "name": "angry",
        "sound_keys": ["angry", "rage", "mad", "growl", "fury", "yell", "snarl"],
        "words": ["angry", "mad", "rage", "furious", "fury", "yell", "annoyed", "hate", "irritated", "outraged", "wrath", "revenge", "threat", "threatened", "curse", "cursed", "punish"],
        "fallback_sound_keys": ["dramatic_impact", "tension_hit"],
    },
    {
        "name": "sad",
        "sound_keys": ["sad", "cry", "crying", "tears", "sorrow", "grief", "mourn", "mourning", "heartbroken", "depressed", "weep", "weeping", "lament"],
        "words": ["sad", "cry", "crying", "tears", "sorrow", "grief", "mourn", "mourning", "heartbroken", "depressed", "pain", "weep", "weeping", "lament", "loss", "tragic", "tragedy", "sob", "sobbing"],
        "fallback_sound_keys": ["dramatic_impact", "thud"],
    },
    {
        "name": "happy",
        "sound_keys": ["happy", "joy", "cheerful", "yay", "celebrate", "celebration", "glad"],
        "words": ["happy", "joy", "joyful", "excited", "fun", "glad", "smile", "smiling", "cheerful", "celebrate", "celebrating", "celebration", "yay", "blessed", "delight", "cheer", "cheering", "party"],
        "fallback_sound_keys": ["victory_cheer", "royal_fanfare", "coin_ding"],
    },
    {
        "name": "laugh",
        "sound_keys": ["laugh", "laughter", "giggle", "chuckle", "comic_boing", "cartoon_boing", "boing"],
        "words": ["laugh", "laughing", "laughter", "funny", "chuckle", "giggle", "joke", "joking", "hilarious", "haha", "ridiculous", "fool", "foolish", "comedy", "absurd", "blunder"],
        "fallback_sound_keys": ["comic_boing", "cartoon_boing"],
    },
    {
        "name": "fear",
        "sound_keys": ["fear", "scared", "horror", "terrified", "spooky", "screaming", "scream", "creepy"],
        "words": ["fear", "scared", "horror", "terrified", "creepy", "spooky", "dread", "panic", "frightened", "ghost", "monster", "nightmare", "shiver", "tremble", "screaming", "scream"],
        "fallback_sound_keys": ["tension_hit", "dramatic_impact"],
    },
    {
        "name": "love",
        "sound_keys": ["love", "romantic", "kiss", "heart"],
        "words": ["love", "loving", "romantic", "romance", "sweetheart", "kiss", "kissed", "beloved", "darling", "passion"],
        "fallback_sound_keys": ["royal_fanfare", "coin_ding"],
    },
    {
        "name": "impact",
        "sound_keys": ["punch", "hit", "slap", "thud", "strike", "dramatic_impact", "impact", "knock"],
        "words": ["punch", "punched", "hit", "strike", "struck", "slap", "slapped", "knock", "knocked", "beat", "thud", "smack", "slam", "crash", "crashed", "impact", "crush", "crushed", "brawl", "smash"],
        "fallback_sound_keys": ["dramatic_impact", "sword_clash", "thud"],
    },
    {
        "name": "explosion",
        "sound_keys": ["cannon_boom", "cannon", "explosion", "boom", "blast", "bomb"],
        "words": ["cannon", "cannons", "artillery", "bomb", "bombs", "bombed", "explosion", "explode", "exploded", "boom", "blast", "blasted", "fire", "burned", "burning", "ruin", "burst"],
        "fallback_sound_keys": ["cannon_boom", "dramatic_impact"],
    },
    {
        "name": "whoosh",
        "sound_keys": ["cinematic_whoosh", "whoosh", "swoosh", "swing", "rush"],
        "words": ["whoosh", "swoosh", "swing", "rush", "rushed", "fast", "speed", "flew", "fly", "flying", "zoom", "quick", "swift", "dash", "dashed", "jump", "leap", "run", "running", "escape", "escaped"],
        "fallback_sound_keys": ["cinematic_whoosh", "arrow_fly_hit"],
    },
    {
        "name": "money",
        "sound_keys": ["coin_ding", "ding", "coin", "money", "cash", "gold", "wealth"],
        "words": ["money", "gold", "cash", "coin", "coins", "wealth", "wealthy", "rich", "riches", "fortune", "treasure", "treasures", "tax", "taxes", "profit"],
        "fallback_sound_keys": ["coin_ding", "royal_fanfare"],
    },
    {
        "name": "victory",
        "sound_keys": ["victory_cheer", "victory", "cheer", "royal_fanfare", "fanfare", "triumph"],
        "words": ["victory", "victorious", "won", "win", "winner", "triumph", "triumphant", "conquer", "conquered", "celebrated", "cheered", "cheer", "jubilant", "glory", "champion"],
        "fallback_sound_keys": ["victory_cheer", "royal_fanfare"],
    },
    {
        "name": "defeat",
        "sound_keys": ["dramatic_impact", "thud", "dead", "defeat", "loss", "fail"],
        "words": ["defeat", "defeated", "fallen", "fell", "slain", "crushed", "shattered", "collapsed", "died", "dead", "casualty", "disaster", "executed", "perish"],
        "fallback_sound_keys": ["dramatic_impact", "thud"],
    },
    {
        "name": "tension",
        "sound_keys": ["tension_hit", "tension", "suspense", "heartbeat"],
        "words": ["betray", "betrayal", "plot", "conspiracy", "trap", "ambush", "secret", "poison", "danger", "dangerous", "threat", "shadow", "crept", "lurking"],
        "fallback_sound_keys": ["tension_hit", "dramatic_impact"],
    },
    {
        "name": "swords",
        "sound_keys": ["sword_clash", "sword", "clash", "blade"],
        "words": ["battle", "clash", "swords", "sword", "fight", "combat", "duel", "melee", "assault", "blade", "blades", "steel"],
        "fallback_sound_keys": ["sword_clash", "war_horn"],
    },
    {
        "name": "arrow",
        "sound_keys": ["arrow_fly_hit", "arrow"],
        "words": ["arrow", "arrows", "archer", "archers", "shot", "pierced", "volley", "bow"],
        "fallback_sound_keys": ["arrow_fly_hit"],
    },
    {
        "name": "horses",
        "sound_keys": ["cavalry_gallop", "gallop", "horse"],
        "words": ["cavalry", "horse", "horses", "gallop", "mounted", "knights charged", "cavalry charged", "charge"],
        "fallback_sound_keys": ["cavalry_gallop", "taiko_drum"],
    },
    {
        "name": "horn",
        "sound_keys": ["war_horn", "horn"],
        "words": ["war", "invade", "invasion", "fleet", "army", "crusade", "legion", "legions", "campaign"],
        "fallback_sound_keys": ["war_horn"],
    },
    {
        "name": "drum",
        "sound_keys": ["taiko_drum", "drum"],
        "words": ["march", "marched", "advance", "advanced", "rally", "troops", "frontier", "prepared"],
        "fallback_sound_keys": ["taiko_drum"],
    },
    {
        "name": "fanfare",
        "sound_keys": ["royal_fanfare", "fanfare", "trumpet"],
        "words": ["crown", "crowned", "coronation", "king", "queen", "emperor", "throne", "palace", "reign", "monarch"],
        "fallback_sound_keys": ["royal_fanfare"],
    },
    {
        "name": "camera",
        "sound_keys": ["camera", "shutter", "click"],
        "words": ["camera", "shutter", "photo", "picture", "snapshot", "photograph", "pose", "flash", "capture"],
        "fallback_sound_keys": ["camera-shutter", "camera shutter 2", "click"],
    },
]

def heuristic_intensity_mapping(cues, intensity_labels: list[str], sfx_density: float = 0.25) -> dict[int, str]:
    """Smart heuristic dialogue audio matcher for emotion, reaction, and intensity sound effects."""
    if not intensity_labels or not cues:
        return {}

    density = sfx_density / 100.0 if sfx_density > 1.0 else sfx_density
    if density <= 0.01:
        return {}

    min_cue_gap = max(1, int(round(1.0 / max(density, 0.05))))
    mapping = {}
    lower_sfx = {lbl.lower(): lbl for lbl in intensity_labels}
    last_sfx_idx = -9999
    recent_sounds = []

    def find_sound_by_keys(keys: list[str], avoid: list[str] = None):
        candidates = []
        for k in keys:
            k_lower = k.lower()
            for sfx_key, original in lower_sfx.items():
                if k_lower in sfx_key or sfx_key in k_lower:
                    if original not in candidates:
                        candidates.append(original)
        if not candidates:
            return None
        if avoid:
            filtered = [c for c in candidates if c not in avoid]
            if filtered:
                return filtered[0]
        return candidates[0]

    # Pre-resolve sound files for each rule from the available pool
    rule_sound_map = []
    for rule in EMOTION_AND_SFX_RULES:
        sound = find_sound_by_keys(rule["sound_keys"])
        if not sound and "fallback_sound_keys" in rule:
            sound = find_sound_by_keys(rule["fallback_sound_keys"])
        if sound:
            rule_sound_map.append((rule["words"], rule["sound_keys"], rule.get("fallback_sound_keys", [])))

    for idx, cue in enumerate(cues):
        if idx - last_sfx_idx < min_cue_gap:
            continue

        cue_text = (cue.text or "").lower()
        matched = None

        # 1. Match semantic emotion and sound effect rules avoiding recent_sounds
        for words, sound_keys, fallback_keys in rule_sound_map:
            if any(re.search(r'\b' + re.escape(w) + r'\b', cue_text) for w in words):
                sound = find_sound_by_keys(sound_keys, avoid=recent_sounds)
                if not sound and fallback_keys:
                    sound = find_sound_by_keys(fallback_keys, avoid=recent_sounds)
                # If all matched are in recent_sounds, fall back to any available match
                if not sound:
                    sound = find_sound_by_keys(sound_keys) or (find_sound_by_keys(fallback_keys) if fallback_keys else None)
                if sound:
                    matched = sound
                    break

        # 2. Dynamic direct word match with custom audio filenames
        if not matched:
            custom_matches = []
            for sfx_key, original in lower_sfx.items():
                clean_stem = re.sub(r'[^a-zA-Z0-9]', ' ', sfx_key).strip()
                tokens = [t for t in clean_stem.split() if len(t) > 3 and t not in ("sound", "audio", "effect")]
                if any(re.search(r'\b' + re.escape(tok) + r'\b', cue_text) for tok in tokens):
                    custom_matches.append(original)
            if custom_matches:
                non_recent = [m for m in custom_matches if m not in recent_sounds]
                matched = non_recent[0] if non_recent else custom_matches[0]

        if matched:
            mapping[idx] = matched
            last_sfx_idx = idx
            recent_sounds.append(matched)
            if len(recent_sounds) > 3:
                recent_sounds.pop(0)

    print(f"[HD SFX Director] Professionally mapped {len(mapping)} sound triggers across {len(cues)} cues (density={density:.2f}, min_gap={min_cue_gap}): {list(mapping.values())[:8]}...", flush=True)
    return mapping


def analyze_cues_intensity(cues, intensity_labels: list[str], api_key: str = "", provider: str = "openai", api_model: str = None, progress_callback=None, sfx_density: float = 0.25) -> dict[int, str]:
    if not intensity_labels or not cues:
        return {}

    density = sfx_density / 100.0 if sfx_density > 1.0 else sfx_density
    if density <= 0.01:
        return {}

    min_cue_gap = max(1, int(round(1.0 / max(density, 0.05))))

    if not api_key:
        return heuristic_intensity_mapping(cues, intensity_labels, sfx_density=density)

    mapping = {}
    chunk_size = 50
    sample_1 = intensity_labels[0]
    sample_2 = intensity_labels[1] if len(intensity_labels) > 1 else intensity_labels[0]
    labels_formatted = ", ".join(f'"{lbl}"' for lbl in intensity_labels)
    extra_cache_key = f"{','.join(sorted(intensity_labels))}_d{int(density*100)}"

    for start_idx in range(0, len(cues), chunk_size):
        chunk_cues = cues[start_idx:start_idx+chunk_size]

        prompt = (
            "You are an expert audio designer and video editor.\n"
            "Your task is to analyze dialogue subtitles and assign appropriate emotion or sound effects to specific lines "
            "based on the dialogue context, emotional tone, actions, drama, or humor.\n\n"
            f"Available Sound Effects Pool:\n[{labels_formatted}]\n\n"
            "Instructions:\n"
            "1. You can choose either:\n"
            "   (a) An expressive emotion or audio effect category: angry, sad, crying, happy, laugh, funny, shock, surprise, wow, fear, scared, confused, awkward, lazy, guilt, fail, wrong, worry, idea, punch, hit, impact, boom, explosion, whoosh, ding, bell, money, victory, tension, clock, phone, camera.\n"
            "   (b) OR any exact sound filename from the available sound effects pool above.\n"
            "2. Match the emotional feeling, tone, or implied action of each line with the best fitting sound effect or emotion.\n"
            f"3. Pacing: Assign an appropriate sound to about 1 sound every {min_cue_gap} lines (~{int(density * 100)}% of lines) to maintain engaging, emotionally dynamic audio. Do NOT spam sounds or leave too many gaps.\n"
            "4. If no sound fits the line or for quiet speech, assign \"none\". Do NOT assign sounds to consecutive lines back-to-back.\n\n"
            "Respond ONLY with a valid JSON object mapping the subtitle index (as a string) to the chosen emotion or sound effect name.\n"
            f'Example: {{"{start_idx}": "shock", "{start_idx + min_cue_gap}": "{sample_2}"}}\n\n'
            "Subtitles:\n"
        )
        for j, cue in enumerate(chunk_cues):
            prompt += f"[{start_idx + j}] {cue.text}\n"

        chunk_text = "\n".join(c.text for c in chunk_cues)
        cache_file = _get_cache_path(chunk_text, "intensity", extra_cache_key)
        if progress_callback:
            total_chunks = (len(cues) + chunk_size - 1) // chunk_size
            progress_callback(start_idx // chunk_size, total_chunks)
        if cache_file.exists():
            try:
                cached_data = json.loads(cache_file.read_text())
                if cached_data:
                    mapping.update({int(k): v for k, v in cached_data.items()})
                    continue
            except Exception:
                pass

        for attempt in range(2):
            result_text = None
            try:
                result_text = _call_llm_api(prompt, provider, api_key, api_model)
                match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if match:
                    result_text = match.group(0)
                else:
                    result_text = result_text.strip()

                parsed = {}
                try:
                    parsed = json.loads(result_text)
                except json.JSONDecodeError:
                    for m in re.finditer(r'"(\d+)"\s*:\s*"([^"]+)"', result_text):
                        parsed[m.group(1)] = m.group(2)

                if isinstance(parsed, dict) and parsed:
                    valid_results = {}
                    for k, v in parsed.items():
                        if isinstance(v, str):
                            matched_lbl = _resolve_sfx_match(v, intensity_labels)
                            if matched_lbl:
                                mapping[int(k)] = matched_lbl
                                valid_results[str(k)] = matched_lbl
                    if valid_results:
                        cache_file.write_text(json.dumps(valid_results))
                    break
            except Exception as e:
                print(f"[Intensity AI Attempt {attempt+1}] {e}", flush=True)
                time.sleep(2)

    # Filter out any cues that violate min_cue_gap or repeat the same sound back-to-back
    filtered_mapping = {}
    last_idx = -9999
    last_sound = None
    for k in sorted(mapping.keys()):
        snd = mapping[k]
        if k - last_idx >= min_cue_gap and snd != last_sound:
            filtered_mapping[k] = snd
            last_idx = k
            last_sound = snd
    mapping = filtered_mapping

    # Only run the fallback fill pass if the total mapped sounds are below int(len(cues) * density * 0.6)
    min_required_sounds = int(len(cues) * density * 0.6)
    if len(mapping) < min_required_sounds:
        h_all = heuristic_intensity_mapping(cues, intensity_labels, sfx_density=density)
        for idx, snd in h_all.items():
            if idx not in mapping:
                too_close = any(abs(idx - ex_idx) < min_cue_gap for ex_idx in mapping.keys())
                prev_sfx = mapping.get(idx - min_cue_gap)
                next_sfx = mapping.get(idx + min_cue_gap)
                if not too_close and snd != prev_sfx and snd != next_sfx:
                    mapping[idx] = snd

    return mapping


def describe_popup_images_with_ai(popup_paths: dict[str, Path], provider: str = "openai", api_key: str = "", api_model: str = None) -> dict[str, str]:
    """
    Multimodal Vision AI Reader for uploaded popup/sticker PNGs:
    Reads and inspects the image files, extracting visual descriptions (character type,
    emotion, pose, action, props) so the AI dialogue director knows what each image actually depicts.
    Results are cached by image MD5 content hash for instantaneous retrieval.
    """
    if not popup_paths:
        return {}

    descriptions = {}
    for stem, img_path in popup_paths.items():
        if not img_path or not Path(img_path).is_file():
            descriptions[stem] = stem.replace("_", " ")
            continue

        p = Path(img_path)
        try:
            content_bytes = p.read_bytes()
            img_hash = hashlib.md5(content_bytes).hexdigest()
            cache_file = CACHE_DIR / f"vision_{img_hash}.json"
            if cache_file.exists():
                try:
                    data = json.loads(cache_file.read_text(encoding="utf-8"))
                    descriptions[stem] = data.get("description", stem.replace("_", " "))
                    continue
                except Exception:
                    pass

            if not api_key:
                clean_name = re.sub(r"[^a-zA-Z0-9]+", " ", stem).strip()
                descriptions[stem] = clean_name
                continue

            # Build compact base64 thumbnail (max 384px) for fast vision transfer
            im = Image.open(p)
            if im.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.thumbnail((384, 384), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85)
            b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

            prompt = (
                "Describe this character sticker in 6-12 words: state character type, action, pose, emotion, and any key props."
            )

            desc = ""
            prov_lower = (provider or "").lower()
            if prov_lower in ("nvidia", "openai"):
                import openai, httpx
                base_url = "https://integrate.api.nvidia.com/v1" if prov_lower == "nvidia" else None
                model = api_model or ("meta/llama-3.2-11b-vision-instruct" if prov_lower == "nvidia" else "gpt-4o-mini")
                client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=httpx.Timeout(45.0, connect=10.0, read=45.0, write=10.0)
                )
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_str}"}}
                        ]
                    }],
                    max_tokens=60,
                    temperature=0.2
                )
                desc = (resp.choices[0].message.content or "").strip()
            elif prov_lower == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content([prompt, im])
                desc = (resp.text or "").strip()

            if desc:
                desc = re.sub(r'^(the image features|this image shows|the character is|a drawing of)\s*', '', desc, flags=re.IGNORECASE).strip('".\' ')
                descriptions[stem] = desc
                try:
                    cache_file.write_text(json.dumps({"description": desc, "stem": stem}), encoding="utf-8")
                except Exception:
                    pass
                print(f"[Vision AI] Identified '{stem}': {desc}", flush=True)
            else:
                descriptions[stem] = stem.replace("_", " ")

        except Exception as e:
            print(f"[Vision AI Error] Could not inspect {stem}: {e}", flush=True)
            descriptions[stem] = stem.replace("_", " ")

    return descriptions


def analyze_cues_popups(
    cues,
    popup_paths_or_labels,
    api_key: str = "",
    provider: str = "openai",
    custom_prompt: str | None = "",
    api_model: str = None,
    progress_callback=None
) -> dict[int, str]:
    if not popup_paths_or_labels or not cues:
        return {}

    custom_prompt = (custom_prompt or "").strip()

    popup_paths = {}
    if isinstance(popup_paths_or_labels, dict):
        popup_paths = popup_paths_or_labels
        popup_labels = list(popup_paths.keys())
    else:
        popup_labels = list(popup_paths_or_labels)
        popup_paths = {}

    if not api_key:
        return heuristic_popup_mapping(cues, popup_labels)

    # 1. Run Vision AI reader on uploaded images if available
    descriptions = {}
    if popup_paths:
        descriptions = describe_popup_images_with_ai(popup_paths, provider=provider, api_key=api_key, api_model=api_model)

    # Build image catalog with visual descriptions
    catalog_lines = []
    for lbl in popup_labels:
        desc = descriptions.get(lbl, lbl.replace("_", " "))
        catalog_lines.append(f'- "{lbl}": {desc}')
    catalog_text = "\n".join(catalog_lines)

    mapping = {}
    used_popups = set()
    chunk_size = 50
    lower_labels = {lbl.lower(): lbl for lbl in popup_labels}

    catalog_hash = hashlib.md5(catalog_text.encode("utf-8")).hexdigest()[:10]

    for start_idx in range(0, len(cues), chunk_size):
        chunk_cues = cues[start_idx:start_idx+chunk_size]

        available_unused = [lbl for lbl in popup_labels if lbl not in used_popups]
        if not available_unused:
            break

        chunk_catalog = "\n".join(f'- "{lbl}": {descriptions.get(lbl, lbl.replace("_", " "))}' for lbl in available_unused)

        prompt = (
            "You are the Animation Director for high-retention animated explainer videos.\n"
            "Below is the catalog of available character popup images and their exact visual descriptions:\n"
            f"{chunk_catalog}\n\n"
            "YOUR TASK:\n"
            "Read each subtitle dialogue line and assign the best-matching character popup image based on what the character is doing, feeling, or holding.\n\n"
            "CRITICAL CONSTRAINTS (STRICT SINGLE-USE RULE):\n"
            "1. EACH IMAGE MUST BE USED AT MOST ONCE in the entire video. Once an image is placed, it CANNOT be used again for any other cue. NEVER repeat an image.\n"
            "2. ZERO LOOPING: Do not repeat any character image under any circumstance.\n"
            "3. ACCURACY: Match the character to the dialogue where its specific emotion, action, or theme is directly spoken.\n"
            "4. If a dialogue line has no matching unused character or is purely transitional, assign 'none'.\n\n"
        )
        if custom_prompt:
            prompt += f"USER DIRECTIVES:\n{custom_prompt}\n\n"
        prompt += "Respond ONLY with a valid JSON object mapping the subtitle index (as a string) to the chosen character image name or 'none'.\n"
        prompt += f"Example: {{\"0\": \"{available_unused[0]}\", \"2\": \"none\"}}\n\n"
        prompt += "Subtitles:\n"
        for j, cue in enumerate(chunk_cues):
            prompt += f"[{start_idx + j}] {cue.text or ''}\n"

        chunk_text = "\n".join((c.text or "") for c in chunk_cues)
        cache_file = _get_cache_path(chunk_text, "popups", extra_key=f"{catalog_hash}_{start_idx}")
        if progress_callback:
            total_chunks = (len(cues) + chunk_size - 1) // chunk_size
            progress_callback(start_idx // chunk_size, total_chunks)

        chunk_results = None
        if cache_file.exists():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                chunk_results = cached_data
            except Exception:
                pass

        if chunk_results is None:
            for attempt in range(2):
                try:
                    result_text = _call_llm_api(prompt, provider, api_key, api_model)
                    match = re.search(r"\{.*\}", result_text, re.DOTALL)
                    if match:
                        result_text = match.group(0)
                    else:
                        result_text = result_text.strip()

                    parsed = {}
                    try:
                        parsed = json.loads(result_text)
                    except json.JSONDecodeError:
                        for m in re.finditer(r'"(\d+)"\s*:\s*"([^"]+)"', result_text):
                            parsed[m.group(1)] = m.group(2)

                    if isinstance(parsed, dict) and parsed:
                        chunk_results = parsed
                        try:
                            cache_file.write_text(json.dumps(chunk_results), encoding="utf-8")
                        except Exception:
                            pass
                        break
                except Exception as e:
                    print(f"[Character AI Attempt {attempt+1}] {e}", flush=True)
                    time.sleep(2)

        # Enforce strict single-use across all chunks
        if chunk_results:
            for k, v in chunk_results.items():
                if isinstance(v, str):
                    v_clean = v.lower().strip()
                    if v_clean in lower_labels:
                        actual_lbl = lower_labels[v_clean]
                        if actual_lbl not in used_popups:
                            mapping[int(k)] = actual_lbl
                            used_popups.add(actual_lbl)

    # 2. Guarantee that ALL uploaded popup assets in the box are utilized:
    # If any images remain unassigned, place each unused image once on an available cue
    unused_popups = [lbl for lbl in popup_labels if lbl not in used_popups]
    if unused_popups:
        def nat_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        sorted_unused = sorted(unused_popups, key=nat_sort_key)

        available_cues = []
        last_idx = -3
        for idx, cue in enumerate(cues):
            if idx in mapping:
                last_idx = idx
                continue
            if idx - last_idx >= 2 and len((cue.text or "").split()) >= 3:
                available_cues.append(idx)
                last_idx = idx

        if len(available_cues) < len(sorted_unused):
            for idx in range(len(cues)):
                if idx not in mapping and idx not in available_cues:
                    available_cues.append(idx)
            available_cues.sort()

        for step, unassigned in enumerate(sorted_unused):
            if step < len(available_cues):
                target_cue = available_cues[step]
                mapping[target_cue] = unassigned
                used_popups.add(unassigned)

    print(f"[Dialogue Character Director] Finalized {len(mapping)} single-use character actions (used {len(used_popups)}/{len(popup_labels)} unique images, zero loops): {list(mapping.values())[:8]}...", flush=True)
    return mapping


analyze_cues_characters = analyze_cues_popups
