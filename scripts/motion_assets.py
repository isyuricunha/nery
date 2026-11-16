"""Shared cel slicing and deterministic atlas packing, without interpolation."""
from __future__ import annotations
import json
from pathlib import Path
from statistics import median
import numpy as np
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'pet/frames-generated/motion-v4/source'
W, H, FLOOR = 192, 208, 195
NAMES = ('idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed', 'waiting', 'running', 'review')
FILES = ('idle', 'walk', 'walk', 'waving', 'jumping', 'failed', 'waiting', 'working', 'review')
NATIVE_KEYS = ((0,3,4,5,6,10), tuple(range(0,32,4)), tuple(range(0,32,4)), (3,4,5,7), (2,4,5,6,11), (0,1,2,3,4,6,8,11), (0,2,4,6,8,10), (0,2,4,6,8,10), (0,2,4,6,8,10))
DURATIONS = (
    (620,160,150,150,90,90,100,140,170,170,170,330),
    (30,)*32, (30,)*32,
    (100,80,80,80,110,110,110,110,110,80,80,160),
    (110,80,90,60,70,100,70,60,60,90,100,160),
    (150,100,100,100,100,100,100,100,120,140,160,500),
    (350,120,120,140,160,180,260,180,160,140,120,350),
    (110,)*12, (160,140,140,120,100,100,100,120,140,140,160,200))
LOOPS = (True,True,True,False,False,False,True,True,True)
LABELS = ('Idle','Walking right','Walking left','Waving','Jumping','Failed','Waiting for input','Working','Reviewing')
STATIC_FRAMES = (0,0,0,4,0,11,5,0,0)
JUMP_LIFT = (0,0,0,-4,-19,-28,-15,0,0,0,0,0)

def bounds(im: Image.Image) -> tuple[int,int,int,int]:
    box = im.getchannel('A').point(lambda a: 255 if a >= 64 else 0).getbbox()
    if box is None:
        raise ValueError('Empty animation cel')
    return box

def isolate_character(cel: Image.Image) -> Image.Image:
    """Discard disconnected neighboring-cell artwork before deriving pivots.

    The character's body occupies the cell center. Flood-fill that silhouette,
    keeping original colors and antialiasing; never infer a pivot from debris.
    """
    data = np.array(cel)
    mask = (data[:,:,3] > 16).astype(np.uint8)*255
    ys,xs = np.where(mask)
    if not len(xs):
        raise ValueError('Empty character cel')
    closest = np.argmin((xs-cel.width/2)**2 + (ys-cel.height/2)**2)
    component = Image.fromarray(mask).copy()
    ImageDraw.floodfill(component,(int(xs[closest]),int(ys[closest])),128)
    data[np.array(component)!=128] = 0
    return Image.fromarray(data)

def source_cells(name: str, source_dir: Path|None=None) -> list[Image.Image]:
    sheet = Image.open((source_dir or SOURCE) / f'{name}.png').convert('RGBA')
    rows = 4 if name == 'walk' else 3
    cells = []
    for i in range(rows*4):
        row,col = divmod(i,4)
        cel = sheet.crop((round(col*sheet.width/4), round(row*sheet.height/rows), round((col+1)*sheet.width/4), round((row+1)*sheet.height/rows)))
        data = np.array(cel)
        # Almost invisible alpha=1 generator specks must not affect pivots.
        data[data[:,:,3] <= 16] = 0
        clean = Image.fromarray(data)
        cells.append(isolate_character(clean) if name == 'failed' else clean)
    return cells

