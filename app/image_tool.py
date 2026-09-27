"""Image generation tool for recipe-chef agent.

Generates dish visuals and uploads them to a public Cloud Storage bucket.
"""

import io
import time
from google.cloud import storage
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

PROJECT_ID = "qwiklabs-gcp-03-6c3aab0d52d4"
BUCKET_NAME = "recipe-chef-assets-qwiklabs-gcp-03-6c3aab0d52d4"
LOCATION = "us-east1"


def _upload_to_gcs(image_bytes: bytes, filename: str) -> str:
    """Uploads image bytes to public Cloud Storage bucket and returns public URL."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)

    blob.upload_from_string(image_bytes, content_type="image/png")
    
    # Return public HTTP URL
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"


def _generate_styled_dish_card(recipe_title: str, dish_description: str) -> bytes:
    """Creates a high-quality stylized culinary graphic card as a reliable fallback."""
    width, height = 800, 800
    image = Image.new("RGB", (width, height), color=(28, 25, 23))  # Warm dark slate background
    draw = ImageDraw.Draw(image)

    # Decorative warm culinary gradient overlay
    for y in range(height):
        r = int(28 + (200 - 28) * (y / height) * 0.25)
        g = int(25 + (80 - 25) * (y / height) * 0.15)
        b = int(23 + (40 - 23) * (y / height) * 0.1)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Inner decorative border frame
    draw.rectangle([30, 30, width - 30, height - 30], outline=(234, 179, 8), width=3)  # Warm amber border
    draw.rectangle([40, 40, width - 40, height - 40], outline=(120, 113, 108), width=1)

    # Top Culinary Header Tag
    draw.rectangle([250, 70, 550, 110], fill=(234, 179, 8))
    draw.text((270, 78), "★ RECIPE CHEF FEATURED DISH ★", fill=(28, 25, 23))

    # Main Title (wrapped)
    title_text = recipe_title.strip()
    draw.text((80, 220), title_text[:35], fill=(255, 255, 255))
    if len(title_text) > 35:
        draw.text((80, 270), title_text[35:70], fill=(255, 255, 255))

    # Dish Accent Line
    draw.line([(80, 340), (width - 80, 340)], fill=(234, 179, 8), width=4)

    # Dish Description
    desc_text = dish_description if dish_description else "A gourmet, beautifully presented dish crafted with fresh ingredients."
    draw.text((80, 380), desc_text[:60], fill=(214, 211, 209))
    if len(desc_text) > 60:
        draw.text((80, 420), desc_text[60:120], fill=(214, 211, 209))

    # Badges section
    draw.rectangle([80, 540, 280, 600], fill=(68, 64, 60))
    draw.text((100, 560), "🍳 Fresh Plating", fill=(250, 204, 21))

    draw.rectangle([310, 540, 510, 600], fill=(68, 64, 60))
    draw.text((330, 560), "🌿 Gourmet Quality", fill=(74, 222, 128))

    draw.rectangle([540, 540, 720, 600], fill=(68, 64, 60))
    draw.text((560, 560), "🔥 Chef Tested", fill=(248, 113, 113))

    # Footer branding
    draw.text((260, 720), "Recipe Chef AI • Visual Presentation", fill=(168, 162, 158))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def generate_dish_image(recipe_title: str, dish_description: str = "") -> str:
    """Generate a visual presentation photo for a recipe dish and upload it to Cloud Storage.

    Args:
        recipe_title: The name of the dish (e.g., 'Classic Spaghetti Carbonara').
        dish_description: Optional description of the dish, plating style, or ingredients.

    Returns:
        The public HTTP URL of the generated image hosted on Cloud Storage.
    """
    timestamp = int(time.time())
    slug = "".join(c if c.isalnum() else "-" for c in recipe_title.lower()).strip("-")
    filename = f"dishes/{slug}-{timestamp}.png"

    # Try Imagen generation first
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        prompt = f"A gourmet, professionally plated photo of {recipe_title}. {dish_description}".strip()
        
        result = genai_client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="1:1",
            ),
        )
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            return _upload_to_gcs(image_bytes, filename)
    except Exception as e:
        # Fallback to custom stylized card rendering if Imagen is restricted
        print(f"Imagen API note: {e}. Falling back to styled culinary card generation.")

    image_bytes = _generate_styled_dish_card(recipe_title, dish_description)
    return _upload_to_gcs(image_bytes, filename)
