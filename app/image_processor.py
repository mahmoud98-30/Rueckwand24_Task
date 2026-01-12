from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os

STATIC_IMAGE_PATH = "static/original_image.jpg"
OUTPUT_DIR = "output/pdfs"


def ensure_directories():
    """Ensure output directory exists"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("static", exist_ok=True)


def crop_and_create_pdf(width: float, height: float, item_id: int) -> str:
    """
    Crop image from top-left corner and create a PDF with timestamp

    Args:
        width: Width in pixels to crop
        height: Height in pixels to crop
        item_id: ID of the item for filename

    Returns:
        str: Path to the created PDF file
    """
    ensure_directories()

    # Check if static image exists
    if not os.path.exists(STATIC_IMAGE_PATH):
        raise FileNotFoundError(f"Static image not found at {STATIC_IMAGE_PATH}")

    # Open the original image
    original_image = Image.open(STATIC_IMAGE_PATH)

    # Ensure we don't crop beyond image boundaries
    crop_width = min(int(width), original_image.width)
    crop_height = min(int(height), original_image.height)

    # Crop from top-left (0, 0) to (width, height)
    cropped_image = original_image.crop((0, 0, crop_width, crop_height))

    # Save cropped image temporarily
    temp_image_path = f"{OUTPUT_DIR}/temp_cropped_{item_id}.jpg"
    cropped_image.save(temp_image_path, "JPEG")

    # Create PDF with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"item_{item_id}_{timestamp}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    # Create PDF
    c = canvas.Canvas(pdf_path, pagesize=(crop_width, crop_height))

    # Add timestamp text at the top
    c.setFont("Helvetica", 12)
    c.drawString(10, crop_height - 20, f"Generated: {timestamp}")

    # Add the cropped image
    c.drawImage(temp_image_path, 0, 0, width=crop_width, height=crop_height)

    c.save()

    # Clean up temporary image
    os.remove(temp_image_path)

    return pdf_path