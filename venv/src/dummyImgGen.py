import os
import json
import random
from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# Configuration
# ---------------------------

# Get the directory of the current file.
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    current_dir = os.getcwd()

# Path to the JSON file.
PUZZLE_DATA_JSON = os.path.join(current_dir, "assets", "asoc", "puzzle_data_sr.json")

# Directory where dummy icons will be saved.
ICONS_DIR = os.path.join(current_dir, "assets", "asoc", "icons")

# Image settings.
IMAGE_SIZE = (200, 80)
TEXT_COLOR = (0, 0, 0)  # Black text.

# ---------------------------
# Load a font with good Unicode support.
# ---------------------------
def load_font(size=14):
    font_candidates = [
        "Toxigenesis BD",        # Your preferred font (case-sensitive).
        "toxigenesis bd",        # Try lower-case, just in case.
        "DejaVuSans.ttf",        # Common font with good Unicode support.
    ]
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    # Fallback to the default PIL font (note: it may not support all Unicode characters).
    print("Warning: None of the preferred fonts found. Using default font.")
    return ImageFont.load_default()

FONT = load_font(14)

# ---------------------------
# Ensure the icons folder exists
# ---------------------------
os.makedirs(ICONS_DIR, exist_ok=True)

# ---------------------------
# Load Puzzle Data from JSON
# ---------------------------
with open(PUZZLE_DATA_JSON, "r", encoding="utf8") as f:
    puzzle_data = json.load(f)

# ---------------------------
# Function to create a dummy image using a given Serbian filename as text.
# Each image will have a random light background color.
# ---------------------------
def create_dummy_icon(srpski_filename, size=IMAGE_SIZE):
    # Generate a random light background color (each RGB channel between 200 and 255).
    background_color = tuple(random.randint(200, 255) for _ in range(3))
    
    # Create a new image with the random background color.
    img = Image.new("RGB", size, background_color)
    draw = ImageDraw.Draw(img)
    
    # Use the srpski text (uppercase) as the label.
    base_name = os.path.splitext(srpski_filename)[0]
    text = base_name.replace("_", " ").upper()
    
    # Get text bounding box (compatible with Pillow 10+)
    bbox = draw.textbbox((0, 0), text, font=FONT)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text in the image.
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2

    # Draw text onto the image.
    draw.text((x, y), text, fill=TEXT_COLOR, font=FONT)
    return img

# ---------------------------
# Create and Save Dummy Images
# ---------------------------
# Iterate over each puzzle and then each column.
for puzzle in puzzle_data:
    columns = puzzle.get("columns", {})
    for col_data in columns.values():
        icons = col_data.get("icons", [])
        srpski_list = col_data.get("srpski", [])
        # Ensure that both lists have the same length.
        for icon_filename, srpski_filename in zip(icons, srpski_list):
            image_path = os.path.join(ICONS_DIR, icon_filename)
            # Create dummy image using the Serbian text and a random light background.
            img = create_dummy_icon(srpski_filename)
            try:
                img.save(image_path, "PNG")
                print(f"Created dummy image: {image_path}")
            except Exception as e:
                print(f"Error saving {image_path}: {e}")
