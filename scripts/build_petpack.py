#!/usr/bin/env python3
"""Build the Nery Mizuki Petdex v2 atlas with anatomically intact keyframes.

Frames: 8 x 11 cells of 192x208 (1536x2288). State frame counts:
idle 6, right 8, left 8, wave 4, jump 5, failed 8, waiting 6,
working 6, review 6. Rows 9-10 reserved for future look art.

Approved character art + *curated* semantic key poses are the only inputs;
this does NOT modify original images. Walking never horizontally flips
isolated limbs. For reverse direction, mirror the COMPLETE normalized figure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageOps
from build_walk_animation import native_frames, build_smooth_walk_atlas

ROOT=Path(__file__).resolve().parents[1]
KIT=ROOT/"assets/mascot/kit-v1/transparent"
KEYS=ROOT/"pet/frames-generated/semantic-v2"
OLD=ROOT/"pet/frames-generated"
W,H=192,208
COLS,ROWS=8,11
ORDER=("idle","running-right","running-left","waving","jumping",
       "failed","waiting","running","review")
COUNTS=(6,8,8,4,5,8,6,6,6)

def image(path:Path)->Image.Image:
    if not path.is_file(): raise FileNotFoundError(path)
    return Image.open(path).convert("RGBA")

def bbox(im:Image.Image)->tuple[int,int,int,int]:
    bounds=im.getchannel("A").getbbox()
    if bounds is None: raise ValueError("Empty sprite frame")
    return bounds

def cell(im:Image.Image, target_height:int, lift:int=0)->Image.Image:
    b=bbox(im)
    scale=min(1.,target_height/(b[3]-b[1]),176/(b[2]-b[0]))
    if scale!=1:
        im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),
                     Image.Resampling.LANCZOS)
    b=bbox(im)
    result=Image.new("RGBA",(W,H))
    result.alpha_composite(im,(round((W-b[2]+b[0])/2-b[0]),
                               H-12-b[3]+lift))
    return result

def warped(im:Image.Image,dx:float=0,dy:float=0,
           cx:float=94,cy:float=60,rx:float=40,ry:float=55)->Image.Image:
    """Tiny localized breathing/hand/head motion; no limb mirroring.

    Fully transparent colors are sampled using premultiplied alpha.
    For walking, the hip/feet are NOT warped by this upper-body field.
    """
    if not dx and not dy:return im.copy()
    pixels=np.asarray(im,dtype=np.float32)/255.
    yy,xx=np.indices((H,W),dtype=np.float32)
    weight=np.exp(-.5*(((xx-cx)/rx)**2+((yy-cy)/ry)**2))
    ux=np.clip(xx-dx*weight,0,W-1)
    vy=np.clip(yy-dy*weight,0,H-1)
    x0=ux.astype(np.int32); y0=vy.astype(np.int32)
    x1=np.minimum(x0+1,W-1); y1=np.minimum(y0+1,H-1)
    fx=(ux-x0)[...,None]; fy=(vy-y0)[...,None]
    alpha=pixels[:,:,3:4]
    rgb=pixels[:,:,:3]*alpha
    def sample(data):
        top=data[y0,x0]*(1-fx)+data[y0,x1]*fx
        bot=data[y1,x0]*(1-fx)+data[y1,x1]*fx
        return top*(1-fy)+bot*fy
    a=sample(alpha);p=sample(rgb)
    colors=np.divide(p,a,out=np.zeros_like(p),where=a>1e-6)
    return Image.fromarray(np.uint8(np.clip(np.dstack((colors,a))*255,0,255).round()),"RGBA")

def load(family:str,name:str)->Image.Image:
    im=image(KEYS/family/f"{name}.png")
    if im.size!=(W,H): raise ValueError(f"{family}/{name} is {im.size}")
    return im

def transition(family:str)->Image.Image:
    im=image(ROOT/"pet/frames-generated/semantic-v3"/family/"transition.png")
    if im.size!=(W,H):
        raise ValueError(f"{family}/transition is {im.size}, expected {(W,H)}")
    return im

def gait(right:bool)->list[Image.Image]:
    """Eight true sequential keys sampled from the curated 16-frame walk.

    The face, hair and upper body are pixel-identical across all 16 sources;
    only pose-specific drawn legs change. No frame warps or half-body flips.
    """
    return native_frames(right)

def idle()->list[Image.Image]:
    stand=cell(image(KIT/"nery-fullbody.png"),177)
    # Feet stay planted; only upper head, hair and torso breathe gently.
    movement=((0,0),(0,-1),(0,-2),(0,-1),(0,0),(0,1))
    return [warped(stand,dx,dy,cy=66,rx=60,ry=67) for dx,dy in movement]

def waving()->list[Image.Image]:
    raw=[image(OLD/f"wave/{n:02}.png") for n in (1,2,4,6)]
    boxes=[bbox(im) for im in raw]
    scale=min(1.,179/max(b[3]-b[1] for b in boxes),
                175/max(b[2]-b[0] for b in boxes))
    frames=[]
    for im,shift in zip(raw,(-5,2,8,-4)):
        size=(round(im.width*scale),round(im.height*scale))
        scaled=im.resize(size,Image.Resampling.LANCZOS)
        b=bbox(scaled)
        result=Image.new("RGBA",(W,H))
        result.alpha_composite(scaled,(round(W/2-(b[0]+b[2])/2),
                                       H-12-b[3]))
        frames.append(warped(result,dx=shift,cx=62,cy=55,rx=29,ry=35))
    return frames

def jumping()->list[Image.Image]:
    # End standing, not locked indefinitely into the crouch.
    originals=[image(OLD/f"jump/{k:02}.png") for k in (1,2,3,3,6)]
    boxes=[bbox(im) for im in originals]
    factor=min(1.,166/max(b[3]-b[1] for b in boxes),
                 176/max(b[2]-b[0] for b in boxes))
    arc=(0,-10,-24,-9,0)
    frames=[]
    for im,lift in zip(originals,arc):
        scaled=im.resize((round(im.width*factor),round(im.height*factor)),
                          Image.Resampling.LANCZOS)
        b=bbox(scaled)
        result=Image.new("RGBA",(W,H))
        result.alpha_composite(scaled,(round(W/2-(b[0]+b[2])/2),
                                       H-12-b[3]+lift))
        frames.append(result)
    return frames

def failed()->list[Image.Image]:
    shocked=load("failed","startle")
    middle=transition("failed")
    sad=load("failed","dejected")
    # Surprise -> dejected. Two genuinely different expressions, no squat.
    return [
        shocked.copy(),
        warped(shocked,-2,0,cx=96,cy=85,rx=57,ry=80),
        middle.copy(),  # hands lowering, expression changing
        sad.copy(),
        warped(sad,0,1,cx=96,cy=80,rx=55,ry=75),
        warped(sad,0,2,cx=96,cy=80,rx=55,ry=75),
        warped(sad,0,1,cx=96,cy=80,rx=55,ry=75),
        sad.copy(),
    ]

def waiting()->list[Image.Image]:
    attentive=load("waiting","attentive")
    middle=transition("waiting")
    ask=load("waiting","ask")
    # Held hands -> BOTH palms up -> held hands, not waving hello.
    return [
        attentive.copy(),
        warped(attentive,0,-1,cx=93,cy=78,rx=63,ry=70),
        middle.copy(),
        ask.copy(),
        middle.copy(),
        warped(attentive,0,1,cx=93,cy=78,rx=63,ry=70),
    ]

def working()->list[Image.Image]:
    typing=load("working","typing")
    active=load("working","active")
    return [
        typing.copy(), active.copy(),
        warped(active,1,0,cx=101,cy=128,rx=35,ry=26),
        typing.copy(),
        warped(typing,-1,0,cx=98,cy=127,rx=35,ry=26),
        active.copy(),
    ]

def reviewing()->list[Image.Image]:
    inspect=load("review","inspect")
    mark=load("review","mark")
    # Clipboard checking, with eyes/pen moving subtly, never a sad reaction.
    return [
        inspect.copy(),
        warped(inspect,0,1,cx=93,cy=65,rx=54,ry=60),
        mark.copy(),
        warped(mark,0,-1,cx=91,cy=115,rx=30,ry=25),
        mark.copy(),
        inspect.copy(),
    ]

def build_atlas()->Image.Image:
    rendered={
        "idle":idle(), "running-right":gait(True),"running-left":gait(False),
        "waving":waving(),"jumping":jumping(),"failed":failed(),
        "waiting":waiting(),"running":working(),"review":reviewing(),
    }
    atlas=Image.new("RGBA",(W*COLS,H*ROWS))
    for row,state in enumerate(ORDER):
        seq=rendered[state]
        if len(seq)!=COUNTS[row]:raise ValueError(f"{state} requires {COUNTS[row]} frames")
        for col,im in enumerate(seq):
            if im.size!=(W,H):raise ValueError(f"{state} frame {col} invalid {im.size}")
            atlas.alpha_composite(im,(col*W,row*H))
    return atlas

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=ROOT/"pet/nery")
    a=p.parse_args()
    atlas=build_atlas()
    a.out.mkdir(parents=True,exist_ok=True)
    atlas.save(a.out/"spritesheet.webp","WEBP",quality=92,method=6)
    atlas.save(a.out/"spritesheet.png","PNG")
    build_smooth_walk_atlas(a.out)
    meta={
        "id":"nery","displayName":"Nery Mizuki",
        "description":"Nery Mizuki, the official mascot of Mnerys (\u0027Built to be yours\u0027): a curious copper-haired chibi who keeps you company while your agent works.",
        "spriteVersionNumber":2,"spritesheetPath":"spritesheet.webp"
    }
    (a.out/"pet.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",
                                    encoding="utf-8")
    print("Built Nery v2:",atlas.size,"state frame counts:",dict(zip(ORDER,COUNTS)))

if __name__=="__main__":
    main()
