import math

# Test target word counts:
for dur in [1, 3, 5, 10, 15, 30]:
    target_words = int(dur * 145)
    print(f"{dur} min -> {target_words} words (approx {target_words // 20} scenes)")
