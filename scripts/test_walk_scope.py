"""The locomotion fix must not change any other shipped action drawing."""
from pathlib import Path
import hashlib
import json
import unittest
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

class WalkingScopeTests(unittest.TestCase):
    def test_other_states_match_saved_failed_fix_milestone(self):
        reference=json.loads((ROOT/'pet/frames-generated/motion-v5/preserved-states.json').read_text())
        data=json.loads((ROOT/'pet/nery/motion.json').read_text())
        atlas=Image.open(ROOT/'pet/nery/motion.webp').convert('RGBA')
        for state in data['states']:
            if state['row'] in (1,2):
                continue
            actual=[]
            for i in range(state['count']):
                cel=np.array(atlas.crop((i*192,state['row']*208,(i+1)*192,(state['row']+1)*208)))
                cel[cel[:,:,3]==0]=0
                actual.append(hashlib.sha256(cel.tobytes()).hexdigest())
            self.assertEqual(actual,reference['states'][state['id']],state['id'])
            for key,value in reference['timing'][state['id']].items():
                self.assertEqual(state[key],value,f'{state["id"]}: {key}')

if __name__=='__main__':
    unittest.main()
