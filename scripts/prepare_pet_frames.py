#!/usr/bin/env python3
"""Curate generated sheets and preserve approved silhouettes for blink edits."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from split_cells import remove_background

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'pet/frames-generated'
# The wave API returned four columns, despite the requested three. Curate six
# actual right-arm wave drawings; do not include the retry's left-arm poses.
im=Image.open(BASE/'strips/wave.png')
for i,(r,c) in enumerate([(0,0),(0,1),(0,2),(1,2),(1,1),(1,0)],1):
 cell=im.crop((c*256,r*512,(c+1)*256,(r+1)*512))
 remove_background(cell,6).save(BASE/f'wave/{i:02d}.png')
im=Image.open(BASE/'strips/jump-retry.png')
for i in range(6):
 r,c=divmod(i,3)
 cell=im.crop((round(c*im.width/3),r*512,round((c+1)*im.width/3),(r+1)*512))
 remove_background(cell,6).save(BASE/f'jump/{i+1:02d}.png')
# Four closed/half-closed fullbody and happy variants retained for reuse.
im=Image.open(BASE/'strips/blink.png')
for i in [0,1,3,4]:
 r,c=divmod(i,3)
 cell=im.crop((round(c*im.width/3),r*512,round((c+1)*im.width/3),(r+1)*512))
 remove_background(cell,6).save(BASE/f'blink/{i+1:02d}.png')
# Use only generated eyelid patches on the approved poses. All other approved
# pixels, including the hoodie (which resembles the background), stay intact.
specs={
 'failed':('thinking', [((350,548,520,655),(75,99,113,132)),((641,480,811,581),(127,85,162,119))]),
 'waiting':('coffee', [((535,466,693,546),(114,95,150,119)),((791,430,931,500),(175,91,205,114))]),
 'review':('with-cat',[((477,575,618,652),(133,102,173,131)),((684,510,795,575),(193,91,220,113))])}
(BASE/'blink/variants').mkdir(exist_ok=True)
for state,(pose,patches) in specs.items():
 target=Image.open(ROOT/f'assets/mascot/kit-v1/transparent/nery-{pose}.png').convert('RGBA')
 generated=Image.open(BASE/f'strips/blink-{state}.png').convert('RGBA')
 for source,box in patches:
  size=(box[2]-box[0],box[3]-box[1]); patch=generated.crop(source).resize(size,Image.Resampling.LANCZOS)
  mask=Image.new('L',size); ImageDraw.Draw(mask).ellipse((1,1,size[0]-2,size[1]-2),fill=255)
  mask=mask.filter(ImageFilter.GaussianBlur(1))
  target.paste(patch,box[:2],mask)
 target.save(BASE/f'blink/variants/{state}.png')
 old=BASE/f'blink/{state}.png'
 if old.exists(): old.unlink()
