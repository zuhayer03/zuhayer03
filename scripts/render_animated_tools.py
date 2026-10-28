#!/usr/bin/env python3
"""ZF / Neon Atelier — cinematic, real-logo GIF cards and category showcase.

Real icon sources: scripts/tool_icons.json. No fabricated tool logos.
Outputs 29 independently animated 200 px GIFs and one widescreen showcase.
All animation is baked into actual GIF frames for GitHub README support.
"""
from __future__ import annotations
import io
import json
import math
import random
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
OUT = TARGET / "tool-animations"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 200
FRAMES = 24
BASE = (10, 17, 25)
IVORY = (242, 251, 238)
COLORS = [
    (219, 255, 106), (127, 233, 215), (186, 157, 255),
    (255, 165, 121), (98, 183, 253), (250, 125, 189), (157, 242, 164),
]
GROUPS = [
    ("01", "CORE / CODE", 0, 6),
    ("02", "AI / CODING", 6, 10),
    ("03", "AGENT SYSTEMS", 10, 16),
    ("04", "MODEL / INFRA", 16, 20),
    ("05", "QUALITY / CODE", 20, 23),
    ("06", "DESIGN / RESEARCH", 25, 29),
    ("07", "PRACTICE / DSA", 23, 25),
]
GROUP_COLORS = [(207,255,91),(166,153,255),(89,222,200),(104,189,254),
                (255,151,172),(255,174,126),(153,243,151)]

def font(size, bold=False):
    filenames = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for filename in filenames:
        if Path(filename).is_file():
            return ImageFont.truetype(filename,size)
    return ImageFont.load_default()

def icon_data(source):
    if source.startswith("assets/"):
        return (ROOT / source).read_bytes()
    if not source.startswith("https://"):
        raise ValueError("Not an allowed icon source")
    last = None
    for attempt in range(4):
        try:
            req = Request(source,headers={
                "User-Agent":"Mozilla/5.0 (compatible; ZF-Animated-Icon-Art/2.0)",
                "Accept":"image/svg+xml,image/webp,image/png,image/*,*/*;q=0.8",
            })
            with urlopen(req,timeout=24) as response:
                data=response.read(2_000_000)
            if data:return data
            raise ValueError("Empty icon")
        except Exception as exc:
            last=exc
            time.sleep(attempt+1)
    raise RuntimeError(f"Failed to retrieve {source}: {last}")

def logo_for(source):
    raw=icon_data(source)
    if b"<svg" in raw[:650] or source.lower().split("?")[0].endswith(".svg"):
        png=cairosvg.svg2png(bytestring=raw,output_width=360,output_height=360)
        logo=Image.open(io.BytesIO(png)).convert("RGBA")
    else:
        logo=Image.open(io.BytesIO(raw)).convert("RGBA")
    logo.thumbnail((310,310),Image.Resampling.LANCZOS)
    if logo.width<8 or logo.height<8:
        raise ValueError("Source icon too small: "+source)
    return logo

def accent(index):
    for cat,group in enumerate(GROUPS):
        if group[2] <= index < group[3]:
            return GROUP_COLORS[cat],group[0]
    return COLORS[index%len(COLORS)],"ZF"

def rect(draw,box,fill,radius=15,outline=None,width=1):
    draw.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)

def mix(a,b,t):
    return tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))

def prepare_background(color):
    w=SIZE*2
    im=Image.new("RGB",(w,w),BASE)
    d=ImageDraw.Draw(im)
    # Chiaroscuro colored halo, composited once for every tile.
    layer=Image.new("RGBA",(w,w))
    gl=ImageDraw.Draw(layer,"RGBA")
    for rad in range(190,30,-14):
        opacity=2+int((190-rad)*.038)
        gl.ellipse((200-rad,196-rad,200+rad,196+rad),fill=(*color,opacity))
    layer=layer.filter(ImageFilter.GaussianBlur(19))
    im=Image.alpha_composite(im.convert("RGBA"),layer)
    d=ImageDraw.Draw(im,"RGBA")
    # Technical grid with restrained noise and depth.
    for q in range(20,w,40):
        d.line((q,0,q,w),fill=(177,226,202,15))
        d.line((0,q,w,q),fill=(177,226,202,15))
    # Shape language: beveled glass card, strong corner trim.
    rect(d,(12,12,388,388),(11,21,28,255),36,(*color,118),3)
    rect(d,(22,22,378,378),(15,28,35,255),28,(*color,27),2)
    d.line((44,26,148,26),fill=(*color,220),width=4)
    d.line((26,43,26,136),fill=(*color,170),width=3)
    d.line((251,374,357,374),fill=(*color,180),width=3)
    # Frosted emblem mounting surface; does not erase the brand mark colors.
    rect(d,(103,104,297,298),(25,40,48,247),51,(*color,145),3)
    rect(d,(111,112,289,290),(19,31,38,210),45,(215,246,226,30),2)
    d.text((39,43),"ZF / TOOL SYSTEM",font=font(14,True),fill=(176,215,190,220))
    d.text((40,337),"ENGINEERING  /  ACTIVE",font=font(12,False),fill=(130,166,149,205))
    d.text((339,332),"↗",font=font(29,True),fill=(*color,255))
    return im

