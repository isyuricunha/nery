"""Render the illustrated proportion candidate using the existing cel pipeline."""
from pathlib import Path
import sys
from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'scripts'))
import motion_assets

if __name__=='__main__':
    frames=[]
    for cel in motion_assets.normalized_sheet('walk',HERE/'rounded'):
        bg=Image.new('RGBA',cel.size,(33,25,21,255))
        bg.alpha_composite(cel)
        frames.append(bg.convert('RGB'))
    frames[0].save(HERE/'rounded.gif',save_all=True,append_images=frames[1:],
                   duration=70,loop=0,optimize=False,disposal=1)
