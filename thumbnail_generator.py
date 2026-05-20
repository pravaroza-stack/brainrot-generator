#!/usr/bin/env python3
"""Generate eye-catching thumbnails for brainrot YouTube Shorts."""

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent
FONT_PATH = SCRIPT_DIR / "Roboto-ExtraBold.ttf"
OUTPUT_PATH = SCRIPT_DIR / "thumbnail.png"

# YouTube Shorts thumbnail size (9:16 aspect ratio)
THUMBNAIL_WIDTH = 1080
THUMBNAIL_HEIGHT = 1920

# Brainrot color palettes (background, text, accent)
COLOR_SCHEMES = [
    {"bg": "#FF0050", "text": "#FFFFFF", "accent": "#FFFF00"},  # Red + White + Yellow
    {"bg": "#7B2FFF", "text": "#FFFFFF", "accent": "#00FF88"},  # Purple + White + Green
    {"bg": "#FF6B00", "text": "#FFFFFF", "accent": "#00FFFF"},  # Orange + White + Cyan
    {"bg": "#00D4FF", "text": "#000000", "accent": "#FF0050"},  # Cyan + Black + Red
    {"bg": "#FFDD00", "text": "#000000", "accent": "#FF0050"},  # Yellow + Black + Red
    {"bg": "#FF1493", "text": "#FFFFFF", "accent": "#00FF00"},  # Pink + White + Green
]

# Hook emojis for thumbnails
HOOK_EMOJIS = ["🤯", "😱", "🔥", "💀", "⚡", "🧠", "😵", "🚀", "💯", "🎯", "⚠️", "❌", "✅"]


def extract_hook(title: str) -> str:
    """Extract or create a punchy hook from the title."""
    # Remove emojis from title for text
    import re
    clean_title = re.sub(r'[^\w\s\-\?!।]', '', title, flags=re.UNICODE).strip()

    # If title is short enough, use it
    if len(clean_title) <= 25:
        return clean_title.upper()

    # Otherwise, extract key phrase
    hooks = [
        "MIND BLOWN",
        "YEH SUNO",
        "FACTS",
        "REAL HAI",
        "SHOCKING",
    ]

    # Try to use first few words
    words = clean_title.split()[:4]
    short_hook = " ".join(words)
    if len(short_hook) <= 25:
        return short_hook.upper()

    return random.choice(hooks)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> list:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def generate_thumbnail(title: str, topic_id: str = "", output_path: str = None) -> str:
    """Generate a brainrot-style thumbnail."""

    if output_path is None:
        output_path = str(OUTPUT_PATH)

    # Pick random color scheme
    colors = random.choice(COLOR_SCHEMES)

    # Create image
    img = Image.new('RGB', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), colors["bg"])
    draw = ImageDraw.Draw(img)

    # Load font (try different sizes)
    try:
        font_large = ImageFont.truetype(str(FONT_PATH), 120)
        font_medium = ImageFont.truetype(str(FONT_PATH), 80)
        font_emoji = ImageFont.truetype(str(FONT_PATH), 200)
    except Exception:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_emoji = font_large

    # Extract hook text
    hook = extract_hook(title)

    # Add decorative elements - diagonal stripes
    stripe_color = colors["accent"]
    for i in range(-THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH + THUMBNAIL_HEIGHT, 80):
        draw.line([(i, 0), (i + THUMBNAIL_HEIGHT, THUMBNAIL_HEIGHT)],
                  fill=stripe_color, width=20)

    # Add semi-transparent overlay for text readability
    overlay = Image.new('RGBA', (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Center box for text
    box_margin = 50
    box_top = THUMBNAIL_HEIGHT // 3
    box_bottom = THUMBNAIL_HEIGHT * 2 // 3
    overlay_draw.rectangle(
        [box_margin, box_top, THUMBNAIL_WIDTH - box_margin, box_bottom],
        fill=colors["bg"] + "EE"  # Semi-transparent
    )

    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Draw main text
    lines = wrap_text(hook, font_large, THUMBNAIL_WIDTH - 120, draw)

    # Calculate total text height
    line_height = 130
    total_text_height = len(lines) * line_height
    start_y = (THUMBNAIL_HEIGHT - total_text_height) // 2

    # Draw each line centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (THUMBNAIL_WIDTH - text_width) // 2
        y = start_y + (i * line_height)

        # Draw text shadow
        draw.text((x + 4, y + 4), line, font=font_large, fill="#000000")
        # Draw main text
        draw.text((x, y), line, font=font_large, fill=colors["text"])

    # Add emoji at top
    emoji = random.choice(HOOK_EMOJIS)
    emoji_y = box_top - 150
    # Draw emoji text (will show as text if emoji font not available)
    draw.text((THUMBNAIL_WIDTH // 2 - 50, emoji_y), emoji, font=font_medium, fill=colors["accent"])

    # Add "CHINU" branding at bottom
    brand_text = "CHINU EXPLAINS"
    bbox = draw.textbbox((0, 0), brand_text, font=font_medium)
    brand_width = bbox[2] - bbox[0]
    brand_x = (THUMBNAIL_WIDTH - brand_width) // 2
    brand_y = THUMBNAIL_HEIGHT - 200

    # Brand background
    draw.rectangle(
        [brand_x - 20, brand_y - 10, brand_x + brand_width + 20, brand_y + 90],
        fill=colors["accent"]
    )
    draw.text((brand_x, brand_y), brand_text, font=font_medium, fill="#000000")

    # Save
    img.save(output_path, "PNG", quality=95)
    print(f"Thumbnail saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # Test with sample title
        title = "Mitochondria Facts That Will Blow Your Mind 🤯"
    else:
        title = sys.argv[1]

    generate_thumbnail(title)
    print("Done!")
