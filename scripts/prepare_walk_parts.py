"""Reproduce the isolated locomotion parts from the retained source artwork."""
from pathlib import Path
from PIL import Image
from motion_assets import isolate_character,bounds

RIG=Path(__file__).resolve().parents[1]/'pet/frames-generated/motion-v5/rig'
NAMES=('body','near-arm','far-arm','thigh','shin','shoe')

def main():
    sheet=Image.open(RIG/'source.png').convert('RGBA')
    assert sheet.size==(1536,1024),'unexpected six-part sheet geometry'
    for i,name in enumerate(NAMES):
        if name=='shin':
            cel=Image.open(RIG/'shin-source.png').convert('RGBA')
        else:
            col,row=i%3,i//3
            # The upper body's shorts extend seven pixels into the gutter.
            # Include them, and remove neighboring disconnected fragments.
            cel=sheet.crop((col*512,row*512,(col+1)*512,(row+1)*512+(28 if i==0 else 0)))
        cel=isolate_character(cel)
        cel.crop(bounds(cel)).save(RIG/f'{name}.png')

if __name__=='__main__':
    main()
