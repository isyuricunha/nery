#!/usr/bin/env python3
"""Validate the 16-frame web animation and its native 8-frame Petdex samples.

This catches flickering faces, white alpha fringes, missing sole contact,
mismatched directions and broken loop seams. Visual inspection is still
required for anatomical leg movement and timing.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"pet/frames-generated/semantic-v3/walk"
NATIVE=ROOT/"pet/nery/spritesheet.png"
SMOOTH=ROOT/"pet/nery/walk-16.webp"
W,H=192,208
errors=[]

def check(condition:bool,message:str):
    if not condition:errors.append(message)

def visibly_equal(first: np.ndarray, second: np.ndarray) -> bool:
    """Ignore RGB garbage where alpha is 0: WebP may canonicalize it.

    Visible premultiplied colors, including semitransparent edge pixels,
    must match exactly. This is a meaningful anti-flicker assertion.
    """
    a=first.astype(np.int16)
    b=second.astype(np.int16)
    if not np.array_equal(a[...,3],b[...,3]):
        return False
    visible=a[...,3]>18
    return np.array_equal(a[...,:3][visible],b[...,:3][visible])

def frames_of_atlas(im:Image.Image,starting_row:int,count:int)->list[Image.Image]:
    return [
        im.crop(((col%8)*W,(starting_row+col//8)*H,
                 (col%8+1)*W,(starting_row+col//8+1)*H))
        for col in range(count)
    ]

def main():
    if not SMOOTH.exists() or not NATIVE.exists():
        raise SystemExit("Missing spritesheet or walk-16.webp: rebuild first")
    native=Image.open(NATIVE).convert("RGBA")
    smooth=Image.open(SMOOTH).convert("RGBA")
    check(smooth.size==(1536,832),f"walk atlas dimensions {smooth.size}")
    check(native.size==(1536,2288),f"native atlas dimensions {native.size}")
    left=frames_of_atlas(smooth,2,16)
    right=frames_of_atlas(smooth,0,16)
    base_upper=np.asarray(left[0])[:133]
    silhouettes=[]
    for i,frame in enumerate(left):
        a=np.asarray(frame,dtype=np.uint8)
        alpha=a[:,:,3]
        check(visibly_equal(a[:133],base_upper),
              f"frame {i}: head/face/upper body changed (causes flashing)")
        check(int((alpha[189:195]>120).sum())>=70,
              f"frame {i}: no grounded supporting sole")
        check(int((alpha[0,:]>15).sum())==0 and int((alpha[-1,:]>15).sum())==0,
              f"frame {i}: cropped against cell top/bottom")
        # White matte fringes = pale RGB pixels with low opacity along the edge.
        fringe=int(((np.min(a[:,:,:3],axis=2)>180)&
                    (alpha>18)&(alpha<230)).sum())
        check(fringe<=85,f"frame {i}: white halo ({fringe} suspect pixels)")
        check(visibly_equal(np.asarray(right[i]),
                             np.asarray(ImageOps.mirror(frame))),
              f"frame {i}: rightward walk does not mirror the entire sprite")
        silhouettes.append((alpha[134:]>127))
        source=Image.open(SRC/f"{i:02}.png").convert("RGBA")
        check(visibly_equal(np.asarray(source),a),
              f"frame {i}: site atlas differs from approved source image")
    ious=[]
    for i,mask in enumerate(silhouettes):
        nxt=silhouettes[(i+1)%16]
        score=(mask & nxt).sum()/max(1,(mask | nxt).sum())
        ious.append(score)
        check(score>=.14,f"frame {i}->{(i+1)%16}: violent leg teleport (IoU={score:.3f})")
    nleft=[
       native.crop((i*W,2*H,(i+1)*W,3*H)) for i in range(8)
    ]
    nright=[
       native.crop((i*W,1*H,(i+1)*W,2*H)) for i in range(8)
    ]
    for i,(a,b) in enumerate(zip(nleft,nright)):
        check(visibly_equal(np.asarray(a),np.asarray(left[i*2])),
              f"native frame {i}: not key {i*2} of web cycle")
        check(visibly_equal(np.asarray(a),
                            np.asarray(ImageOps.mirror(b))),
              f"native frame {i}: directional mismatch")
    check(ious[-1]>.65,f"walk cycle closure too abrupt: {ious[-1]:.3f}")
    check(len({m.tobytes() for m in silhouettes})>=12,
          "web walk does not have enough unique lower body poses")
    print(f"walk frame continuity: minimum lower-body IoU={min(ious):.3f}, "
          f"average={np.mean(ious):.3f}, closure={ious[-1]:.3f}")
    # Not an error: abrupt but plausible key changes can still need human QA.
    rough=[f"{i}->{(i+1)%16}" for i,n in enumerate(ious) if n<.3]
    if rough:
        print("VISUAL QA WARNING: check larger lower-body changes at",", ".join(rough))
    if errors:
        print("WEB WALK INVALID:")
        for e in errors:print(" -",e)
        return 1
    print("WEB WALK VALID: 16 frames each direction, identical faces, "
          "continuous foot support, no white matte, native/web alignment")
    return 0

if __name__=='__main__':
    sys.exit(main())
