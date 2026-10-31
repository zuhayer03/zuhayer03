#!/usr/bin/env python3
"""Animate the EXISTING original GitHub profile SVG artwork without redesign.

Renders each original file at retina resolution, preserving typography, colors,
layout, backgrounds, and original link targets. Only subtle illustration
details move (chart bars, network ring, shield outline, portal orbit, etc.).
The static source SVGs are never overwritten.

Output branch: dist/animated/{identity,mission,network-monitor,finance-tracker,
algoarena,threattrace,portfolio,lab,signoff}.gif and .png.

Requires Pillow and CairoSVG. No synthetic project logos or downloaded stock art.
"""
from __future__ import annotations

from io import BytesIO
import math
from pathlib import Path
import re
import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "animated"
OUT.mkdir(parents=True, exist_ok=True)
FRAMES = 20
DELAY_MS = 125
TAU = math.tau

SOURCES = {
    "identity": ("assets/identity.svg", 1.5),
    "mission": ("assets/current-mission.svg", 1.6),
    "network-monitor": ("assets/feature-network-monitor.svg", 2),
    "finance-tracker": ("assets/feature-finance-tracker.svg", 2),
    "algoarena": ("assets/feature-algoarena.svg", 2),
    "threattrace": ("assets/feature-threattrace.svg", 2),
    "portfolio": ("assets/portal-portfolio.svg", 2),
    "lab": ("assets/portal-lab.svg", 2),
    "signoff": ("assets/signoff.svg", 1.5),
}

def replace_once(svg: str, before: str, after: str) -> str:
    if svg.count(before) != 1:
        raise AssertionError(f"Original SVG changed; expected exactly one: {before[:100]}")
    return svg.replace(before, after, 1)

def add_svg(svg: str, markup: str) -> str:
    if not svg.endswith("</svg>") and not svg.endswith("</svg>\n"):
        raise AssertionError("SVG does not end in </svg>")
    index = svg.rfind("</svg>")
    return svg[:index] + markup + svg[index:]

def bar_update(svg: str, x: int, original_y: int, original_h: int,
               baseline: int, wave: float, amplitude: int = 10) -> str:
    height = max(15, round(original_h + amplitude * wave))
    y = baseline - height
    original = f'<rect x="{x}" y="{original_y}" width="24" height="{original_h}"'
    changed = f'<rect x="{x}" y="{y}" width="24" height="{height}"'
    return replace_once(svg, original, changed)

