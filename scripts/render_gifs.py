#!/usr/bin/env python3
"""Render original lightweight GIF artwork for the Z✳F GitHub profile.

Uses only Pillow. These are portfolio illustrations, not recordings of the CLI tools.
Run: python scripts/render_gifs.py [destination-dir]
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import sys

DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
DEST.mkdir(parents=True, exist_ok=True)

BG = (10, 18, 17)
PANEL = (18, 29, 27)
LIME = (217, 255, 101)
WHITE = (238, 245, 229)
MUTED = (145, 170, 153)
CYAN = (121, 222, 202)
PURPLE = (185, 159, 232)
PEACH = (246, 183, 151)

def font(size, bold=False):
    options = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for path in options:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

F_SMALL = font(15)
F_TINY = font(12)
F_MED = font(20, True)
F_BIG = font(29, True)
F_TITLE = font(24, True)

def rounded(draw, rect, radius=18, fill=PANEL, outline=(51, 83, 69), width=2):
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)

def grid(draw, w, h, step=34):
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(19, 37, 32))
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(19, 37, 32))

def save(frames, name, duration):
    out = DEST / name
    # Use a shared fixed palette to prevent color popping between frames.
    palette = [BG, PANEL, LIME, WHITE, MUTED, CYAN, PURPLE, PEACH,
               (45, 75, 58), (28, 48, 42), (52, 68, 59), (110, 143, 94),
               (43, 69, 63), (32, 42, 39), (71, 90, 74), (244, 215, 156)]
    palette_bytes = []
    for color in palette:
        palette_bytes.extend(color)
    palette_bytes += [0] * (768 - len(palette_bytes))
    paletted = []
    for frame in frames:
        canvas = Image.new("P", frame.size)
        canvas.putpalette(palette_bytes)
        # Quantize each frame against the same palette.
        canvas = frame.quantize(palette=canvas, dither=Image.Dither.NONE)
        paletted.append(canvas)
    paletted[0].save(out, save_all=True, append_images=paletted[1:],
                     duration=duration, loop=0, optimize=False, disposal=2)
    print(f"Created {out}: {out.stat().st_size:,} bytes")

def terminal_gif():
    frames = []
    command = "build --with-purpose"
    stages = ["JAVA / DSA / FUNDAMENTALS", "PYTHON / PRACTICAL TOOLS", "AI / AUTOMATION / RESEARCH"]
    steps = 46
    for t in range(steps):
        img = Image.new("RGB", (980, 274), BG)
        d = ImageDraw.Draw(img)
        grid(d, 980, 274, 40)
        rounded(d, (9, 9, 971, 264), 20)
        d.rounded_rectangle((9, 9, 971, 55), radius=18, fill=(28, 43, 37))
        d.rectangle((10, 39, 970, 55), fill=(28, 43, 37))
        for x, c in ((35, PEACH), (55, LIME), (75, CYAN)):
            d.ellipse((x-6, 26, x+6, 38), fill=c)
        d.text((107, 24), "zuhayer@github  /  WORKSPACE", font=F_SMALL, fill=WHITE)
        d.text((855, 24), "● LIVE", font=F_SMALL, fill=LIME)
        d.text((32, 78), "zuhayer@github:~$", font=F_MED, fill=CYAN)
        n = max(0, min(len(command), t-4))
        x = 258
        typed = command[:n]
        d.text((x, 78), typed, font=F_MED, fill=WHITE)
        if t % 8 < 5:
            bbox = d.textbbox((0, 0), typed, font=F_MED)
            d.rectangle((x+bbox[2]+4, 82, x+bbox[2]+14, 100), fill=LIME)
        d.line((32, 120, 947, 120), fill=(58, 91, 69), width=2)
        for i, s in enumerate(stages):
            y = 137 + i*36
            awake = t > 14 + i*7
            c = LIME if awake else MUTED
            symbol = "✓" if awake else "·"
            # Some monospaced fonts lack checkmark; simple geometric status icon is reliable.
            d.ellipse((36, y+6, 48, y+18), fill=c if awake else (47, 68, 57))
            d.text((62, y), s, font=F_SMALL, fill=WHITE if awake else MUTED)
            if awake:
                d.text((816, y), "[ READY ]", font=F_SMALL, fill=LIME)
        d.text((32, 252), "Z✳F / SOFTWARE · SYSTEMS · CURIOSITY", font=F_TINY, fill=MUTED)
        frames.append(img)
    save(frames, "dev-console.gif", 90)

def tools_gif():
    groups = [
      ("01 / CORE CODE", "JAVA   PYTHON   GIT   GITHUB   VSCODE   INTELLIJ", CYAN),
      ("02 / AI CODING", "CURSOR   COPILOT   CLAUDE CODE   ANTIGRAVITY", PURPLE),
      ("03 / AGENTS", "LANGGRAPH   GOOGLE ADK   LIVEKIT   BROWSER USE", LIME),
      ("04 / AUTOMATION", "COMPOSIO   PAPERCLIP   WORKFLOWS", PEACH),
      ("05 / AI INFRA", "HUGGING FACE   OLLAMA   SUPABASE AI   E2B", CYAN),
      ("06 / CODE QUALITY", "CODERABBIT   LANGSMITH   SENTRY SEER", PURPLE),
      ("07 / CREATIVE", "FIGMA   NOTION   NOTEBOOKLM   PERPLEXITY", PEACH),
      ("08 / PRACTICE", "LEETCODE   NEETCODE", LIME),
    ]
    frames = []
    # 8 categories, 7 frames each for readable GIF.
    for i, (title, sub, color) in enumerate(groups):
        for step in range(7):
            img = Image.new("RGB", (980, 196), BG)
            d = ImageDraw.Draw(img)
            grid(d, 980, 196, 41)
            rounded(d, (8, 8, 971, 188), 19)
            d.rectangle((15, 16, 20, 180), fill=color)
            d.text((39, 25), "THE TOOL UNIVERSE / Z✳F", font=F_SMALL, fill=MUTED)
            d.text((39, 60), title, font=F_BIG, fill=color)
            d.text((39, 119), sub, font=F_SMALL, fill=WHITE)
            d.text((800, 25), "08 MODES", font=F_TINY, fill=MUTED)
            for j in range(8):
                x = 40 + j*110
                d.rounded_rectangle((x, 160, x+98, 166), radius=3, fill=color if j == i else (43, 70, 57))
            d.text((835, 177), f"{i+1:02d} / 08", font=F_TINY, fill=MUTED)
            frames.append(img)
    save(frames, "tool-reel.gif", 145)

if __name__ == "__main__":
    terminal_gif()
    tools_gif()
