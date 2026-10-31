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

def build_pipeline_gif():
    """Animated engineering storyboard: idea -> code -> tests -> ship."""
    frames = []
    stages = [
        ("01 / THINK", "PROBLEM", CYAN),
        ("02 / CODE", "BUILD", PURPLE),
        ("03 / TEST", "VERIFY", PEACH),
        ("04 / SHIP", "RELEASE", LIME),
    ]
    for t in range(64):
        img = Image.new("RGB", (980, 248), BG)
        d = ImageDraw.Draw(img)
        grid(d, 980, 248, 35)
        rounded(d, (8, 8, 971, 240), radius=18)
        d.text((30, 24), "Z/F  //  IDEA TO REALITY", font=F_TITLE, fill=WHITE)
        d.text((782, 29), "BUILD LOOP / 001", font=F_TINY, fill=MUTED)
        stage_index = min(3, t // 16)
        for index, (label, caption, col) in enumerate(stages):
            x = 25 + 236*index
            active = index == stage_index
            complete = index < stage_index
            border = col if active or complete else (45, 75, 58)
            rounded(d, (x, 81, x+217, 184), radius=13,
                    fill=(28, 48, 42) if active else PANEL,
                    outline=border, width=3 if active else 1)
            d.text((x+15, 99), label, font=F_SMALL, fill=col if active or complete else MUTED)
            d.text((x+15, 130), caption, font=F_MED, fill=WHITE if active or complete else MUTED)
            d.rectangle((x+15, 163, x+191, 167), fill=(43, 70, 57))
            if complete:
                width = 176
            elif active:
                width = max(8, int(176*((t % 16)+1)/16))
            else:
                width = 0
            if width:
                d.rectangle((x+15, 163, x+15+width, 167), fill=col)
            if index < 3:
                d.line((x+217, 130, x+235, 130), fill=MUTED, width=2)
        # A luminescent packet moves along the four-stage pathway.
        packet_x = int(55+(t / 63)*855)
        packet_y = int(210+5*math.sin(t*.25))
        d.ellipse((packet_x-6, packet_y-6, packet_x+6, packet_y+6), fill=LIME)
        d.line((27, 211, 954, 211), fill=(47, 68, 57), width=2)
        d.ellipse((packet_x-6, packet_y-6, packet_x+6, packet_y+6), fill=LIME)
        d.text((30, 224), "LEARN DEEPLY  /  BUILD PRACTICALLY  /  SHIP BETTER", font=F_TINY, fill=MUTED)
        frames.append(img)
    save(frames, "build-pipeline.gif", 95)

def spotify_lofi_player_gif():
    """Animated Spotify-style playlist PREVIEW for GitHub README.

    Visual-only GIF; the enclosing README anchor opens the actual public
    Spotify-curated playlist. Never imply sound plays inside GitHub.
    """
    from PIL import Image
    green = (30, 215, 96)
    pale = (236, 245, 237)
    second = (157, 190, 169)
    dark = (9, 17, 18)
    surface = (19, 29, 28)
    overlay = (28, 43, 40)
    mint = (185, 243, 202)
    tiny = font(15)
    subtitle = font(17)
    mid = font(23, True)
    title = font(43, True)
    frames = []
    count = 36
    for t in range(count):
        phase = 2 * math.pi * t / count
        im = Image.new("RGB", (980, 330), dark)
        d = ImageDraw.Draw(im)

        # Familiar streaming-player proportions; self-created artwork.
        d.rounded_rectangle((7, 7, 973, 323), radius=24,
                            fill=surface, outline=(58, 89, 76), width=2)
        d.rounded_rectangle((21, 21, 959, 309), radius=19,
                            fill=dark, outline=(31, 51, 42), width=2)
        d.rounded_rectangle((33, 67, 239, 273), radius=17, fill=(29, 73, 53))
        d.ellipse((41, 74, 231, 266), fill=(19, 51, 43))
        # Original vinyl illustration with rotating reflection streaks.
        cx, cy = 137, 170
        d.ellipse((57, 90, 217, 250), fill=(14, 23, 23), outline=(57, 109, 76), width=4)
        for radius in (61, 47, 33):
            d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                      outline=(48, 75, 59), width=2)
        for offset in (0.4, 2.7, 4.6):
            ang = phase + offset
            x1 = cx + int(42*math.cos(ang))
            y1 = cy + int(42*math.sin(ang))
            x2 = cx + int(62*math.cos(ang))
            y2 = cy + int(62*math.sin(ang))
            d.line((x1, y1, x2, y2), fill=(129, 180, 148), width=5)
        d.ellipse((119, 152, 155, 188), fill=green)
        d.ellipse((132, 165, 142, 175), fill=(18, 34, 26))

        # Brand cue, not a ripped album cover or a playable widget.
        d.ellipse((881, 34, 923, 76), fill=green)
        for shift in (0, 8, 16):
            d.arc((890, 42+shift, 915, 58+shift), 202, 338, fill=(8, 33, 19), width=3)
        d.text((765, 48), "SPOTIFY", font=font(18, True), fill=pale)

        d.text((267, 49), "YOUR FOCUS MIX  /  CURATED PLAYLIST", font=tiny, fill=green)
        d.text((262, 88), "LOFI BEATS", font=title, fill=pale)
        d.text((266, 149), "Soft beats for studying, building & coding.", font=subtitle, fill=second)

        # Deliberately moving equalizer (decorative, not real audio levels).
        d.text((267, 188), "FOCUS SESSION", font=tiny, fill=second)
        for k in range(13):
            x = 473 + k * 17
            h = 12 + int(32 * (0.5 + 0.5 * math.sin(phase*2 + k*0.85)))
            d.rounded_rectangle((x, 216-h, x+8, 216), radius=3,
                                fill=green if k%3!=0 else mint)

        # Player-inspired progress: visual loop, not Spotify song timing.
        d.rounded_rectangle((266, 241, 792, 247), radius=3, fill=(52, 68, 59))
        progress = int((t+1)/count * 526)
        d.rounded_rectangle((266, 241, 266+progress, 247), radius=3, fill=green)
        d.ellipse((261+progress, 238, 271+progress, 250), fill=mint)

        # Large apparent play button; GitHub only supports the whole image link.
        d.ellipse((825, 137, 920, 232), fill=green)
        d.polygon([(862, 161), (862, 208), (895, 185)], fill=(12, 32, 20))
        d.text((268, 276), "CLICK THE PLAYER TO LISTEN ON SPOTIFY  ↗",
               font=tiny, fill=pale)
        d.text((785, 284), "NO AUDIO IN GIF", font=font(11), fill=second)
        frames.append(im)

    # Shared palette reduces flicker; PNG is a reduced-motion alternative.
    still = DEST / "spotify-lofi-player.png"
    frames[0].save(still, optimize=True)
    key = frames[0].quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    palette_frames = [frame.quantize(palette=key, dither=Image.Dither.NONE)
                      for frame in frames]
    target = DEST / "spotify-lofi-player.gif"
    palette_frames[0].save(
        target, save_all=True, append_images=palette_frames[1:],
        duration=110, loop=0, optimize=True, disposal=2
    )
    with Image.open(target) as result:
        assert result.n_frames >= 20, result.n_frames
        assert result.info.get("loop") == 0
    assert target.stat().st_size > 10000
    print(f"Created {target}: {target.stat().st_size:,} bytes "
          f"({len(frames)} looping frames); still: {still}", flush=True)


if __name__ == "__main__":
    terminal_gif()
    tools_gif()
    build_pipeline_gif()
    spotify_lofi_player_gif()
