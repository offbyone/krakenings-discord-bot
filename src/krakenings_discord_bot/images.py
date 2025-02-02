import os
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Dimensions:
    width: int
    height: int


def make_vs_image(
    team1_logo: Image.Image, team2_logo: Image.Image, dimensions: Dimensions
) -> Image.Image:
    # Resize team logos to fit half of the output width
    output_width, output_height = dimensions.width, dimensions.height
    resize_width = output_width // 2
    resize_height = output_height
    team1_logo = team1_logo.resize((resize_width, resize_height), Image.LANCZOS)
    team2_logo = team2_logo.resize((resize_width, resize_height), Image.LANCZOS)

    # Create output canvas
    out_image = Image.new("RGBA", (output_width, output_height), (255, 255, 255, 255))

    # Paste team logos side by side
    out_image.paste(team1_logo, (0, 0), team1_logo)
    out_image.paste(team2_logo, (resize_width, 0), team2_logo)

    # Add "vs" text in the center
    draw = ImageDraw.Draw(out_image)
    font_size = 120
    try:
        # Use a simple font bundled with Pillow
        font = ImageFont.truetype(find_font("Futura"), font_size)
    except IOError:
        # Fallback if the font is unavailable
        font = ImageFont.load_default()

    text = "VS"
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font=font)
    text_x = (output_width - text_width) // 2
    text_y = (output_height - text_height) // 2

    apply_gradient(out_image, dimensions, draw, text, (text_x, text_y), font)
    # draw.text((text_x, text_y), text, fill="black", font=font)

    return out_image


# Create gradient text effect
def apply_gradient(image: Image.Image, d: Dimensions, draw, text, position, font):
    base_color = (50, 200, 255)  # Light blue
    top_color = (255, 0, 255)  # Neon pink

    text_mask = Image.new("L", (d.width, d.height), 0)
    text_draw = ImageDraw.Draw(text_mask)
    text_draw.text(position, text, font=font, fill=255)

    gradient = np.linspace(0, 1, d.height)
    color_array = np.array(
        [
            (
                int(base_color[0] * (1 - g) + top_color[0] * g),
                int(base_color[1] * (1 - g) + top_color[1] * g),
                int(base_color[2] * (1 - g) + top_color[2] * g),
            )
            for g in gradient
        ],
        dtype=np.uint8,
    )

    gradient_img = Image.fromarray(
        np.tile(color_array, (d.width, 1, 1)).transpose(1, 0, 2), "RGB"
    )
    gradient_text = Image.composite(
        gradient_img, Image.new("RGB", (d.width, d.height)), text_mask
    )

    image.paste(gradient_text, (0, 0), text_mask)


def find_font(font_name):
    font_dirs = [
        "/System/Library/Fonts/",  # MacOS
        "/Library/Fonts/",  # MacOS
        os.path.expanduser("~/Library/Fonts/"),  # MacOS user fonts
        "/usr/share/fonts/",  # Linux system-wide
        os.path.expanduser("~/.fonts/"),  # Linux user-installed
        "C:\\Windows\\Fonts\\",  # Windows
    ]

    for font_dir in font_dirs:
        if os.path.exists(font_dir):  # Check if directory exists
            for root, _, files in os.walk(font_dir):
                for file in files:
                    if font_name.lower() in file.lower():
                        return os.path.join(root, file)

    return None  # Return None if not found
