from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from io import BytesIO
import os

STATIC_IMAGE_PATH = "app/assets/source.jpg"
OUTPUT_DIR = "app/storage/pdfs"


def ensure_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def crop_and_create_pdf(width: float, height: float, item_id: int) -> str:
    ensure_directories()

    if not os.path.exists(STATIC_IMAGE_PATH):
        raise FileNotFoundError(f"Static image not found at {STATIC_IMAGE_PATH}")

    # 1️⃣ Load image safely
    original_image = Image.open(STATIC_IMAGE_PATH)
    original_image = original_image.convert("RGB")

    crop_width = min(int(width), original_image.width)
    crop_height = min(int(height), original_image.height)

    if crop_width <= 0 or crop_height <= 0:
        raise ValueError("Width and height must be greater than 0")

    # 2️⃣ Crop top-left
    cropped_image = original_image.crop((0, 0, crop_width, crop_height))

    # 3️⃣ Convert cropped image → BYTES (this is the key)
    img_buffer = BytesIO()
    cropped_image.save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    image_reader = ImageReader(img_buffer)

    # 4️⃣ Create PDF
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"item_{item_id}_{timestamp}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=(crop_width, crop_height))

    # Draw image
    c.drawImage(
        image_reader,
        0,
        0,
        width=crop_width,
        height=crop_height,
        mask="auto",
    )

    # Timestamp
    c.setFont("Helvetica", 12)
    c.drawString(10, crop_height - 20, f"Generated: {timestamp} UTC")

    c.showPage()
    c.save()

    return pdf_path
