"""Validate shipped occasion assets, including anchors and cycle closure."""
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class OccasionAssets(unittest.TestCase):
    def test_atlas_and_grounded_cels(self):
        data = json.loads((ROOT/'pet/occasions/occasions.json').read_text())
        atlas = Image.open(ROOT/'pet/occasions/occasions.webp').convert('RGBA')
        w, h = data['cellWidth'], data['cellHeight']
        self.assertEqual(atlas.size, (w*12, h*2))
        for state in data['states']:
            self.assertEqual(sum(state['durations']), 1940)
            frames = []
            for index in range(12):
                frame = atlas.crop((index*w,state['row']*h,(index+1)*w,(state['row']+1)*h))
                a = np.array(frame)[:,:,3]
                ys, xs = np.where(a > 64)
                self.assertGreater(xs.min(), 3)
                self.assertLess(xs.max(), w-4)
                self.assertGreater(ys.min(), 3)
                self.assertEqual(ys.max(), 261)
                # Both planted shoe silhouettes remain centered.
                fy, fx = np.where(a[-38:] > 128)
                self.assertLessEqual(abs((fx.min()+fx.max())/2 - w/2), 1.5)
                pixels = np.array(frame)
                pixels[pixels[:,:,3] == 0] = 0
                frames.append(pixels)
            self.assertTrue(np.array_equal(frames[0],frames[-1]))
            self.assertFalse(np.array_equal(frames[0],frames[6]))

    def test_pose_exports_are_transparent_and_native_sized(self):
        kit = ROOT/'assets/mascot/kit-v2'
        data = json.loads((kit/'manifest.json').read_text())
        for pose in data['poses']:
            im = Image.open(kit/'transparent'/pose['file'])
            self.assertEqual(im.size,(pose['width'],pose['height']))
            a = np.array(im.getchannel('A'))
            self.assertEqual(a[0,0],0)
            self.assertGreater(np.count_nonzero(a==0),a.size*0.15)


if __name__ == '__main__':
    unittest.main()