def alter(slug: str, original: str, frame: int) -> str:
    phase = TAU * frame / FRAMES
    s = original

    if slug == "network-monitor":
        # The original dotted 93px network ring rotates gently.
        angle = 16 * math.sin(phase)
        s = replace_once(s,
            '<circle cx="467" cy="145" r="93" stroke-dasharray="3 11" opacity=".6"/>',
            f'<circle cx="467" cy="145" r="93" stroke-dasharray="3 11" opacity=".6" transform="rotate({angle:.2f} 467 145)"/>')
        # Four real network nodes pulse in place rather than jumping.
        for i, (x,y) in enumerate(((365,65),(580,64),(365,242),(579,242))):
            r = 10 + round(1.2 * math.sin(phase + i * 1.4))
            s = replace_once(s,
                f'<circle cx="{x}" cy="{y}" r="10" fill="#306d59"/>',
                f'<circle cx="{x}" cy="{y}" r="{r}" fill="#306d59"/>')

    elif slug == "finance-tracker":
        # Sample chart bars move a few pixels; the chart and typography remain.
        for i,(x,y,h) in enumerate(((18,145,62),(53,117,90),(88,85,122),(123,136,71),(158,102,105))):
            s=bar_update(s,x,y,h,207,math.sin(phase + i * .72),8)

    elif slug == "algoarena":
        # Sorting bars breathe by a small amount, anchored to the original baseline.
        # These source bars use a translated local coordinate system.
        bars=((0,147,91),(33,81,157),(66,118,120),(99,35,203),
              (132,102,136),(165,65,173),(198,128,110))
        for i,(x,y,h) in enumerate(bars):
            size=max(55,round(h+10*math.sin(phase+i*.83)))
            s=replace_once(s,
                f'<rect x="{x}" y="{y}" width="22" height="{h}" rx="4"/>',
                f'<rect x="{x}" y="{238-size}" width="22" height="{size}" rx="4"/>')

    elif slug == "threattrace":
        # Gently animate the existing shield's outline, no new illustration.
        opacity = .38 + .20*(.5 + .5*math.sin(phase))
        s=replace_once(s,
            'stroke="#91d4a5" opacity=".5" stroke-width="2"',
            f'stroke="#91d4a5" opacity="{opacity:.3f}" stroke-width="2"')
        opacity2=.20 + .25*(.5+.5*math.cos(phase))
        s=add_svg(s,
            f'<path d="M472 41L565 76V170C565 218 527 253 472 275C417 253 379 218 379 170V76z"'
            f' fill="none" stroke="#91d4a5" stroke-width="1.5" opacity="{opacity2:.3f}"/>')

    elif slug == "portfolio":
        # Original two orbital rings move, exactly within the original placement.
        s=replace_once(s,'rotate(-25 507 102)',
            f'rotate({-25+13*math.sin(phase):.2f} 507 102)')
        s=replace_once(s,'rotate(55 507 102)',
            f'rotate({55-10*math.sin(phase):.2f} 507 102)')
        x=507+68*math.cos(phase)
        y=102+34*math.sin(phase)
        s=add_svg(s,f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.3" fill="#efffc5" opacity=".8"/>')

    elif slug == "lab":
        # Same tilted panel and original chart bars; just gentle visual motion.
        s=replace_once(s, 'rotate(8 70 70)',
            f'rotate({8+1.5*math.sin(phase):.2f} 70 70)')
        for i,(x,y,h) in enumerate(((20,107,20),(46,88,39),(72,99,28),(98,72,55))):
            size=max(12,round(h+4*math.sin(phase+i*.7)))
            s=replace_once(s,f'<rect x="{x}" y="{y}" width="17" height="{h}"/>',
                f'<rect x="{x}" y="{127-size}" width="17" height="{size}"/>')

    elif slug == "identity":
        # The original SVG already has native SMIL motion. GIF frames add
        # a minimal glint near the sculpture, without shifting any text.
        x=977+54*math.cos(phase)
        y=278+37*math.sin(phase)
        s=add_svg(s,f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#f2ffc6" opacity=".6"/>')

    elif slug == "mission":
        # The existing progress underline gains a slow traveling marker.
        x=30+353*frame/(FRAMES-1)
        s=add_svg(s,f'<circle cx="{x:.1f}" cy="199" r="4.0" fill="#fbffce" opacity=".72"/>')

    elif slug == "signoff":
        # The arrow remains where it is; only a tiny underline glint travels.
        x=28+620*frame/(FRAMES-1)
        s=add_svg(s,f'<path d="M{x:.1f} 112h28" stroke="#3d5a23" opacity=".45" stroke-width="3" stroke-linecap="round"/>')

    return s

def render_svg(svg: str, scale: float) -> Image.Image:
    # Canvas size explicitly equals original SVG size * retina factor.
    match = re.search(r'<svg[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"',svg)
    if not match:
        raise ValueError("Original SVG has no known size")
    w,h=map(int,match.groups())
    raw=cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                         output_width=round(w*scale), output_height=round(h*scale))
    return Image.open(BytesIO(raw)).convert("RGB")

def publish(name: str, source: Path, scale: float) -> None:
    original=source.read_text(encoding="utf-8").strip()
    frames=[]
    for i in range(FRAMES):
        s=alter(name,original,i)
        frames.append(render_svg(s,scale))
    # Explicit PNG fallback preserves the source's still appearance.
    original_img=render_svg(original,scale)
    original_img.save(OUT / f"{name}.png",optimize=True)
    # Per-frame palette: preserves colored icons and sharp, original typography.
    # No noise or destructive 3D restyling.
    indexed=[f.quantize(colors=224,method=Image.Quantize.MEDIANCUT,
                        dither=Image.Dither.NONE) for f in frames]
    path=OUT / f"{name}.gif"
    indexed[0].save(path,save_all=True,append_images=indexed[1:],
                    duration=DELAY_MS,loop=0,optimize=True,disposal=2)
    with Image.open(path) as output:
        assert output.n_frames >= 10, (name,output.n_frames)
        assert output.width >= 900, (name,output.size)
    assert path.stat().st_size > 2000
    print(f"ANIMATED {name:17} {frames[0].size} {path.stat().st_size:,} bytes",flush=True)

def main() -> None:
    for name,(path,scale) in SOURCES.items():
        publish(name,ROOT/path,scale)
    gifs=sorted(OUT.glob("*.gif"))
    pngs=sorted(OUT.glob("*.png"))
    assert len(gifs)==len(pngs)==len(SOURCES)==9
    print("SUCCESS: animated nine unchanged original source illustrations, "
          "with retina PNG accessibility fallbacks",flush=True)

if __name__=="__main__":
    main()
