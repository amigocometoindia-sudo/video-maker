import math
import re

def split_sentence_into_cues(start_ms: int, duration_ms: int, sentence: str, max_duration_ms: int = 2400) -> list[dict]:
    """Splits long spoken sentences into snappy, dynamic 1.5-2.5s scene cuts matching YouTube cartoon documentary pacing."""
    words = sentence.split()
    if duration_ms <= max_duration_ms or len(words) <= 5:
        return [{"start_ms": start_ms, "duration_ms": duration_ms, "text": sentence}]

    target_chunks = max(2, math.ceil(duration_ms / max_duration_ms))
    words_per_chunk = math.ceil(len(words) / target_chunks)
    phrases = []
    for w_idx in range(0, len(words), words_per_chunk):
        chunk_words = words[w_idx:w_idx + words_per_chunk]
        if chunk_words:
            phrases.append(" ".join(chunk_words))

    # Rebalance if last phrase is too short (e.g. 1 word)
    if len(phrases) >= 2 and len(phrases[-1].split()) <= 2:
        phrases[-2] = phrases[-2] + " " + phrases[-1]
        phrases.pop()

    total_chars = max(sum(len(p) for p in phrases), 1)
    results = []
    elapsed = 0
    for idx, p in enumerate(phrases):
        if idx == len(phrases) - 1:
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

sample_sentence = "Throughout history, few stories are as fascinating as The Battle of Hastings 1066."
cuts = split_sentence_into_cues(0, 5600, sample_sentence, max_duration_ms=2200)
print(f"Original: 5.6s -> Split into {len(cuts)} snappy cuts:")
for c in cuts:
    print(f"  {c['start_ms']}ms -> {c['start_ms'] + c['duration_ms']}ms ({c['duration_ms']/1000:.1f}s): \"{c['text']}\"")