def normalized_sheet(name: str, source_dir: Path|None=None) -> list[Image.Image]:
    cells = source_cells(name,source_dir)
    boxes = [bounds(cel) for cel in cells]
    heights = [b[3]-b[1] for b in boxes]
    reference = median((heights[0],heights[-1])) if name == 'jumping' else median(heights)
    scale = 177/reference
    if max((b[2]-b[0])*scale for b in boxes) > 176:
        raise ValueError(f'{name}: artwork too wide at common body scale')
    result = []
    for index,cel in enumerate(cells):
        cel = cel.resize((round(cel.width*scale),round(cel.height*scale)),Image.Resampling.LANCZOS)
        b = bounds(cel)
        # A raised hand must not displace the torso: use the head anchor.
        head = cel.getchannel('A').crop((0,b[1],cel.width,b[1]+65))
        hb = head.point(lambda a:255 if a>=96 else 0).getbbox()
        if hb is None:
            raise ValueError(f'{name}/{index}: no head anchor')
        x = round(W/2-(hb[0]+hb[2])/2)
        if name == 'failed':
            # A stationary reaction is anchored by its planted feet. Hair
            # changing silhouette must not translate the entire body.
            foot = cel.getchannel('A').crop((0,b[3]-26,cel.width,b[3]))
            foot_box = foot.point(lambda a:255 if a>=128 else 0).getbbox()
            if foot_box is None:
                raise ValueError(f'failed/{index}: missing foot anchor')
            x = round(W/2-(foot_box[0]+foot_box[2])/2)
        lift = JUMP_LIFT[index] if name == 'jumping' else 0
        y = FLOOR+1-b[3]+lift
        frame = Image.new('RGBA',(W,H))
        frame.alpha_composite(cel,(x,y))
        fb = bounds(frame)
        if min(fb[0],fb[1])<3 or fb[2]>W-3:
            raise ValueError(f'{name}/{index}: sprite clipped ({fb})')
        result.append(frame)
    return result

def normalized(name: str) -> list[Image.Image]:
    if name == 'walk':
        from walk_motion import frames
        return list(frames())
    return normalized_sheet(name)

def animations() -> list[list[Image.Image]]:
    sources = {name:normalized(name) for name in dict.fromkeys(FILES)}
    return [[ImageOps.mirror(f) for f in sources[name]] if row==1 else sources[name] for row,name in enumerate(FILES)]

def manifest() -> dict:
    return {'version':5,'cellWidth':W,'cellHeight':H,'columns':32,'floor':FLOOR,'walkDistance':30,
            'states':[dict(id=name,label=LABELS[row],row=row,count=len(DURATIONS[row]),durations=list(DURATIONS[row]),loop=LOOPS[row],returnToIdle=row in (3,4),staticFrame=STATIC_FRAMES[row],nativeKeys=list(NATIVE_KEYS[row])) for row,name in enumerate(NAMES)]}

def build(out: Path) -> None:
    out.mkdir(parents=True,exist_ok=True)
    sequences = animations()
    native = Image.new('RGBA',(W*8,H*11))
    web = Image.new('RGBA',(W*32,H*9))
    walk = Image.new('RGBA',(W*8,H*4))
    full_walk = Image.new('RGBA',(W*8,H*8))
    for row,seq in enumerate(sequences):
        for col,frame in enumerate(seq):
            web.alpha_composite(frame,(col*W,row*H))
        for col,index in enumerate(NATIVE_KEYS[row]):
            native.alpha_composite(seq[index],(col*W,row*H))
    for base_row,seq in ((0,sequences[1]),(2,sequences[2])):
        for i,frame in enumerate(seq[::2]):
            walk.alpha_composite(frame,((i%8)*W,(base_row+i//8)*H))
    for base_row,seq in ((0,sequences[1]),(4,sequences[2])):
        for i,frame in enumerate(seq):
            full_walk.alpha_composite(frame,((i%8)*W,(base_row+i//8)*H))
    for name,atlas in (('spritesheet',native),('motion',web),('walk-16',walk),('walk-32',full_walk)):
        atlas.save(out/f'{name}.webp','WEBP',lossless=True,method=6)
        if name=='spritesheet':
            atlas.save(out/f'{name}.png','PNG')
    (out/'motion.json').write_text(json.dumps(manifest(),indent=2)+'\n',encoding='utf-8')
    (out/'pet.json').write_text(json.dumps({'id':'nery','displayName':'Nery Mizuki','description':"Nery Mizuki, the official mascot of Mnerys: a curious copper-haired chibi who keeps the Mizukis company while the agent works.",'spriteVersionNumber':2,'spritesheetPath':'spritesheet.webp'},indent=2)+'\n',encoding='utf-8')
    print(f'Built motion v5: {sum(map(len,sequences))} web frames; compatible Petdex v2 atlas')
