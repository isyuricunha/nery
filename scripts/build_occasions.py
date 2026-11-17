"""Build the additive occasion kit and web-only drawn animation atlas.

The original kit and nine-state native pet are never modified.
"""
from pathlib import Path
import hashlib
import json
import base64
from statistics import median

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'pet/frames-generated/occasions-v1/source'
OUT = ROOT / 'pet/occasions'
KIT = ROOT / 'assets/mascot/kit-v2'
W, H, FLOOR = 256, 277, 262
DURATIONS = [160, 100, 100, 100, 100, 180, 360, 140, 120, 120, 140, 320]


def visible_bounds(im):
    box = im.getchannel('A').point(lambda a: 255 if a > 64 else 0).getbbox()
    if box is None:
        raise ValueError('Empty occasion artwork')
    return box


def sequence(name):
    source = Image.open(SOURCE / f'{name}.png').convert('RGBA')
    if source.size != (1536, 1024):
        raise ValueError(f'{name}: source must be a 4x3 grid on 1536x1024')
    cells = []
    for i in range(12):
        row, col = divmod(i, 4)
        cel = source.crop((col*384, round(row*1024/3), (col+1)*384, round((row+1)*1024/3)))
        data = np.array(cel)
        data[data[:, :, 3] <= 16] = 0
        cells.append(Image.fromarray(data))
    boxes = [visible_bounds(c) for c in cells]
    scale = 235 / median(b[3]-b[1] for b in boxes)
    frames = []
    for cel, box in zip(cells, boxes):
        # Feet are planted; align by the shoe silhouette, independent of arms.
        foot = cel.getchannel('A').crop((0, box[3]-25, cel.width, box[3]))
        fb = foot.point(lambda a: 255 if a > 128 else 0).getbbox()
        if fb is None:
            raise ValueError(f'{name}: missing foot anchor')
        pivot = (fb[0]+fb[2])/2
        frame = Image.new('RGBA', (W, H))
        cel = cel.resize((round(cel.width*scale), round(cel.height*scale)), Image.Resampling.LANCZOS)
        frame.alpha_composite(cel, (round(W/2-pivot*scale), FLOOR-visible_bounds(cel)[3]))
        b = visible_bounds(frame)
        if min(b[:2]) < 4 or b[2] > W-4 or b[3] > FLOOR+1:
            raise ValueError(f'{name}: clipped cel {b}')
        frames.append(frame)
    # The final resting pose must be the exact starting pose, not a near copy.
    frames[-1] = frames[0].copy()
    return cells, frames


def main():
    OUT.mkdir(exist_ok=True)
    (KIT/'transparent').mkdir(parents=True, exist_ok=True)
    (KIT/'preview').mkdir(exist_ok=True)
    atlas = Image.new('RGBA', (W*12, H*2))
    states = []
    for row, name in enumerate(('celebrate', 'heart')):
        cells, frames = sequence(name)
        for col, frame in enumerate(frames):
            atlas.alpha_composite(frame, (col*W, row*H))
        states.append(dict(id=name,row=row,count=12,durations=DURATIONS,loop=False,staticFrame=6))
        pose = cells[5 if name == 'celebrate' else 6]
        pose = pose.crop(visible_bounds(pose))
        pose.save(KIT/'transparent'/f'nery-{name}.png')
        pose.save(KIT/'transparent'/f'nery-{name}.webp',lossless=True,method=6)
        bg_frames = []
        for frame in frames:
            bg = Image.new('RGBA', (W,H), (11,11,10,255))
            bg.alpha_composite(frame)
            bg_frames.append(bg.convert('RGB'))
        bg_frames[0].save(OUT/f'{name}.gif',save_all=True,append_images=bg_frames[1:],duration=DURATIONS,loop=0,disposal=2,optimize=False)
    birthday = Image.open(KIT/'source/birthday.png').convert('RGBA')
    birthday = birthday.crop(visible_bounds(birthday))
    birthday.save(KIT/'transparent/nery-birthday.png')
    birthday.save(KIT/'transparent/nery-birthday.webp',lossless=True,method=6)
    atlas.save(OUT/'occasions.webp', lossless=True, method=6)
    version = hashlib.sha256((OUT/'occasions.webp').read_bytes()).hexdigest()[:16]
    data = dict(version=1,assetVersion=version,cellWidth=W,cellHeight=H,columns=12,states=states)
    (OUT/'occasions.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    poses = []
    preview = Image.new('RGB',(900,460),(11,11,10))
    draw = ImageDraw.Draw(preview)
    for i,name in enumerate(('celebrate','heart','birthday')):
        path = KIT/'transparent'/f'nery-{name}.webp'
        im = Image.open(path).convert('RGBA')
        poses.append(dict(id=name,file=f'nery-{name}.webp',width=im.width,height=im.height))
        im.thumbnail((260,390),Image.Resampling.LANCZOS)
        preview.paste(im,(i*300+(300-im.width)//2,15+(390-im.height)//2),im)
        draw.text((i*300+24,427),name,fill=(231,201,140))
    (KIT/'manifest.json').write_text(json.dumps(dict(version='2.0',license='../LICENSE.md',poses=poses),indent=2)+'\n',encoding='utf-8')
    preview.save(KIT/'preview/occasions.jpg',quality=94,subsampling=0)
    cards = ''.join('<figure><figcaption>'+name+'</figcaption><img alt="Nery: '+name+'" src="data:image/gif;base64,'+
                    base64.b64encode((OUT/f'{name}.gif').read_bytes()).decode()+'"></figure>' for name in ('celebrate','heart'))
    (OUT/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Nery — occasion animation review</title><style>body{background:#0b0b0a;color:#e7c98c;font:16px system-ui;margin:40px}h1{font-size:24px}main{display:flex;gap:30px;flex-wrap:wrap}figure{margin:0;padding:25px;border:1px solid #d6a84f55;border-radius:12px}img{display:block;width:256px;height:277px}figcaption{margin-bottom:15px}</style>'
        '<h1>Nery Mizuki — occasion animations</h1><p>Actual exported GIFs · original playback timing · 12 drawings per action.</p><main>'+cards+'</main></html>',encoding='utf-8')
    print('Built three poses and two 12-cel animations; original kit and pet unchanged.')


if __name__ == '__main__':
    main()
