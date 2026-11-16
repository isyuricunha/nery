"""Animate only locomotion, using parts referenced against existing Idle art.

Rigid part transforms and two-bone joints preserve leg length. Planted feet
translate linearly against page travel, rather than skating between cels.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageChops

ROOT=Path(__file__).resolve().parents[1]
RIG=ROOT/'pet/frames-generated/motion-v5/rig'
W,H,COUNT,SAMPLE=192,208,32,4
STRIDE,STANCE,BONE=36.,.6,29.5
PAGE_DISTANCE=STRIDE/STANCE/2
PART_SIZES={'body':(412,508),'near-arm':(213,321),'far-arm':(180,320),
            'thigh':(196,371),'shin':(639,1688),'shoe':(301,221)}

@lru_cache
def part(name,far=False):
    im=Image.open(RIG/f'{name}.png').convert('RGBA')
    if im.size!=PART_SIZES[name]:
        raise ValueError(f'{name}: artwork changed size; update its joint registration')
    if far:
        alpha=im.getchannel('A')
        im=ImageEnhance.Brightness(im.convert('RGB')).enhance(.82).convert('RGBA')
        im.putalpha(alpha)
    return im

def draw_part(canvas,im,source_a,source_b,target_a,target_b):
    sa,sb,ta,tb=(np.array(p,dtype=float) for p in (source_a,source_b,target_a,target_b))
    sd,td=sb-sa,tb-ta
    scale=np.linalg.norm(td)/np.linalg.norm(sd)
    angle=math.atan2(td[1],td[0])-math.atan2(sd[1],sd[0])
    c,s=math.cos(angle)*scale,math.sin(angle)*scale
    matrix=np.array(((c,-s,0.),(s,c,0.),(0.,0.,1.)))
    matrix[:2,2]=ta-matrix[:2,:2]@sa
    matrix[:2]*=SAMPLE
    inv=np.linalg.inv(matrix)
    layer=im.convert('RGBa').transform(canvas.size,Image.Transform.AFFINE,
        tuple(inv[:2].flatten()),resample=Image.Resampling.BICUBIC).convert('RGBA')
    canvas.alpha_composite(layer)

def limb(canvas,name,far,start,end,width):
    im=part(name,far)
    a=np.array((im.width*.5,im.height*.15))
    b=np.array((im.width*.5,im.height*.88))
    if name=='shin':
        a[1],b[1]=im.height*.13,im.height*.92
    native_width=im.width*BONE/(b[1]-a[1])
    factor=width/native_width
    im=im.resize((round(im.width*factor),im.height),Image.Resampling.LANCZOS)
    a[0]*=factor;b[0]*=factor
    draw_part(canvas,im,a,b,start,end)

SHOE_SCALE=28/301
SHOE_ANCHOR=np.array((237.,95.))
ANKLE_Y=195-(221-SHOE_ANCHOR[1])*SHOE_SCALE

def foot_pose(phase):
    p=phase%1
    if p<STANCE:
        return np.array((-STRIDE/2+STRIDE*p/STANCE,ANKLE_Y)),0.,True
    t=(p-STANCE)/(1-STANCE)
    # Hermite swing matches the stance velocity at both ends. Squared lift
    # also starts/ends with zero vertical speed, avoiding toe-off/landing jerks.
    start,end=STRIDE/2,-STRIDE/2
    tangent=(1-STANCE)*STRIDE/STANCE
    x=(2*t**3-3*t*t+1)*start+(t**3-2*t*t+t)*tangent
    x+=(-2*t**3+3*t*t)*end+(t**3-t*t)*tangent
    y=ANKLE_Y-16*math.sin(math.pi*t)**2
    angle=math.radians(-18*math.sin(2*math.pi*t)*math.sin(math.pi*t))
    return np.array((x,y)),angle,False

def knee_for(hip,ankle):
    delta=ankle-hip;distance=float(np.linalg.norm(delta))
    if distance>=2*BONE:
        raise ValueError(f'Unreachable ankle ({distance:.2f}px)')
    bend=math.sqrt(BONE**2-(distance/2)**2)
    return (hip+ankle)/2+np.array((-delta[1],delta[0]))/distance*bend

def pose(phase):
    bob=2*math.sin(4*math.pi*phase)
    hip=np.array((96.,128.+bob))
    legs=[]
    for p,offset in ((phase+.5,-1.),(phase,1.)):
        ankle,angle,support=foot_pose(p)
        ankle[0]+=96+offset
        root=hip+np.array((offset,0.))
        legs.append(dict(hip=root,knee=knee_for(root,ankle),ankle=ankle,angle=angle,support=support))
    return bob,legs

def draw_leg(canvas,leg,far):
    skin=Image.new('RGBA',canvas.size)
    limb(skin,'thigh',far,leg['hip'],leg['knee'],22.)
    limb(skin,'shin',far,leg['knee'],leg['ankle'],18.)
    # Blend the illustrated skin texture only inside the overlapping joint.
    # Outer ink/alpha stays intact; no cap rings or extra doll joints.
    center=leg['knee']*SAMPLE;radius=9*SAMPLE
    joint=Image.new('L',canvas.size)
    ImageDraw.Draw(joint).ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius),fill=255)
    joint=ImageChops.multiply(joint.filter(ImageFilter.GaussianBlur(.65*SAMPLE)),skin.getchannel('A').filter(ImageFilter.MinFilter(7)))
    raw=part('thigh',far)
    texture=raw.crop((raw.width*.25,raw.height*.4,raw.width*.75,raw.height*.6)).resize((radius*2,radius*2),Image.Resampling.BICUBIC)
    patch=Image.new('RGBA',canvas.size)
    patch.paste(texture,(round(center[0]-radius),round(center[1]-radius)))
    patch.putalpha(ImageChops.multiply(patch.getchannel('A'),joint))
    skin.alpha_composite(patch);canvas.alpha_composite(skin)
    a=leg['angle'];tip=leg['ankle']+np.array((28*math.cos(a),28*math.sin(a)))
    draw_part(canvas,part('shoe',far),SHOE_ANCHOR,SHOE_ANCHOR+np.array((301.,0.)),leg['ankle'],tip)

@lru_cache
def frames():
    seq=[]
    for i in range(COUNT):
        phase=i/COUNT;bob,legs=pose(phase)
        canvas=Image.new('RGBA',(W*SAMPLE,H*SAMPLE))
        lean=math.radians(math.sin(2*math.pi*phase))
        def body_point(x,y):
            dx,dy=x-96,y-132
            return np.array((96+dx*math.cos(lean)-dy*math.sin(lean),
                             132+bob+dx*math.sin(lean)+dy*math.cos(lean)))
        swing=10*math.cos(2*math.pi*phase)
        far_shoulder=body_point(92,94)
        far_hand=far_shoulder+np.array((-swing,math.sqrt(32**2-swing**2)))
        draw_part(canvas,part('far-arm'),(65,35),(125,285),far_shoulder,far_hand)
        draw_leg(canvas,legs[0],True);draw_leg(canvas,legs[1],False)
        draw_part(canvas,part('body'),(150,508),(150,0),body_point(96,132),body_point(96,19))
        shoulder=body_point(101,94)
        hand=shoulder+np.array((swing,math.sqrt(32**2-swing**2)))
        draw_part(canvas,part('near-arm'),(160,35),(47,285),shoulder,hand)
        seq.append(canvas.resize((W,H),Image.Resampling.LANCZOS))
    return tuple(seq)

if __name__=='__main__':
    out=ROOT/'.work';out.mkdir(exist_ok=True)
    sequence=[];sheet=Image.new('RGB',(W*8,H*4),(33,25,21))
    for i,frame in enumerate(frames()):
        bg=Image.new('RGBA',(W,H),(33,25,21,255));bg.alpha_composite(frame)
        image=bg.convert('RGB');sequence.append(image);sheet.paste(image,((i%8)*W,(i//8)*H))
    sequence[0].save(out/'idle-based-walk.gif',save_all=True,append_images=sequence[1:],duration=30,loop=0,optimize=False,disposal=1)
    sheet.save(out/'idle-based-walk.jpg',quality=94)
