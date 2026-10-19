import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from srt_parser import Cue
from auto_generator import detect_topic_domain, generate_script_with_ai, render_thematic_canvas
from llm_analyzer import heuristic_popup_mapping
from video_generator import build_dialogue_motion_expressions
from server import get_channel_character_assets

def test_multi_genre_explainer_suite():
    print("=== TEST 1: Topic Domain Classifier ===")
    topics = {
        "how elon musk got that much money": "tech_business",
        "why you overthink and how to stop": "psychology_mind",
        "what did ancient human do all day": "science_nature",
        "1000 years of the roman empire": "history_war",
    }
    for topic, expected in topics.items():
        domain = detect_topic_domain(topic)
        print(f"Topic: '{topic}' -> Detected Domain: {domain}")
        assert domain == expected, f"Expected {expected}, got {domain}"

    print("\n=== TEST 2: Multi-Genre Script Generator ===")
    for topic in ["how elon musk got that much money", "why you overthink", "what did ancient human do"]:
        script = generate_script_with_ai(topic)
        print(f"\n[Script for: {topic}] ({len(script.split())} words):")
        print(f"  {script[:110]}...")
        assert len(script) > 80, f"Script too short for {topic}"

    print("\n=== TEST 3: Multi-Genre Character Action Matching ===")
    assets = get_channel_character_assets()
    available_stems = list(assets.keys())

    test_cues = [
        # Tech & Wealth
        Cue(start_ms=0, end_ms=3000, text="Elon invested his entire fortune, risking hundreds of millions of dollars."),
        # Psychology & Overthinking
        Cue(start_ms=3000, end_ms=6000, text="Your brain starts overthinking, trapped in endless loops of anxiety and worry."),
        # Idea & Eureka
        Cue(start_ms=6000, end_ms=9000, text="Suddenly, a brilliant breakthrough idea sparked the perfect solution!"),
        # Ancient Human & Fire
        Cue(start_ms=9000, end_ms=12000, text="Ancient humans gathered around the blazing fire to cook meat and stay warm."),
    ]

    mapping = heuristic_popup_mapping(test_cues, available_stems)
    for idx, cue in enumerate(test_cues):
        matched = mapping.get(idx)
        print(f"Cue [{idx}] ('{cue.text[:45]}...'): -> Character: {matched}")
        assert matched is not None, f"Failed to match character for cue {idx}"

    print("\n=== TEST 4: Motion Engine for Modern Actions ===")
    for idx, cue in enumerate(test_cues):
        char_stem = mapping.get(idx, "")
        anim_expr, pop_size, cam_shake = build_dialogue_motion_expressions(
            cue_text=cue.text,
            duration=3.0,
            popup_stem=char_stem,
            aspect_ratio="16:9",
            index=idx,
        )
        print(f"Cue [{idx}] Character {char_stem}: size={pop_size}px, anim={anim_expr[:70]}...")
        assert "x=" in anim_expr and "y=" in anim_expr, f"Invalid motion expression for cue {idx}"

    print("\n=== TEST 5: Thematic Procedural Canvases ===")
    for topic in ["How Elon Musk Got Rich", "Why You Overthink", "What Did Ancient Humans Do", "Roman Empire"]:
        canvas = render_thematic_canvas(topic, "test cue text", 0, 640, 360)
        assert canvas.size == (640, 360), "Canvas generation failed"
        print(f"Rendered canvas for: '{topic}' ({canvas.size[0]}x{canvas.size[1]})")

    print("\n=== ALL MULTI-GENRE TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_multi_genre_explainer_suite()
