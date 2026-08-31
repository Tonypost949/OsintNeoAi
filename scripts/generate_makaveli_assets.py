import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_holographic_eye(size=1024, chromatic_intensity=0.5, bg_color=(10, 14, 23, 255), transparent=False, white_stroke=False):
    # Create base RGBA canvas
    if transparent:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    else:
        img = Image.new("RGBA", (size, size), bg_color)
    
    center = (size // 2, size // 2)
    radius = int(size * 0.42)
    
    # Separate channels for chromatic aberration
    r_img = Image.new("L", (size, size), 0)
    g_img = Image.new("L", (size, size), 0)
    b_img = Image.new("L", (size, size), 0)
    
    # Master grayscale template
    master = Image.new("L", (size, size), 0)
    m_draw = ImageDraw.Draw(master)
    
    cx, cy = center
    
    # Outer tactical radar rings
    for r in [radius, int(radius * 0.88), int(radius * 0.72), int(radius * 0.52), int(radius * 0.32), int(radius * 0.12)]:
        m_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=max(2, size // 300))
    
    # Radar tick marks
    num_ticks = 36
    for i in range(num_ticks):
        angle = (2 * math.pi / num_ticks) * i
        r_inner = radius if i % 3 != 0 else int(radius * 0.92)
        r_outer = int(radius * 1.06)
        x1 = cx + int(r_inner * math.cos(angle))
        y1 = cy + int(r_inner * math.sin(angle))
        x2 = cx + int(r_outer * math.cos(angle))
        y2 = cy + int(r_outer * math.sin(angle))
        m_draw.line([(x1, y1), (x2, y2)], fill=255, width=max(2, size // 400))
        
    # Crosshairs / Tactical Grid
    m_draw.line([(cx - radius * 1.1, cy), (cx + radius * 1.1, cy)], fill=200, width=max(1, size // 500))
    m_draw.line([(cx, cy - radius * 1.1), (cx, cy + radius * 1.1)], fill=200, width=max(1, size // 500))
    
    # Eye Shape (Almond Arc)
    eye_w = int(radius * 0.85)
    eye_h = int(radius * 0.45)
    
    points_up = []
    points_down = []
    for step in range(-eye_w, eye_w + 1, 4):
        norm = step / eye_w
        y_offset = int((1.0 - norm**2) * eye_h)
        points_up.append((cx + step, cy - y_offset))
        points_down.append((cx + step, cy + y_offset))
    
    m_draw.line(points_up, fill=255, width=max(4, size // 150))
    m_draw.line(points_down, fill=255, width=max(4, size // 150))
    
    # Iris & Pupil
    iris_r = int(radius * 0.38)
    pupil_r = int(radius * 0.16)
    m_draw.ellipse([cx - iris_r, cy - iris_r, cx + iris_r, cy + iris_r], outline=255, width=max(3, size // 200))
    m_draw.ellipse([cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r], fill=255)
    
    # Hexagon overlay
    hex_r = int(radius * 0.6)
    hex_points = []
    for i in range(6):
        a = (math.pi / 3) * i - (math.pi / 6)
        hx = cx + int(hex_r * math.cos(a))
        hy = cy + int(hex_r * math.sin(a))
        hex_points.append((hx, hy))
    hex_points.append(hex_points[0])
    m_draw.line(hex_points, fill=180, width=max(2, size // 350))
    
    # Nodes around perimeter
    node_r = int(radius * 0.78)
    for i in range(8):
        a = (2 * math.pi / 8) * i + 0.2
        nx = cx + int(node_r * math.cos(a))
        ny = cy + int(node_r * math.sin(a))
        m_draw.rectangle([nx - 6, ny - 6, nx + 6, ny + 6], fill=255)
        m_draw.line([(cx, cy), (nx, ny)], fill=100, width=1)

    # Chromatic aberration offsets
    offset_dist = int(12 * chromatic_intensity * (size / 512.0))
    
    # Paste channels with slight offset
    r_img.paste(master, (-offset_dist, -offset_dist // 2))
    g_img.paste(master, (0, 0))
    b_img.paste(master, (offset_dist, offset_dist // 2))
    
    # Channel colors
    r_channel = r_img.point(lambda p: int(p * 0.45 * chromatic_intensity + p * 0.1))
    g_channel = g_img.point(lambda p: int(p * 0.85))
    b_channel = b_img.point(lambda p: int(min(255, p * 1.35)))
    
    alpha_bright = master.point(lambda p: min(255, p * 2))
    
    # Glow layers
    glow = master.filter(ImageFilter.GaussianBlur(radius=int(size * 0.045)))
    glow_color = Image.new("RGBA", (size, size), (0, 210, 255, 0))
    glow_alpha = glow.point(lambda p: int(p * 0.85))
    glow_color.putalpha(glow_alpha)
    
    inner_glow = master.filter(ImageFilter.GaussianBlur(radius=int(size * 0.015)))
    inner_glow_color = Image.new("RGBA", (size, size), (140, 90, 255, 0))
    inner_glow_alpha = inner_glow.point(lambda p: int(p * 0.65 * chromatic_intensity))
    inner_glow_color.putalpha(inner_glow_alpha)

    # Composite
    comp_rgb = Image.merge("RGB", (r_channel, g_channel, b_channel))
    comp_rgba = comp_rgb.convert("RGBA")
    comp_rgba.putalpha(alpha_bright)
    
    final_canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0) if transparent else bg_color)
    final_canvas = Image.alpha_composite(final_canvas, glow_color)
    final_canvas = Image.alpha_composite(final_canvas, inner_glow_color)
    final_canvas = Image.alpha_composite(final_canvas, comp_rgba)
    
    # White stroke if requested
    if white_stroke:
        stroke_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(stroke_img)
        s_draw.ellipse([cx - radius * 1.12, cy - radius * 1.12, cx + radius * 1.12, cy + radius * 1.12], outline=(255, 255, 255, 230), width=max(4, size // 120))
        final_canvas = Image.alpha_composite(final_canvas, stroke_img)
        
    return final_canvas

def create_banner(width=820, height=312, dark=True):
    bg_color = (8, 12, 22, 255) if dark else (245, 248, 252, 255)
    banner = Image.new("RGBA", (width, height), bg_color)
    
    eye_size = int(height * 0.88)
    eye = create_holographic_eye(size=eye_size, chromatic_intensity=0.5, transparent=True)
    
    banner.paste(eye, (24, (height - eye_size) // 2), eye)
    
    draw = ImageDraw.Draw(banner)
    grid_color = (0, 180, 255, 25 if dark else 15)
    for x in range(0, width, 30):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 30):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
    text_x = eye_size + 45
    t_primary = (0, 230, 255) if dark else (10, 40, 95)
    t_secondary = (255, 255, 255) if dark else (20, 25, 35)
    t_muted = (120, 160, 200) if dark else (90, 105, 130)
    
    draw.text((text_x, int(height * 0.20)), "MAKAVELI", fill=t_secondary)
    draw.text((text_x + 100, int(height * 0.20)), "// OSINT AGENT", fill=t_primary)
    draw.text((text_x, int(height * 0.42)), "ZERO-NOISE FORENSIC INTELLIGENCE ENGINE", fill=t_primary)
    draw.text((text_x, int(height * 0.58)), "MISSION: CORRELATE. DEANONYMIZE. EXPOSE.", fill=t_muted)
    draw.text((text_x, int(height * 0.74)), "STATUS: PUBLIC ENFORCEMENT // LIVE HUD // GITHUB SYNC", fill=t_muted)
    
    draw.line([(width - 40, 20), (width - 20, 20), (width - 20, 40)], fill=t_primary, width=2)
    draw.line([(width - 40, height - 20), (width - 20, height - 20), (width - 20, height - 40)], fill=t_primary, width=2)
    
    return banner

def generate_all():
    out_dirs = [
        r"C:\OSINTNEOAI\makavelli\avatar",
        r"C:\OSINTNEOAI\makaveli\avatar"
    ]
    
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)
        
    print("Generating Master Holographic Eye Avatar (1024x1024)...")
    master_1024 = create_holographic_eye(size=1024, chromatic_intensity=0.5, transparent=False)
    master_trans_1024 = create_holographic_eye(size=1024, chromatic_intensity=0.5, transparent=True)
    master_white_stroke = create_holographic_eye(size=1024, chromatic_intensity=0.5, transparent=True, white_stroke=True)
    master_25pct = create_holographic_eye(size=1024, chromatic_intensity=0.25, transparent=False)
    
    fb_180 = master_1024.resize((180, 180), Image.Resampling.LANCZOS)
    ig_320 = master_1024.resize((320, 320), Image.Resampling.LANCZOS)
    
    banner_dark = create_banner(820, 312, dark=True)
    banner_light = create_banner(820, 312, dark=False)
    
    files_to_save = {
        "holographic_eye_avatar.png": master_1024,
        "holographic_eye_avatar.webp": master_1024,
        "circular_transparent.png": master_trans_1024,
        "holographic_eye_avatar_white_stroke_transparent.png": master_white_stroke,
        "neon_blue_circular_25percent.png": master_25pct,
        "neon_blue_circular_25percent.webp": master_25pct,
        "osint_neo_ai_logo.png": master_1024,
        "osint_neo_ai_logo.webp": master_1024,
        "facebook_avatar_180.png": fb_180,
        "instagram_avatar_320.png": ig_320,
        "highres_1024.png": master_1024,
        "banner_black.png": banner_dark,
        "banner_black.webp": banner_dark,
        "banner_white.png": banner_light,
        "banner_white.webp": banner_light,
    }
    
    for d in out_dirs:
        for fname, img in files_to_save.items():
            fpath = os.path.join(d, fname)
            img.save(fpath)
            print(f"Saved: {fpath}")
            
    print("All avatar and banner assets successfully generated.")

if __name__ == "__main__":
    generate_all()
