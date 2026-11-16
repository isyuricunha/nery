#!/usr/bin/env python3
"""Check all shipped web actions and their native sampling contract."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from validate_walk_animation import visibly_equal

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'pet/nery'

def validate_stationary_reaction(frames):
    centers=[]
    for frame in frames:
        _,xs=np.where(frame[170:197,:,3]>127)
        assert len(xs), 'failed: feet are missing'
        centers.append((xs.min()+xs.max())/2)
    assert max(centers)-min(centers)<=2, f'failed: body shifts sideways ({centers})'

def main():
    data=json.loads((PACK/'motion.json').read_text())
    atlas=Image.open(PACK/'motion.webp').convert('RGBA')
    native=Image.open(PACK/'spritesheet.png').convert('RGBA')
    assert atlas.size==(data['columns']*192,1872), 'wrong web atlas geometry'
    assert len(data['states'])==9
    all_frames=[]
    for row,state in enumerate(data['states']):
        count=state['count']
        assert len(state['durations'])==count
        assert all(20<=d<=1000 for d in state['durations']), 'invalid exposure'
        frames=[np.array(atlas.crop((i*192,row*208,(i+1)*192,(row+1)*208))) for i in range(count)]
        tops=[]; feet=[]; centers=[]
        for i,f in enumerate(frames):
            y,x=np.where(f[:,:,3]>127)
            assert len(x)>900, f'{state["id"]}/{i}: empty drawing'
            assert x.min()>=3 and x.max()<189 and y.min()>=3 and y.max()<205, f'{state["id"]}/{i}: clipped'
            tops.append(y.min());feet.append(y.max())
            hy,hx=np.where(f[:105,:,3]>127)
            centers.append((hx.min()+hx.max())/2)
        if state['id']=='failed':
            validate_stationary_reaction(frames)
        if row!=4:
            assert max(feet)-min(feet)<=2, f'{state["id"]}: feet bounce on flat ground'
            assert max(centers)-min(centers)<=6, f'{state["id"]}: head pivot jitter'
            assert max(tops)-min(tops)<=10, f'{state["id"]}: scale/height jitter'
        else:
            assert feet[4]<feet[3] and feet[5]<feet[4], 'jump must ascend'
            assert feet[5]<feet[6]<feet[7], 'jump must descend'
            assert abs(feet[0]-feet[-1])<=2, 'landing misses original floor'
            assert feet[0]-feet[5]>=20, 'jump never leaves the ground'
        for i,key in enumerate(state['nativeKeys']):
            sample=np.array(native.crop((i*192,row*208,(i+1)*192,(row+1)*208)))
            assert visibly_equal(sample,frames[key]), f'{state["id"]}: native sample differs'
        unused=np.array(atlas.crop((count*192,row*208,data['columns']*192,(row+1)*208)))
        assert not np.any(unused[:,:,3]), f'{state["id"]}: stray unused cells'
        assert len({f.tobytes() for f in frames})==count, f'{state["id"]}: duplicate cels'
        all_frames.append(frames)
        print(f'PASS {state["id"]}: {count} cels, floor/pivot/alpha/native samples')
    assert data['states'][3]['returnToIdle'] and data['states'][4]['returnToIdle']
    assert not data['states'][5]['loop'], 'disappointment must hold instead of repeatedly startling'
    print('WEB MOTION VALID: all nine states; drawn anatomy still requires visual review')

if __name__=='__main__':
    main()
