#!/usr/bin/env python3
"""Render story-driven GIF demonstrations for the existing programming-journey repo.

These are clearly labeled *sample visualizations* of genuine project concepts,
not captured application recordings or fabricated real-world metrics.

Publish: dist/demos/{network,finance,sorting,security,project-reel}.gif and .png
Requires: pillow (installed by the existing profile GIF workflow).
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "demos"
OUT.mkdir(parents=True, exist_ok=True)
FRAMES = 24
DURATION = 110
COLORS = {
    "network": ((216, 239, 224), (35, 106, 81), (28, 64, 52)),
    "finance": ((237, 222, 245), (147, 105, 180), (59, 38, 74)),
    "sorting": ((248, 200, 170), (178, 99, 62), (70, 45, 31)),
    "security": ((218, 236, 225), (60, 118, 89), (26, 63, 49)),
}
DARK = (23, 32, 40)
MUTED = (94, 108, 112)
WHITE = (255, 255, 255)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans"

def ft(n, bold=False, mono=False):
    stem = MONO if mono else SANS
    try:
        return ImageFont.truetype(stem + ("-Bold.ttf" if bold else ".ttf"), n)
    except OSError:
        return ImageFont.load_default()

H1=ft(40, True)
H2=ft(26, True)
LABEL=ft(18,True)
CAP=ft(15)
TINY=ft(13,False,True)
MON=ft(19,False,True)

def box(d,rect,fill,outline=None,r=14,width=2):
    d.rounded_rectangle(rect, radius=r, fill=fill, outline=outline, width=width)

def middle(d,s,x,y,f,color):
    b=d.textbbox((0,0),s,font=f)
    d.text((x-(b[2]-b[0])/2,y),s,font=f,fill=color)

def make_base(kind,title,subtitle):
    bg,accent,ink=COLORS[kind]
    im=Image.new("RGB",(1040,400),bg)
    d=ImageDraw.Draw(im)
    box(d,(2,2,1037,397),bg,accent,19,2)
    d.text((31,24),"PROJECT LAB   /   SAMPLE VISUALIZATION",font=TINY,fill=accent)
    d.text((31,52),title,font=H1,fill=ink)
    d.text((31,111),subtitle,font=CAP,fill=ink)
    d.line((31,145,1008,145),fill=accent,width=2)
    return im,d,accent,ink

def footer(d,label,accent):
    d.line((31,344,1008,344),fill=accent,width=1)
    d.text((31,360),label,font=TINY,fill=accent)
    d.text((1007,360),"ILLUSTRATIVE / NOT LIVE DATA",font=TINY,fill=accent,anchor="ra")

def draw_network(t):
    im,d,a,ink=make_base("network","Network Monitor","From target configuration to a readable connectivity report.")
    p=t/FRAMES
    centers=[(185,241),(520,241),(844,241)]
    for i,(x,y) in enumerate(centers):
        box(d,(x-112,175,x+112,291),WHITE,a,18)
        middle(d,["TARGET","TCP CHECK","REPORT"][i],x,195,LABEL,ink)
        middle(d,["demo.local:443","Connect & time","CSV + JSON"][i],x,239,CAP,ink)
    for left,right in ((300,405),(630,728)):
        d.line((left,242,right,242),fill=a,width=4)
        d.polygon([(right-8,233),(right,242),(right-8,251)],fill=a)
    # Always-moving sample packet (and a trailing marker).
    motion=(t % FRAMES)/(FRAMES-1)
    x=300 + motion*(428)
    d.ellipse((x-9,233,x+9,251),fill=(255, 250, 245),outline=a,width=4)
    for j,(x,y) in enumerate(centers):
        r=6 + int(2*math.sin(t*.5+j))
        d.ellipse((x-110,y-65,x-110+2*r,y-65+2*r),fill=a)
    footer(d,"TCP connectivity checks / report pipeline",a)
    return im

def draw_finance(t):
    im,d,a,ink=make_base("finance","Finance Tracker","See fictional spending grouped into local budgeting categories.")
    vals=[65,112,89,148,104]
    names=["FOOD","TRANSIT","BILLS","STUDY","OTHER"]
    box(d,(40,165,1000,330),WHITE,a,18)
    progress=(1-math.cos(math.pi*t/12))/2
    for i,(target,name) in enumerate(zip(vals,names)):
        x=115+i*185
        y_bottom=308
        actual=max(4,round(target*(.65+.35*progress)))
        color=(226,147,125) if i==3 else a
        box(d,(x,y_bottom-actual,x+73,y_bottom),color,r=5)
        middle(d,name,x+36,188,TINY,ink)
    footer(d,"SAMPLE CATEGORY CHART / NO REAL FINANCIAL DATA",a)
    return im

def bubble_swaps():
    values=[6,3,8,2,7,4]
    states=[(values.copy(),-1)]
    for end in range(len(values)-1,0,-1):
        for j in range(end):
            if values[j] > values[j+1]:
                values[j],values[j+1]=values[j+1],values[j]
                states.append((values.copy(),j))
    return states

SORT_STATES=bubble_swaps()

def draw_sorting(t):
    im,d,a,ink=make_base("sorting","AlgoArena","Bubble Sort / six sample values / each swap advances the animation.")
    box(d,(38,167,1002,328),WHITE,a,18)
    progress=int(t*(len(SORT_STATES)-1)/(FRAMES-1))
    nums,swap=SORT_STATES[progress]
    for j,val in enumerate(nums):
        x=102+j*150
        height=18*val
        color=(245,160,75) if j in (swap,swap+1) else a
        box(d,(x,299-height,x+82,299),color,r=7)
        middle(d,str(val),x+41,270-height,MON,ink)
    d.text((776,176),f"SWAP {progress:02}/{len(SORT_STATES)-1:02}",font=TINY,fill=a)
    # A moving playhead keeps each GIF frame unique between discrete swaps.
    x=766+t*8
    d.line((763,317,958,317),fill=a,width=2)
    d.ellipse((x-6,311,x+6,323),fill=(255,245,226),outline=a,width=2)
    footer(d,"EDUCATIONAL SORT VISUALIZATION / SORTED STATE AT LOOP END",a)
    return im

def draw_security(t):
    im,d,a,ink=make_base("security","ThreatTrace","Synthetic login events: a repeated-failure rule triggers at 3.")
    events=["08:20:01   203.0.113.7   FAIL",
            "08:20:07   203.0.113.7   FAIL",
            "08:20:12   192.0.2.5     SUCCESS",
            "08:20:17   203.0.113.7   FAIL"]
    box(d,(35,171,703,326),WHITE,a,16)
    for j,e in enumerate(events):
        active=j<=int(t*4/FRAMES)
        d.text((55,190+j*31),e,font=MON,fill=ink if active else (177,188,186))
    box(d,(732,172,1001,326),(30,66,50),r=16)
    n=min(3,sum(1 for e in events[:1+int(t*4/FRAMES)] if "203.0.113.7" in e))
    middle(d,"FAIL COUNT",867,195,CAP,(217,240,224))
    middle(d,str(n)+" / 3",867,229,H2,(244,255,237))
    middle(d,"RULE ALERT" if n>=3 else "CHECKING",867,280,LABEL,(222,255,172) if n>=3 else (180,216,196))
    # A subtle timeline playhead communicates the continuous loop while
    # preserving discrete synthetic login events and their exact counts.
    mx=766+t*8
    d.line((763,318,960,318),fill=a,width=2)
    d.ellipse((mx-5,313,mx+5,323),fill=(209,241,219),outline=a,width=2)
    footer(d,"SYNTHETIC DOCUMENTATION-RANGE IP / NO LIVE ANALYSIS",a)
    return im

def draw_reel(t):
    im=Image.new("RGB",(1200,360),DARK)
    d=ImageDraw.Draw(im)
    box(d,(2,2,1196,357),(21,32,39),(85,116,108),20)
    d.text((40,25),"IDEAS IN MOTION",font=ft(31,True),fill=(235,247,238))
    d.text((40,74),"Four real learning projects · four different kinds of problems",font=CAP,fill=(181,203,196))
    names=[("NETWORK", "MONITOR","network"),("FINANCE","TRACKER","finance"),
           ("ALGO","ARENA","sorting"),("THREAT","TRACE","security")]
    for i,(top,bottom,kind) in enumerate(names):
        bg,a,ink=COLORS[kind]
        x=24+i*294
        y=124
        box(d,(x,y,x+277,330),bg,r=15)
        d.text((x+18,y+17),top,font=LABEL,fill=ink)
        d.text((x+18,y+41),bottom,font=LABEL,fill=ink)
        if i==0:
            points=[(x+90,y+129),(x+180,y+121),(x+151,y+90)]
            d.line(points+[points[0]],fill=a,width=3)
            for k,(nx,ny) in enumerate(points):
                r=7+int(2*math.sin(t*.37+k))
                d.ellipse((nx-r,ny-r,nx+r,ny+r),fill=a)
        elif i==1:
            for k,h in enumerate([33,57,44,75,53]):
                osc=6*math.sin(t*.32+k)
                box(d,(x+36+k*38,y+179-h-osc,x+60+k*38,y+179),a,r=3)
        elif i==2:
            values,_=SORT_STATES[int(t*(len(SORT_STATES)-1)/(FRAMES-1))]
            for k,v in enumerate(values):
                box(d,(x+23+k*39,y+186-14*v,x+48+k*39,y+186),a,r=3)
        else:
            d.polygon([(x+139,y+85),(x+206,y+109),(x+202,y+155),
                       (x+139,y+187),(x+75,y+155),(x+72,y+109)],fill=a)
            middle(d,"!",x+139,y+105,ft(63,True),bg)
        d.text((x+18,y+190),"PROJECT / "+str(i+1).zfill(2),font=TINY,fill=ink)
    return im

def publish(name,render):
    frames=[render(t) for t in range(FRAMES)]
    first=frames[0]
    first.save(OUT/(name+".png"),optimize=True)
    indexed=[f.quantize(colors=192,method=Image.Quantize.MEDIANCUT,
                        dither=Image.Dither.NONE) for f in frames]
    target=OUT/(name+".gif")
    indexed[0].save(target,save_all=True,append_images=indexed[1:],
                    loop=0,duration=DURATION,optimize=True,disposal=2)
    with Image.open(target) as image:
        assert image.n_frames >= 12,(name,image.n_frames)
        assert image.width>=1000,(name,image.size)
    assert target.stat().st_size>2000
    print(f"OK {name} {first.size} {target.stat().st_size:,} bytes",flush=True)

def main():
    for name,fn in (("network",draw_network),("finance",draw_finance),
                    ("sorting",draw_sorting),("security",draw_security),
                    ("project-reel",draw_reel)):
        publish(name,fn)
    assert len(list(OUT.glob("*.gif")))==5
    assert len(list(OUT.glob("*.png")))==5
    print("Five original sample-project motion walkthrough GIFs generated and validated",flush=True)

if __name__=="__main__":
    main()
