#!/usr/bin/env python3
"""Reproducible animated GitHub tool dashboard based on the user's reference.

Nine matching dark navy / glass cards; authentic logos on white squares,
gradient number badges, subtle drifting icon tiles, gently moving accent
highlights and clean descriptor strips. GitHub gets GIFs; PNGs are
the reduced-motion fallbacks. No JavaScript is used in GitHub README.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FRAMES = 600, 448, 18
NAVY = (12, 23, 41)
PANEL = (17, 31, 52)
INK = (240, 245, 255)
MUTED = (179, 193, 215)
WHITE = (255, 255, 255)
BORDER = (56, 75, 106)
CONFIG = [
    ("core", "01", "PROGRAMMING / DEVELOPMENT", (153, 117, 253),
     [0,1,2,3,4,5], "Foundations", "Java · Python · Git · Source control"),
    ("coding", "02", "AI-ASSISTED CODING", (70, 158, 255),
     [6,7,8,9], "Assisted Development", "Faster iteration, strong foundations first"),
    ("agents", "03", "AGENTS / AUTOMATION", (63, 211, 165),
     [10,11,12,13,14,15], "Workflow Engineering", "Agents · Orchestration · Integrations"),
    ("infra", "04", "MODELS / INFRASTRUCTURE", (255, 180, 67),
     [16,17,18,19], "Models & Sandboxes", "Local models · Cloud APIs · Runtimes"),
    ("quality", "05", "QUALITY / OBSERVABILITY", (246, 96, 125),
     [20,21,22], "Reliability & Observability", "Testing · Monitoring · Error analysis"),
    ("design", "06", "DESIGN / RESEARCH", (242, 112, 173),
     [25,26,27,28], "Design & Research", "Prototyping · Notes · Productivity"),
    ("practice", "07", "CODING PRACTICE", (149, 123, 252),
     [23,24], "Learn / Test / Refine", "Review · Trace · Solve · Repeat"),
]

def font(size, bold=False):
    root="/usr/share/fonts/truetype/dejavu/DejaVuSans"
    try:
        return ImageFont.truetype(root+("-Bold.ttf" if bold else ".ttf"),size)
    except OSError:
        return ImageFont.load_default()

TITLE=font(23,True)
NAME=font(16)
FOOT_TITLE=font(20,True)
FOOT_SUB=font(15)
BADGE_FONT=font(23,True)
TAG=font(11,True)
STEP=font(18,True)

def blend(a,b,f):
    return tuple(max(0,min(255,round(a[i]*(1-f)+b[i]*f))) for i in range(3))

def roundrect(draw,xy,r,fill,outline=None,width=1):
    draw.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=width)

def center(draw,text,x,y,f,fill):
    bbox=draw.textbbox((0,0),text,font=f)
    draw.text((x-(bbox[2]-bbox[0])/2,y),text,font=f,fill=fill)

from functools import lru_cache

@lru_cache(maxsize=20)
def _panel_cached(w,h,accent):
    """Build each category background once; frame motion happens in the art."""
    im=Image.new("RGB",(w,h))
    pixels=im.load()
    for y in range(h):
        for x in range(w):
            shade=(x/w*.15+y/h*.48)
            halo=max(0,1-math.hypot(x-w*.26,y-h*.12)/(w*.8))
            color=blend((18,33,55),(9,18,35),shade)
            pixels[x,y]=blend(color,accent,.10*halo)
    d=ImageDraw.Draw(im)
    roundrect(d,(2,2,w-3,h-3),23,None,BORDER,2)
    d.line((28,5,w-38,5),fill=blend(NAVY,accent,.23),width=1)
    return im

def panel(w,h,accent,t):
    return _panel_cached(w,h,tuple(accent)).copy()


def header(image,title,number,accent,t):
    d=ImageDraw.Draw(image)
    x,y=29,23
    # Layered number badge inspired by the reference—not a flat badge.
    for r in (30,27,24):
        a=.15 if r==30 else .37 if r==27 else .9
        cc=blend((19,33,51),accent,a)
        d.ellipse((x+28-r,y+28-r,x+28+r,y+28+r),fill=cc)
    center(d,number,x+28,y+11,BADGE_FONT,WHITE)
    d.text((104,37),title,font=TITLE,fill=INK)
    d.line((104,85,185,85),fill=accent,width=4)
    d.line((193,85,image.width-26,85),fill=blend(BORDER,NAVY,.25),width=1)
    sparkle=104+round((t/(FRAMES-1))*81)
    d.ellipse((sparkle-2,83,sparkle+2,87),fill=blend(WHITE,accent,.25))

def paste_logo(base,logo,cx,cy,maxwidth):
    icon=logo.convert("RGBA")
    scale=min(maxwidth/icon.width,maxwidth/icon.height)
    img=icon.resize((max(1,round(icon.width*scale)),max(1,round(icon.height*scale))),Image.Resampling.LANCZOS)
    base.paste(img,(round(cx-img.width/2),round(cy-img.height/2)),img)

def short_name(s):
    overrides={
        "IntelliJ IDEA":["IntelliJ IDEA"],
        "Google Antigravity":["Google","Antigravity"],
        "GitHub Copilot":["GitHub","Copilot"],
        "LiveKit Agents":["LiveKit","Agents"],
        "Hugging Face":["Hugging","Face"],
        "Supabase AI":["Supabase","AI"],
        "Sentry Seer":["Sentry","Seer"],
    }
    return overrides.get(s,[s])

def tile(image,name,logo,x,y,t,accent,seed,compact):
    """White logo tile with moving 3D-style drop shadow and restrained bobbing."""
    d=ImageDraw.Draw(image)
    side=78 if compact else 90
    bob=round(2.5*math.sin(2*math.pi*t/FRAMES+seed*.87))
    yy=y+bob
    # Soft shadow and offset depth—white card stays crisp.
    roundrect(d,(x+5,yy+8,x+side+6,yy+side+9),13,(7,14,24))
    roundrect(d,(x,yy,x+side,yy+side),13,WHITE,(229,235,242),1)
    paste_logo(image,logo,x+side/2,yy+side/2,side-25)
    # Thin changing highlight on lower edge rather than generic neon rings.
    px=x+12+(t/(FRAMES-1))*(side-39)
    d.line((px,yy+side-3,px+23,yy+side-3),fill=blend(WHITE,accent,.18),width=2)
    labels=short_name(name)
    for n,label in enumerate(labels):
        center(d,label,x+side/2,y+side+7+n*17,font(16),INK)

def symbol(draw,x,y,name,color):
    """Tiny minimal category glyph; adds hierarchy without visual noise."""
    if name=="core":
        for i in range(3):
            yy=y+i*8
            draw.polygon([(x,yy),(x+13,yy-7),(x+26,yy),(x+13,yy+8)],fill=color)
    elif name=="coding":
        draw.polygon([(x+14,y-10),(x,y+8),(x+12,y+8),(x+5,y+30),(x+28,y+3),(x+17,y+3),(x+21,y-10)],fill=color)
    elif name=="agents":
        draw.line((x+2,y+22,x+15,y-3,x+28,y+22),fill=color,width=3)
        for xx,yy in [(x+2,y+22),(x+15,y-3),(x+28,y+22)]:
            draw.ellipse((xx-5,yy-5,xx+5,yy+5),fill=color)
    elif name in ("infra","design","quality"):
        draw.ellipse((x+4,y-5,x+26,y+18),outline=color,width=4)
        draw.ellipse((x+11,y+2,x+19,y+10),fill=color)
    else:
        for i,h in enumerate([12,27,18,34]):
            draw.rounded_rectangle((x+i*8,y+30-h,x+5+i*8,y+30),radius=2,fill=color)

def footer(image,kind,headline,subtitle,accent):
    d=ImageDraw.Draw(image)
    roundrect(d,(22,366,578,427),13,(29,47,73),blend(BORDER,accent,.35),1)
    roundrect(d,(27,371,72,421),12,(25,43,65))
    symbol(d,kind and 34 or 34,kind and 384 or 384,kind,blend(WHITE,accent,.12))
    d.text((89,373),headline,font=FOOT_TITLE,fill=INK)
    d.text((89,401),subtitle,font=FOOT_SUB,fill=MUTED)

def category(cfg,tools,logos,t):
    key,number,title,accent,ids,headline,subtitle=cfg
    image=panel(W,H,accent,t)
    header(image,title,number,accent,t)
    d=ImageDraw.Draw(image)
    roundrect(d,(22,105,578,356),20,(14,26,45),(37,58,83),1)
    count=len(ids)
    compact=count>4
    side=78 if compact else 90
    positions=[35,171,307,443] if compact else [38,178,318,458]
    upper=126 if compact else 144
    lower=230
    for i,idx in enumerate(ids):
        x=positions[i%4]
        y=upper if i<4 else lower
        tile(image,tools[idx]["name"],logos[idx],x,y,t,accent,i,compact)
    if count<=4:
        # Minimal animated activity line fills space but avoids distracting boxes.
        x=50+round(t/(FRAMES-1)*480)
        d.line((48,329,549,329),fill=(42,63,87),width=1)
        d.ellipse((x-3,326,x+3,332),fill=accent)
    footer(image,key,headline,subtitle,accent)
    return image

def mini_block(image,x,y,w,h,label,icon,accent,t,i):
    d=ImageDraw.Draw(image)
    bob=round(math.sin(t*math.tau/FRAMES+i*.6)*2)
    roundrect(d,(x+3,y+bob+6,x+w+3,y+h+bob+6),12,(6,13,24))
    roundrect(d,(x,y+bob,x+w,y+h+bob),12,WHITE,(230,236,243),1)
    center(d,icon,x+w/2,y+10+bob,font(26,True),accent)
    center(d,label,x+w/2,y+h-24+bob,font(13,True),(29,45,70))

def stack(t):
    accent=(69,216,202)
    image=panel(W,H,accent,t)
    header(image,"STACK ARCHITECT","08",accent,t)
    d=ImageDraw.Draw(image)
    roundrect(d,(22,105,578,356),20,(14,26,45),(37,58,83),1)
    data=[("Frontend","▣"),("Backend","≡"),("Data","◉"),
          ("AI/ML","✧"),("Infra","☁"),("Deploy","◆")]
    for i,(label,icon) in enumerate(data):
        # Six side-by-side stages, exactly like the dashboard reference.
        x=30+i*92
        y=177
        mini_block(image,x,y,78,91,label,icon,(44,123,207),t,i)
        if i<5:
            d.text((x+79,y+29),"›",font=font(19,True),fill=accent)
    footer(image,"core","System Architecture","From frontend to deployment",accent)
    return image

def pipeline(t):
    width,height=1220,245
    accent=(129,151,255)
    image=panel(width,height,accent,t)
    d=ImageDraw.Draw(image)
    badge_xy=(34,21)
    for r,alpha in [(31,.22),(26,.6),(22,.9)]:
        color=blend((17,30,48),accent,alpha)
        d.ellipse((badge_xy[0]+27-r,badge_xy[1]+27-r,badge_xy[0]+27+r,badge_xy[1]+27+r),fill=color)
    center(d,"09",61,33,BADGE_FONT,WHITE)
    d.text((115,33),"DEVELOPMENT PIPELINE",font=font(29,True),fill=INK)
    d.line((116,77,226,77),fill=accent,width=4)
    roundrect(d,(25,98,1194,177),17,(15,27,45),(39,58,81),1)
    steps=[("Code","</>",(122,112,252)),("Build","⚙",(67,153,236)),
           ("Test","✓",(47,193,127)),("Deploy","↗",(243,164,55)),("Ship","◆",(242,103,134))]
    for i,(name,glyph,col) in enumerate(steps):
        x=43+i*233
        bob=round(2.0*math.sin(t*math.tau/FRAMES+i*.7))
        roundrect(d,(x+4,109+bob,x+180+4,168+bob+4),11,(8,14,25))
        roundrect(d,(x,109+bob,x+180,166+bob),11,WHITE,(235,240,245),1)
        center(d,glyph,x+90,112+bob,font(22,True),col)
        center(d,name,x+90,143+bob,font(14,True),(23,43,68))
        if i<4:
            center(d,"→",x+202,124,font(25,True),accent)
    roundrect(d,(25,188,1194,232),12,(28,47,73),(56,76,113),1)
    d.text((56,198),"▶",font=font(21,True),fill=accent)
    d.text((97,199),"Code → Build → Test → Deploy → Ship",font=font(18,True),fill=INK)
    return image

def save_gif(frames,path):
    """Publish 2x retina assets with a full local palette per frame.

    The README displays these at roughly half their encoded dimensions.
    That gives GitHub substantially cleaner type/logo edges than the old
    600px GIFs. Each frame gets its own 256-colour palette instead of being
    forced into the first frame's palette, which prevents logo colour loss.
    """
    path.parent.mkdir(parents=True,exist_ok=True)
    scale=2
    retina=[frame.resize((frame.width*scale,frame.height*scale),Image.Resampling.LANCZOS) for frame in frames]
    retina[0].save(path.with_suffix(".png"),optimize=True)
    quantized=[frame.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.FLOYDSTEINBERG) for frame in retina]
    target=path.with_suffix(".gif")
    quantized[0].save(target,save_all=True,append_images=quantized[1:],duration=125,
                      loop=0,optimize=False,disposal=2)
    with Image.open(target) as test:
        assert test.n_frames>=9, (path,test.n_frames)
        assert test.width>=1200, (path,test.size)
    print(f"RETINA RENDER {target.name}: {retina[0].size[0]}x{retina[0].size[1]}, {target.stat().st_size:,} bytes",flush=True)

def render_dashboard(tools,logos,target):
    assert len(tools)==29 and len(logos)==29
    output=Path(target)/"dashboard"
    for config in CONFIG:
        frames=[category(config,tools,logos,i) for i in range(FRAMES)]
        save_gif(frames,output/config[0])
    save_gif([stack(t) for t in range(FRAMES)],output/"stack")
    save_gif([pipeline(t) for t in range(FRAMES)],output/"pipeline")
    assert len(list(output.glob("*.gif")))==9
    assert len(list(output.glob("*.png")))==9
    print("SUCCESS: all nine reference-style dashboard GIFs and static fallbacks",flush=True)
