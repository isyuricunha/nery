"""Render a registered, two-bone cutout walk with a planted stance foot.

The illustrated parts rotate as rigid pieces. Inverse kinematics preserves
bone lengths; the support foot travels linearly opposite to page movement.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageChops

ROOT=Path(__file__).resolve().parents[3]
RIG=Path(__file__).resolve().parent/'rig'
COUNT=32
W,H=192,208
SUPERSAMPLE=4
STRIDE=36.0
STANCE=.6
PAGE_DISTANCE=STRIDE/STANCE/2  # the page companion is drawn at half scale

@lru_cache
def part(name: str, far: bool=False) -> Image.Image:
    im=Image.open(RIG/f'{name}.png').convert('RGBA')
    if far:
        alpha=im.getchannel('A')
        im=ImageEnhance.Brightness(im.convert('RGB')).enhance(.78).convert('RGBA')
        im.putalpha(alpha)
    return im

def transformed(canvas,im,source_a,source_b,target_a,target_b):
    sa=np.array(source_a,dtype=float);sb=np.array(source_b,dtype=float)
    ta=np.array(target_a,dtype=float);tb=np.array(target_b,dtype=float)
    sd=sb-sa;td=tb-ta
    scale=np.linalg.norm(td)/np.linalg.norm(sd)
    angle=math.atan2(td[1],td[0])-math.atan2(sd[1],sd[0])
    c,s=math.cos(angle)*scale,math.sin(angle)*scale
    matrix=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
    matrix[:2,2]=ta-matrix[:2,:2]@sa
    matrix[:2]*=SUPERSAMPLE
    inverse=np.linalg.inv(matrix)
    rendered=im.convert('RGBa').transform(canvas.size,Image.Transform.AFFINE,
        tuple(inverse[:2].flatten()),resample=Image.Resampling.BICUBIC).convert('RGBA')
    canvas.alpha_composite(rendered)

def foot_pose(phase):
    p=phase%1
    if p<STANCE:
        x=-STRIDE/2+STRIDE*p/STANCE
        angle=-math.radians(18)*max(0,(p-.52)/.08)
        ankle=np.array((x,183.75))
        if p>.52:
            # Rotate around the forefoot for heel lift; that support point
            # keeps its linear ground trajectory.
            toe=np.array((x+(32-187)*.105,195.0))
            delta=np.array(((187-32)*.105,(75-176)*.105))
            c,s=math.cos(angle),math.sin(angle)
            ankle=toe+np.array((c*delta[0]-s*delta[1],s*delta[0]+c*delta[1]))
        return ankle,angle,True
    swing=(p-STANCE)/(1-STANCE)
    eased=swing*swing*(3-2*swing)
    x=STRIDE/2-STRIDE*eased
    y=183.75-18*math.sin(math.pi*swing)
    angle=math.radians(-18*math.cos(math.pi*swing/2)+6*math.sin(math.pi*swing))
    return np.array((x,y)),angle,False

def knee_for(hip,ankle,length=23.5):
    delta=ankle-hip
    distance=float(np.linalg.norm(delta))
    if distance>=length*2:
        raise ValueError(f'Unreachable ankle at {distance:.2f}px')
    middle=(hip+ankle)/2
    bend=math.sqrt(length**2-(distance/2)**2)
    # Knees bend forward, toward the left-facing character's toes.
    return middle+np.array((-delta[1],delta[0]))/distance*bend

def pose(phase):
    bob=2.0*math.sin(4*math.pi*phase)
    hip=np.array((96.,143.+bob))
    legs=[]
    for p,offset in ((phase+.5,-1.),(phase,1.)):
        ankle,angle,support=foot_pose(p)
        ankle[0]+=96+offset
        leg_hip=hip+np.array((offset,0.))
        knee=knee_for(leg_hip,ankle)
        legs.append(dict(hip=leg_hip,knee=knee,ankle=ankle,angle=angle,support=support))
    return hip,bob,legs

def draw_leg(canvas,leg,far):
    skin=Image.new('RGBA',canvas.size)
    thigh=part('thigh',far); thigh=thigh.resize((round(thigh.width*1.5),thigh.height),Image.Resampling.LANCZOS)
    transformed(skin,thigh,(70*1.5,25),(65*1.5,290),leg['hip'],leg['knee'])
    shin=part('shin',far); shin=shin.resize((round(shin.width*1.8),shin.height),Image.Resampling.LANCZOS)
    transformed(skin,shin,(55*1.8,22),(58*1.8,323),leg['knee'],leg['ankle'])
    # A cutout's closed end-cap ink must not become a ring across the knee.
    # Cover only the interior joint with the same illustrated thigh texture,
    # retaining the outside silhouette and its ink contour.
    center=leg['knee']*SUPERSAMPLE
    radius=9*SUPERSAMPLE
    joint=Image.new('L',canvas.size)
    ImageDraw.Draw(joint).ellipse((center[0]-radius,center[1]-radius,
                                  center[0]+radius,center[1]+radius),fill=255)
    joint=joint.filter(ImageFilter.GaussianBlur(.65*SUPERSAMPLE))
    joint=ImageChops.multiply(joint,skin.getchannel('A').filter(ImageFilter.MinFilter(7)))
    patch=Image.new('RGBA',canvas.size)
    texture=part('thigh',far).crop((20,100,120,200)).resize((radius*2,radius*2),Image.Resampling.BICUBIC)
    patch.paste(texture,(round(center[0]-radius),round(center[1]-radius)))
    patch.putalpha(ImageChops.multiply(patch.getchannel('A'),joint))
    skin.alpha_composite(patch)
    canvas.alpha_composite(skin)
    angle=leg['angle']
    end=leg['ankle']+np.array((27*math.cos(angle),27*math.sin(angle)))
    transformed(canvas,part('shoe',far),(187,75),(187+27/.105,75),leg['ankle'],end)

@lru_cache
def frames() -> tuple[Image.Image,...]:
    result=[]
    for index in range(COUNT):
        phase=index/COUNT
        hip,bob,legs=pose(phase)
        canvas=Image.new('RGBA',(W*SUPERSAMPLE,H*SUPERSAMPLE))
        far_shoulder=np.array((93.,99.+bob))
        arm_swing=8*math.cos(2*math.pi*phase)
        far_hand=far_shoulder+np.array((-arm_swing,math.sqrt(35**2-arm_swing**2)))
        transformed(canvas,part('far-arm'),(50,20),(50,250),far_shoulder,far_hand)
        draw_leg(canvas,legs[0],True)
        draw_leg(canvas,legs[1],False)
        # Hip registration is below the shorts: the jacket covers the joints.
        transformed(canvas,part('body'),(153,495),(153,0),(96,143+bob),(96,19+bob))
        near_shoulder=np.array((101.,98.+bob))
        near_hand=near_shoulder+np.array((arm_swing,math.sqrt(35**2-arm_swing**2)))
        transformed(canvas,part('near-arm'),(130,23),(26,213),near_shoulder,near_hand)
        result.append(canvas.resize((W,H),Image.Resampling.LANCZOS))
    return tuple(result)

if __name__=='__main__':
    from PIL import ImageDraw
    out=Path(__file__).resolve().parent
    out.mkdir(exist_ok=True)
    seq=[]
    sheet=Image.new('RGB',(W*8,H*4),(33,25,21))
    for i,frame in enumerate(frames()):
        bg=Image.new('RGBA',(W,H),(33,25,21,255))
        d=ImageDraw.Draw(bg)
        d.line((0,196,W,196),fill=(100,80,65))
        for x in range(-60,250,20):
            tx=(x+PAGE_DISTANCE*2*i/COUNT)%220-20
            d.line((tx,198,tx,202),fill=(100,80,65))
        bg.alpha_composite(frame)
        rgb=bg.convert('RGB');seq.append(rgb)
        sheet.paste(rgb,((i%8)*W,(i//8)*H))
    seq[0].save(out/'articulated.gif',save_all=True,append_images=seq[1:],duration=30,loop=0,optimize=False,disposal=1)
    sheet.save(out/'articulated-contact-sheet.jpg',quality=94)
