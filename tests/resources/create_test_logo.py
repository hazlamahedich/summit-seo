"""Script to create a test logo for the PDF Reporter tests."""

from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    """Create a simple test logo."""
    # Create a new image with a white background
    img = Image.new('RGB', (200, 80), color=(255, 255, 255))
    
    # Get a drawing context
    draw = ImageDraw.Draw(img)
    
    # Draw a blue rectangle
    draw.rectangle([10, 10, 190, 70], fill=(0, 102, 204))
    
    # Add text if font is available
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        try:
            # Try a system font
            font = ImageFont.load_default()
        except:
            font = None
    
    if font:
        draw.text((40, 25), "Summit SEO", fill=(255, 255, 255), font=font)
    else:
        # If no font is available, draw a white rectangle
        draw.rectangle([40, 25, 160, 55], fill=(255, 255, 255))
    
    # Save the image
    output_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    img.save(output_path)
    print(f"Test logo created at {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_logo() 