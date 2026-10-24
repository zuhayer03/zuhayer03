#!/usr/bin/env python3
"""Generate small, real-logo, animated GIF tool tiles for the GitHub README.

The 29 source icon URLs/local SVGs are pinned in scripts/tool_icons.json.
Each GIF animates its corresponding brand icon, not a substitute monogram.
Output: dist/tool-animations/<name>.gif. Python 3.12, Pillow, cairosvg.
"""
from __future__ import annotations

import io
import json
import math
import random
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFilter

try:
    import cairosvg
except ImportError as exc:
    raise RuntimeError("Install cairosvg and pillow before generating icons") from exc

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts" / "tool_icons.json"
TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
OUT = TARGET / "tool-animations"
OUT.mkdir(parents=True, exist_ok=True)

ACCENTS = [
    (215, 255, 100),
    (132, 230, 203),
    (194, 166, 241),
    (255, 185, 140),
    (120, 199, 247),
    (238, 143, 191),
    (170, 225, 139),
]
DARK = (13, 23, 22)
WHITE = (245, 249, 237)
SIZE = 96
FRAME_COUNT = 20

def icon_bytes(source: str) -> bytes:
    if source.startswith("assets/"):
        target = ROOT / source
        return target.read_bytes()
    if not source.startswith("https://"):
        raise ValueError("Unexpected icon URI: " + source)
    last_exc = None
    for attempt in range(4):
        try:
            request = Request(source, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ZF-GitHub-Animated-Icons/1.0)",
                "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*,*/*;q=0.7",
            })
            with urlopen(request, timeout=22) as response:
                data = response.read(2_000_000)
            if not data:
                raise ValueError("Empty remote logo")
            return data
        except Exception as exc:
            last_exc = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"Could not fetch {source}: {last_exc}")

def load_logo(source: str) -> Image.Image:
    raw = icon_bytes(source)
    if b"<svg" in raw[:500] or source.lower().split("?")[0].endswith(".svg"):
        # CairoSVG resolves actual brand SVG paths to pixels; no label substitution.
        png = cairosvg.svg2png(bytestring=raw, output_width=120, output_height=120)
        logo = Image.open(io.BytesIO(png)).convert("RGBA")
    else:
        logo = Image.open(io.BytesIO(raw)).convert("RGBA")
    logo.thumbnail((86, 86), Image.Resampling.LANCZOS)
    if not logo.width or not logo.height:
        raise ValueError("Zero-size logo from " + source)
    return logo

def palette_from_image(img: Image.Image):
    return img.convert("RGB").quantize(colors=160, method=Image.Quantize.MEDIANCUT)

def render_frame(logo: Image.Image, accent, style: str, t: int) -> Image.Image:
    # Draw at 2x then downsample. No animations rely on external CSS or JS.
    canvas = Image.new("RGBA", (SIZE * 2, SIZE * 2), DARK + (255,))
    d = ImageDraw.Draw(canvas, "RGBA")
    cx = cy = SIZE
    phase = 2 * math.pi * t / FRAME_COUNT
    pulse = math.sin(phase)
    tilt = 0.0
    float_y = 0.0
    scale = 1.0
    if style in ("float", "bob"):
        float_y = -4.0 * math.sin(phase)
    if style in ("tilt", "orbit"):
        tilt = 5.0 * math.sin(phase)
    if style == "pulse":
        scale = 1.0 + .055 * math.sin(phase)
    if style == "shine":
        float_y = -2.5 * math.sin(phase)
    if style == "sweep":
        tilt = -3.0 * math.sin(phase)

    # Slow luminous orbital ring; fixed geometry but moving luminous marker.
    ring_r = 84 + int(1.7 * math.sin(phase))
    d.ellipse((cx-ring_r, cy-ring_r, cx+ring_r, cy+ring_r),
              outline=(*accent, 110), width=3)
    arc_start = int((t / FRAME_COUNT) * 360) - 75
    d.arc((cx-ring_r, cy-ring_r, cx+ring_r, cy+ring_r),
          start=arc_start, end=arc_start + 69,
          fill=(*accent, 235), width=6)
    ex = cx + ring_r*math.cos(math.radians(arc_start + 70))
    ey = cy + ring_r*math.sin(math.radians(arc_start + 70))
    d.ellipse((ex-5, ey-5, ex+5, ey+5), fill=(*accent, 255))

    # Light neutral panel guarantees actual black logos remain visible.
    y_offset = int(float_y*2)
    shadow = (cx-64, cy-59+y_offset, cx+66, cy+71+y_offset)
    d.rounded_rectangle(shadow, radius=31, fill=(0, 0, 0, 75))
    panel = (cx-65, cy-64+y_offset, cx+65, cy+66+y_offset)
    d.rounded_rectangle(panel, radius=31, fill=WHITE+(255,),
                        outline=(*accent, 235), width=3)
    # Shine swipe around border, not over the brand symbol.
    if style in ("shine", "sweep"):
        sx = int(cx - 45 + (t / (FRAME_COUNT - 1)) * 90)
        d.line([(sx-16, cy-61+y_offset), (sx+16, cy-61+y_offset)],
               fill=(*accent, 235), width=4)

    # Do not warp/replace the product logo, only gentle rotation and float.
    px = 100
    ratio = min(px / logo.width, px / logo.height)
    adjusted = logo.resize((
        max(1, int(logo.width*ratio*scale)),
        max(1, int(logo.height*ratio*scale))),
        Image.Resampling.LANCZOS)
    if tilt:
        adjusted = adjusted.rotate(tilt, expand=True, resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(adjusted, (
        cx - adjusted.width//2,
        cy - adjusted.height//2+y_offset))
    return canvas.convert("RGB").resize((SIZE,SIZE),Image.Resampling.LANCZOS)

def render_tool(tool, index: int) -> int:
    slug = tool["id"]
    logo = load_logo(tool["source"])
    accent = ACCENTS[index % len(ACCENTS)]
    frames = [render_frame(logo, accent, tool["style"], t)
              for t in range(FRAME_COUNT)]
    master = palette_from_image(frames[0])
    palette_frames = [frame.quantize(palette=master, dither=Image.Dither.NONE)
                      for frame in frames]
    filename = OUT / (slug + ".gif")
    palette_frames[0].save(
        filename, format="GIF", save_all=True,
        append_images=palette_frames[1:], duration=110,
        loop=0, optimize=True, disposal=2
    )
    # A real animation must contain multiple distinct frames.
    with Image.open(filename) as check:
        actual_frames = getattr(check, "n_frames", 1)
        if actual_frames < 5:
            raise AssertionError(f"Not a moving GIF: {slug} only {actual_frames} frames")
    print(f"{slug:25} {filename.stat().st_size:>8} bytes  {actual_frames} frames", flush=True)
    return filename.stat().st_size

def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["tools"]
    names = [item["id"] for item in manifest]
    assert len(manifest) == 29 and len(set(names)) == 29, "Expected 29 unique tool logos"
    total = 0
    for index, item in enumerate(manifest):
        total += render_tool(item, index)
    output = list(OUT.glob("*.gif"))
    assert len(output) == len(manifest), f"{len(output)} GIFs for {len(manifest)} tools"
    print(f"SUCCESS: {len(output)} animated brand GIFs, {total/1_000_000:.2f} MB total")

if __name__ == "__main__":
    main()
