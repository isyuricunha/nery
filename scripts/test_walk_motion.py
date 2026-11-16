"""Check stance contact and smooth velocity, not just similar silhouettes."""
import unittest
import numpy as np
from motion_assets import manifest
from walk_motion import pose,foot_pose,BONE,COUNT,STANCE

class WalkMotionTests(unittest.TestCase):
    def test_bones_keep_length_and_knees_bend_forward(self):
        for i in range(COUNT*2):
            _,legs=pose(i/(COUNT*2))
            for leg in legs:
                self.assertAlmostEqual(np.linalg.norm(leg['knee']-leg['hip']),BONE,places=7)
                self.assertAlmostEqual(np.linalg.norm(leg['ankle']-leg['knee']),BONE,places=7)
                self.assertLessEqual(leg['knee'][0],(leg['hip'][0]+leg['ankle'][0])/2)

    def test_stance_foot_does_not_slide_against_page_travel(self):
        displacement=manifest()['walkDistance']*2
        world=[foot_pose(p)[0][0]-p*displacement for p in np.linspace(0,STANCE-.001,30)]
        self.assertLess(max(world)-min(world),.0001)

    def test_every_frame_has_support_and_opposite_steps_alternate(self):
        for i in range(COUNT):
            self.assertTrue(any(l['support'] for l in pose(i/COUNT)[1]))
        first,half=pose(0)[1],pose(.5)[1]
        self.assertLess(first[1]['ankle'][0],first[0]['ankle'][0])
        self.assertGreater(half[1]['ankle'][0],half[0]['ankle'][0])

    def test_toeoff_and_cycle_seam_have_continuous_velocity(self):
        step=.000001
        for boundary in (STANCE,1.):
            before=foot_pose(boundary-step)[0]
            at=foot_pose(boundary)[0]
            after=foot_pose(boundary+step)[0]
            np.testing.assert_allclose((at-before)/step,(after-at)/step,atol=.01)

if __name__=='__main__':
    unittest.main()
