"""
Script to create a sample image for testing the application
Run this before starting the Docker containers
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_sample_image():
    """Create a large sample image with grid and text"""

    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)

    # Create a large image (2000x1500)
    width, height = 2000, 1500
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Draw a grid
    grid_spacing = 100
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill='lightgray', width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill='lightgray', width=1)

    # Draw colored rectangles
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
    rect_size = 200
    for i, color in enumerate(colors):
        x = (i % 3) * 300 + 100
        y = (i // 3) * 300 + 100
        draw.rectangle(
            [(x, y), (x + rect_size, y + rect_size)],
            fill=color,
            outline='black',
            width=3
        )

    # Add text
    try:
        # Try to use a default font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    draw.text((width // 2 - 200, 50), "SAMPLE IMAGE", fill='black', font=font)
    draw.text((50, height - 100), "For Backend Test Task", fill='gray')

    # Add coordinates
    draw.text((10, 10), "(0,0) Top-Left", fill='red')
    draw.text((width - 200, 10), f"({width},0)", fill='blue')
    draw.text((10, height - 30), f"(0,{height})", fill='green')
    draw.text((width - 200, height - 30), f"({width},{height})", fill='purple')

    # Save the image
    output_path = "static/original_image.jpg"
    image.save(output_path, "JPEG", quality=95)

    print(f"✅ Sample image created successfully!")
    print(f"📁 Location: {output_path}")
    print(f"📏 Size: {width}x{height} pixels")
    print(f"\n🚀 You can now run: docker-compose up --build")


if __name__ == "__main__":
    create_sample_image()