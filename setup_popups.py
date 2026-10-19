import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

popups_dir = Path("popups")
popups_dir.mkdir(exist_ok=True)

def get_font(size):
    for path in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/tahoma.ttf"]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return None

def create_badge(filename, bg_color, border_color, symbol, symbol_color="#ffffff", subtext=""):
    img = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer drop shadow
    draw.ellipse([55, 55, 455, 455], fill=(0, 0, 0, 100))
    # Border ring
    draw.ellipse([50, 50, 450, 450], fill=border_color)
    # Inner circle
    draw.ellipse([65, 65, 435, 435], fill=bg_color)

    font_large = get_font(180)
    font_sub = get_font(42)

    # Draw central emoji/symbol
    if font_large:
        draw.text((250, 230), symbol, fill=symbol_color, font=font_large, anchor="mm")
    else:
        draw.text((250, 230), symbol, fill=symbol_color, anchor="mm")

    if subtext:
        # Subtext badge banner at bottom
        draw.rounded_rectangle([100, 360, 400, 430], radius=16, fill="#0f172a", outline=border_color, width=3)
        if font_sub:
            draw.text((250, 395), subtext, fill="#ffffff", font=font_sub, anchor="mm")
        else:
            draw.text((250, 395), subtext, fill="#ffffff", anchor="mm")

    img.save(popups_dir / filename, "PNG")
    print(f"Created {filename}")

# Generate history sticker pack
create_badge("swords.png", "#881337", "#f43f5e", "⚔", "#ffffff", "BATTLE")
create_badge("king.png", "#78350f", "#fbbf24", "👑", "#fef08a", "RULER")
create_badge("skull.png", "#18181b", "#71717a", "💀", "#f4f4f5", "DEFEAT")
create_badge("fire.png", "#7c2d12", "#f97316", "🔥", "#ffedd5", "CONQUEST")
create_badge("gold.png", "#713f12", "#eab308", "💰", "#fef9c3", "WEALTH")
create_badge("surprise.png", "#991b1b", "#ef4444", "!", "#ffffff", "SHOCK")
create_badge("question.png", "#1e3a8a", "#3b82f6", "?", "#ffffff", "CONFUSION")
create_badge("arrow.png", "#064e3b", "#10b981", "➔", "#a7f3d0", "INVASION")

print("All history popup stickers generated successfully!")
