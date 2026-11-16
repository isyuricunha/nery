"""Regressions for stray crop fragments and whole-body anchor displacement."""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from motion_assets import isolate_character, normalized
from validate_motion import validate_stationary_reaction

class AlignmentTests(unittest.TestCase):
    def test_neighboring_fragment_is_removed_without_changing_body(self):
        cel=Image.new('RGBA',(192,208))
        draw=ImageDraw.Draw(cel)
        draw.rectangle((70,30,120,195),fill=(210,120,80,255))
        draw.rectangle((5,55,12,70),fill=(210,120,80,255))
        cleaned=np.array(isolate_character(cel))
        self.assertFalse(cleaned[55:71,5:13,3].any())
        np.testing.assert_array_equal(cleaned[30:196,70:121],np.array(cel)[30:196,70:121])

    def test_actual_failure_sequence_has_planted_feet(self):
        validate_stationary_reaction([np.array(f) for f in normalized('failed')])

    def test_original_sideways_teleport_is_rejected(self):
        frames=[np.array(f) for f in normalized('failed')]
        moved=Image.new('RGBA',(192,208))
        moved.alpha_composite(Image.fromarray(frames[5]),(33,0))
        frames[5]=np.array(moved)
        with self.assertRaisesRegex(AssertionError,'body shifts sideways'):
            validate_stationary_reaction(frames)

if __name__=='__main__':
    unittest.main()
