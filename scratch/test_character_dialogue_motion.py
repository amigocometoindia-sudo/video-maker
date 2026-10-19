import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from srt_parser import Cue
from llm_analyzer import heuristic_popup_mapping
from video_generator import build_dialogue_motion_expressions
from server import get_channel_character_assets

def test_character_dialogue_pipeline():
    print("=== TEST 1: Channel Assets Discovery ===")
    assets = get_channel_character_assets()
    print(f"Total available character assets: {len(assets)}")
    print(f"Sample asset keys: {list(assets.keys())[:8]}")
    assert len(assets) > 0, "No assets found in channel character suite!"

    print("\n=== TEST 2: Dialogue Cue Matching ===")
    test_cues = [
        Cue(start_ms=0, end_ms=3500, text="The Roman legion marched across the desert to confront the enemy."),
        Cue(start_ms=3500, end_ms=7000, text="The Emperor declared war and decreed that all legions advance!"),
        Cue(start_ms=7000, end_ms=10500, text="They clashed violently in a brutal charge of swords and steel!"),
        Cue(start_ms=10500, end_ms=14000, text="Suddenly, an unexpected ambush struck in complete surprise!"),
        Cue(start_ms=14000, end_ms=17500, text="Their commander was defeated and slain on the bloody field."),
        Cue(start_ms=17500, end_ms=21000, text="The victorious warriors cheered in triumphant celebration!"),
    ]

    available_stems = list(assets.keys())
    mapping = heuristic_popup_mapping(test_cues, available_stems)
    for idx, cue in enumerate(test_cues):
        matched_char = mapping.get(idx)
        print(f"Cue [{idx}] (Text: '{cue.text[:42]}...'): Matched Character -> {matched_char}")
        assert matched_char is not None and matched_char != "none", f"Failed to match character for cue {idx}!"

    print("\n=== TEST 3: Action Motion Engine Expressions ===")
    for idx, cue in enumerate(test_cues):
        char_stem = mapping.get(idx, "")
        duration = (cue.end_ms - cue.start_ms) / 1000.0
        anim_expr, pop_size, cam_shake = build_dialogue_motion_expressions(
            cue_text=cue.text,
            duration=duration,
            popup_stem=char_stem,
            aspect_ratio="16:9",
            index=idx,
            has_battle_sfx=("clash" in cue.text),
        )
        is_right = (idx % 2 != 0)
        side = "RIGHT (hflip)" if is_right else "LEFT (normal)"
        print(f"\n[Cue {idx}] Character: {char_stem} | Screen Side: {side}")
        print(f"  Target pop_size: {pop_size}px")
        print(f"  Camera shake: {cam_shake or 'None'}")
        print(f"  Motion Expression:\n    {anim_expr[:90]}...")
        assert "x=" in anim_expr and "y=" in anim_expr, f"Broken anim_expr for cue {idx}"

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_character_dialogue_pipeline()
