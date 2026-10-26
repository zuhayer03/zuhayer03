#!/usr/bin/env python3
"""The clean Z✳F GitHub tool dashboard.

Renders 7 polished, subtly animated category cards with real product logos on
white icon tiles, plus a Stack Architect card and a full-width pipeline.
Used by render_animated_tools.py so the icons are downloaded only once.
Output is GitHub README-compatible GIF and reduced-motion PNG artwork.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

W, H, FRAMES = 600, 425, 14
NAVY = (17, 29, 45)
INK = (239, 244, 250)
MUTED = (171, 185, 203)
WHITE = (250, 251, 252)
BORDER = (53, 74, 96)
CONFIG = [
    ("core", "01", "PROGRAMMING / DEVELOPMENT", (150, 151, 237),
     [0, 1, 2, 3, 4, 5], "Foundations", "Java · Python · Git · Source control"),
    ("coding", "02", "AI-ASSISTED CODING", (104, 169, 248),
     [6, 7, 8, 9], "Assisted Development", "Modern coding tools · Strong fundamentals"),
    ("agents", "03", "AGENTS / AUTOMATION", (79, 204, 163),
     [10, 11, 12, 13, 14, 15], "Workflow Engineering", "Agents · Orchestration · Integrations"),
    ("infra", "04", "MODELS / INFRASTRUCTURE", (250, 181, 89),
     [16, 17, 18, 19], "Models & Sandboxes", "Local models · Cloud tools · Runtimes"),
    ("quality", "05", "QUALITY / OBSERVABILITY", (248, 118, 136),
     [20, 21, 22], "Reliability & Quality", "Code review · Tracing · Error analysis"),
    ("design", "06", "DESIGN / RESEARCH", (237, 147, 189),
     [25, 26, 27, 28], "Design & Research", "Prototyping · Notes · Exploration"),
    ("practice", "07", "CODING PRACTICE", (160, 141, 242),
     [23, 24], "Learn / Test / Refine", "Algorithms · Patterns · Problem solving"),
]

def font(size, bold=False):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
    try:
        return ImageFont.truetype(base + ("-Bold.ttf" if bold else ".ttf"), size)
    except OSError:
        return ImageFont.load_default()

F_TITLE = font(21, True)
F_NAME = font(15, True)
F_SUB = font(16)
F_DESC = font(18, True)
F_CAP = font(12, True)
F_NUMBER = font(23, True)

def rounded(d, xy, r, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def rgb_to_rgba(rgb, alpha=255):
    return tuple(rgb) + (alpha,)

def text_center(d, text, x, y, f, fill):
    box = d.textbbox((0,0), text, font=f)
    d.text((x-(box[2]-box[0])/2,y), text, font=f, fill=fill)

def base_card(w,h):
    im=Image.new("RGB",(w,h),NAVY)
    d=ImageDraw.Draw(im)
    rounded(d,(2,2,w-3,h-3),18,NAVY,BORDER,2)
    return im

def badge(d,x,y,number,color):
    rounded(d,(x,y,x+49,y+48),24,color)
    text_center(d,number,x+24,y+9,F_NUMBER,(16,29,45))

def header(d,title,num,color,w=600):
    badge(d,27,24,num,color)
    d.text((92,37),title,font=F_TITLE,fill=INK)
    d.line((92,79,171,79),fill=color,width=4)
    d.line((182,79,w-29,79),fill=(48,65,83),width=1)

def paste_logo(im,logo,cx,cy,dy=0, maxsize=69):
    logo=logo.convert("RGBA")
    ratio=min(maxsize/logo.width,maxsize/logo.height)
    box=(max(1,round(logo.width*ratio)),max(1,round(logo.height*ratio)))
    asset=logo.resize(box,Image.Resampling.LANCZOS)
    im.paste(asset,(int(cx-asset.width/2),int(cy-asset.height/2+dy)),asset)

def tile(d,im,tool,logo,x,y,dy=0):
    # White tile is intentionally the ONLY bright rectangle.
    tile_y = int(y+dy)
    rounded(d,(x+2,tile_y+4,x+103,tile_y+103),14,(8,15,25))
    rounded(d,(x,tile_y,x+102,tile_y+100),13,WHITE,(229,234,240),1)
    paste_logo(im,logo,x+51,tile_y+50,0)
    label=tool["name"]
    if label in ("Google Antigravity","IntelliJ IDEA","GitHub Copilot","LiveKit Agents","Hugging Face","Supabase AI"):
        split_at=label.rfind(" ")
        lines=[label[:split_at],label[split_at+1:]]
    else:
        lines=[label]
    for line_no,part in enumerate(lines):
        text_center(d,part,x+51,y+110+line_no*18,F_NAME,INK)

def category_card(cfg,tools,logos,t):
    slug,num,title,accent,ids,headline,subtitle=cfg
    frame=base_card(W,H);d=ImageDraw.Draw(frame)
    header(d,title,num,accent)
    # Use a quiet inner panel, not excessive nested visual borders.
    rounded(d,(20,105,580,329),14,(21,35,53),(35,51,69),1)
    n=len(ids)
    xs=[38,178,318,458] if n>=4 else [38+i*140 for i in range(n)]
    if n<=4:
        ys=[152]*n
    else:
        ys=[137]*4+[257]*(n-4)
    phase=2*math.pi*t/FRAMES
    for j,idx in enumerate(ids):
        bob=round(2.3*math.sin(phase+j*.75))
        # Labels are fixed while only logo tiles float subtly.
        tile(d,frame,tools[idx],logos[idx],xs[j%4],ys[j],bob)
    # Less empty vertical space on 4-tool and smaller sections: small understated linework.
    if n<=4:
        d.line((39,290,561,290),fill=(39,56,75),width=1)
        cx=64+int((t/(FRAMES-1))*458)
        d.ellipse((cx-3,287,cx+3,293),fill=accent)
    rounded(d,(21,341,579,407),13,(27,44,64),(48,68,91),1)
    d.rounded_rectangle((35,353,40,396),radius=2,fill=accent)
    d.text((56,351),headline,font=F_DESC,fill=INK)
    d.text((56,378),subtitle,font=F_SUB,fill=MUTED)
    return frame

def stack_card(t):
    accent=(111,204,194)
    image=base_card(W,H)
    d=ImageDraw.Draw(image)
    header(d,"STACK ARCHITECT","08",accent)
    rounded(d,(20,105,580,329),14,(21,35,53),(35,51,69),1)
    labels=["Frontend","Backend","Data","AI / ML","Infra","Deploy"]
    # Simple 3x2 diagram; no misleading technology stack claims.
    centers=[(120,163),(290,163),(460,163),(120,277),(290,277),(460,277)]
    phase=2*math.pi*t/FRAMES
    for i,(x,y) in enumerate(centers):
        lift=round(2.0*math.sin(phase+i*.6))
        rounded(d,(x-64,y-44+lift,x+64,y+35+lift),11,WHITE,(227,232,242),1)
        text_center(d,["⌘","▤","▣","◇","☁","➤"][i],x,y-36+lift,font(24,True),
                    (73,145,189))
        text_center(d,labels[i],x,y+8+lift,font(15,True),(31,48,66))
    d.line((190,163,215,163),fill=accent,width=2)
    d.line((360,163,385,163),fill=accent,width=2)
    d.line((190,277,215,277),fill=accent,width=2)
    d.line((360,277,385,277),fill=accent,width=2)
    rounded(d,(21,341,579,407),13,(27,44,64),(48,68,91),1)
    d.rounded_rectangle((35,353,40,396),radius=2,fill=accent)
    d.text((56,351),"System Architecture",font=F_DESC,fill=INK)
    d.text((56,378),"Explore the flow from concept to deployment",font=F_SUB,fill=MUTED)
    return image

def pipeline_card(t):
    w,h=1220,245
    accent=(153,147,244)
    image=base_card(w,h)
    d=ImageDraw.Draw(image)
    badge(d,26,20,"09",accent)
    d.text((93,32),"DEVELOPMENT PIPELINE",font=font(28,True),fill=INK)
    d.line((94,76,210,76),fill=accent,width=4)
    steps=["Code","Build","Test","Deploy","Ship"]
    colors=[(141,131,240),(91,156,233),(89,196,146),(242,166,94),(225,127,145)]
    icons=["< / >","⚙","+","☁","➤"]
    phase=2*math.pi*t/FRAMES
    for i,step in enumerate(steps):
        x=28+i*242
        movement=round(2*math.sin(phase+i*.6))
        rounded(d,(x,103+movement,x+212,186+movement),12,WHITE,(227,232,242),1)
        text_center(d,icons[i],x+106,108+movement,font(24,True),colors[i])
        text_center(d,step,x+106,151+movement,font(16,True),(31,48,66))
        if i<4:
            d.text((x+218,133),"→",font=font(22,True),fill=accent)
    d.text((30,211),"IDEA → CODE → TEST → DEPLOY → SHIP",font=font(16,True),fill=MUTED)
    return image

def save_animation(frames,outbase):
    outbase.parent.mkdir(parents=True,exist_ok=True)
    frames[0].save(outbase.with_suffix(".png"))
    # Consistent single palette prevents color flicker and keeps files small.
    palette=frames[0].quantize(colors=192,method=Image.Quantize.MEDIANCUT)
    quantized=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
    target=outbase.with_suffix(".gif")
    quantized[0].save(target,format="GIF",save_all=True,
                      append_images=quantized[1:],duration=130,
                      loop=0,optimize=True,disposal=2)
    with Image.open(target) as check:
        assert check.n_frames>=8, (target,check.n_frames)
    print(f"Generated {target.name}: {target.stat().st_size:,} bytes",flush=True)

def render_dashboard(tools,logos,target):
    assert len(tools)==29 and len(logos)==29
    output=Path(target)/"dashboard"
    for cfg in CONFIG:
        frames=[category_card(cfg,tools,logos,t) for t in range(FRAMES)]
        save_animation(frames,output/cfg[0])
    save_animation([stack_card(t) for t in range(FRAMES)],output/"stack")
    save_animation([pipeline_card(t) for t in range(FRAMES)],output/"pipeline")
    assert len(list(output.glob("*.gif")))==9
    assert len(list(output.glob("*.png")))==9
    print("SUCCESS: 9 minimal dashboard animated cards + PNG reduced-motion fallbacks",flush=True)
