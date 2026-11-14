#!/usr/bin/env python3
"""Split a regular sheet; remove only edge-connected background, never global keying."""
import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


def remove_background(im, tolerance=24):
    a = np.array(im.convert('RGBA'))
    rgb = a[..., :3].astype(float)
    edges = np.concatenate((rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]))
    bg = np.median(edges, axis=0)
    eligible = np.max(np.abs(rgb-bg), axis=2) <= tolerance
    h,w = eligible.shape
    seen = np.zeros((h,w),bool)
    queue = deque()
    for y,x in [(0,x) for x in range(w)]+[(h-1,x) for x in range(w)]+[(y,0) for y in range(h)]+[(y,w-1) for y in range(h)]:
        if eligible[y,x] and not seen[y,x]:
            seen[y,x]=True; queue.append((y,x))
    while queue:
        y,x=queue.popleft()
        for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=yy<h and 0<=xx<w and eligible[yy,xx] and not seen[yy,xx]:
                seen[yy,xx]=True; queue.append((yy,xx))
    a[seen]=0
    return Image.fromarray(a)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path); p.add_argument('output',type=Path)
    p.add_argument('--columns',type=int,default=3); p.add_argument('--rows',type=int,default=2)
    p.add_argument('--tolerance',type=int,default=24)
    args=p.parse_args(); im=Image.open(args.source)
    args.output.mkdir(parents=True,exist_ok=True)
    for r in range(args.rows):
        for c in range(args.columns):
            cell=im.crop((round(c*im.width/args.columns),round(r*im.height/args.rows),round((c+1)*im.width/args.columns),round((r+1)*im.height/args.rows)))
            remove_background(cell,args.tolerance).save(args.output/f'{r*args.columns+c+1:02d}.png')
if __name__=='__main__': main()
