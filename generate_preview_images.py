"""
Generate professional preview images for resume templates
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create previews directory
previews_dir = os.path.join(os.path.dirname(__file__), 'static', 'previews')
os.makedirs(previews_dir, exist_ok=True)

# Template preview configurations
templates_config = [
    {
        "id": "sidebar-professional",
        "name": "Sidebar Professional",
        "colors": {
            "primary": "#2c3e50",
            "accent": "#2563eb",
            "bg": "#ffffff",
            "text": "#1f2937"
        },
        "description": "Dark Sidebar\nLayout"
    },
    {
        "id": "modern-clean",
        "name": "Modern Clean",
        "colors": {
            "primary": "#1e7e9c",
            "accent": "#06b6d4",
            "bg": "#ffffff",
            "text": "#1f2937"
        },
        "description": "Two Column\nLayout"
    },
    {
        "id": "header-professional",
        "name": "Header Professional",
        "colors": {
            "primary": "#2d3e5f",
            "accent": "#3d4e6f",
            "bg": "#ffffff",
            "text": "#2d3748"
        },
        "description": "Header Design\nLayout"
    },
    {
        "id": "minimal-clean",
        "name": "Minimal Clean",
        "colors": {
            "primary": "#1f2937",
            "accent": "#6b7280",
            "bg": "#ffffff",
            "text": "#374151"
        },
        "description": "Minimal Design\nLayout"
    }
]

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_preview_image(template_config, output_path):
    """Create a professional preview image for a template"""
    
    # Image dimensions
    width, height = 400, 500
    
    # Parse colors
    primary = hex_to_rgb(template_config["colors"]["primary"])
    accent = hex_to_rgb(template_config["colors"]["accent"])
    bg = hex_to_rgb(template_config["colors"]["bg"])
    text = hex_to_rgb(template_config["colors"]["text"])
    
    # Create image
    img = Image.new('RGB', (width, height), bg)
    draw = ImageDraw.Draw(img)
    
    # Try to use default font, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        text_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 11)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Create template-specific layouts
    if template_config["id"] == "sidebar-professional":
        # Sidebar layout
        draw.rectangle([(0, 0), (140, height)], fill=primary)
        draw.rectangle([(140, 0), (width, height)], fill=bg)
        
        # Sidebar content
        draw.text((10, 20), "Contact", fill=(255, 255, 255), font=text_font)
        draw.line([(10, 40), (130, 40)], fill=accent, width=2)
        
        draw.text((10, 60), "Skills", fill=(255, 255, 255), font=text_font)
        draw.line([(10, 80), (130, 80)], fill=accent, width=2)
        
        # Main content
        draw.text((160, 20), "Name", fill=text, font=title_font)
        draw.text((160, 55), "Professional Title", fill=primary, font=text_font)
        draw.line([(160, 80), (390, 80)], fill=primary, width=2)
        
        draw.text((160, 110), "Profile", fill=primary, font=text_font)
        draw.text((160, 135), "Skilled professional with", fill=text, font=small_font)
        draw.text((160, 150), "strong experience", fill=text, font=small_font)
        
        draw.text((160, 180), "Experience", fill=primary, font=text_font)
        draw.text((160, 205), "Job Title • Company", fill=text, font=small_font)
        draw.text((160, 225), "2023 – Present", fill=text, font=small_font)
        
    elif template_config["id"] == "modern-clean":
        # Two-column modern layout
        draw.rectangle([(0, 0), (width, 60)], fill=accent)
        draw.text((20, 15), "NAME", fill=(255, 255, 255), font=title_font)
        draw.text((20, 40), "Professional Title", fill=bg, font=small_font)
        
        # Two columns
        mid = width // 2
        draw.line([(mid, 60), (mid, height)], fill=primary, width=2)
        
        # Left column
        draw.text((20, 80), "Contact", fill=primary, font=text_font)
        draw.text((20, 110), "• Email", fill=text, font=small_font)
        draw.text((20, 130), "• Phone", fill=text, font=small_font)
        draw.text((20, 150), "• Location", fill=text, font=small_font)
        
        draw.text((20, 190), "Skills", fill=primary, font=text_font)
        draw.text((20, 220), "• Skill 1  • Skill 2", fill=text, font=small_font)
        draw.text((20, 240), "• Skill 3  • Skill 4", fill=text, font=small_font)
        
        # Right column
        draw.text((mid+20, 80), "Profile", fill=primary, font=text_font)
        draw.text((mid+20, 110), "Dynamic professional with", fill=text, font=small_font)
        draw.text((mid+20, 130), "proven track record", fill=text, font=small_font)
        
        draw.text((mid+20, 170), "Experience", fill=primary, font=text_font)
        draw.text((mid+20, 200), "Senior Role • Company", fill=text, font=small_font)
        draw.text((mid+20, 220), "2020 – Present", fill=text, font=small_font)
        
    elif template_config["id"] == "header-professional":
        # Header with accent
        draw.rectangle([(0, 0), (width, 80)], fill=primary)
        draw.rectangle([(0, 75), (width, 85)], fill=accent)
        
        draw.text((20, 20), "PROFESSIONAL NAME", fill=(255, 255, 255), font=title_font)
        draw.text((20, 50), "Career Title & Location", fill=bg, font=small_font)
        
        # Content
        draw.text((20, 110), "Profile Summary", fill=primary, font=text_font)
        draw.text((20, 140), "Expert professional with 10+ years", fill=text, font=small_font)
        draw.text((20, 160), "of industry experience", fill=text, font=small_font)
        
        draw.text((20, 200), "Experience", fill=primary, font=text_font)
        draw.text((20, 230), "Senior Position • Organization", fill=text, font=small_font)
        draw.text((20, 250), "2018 – Present", fill=text, font=small_font)
        
        draw.text((20, 290), "Skills & Languages", fill=primary, font=text_font)
        draw.text((20, 320), "Technical: Python, Java, SQL", fill=text, font=small_font)
        
    else:  # minimal-clean
        # Clean minimal layout
        draw.text((20, 20), "PROFESSIONAL NAME", fill=primary, font=title_font)
        draw.text((20, 50), "Career Title", fill=text, font=text_font)
        draw.line([(20, 70), (380, 70)], fill=primary, width=1)
        
        draw.text((20, 100), "PROFILE", fill=primary, font=text_font)
        draw.text((20, 130), "Results-driven professional with", fill=text, font=small_font)
        draw.text((20, 150), "strong analytical and leadership skills", fill=text, font=small_font)
        
        draw.text((20, 190), "EXPERIENCE", fill=primary, font=text_font)
        draw.text((20, 220), "Senior Role | Company Name", fill=text, font=small_font)
        draw.text((20, 240), "2022 – Present", fill=text, font=small_font)
        draw.text((20, 260), "Managed projects and teams", fill=text, font=small_font)
        
        draw.text((20, 300), "SKILLS", fill=primary, font=text_font)
        draw.text((20, 330), "Python, Java, React, SQL, AWS", fill=text, font=small_font)
    
    # Save image
    img.save(output_path, 'PNG', quality=95)
    print(f"✓ Created preview: {output_path}")

def create_default_image(output_path):
    """Create a default fallback image"""
    width, height = 400, 500
    
    img = Image.new('RGB', (width, height), (240, 240, 245))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw placeholder
    draw.rectangle([(40, 150), (360, 350)], outline=(200, 200, 200), width=2)
    draw.text((130, 200), "Template", fill=(100, 100, 100), font=font)
    draw.text((95, 240), "Preview", fill=(100, 100, 100), font=font)
    draw.text((55, 310), "Resume template will appear here", fill=(150, 150, 150), font=small_font)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✓ Created default preview: {output_path}")

# Generate all preview images
print("Generating preview images...")
for template in templates_config:
    output_path = os.path.join(previews_dir, f"{template['id']}.png")
    create_preview_image(template, output_path)

# Create default image
default_path = os.path.join(previews_dir, "default.png")
create_default_image(default_path)

print("\n✓ All preview images generated successfully!")