def glow_logo(logo):
    px=146
    factor=min(px/logo.width,px/logo.height)
    dims=(max(1,round(logo.width*factor)),max(1,round(logo.height*factor)))
    img=logo.resize(dims,Image.Resampling.LANCZOS)
    return img

def anim_frame(background,logo,color,style,t,index):
    W=SIZE*2
    angle=t*2*math.pi/FRAMES
    frame=background.copy()
    d=ImageDraw.Draw(frame,"RGBA")
    cx,cy=200,201
    orbit=148
    # 3D-style elliptical orbits with live moving beacons.
    d.arc((cx-orbit,cy-112,cx+orbit,cy+112),8,170,fill=(*color,145),width=3)
    d.arc((cx-orbit,cy-112,cx+orbit,cy+112),191,353,fill=(*color,72),width=3)
    arc_t=angle+(index%4)*1.5
    bx=cx+orbit*math.cos(arc_t)
    by=cy+112*math.sin(arc_t)
    d.ellipse((bx-8,by-8,bx+8,by+8),fill=(*color,255))
    # Secondary particle counter-orbits create depth, not a generic blinking ring.
    for k in range(3):
        th=-angle*.75+k*math.tau/3
        xx=cx+115*math.cos(th)
        yy=cy+153*math.sin(th)
        rr=(3,4,3)[k]
        d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(*color,110+40*k))
    # Sweep only within the deep background, never across the logo.
    sx=int((t/FRAMES)*270+42)
    d.line((sx,315,sx+45,315),fill=(*color,175),width=4)
    # Different motion signatures per product.
    up=-8*math.sin(angle) if style in ("float","bob") else -3*math.sin(angle)
    pitch=5*math.sin(angle) if style in ("tilt","orbit","sweep") else 0
    swell=1.04+(.045*math.sin(angle) if style in ("pulse","shine") else .015*math.sin(angle))
    img=logo.resize((round(logo.width*swell),round(logo.height*swell)),Image.Resampling.LANCZOS)
    if pitch:
        img=img.rotate(pitch,expand=True,resample=Image.Resampling.BICUBIC)
    # Crisp brand logo over a soft floor glow.
    a=frame.copy()
    halo=Image.new("RGBA",(W,W))
    hh=ImageDraw.Draw(halo,"RGBA")
    hh.ellipse((149,254+up,251,272+up),fill=(*color,110))
    frame=Image.alpha_composite(a,halo.filter(ImageFilter.GaussianBlur(17)))
    if index == 3:
        # GitHub's genuine dark octocat mark needs a luminous contrasting surface.
        # Leave the source logo unchanged; illuminate only its backing plate.
        plaque=ImageDraw.Draw(frame,"RGBA")
        plaque.rounded_rectangle((120,121,280,281),radius=45,
            fill=(206,235,213,255),outline=(*color,245),width=4)
    frame.alpha_composite(img,(cx-img.width//2,cy-img.height//2+round(up)))
    d=ImageDraw.Draw(frame,"RGBA")
    d.text((320,45),f"{index+1:02}",font=font(18,True),fill=(*color,235))
    # Twinkling edge highlights give each tile a living feel.
    pulse=max(0,math.sin(angle+index))
    pr=2+round(pulse*4)
    d.ellipse((351-pr,69-pr,351+pr,69+pr),fill=(*color,170+round(pulse*85)))
    return frame.convert("RGB").resize((SIZE,SIZE),Image.Resampling.LANCZOS)

def gif_save(frames,dest,duration=92):
    # Single shared palette minimizes flicker across frames.
    source=frames[0].quantize(colors=224,method=Image.Quantize.MEDIANCUT)
    quant=[f.quantize(palette=source,dither=Image.Dither.NONE) for f in frames]
    quant[0].save(dest,save_all=True,append_images=quant[1:],loop=0,
                  duration=duration,optimize=True,disposal=2)
    with Image.open(dest) as probe:
        assert probe.n_frames>=12, (dest,probe.n_frames)

def render_tiles(tools,logos):
    for i,tool in enumerate(tools):
        color,_=accent(i)
        logo=glow_logo(logos[i])
        background=prepare_background(color)
        frames=[anim_frame(background,logo,color,tool["style"],t,i) for t in range(FRAMES)]
        outfile=OUT/(tool["id"]+".gif")
        gif_save(frames,outfile)
        print(f"ICON {i+1:02}/29  {tool['id']}: {outfile.stat().st_size:,} bytes",flush=True)

def sci_bg(w,h):
    bg=Image.new("RGB",(w,h),(8,15,21))
    d=ImageDraw.Draw(bg,"RGB")
    for y in range(h):
        t=y/h
        d.line((0,y,w,y),fill=(round(7+8*t),round(15+13*t),round(23+17*t)),width=1)
    grid=ImageDraw.Draw(bg,"RGBA")
    for x in range(15,w,50):
        grid.line((x,0,x,h),fill=(129,187,150,26),width=1)
    for y in range(15,h,50):
        grid.line((0,y,w,y),fill=(129,187,150,26),width=1)
    return bg

def render_showcase(tools,logos):
    w,h=1120,370
    bg=sci_bg(w,h)
    frames=[]
    for t in range(42):
        frame=bg.copy().convert("RGBA")
        d=ImageDraw.Draw(frame,"RGBA")
        cat=t//6
        phase=(t%6)/6
        color=GROUP_COLORS[cat]
        number,title,start,end=GROUPS[cat]
        # Glowing dimensional central orbital engine.
        center=(810,190)
        for rad in range(154,69,-14):
            d.ellipse((center[0]-rad,center[1]-rad,center[0]+rad,center[1]+rad),
                      fill=(*color,5),outline=(*color,12),width=1)
        d.ellipse((center[0]-106,center[1]-106,center[0]+106,center[1]+106),
                  fill=(17,32,43,255),outline=(*color,190),width=4)
        d.ellipse((center[0]-72,center[1]-72,center[0]+72,center[1]+72),
                  fill=(24,50,54,255),outline=(*color,100),width=3)
        d.arc((center[0]-160,center[1]-126,center[0]+160,center[1]+126),
              int(phase*360)-95,int(phase*360)+135,fill=(*color,220),width=5)
        d.arc((center[0]-180,center[1]-92,center[0]+180,center[1]+92),
              int(-phase*360)-70,int(-phase*360)+45,fill=(*color,140),width=3)
        d.text((748,168),"Z/F",font=font(54,True),fill=(*color,245))
        d.text((40,30),"CREATIVE ENGINEERING / ZF",font=font(17,True),fill=(*color,255))
        d.text((986,31),"LIVE / 29",font=font(14,True),fill=(178,220,191,245))
        d.line((40,59,1070,59),fill=(*color,110),width=2)
        d.text((40,92),number+" / "+title,font=font(27,True),fill=(243,249,237,255))
        d.text((40,133),"TOOLS DON'T BUILD IDEAS.",font=font(22,True),fill=(162,190,175,255))
        d.text((40,163),"PEOPLE DO. BUILD SMARTER.",font=font(22,True),fill=(*color,255))
        # All seven groups cycle through: 3-4 actual brand logos, not fake badges.
        subset=list(range(start,end))[:4]
        for slot,idx in enumerate(subset):
            x=55+slot*116
            rect(d,(x,213,x+100,312),(19,35,42,255),16,(*color,105),2)
            current=logos[idx]
            f=min(64/current.width,64/current.height)
            pic=current.resize((max(1,int(current.width*f)),max(1,int(current.height*f))),
                               Image.Resampling.LANCZOS)
            frame.alpha_composite(pic,(x+50-pic.width//2,y_pos:=258-pic.height//2+round(3*math.sin(phase*math.tau+slot))))
            label=tools[idx]["name"].upper()[:12]
            d.text((x+5,317),label,font=font(10,True),fill=(175,211,186,255))
        d.text((41,350),"CYCLE THROUGH ALL 7 TECHNOLOGY DOMAINS",font=font(14,True),
               fill=(133,171,150,255))
        # Beam traveling along a lower track.
        bx=600+phase*500
        d.line((600,350,1090,350),fill=(*color,70),width=2)
        d.ellipse((bx-5,345,bx+5,355),fill=(*color,245))
        frames.append(frame.convert("RGB"))
    dest=TARGET/"tool-cosmos.gif"
    gif_save(frames,dest,duration=180)
    print(f"SHOWCASE 7 GROUPS {dest.stat().st_size:,} bytes",flush=True)

def main():
    manifest=json.loads((ROOT/"scripts"/"tool_icons.json").read_text(encoding="utf-8"))["tools"]
    assert len(manifest)==29 and len(set(t["id"] for t in manifest))==29
    logos=[logo_for(t["source"]) for t in manifest]
    # Preserve legacy icon GIFs from the output branch; full regeneration
    # is optional because the new GitHub README uses the nine dashboard GIFs.
    if "--full" in sys.argv:
        render_tiles(manifest,logos)
        render_showcase(manifest,logos)
    from render_clean_dashboard import render_dashboard
    render_dashboard(manifest,logos,TARGET)
    print("SUCCESS: clean reference-style dashboard; 29 verified source logos",flush=True)

if __name__=="__main__":
    main()
