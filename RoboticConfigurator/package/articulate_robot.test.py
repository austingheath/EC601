import math
from articulated_robot import ArticulatedRobot
import unittest
import numpy as np

class TestArticulatedRobot(unittest.TestCase):
    """
    Test robot with invalid alpha raises an exception
    """
    def test_invalid_alpha(self):
        with self.assertRaises(Exception):
            ArticulatedRobot([
                (0, 0, 0),
                (math.pi / 4, 0),
            ])

    """
    Test with the Puma 560 robot DH parameters
    """
    def test_forward(self):
        a2 = 1
        d3 = 1
        a3 = 1
        d4 = 5

        r = ArticulatedRobot([
            (0, 0, 0),
            (-1 * math.pi / 2, 0, 0),
            (0, a2, d3),
            (-1 * math.pi / 2, a3, d4),
            (math.pi / 2, 0, 0),
            (-1 * math.pi / 2, 0, 0),
        ])

        # set joints
        ths = (
            math.pi / 2,
            math.pi / 2,
            math.pi / 2,
            math.pi / 2,
            math.pi / 2,
            math.pi,
        )
        c_ths = np.cos(ths).tolist()
        s_ths = np.sin(ths).tolist()

        (c1, c2, c3, c4, c5, c6) = c_ths
        (s1, s2, s3, s4, s5, s6) = s_ths

        # calculate actual joints manually
        c23 = c2*c3-s2*s3
        s23 = c2*s3+s2*c3

        r11 = c1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)+s1*(s4*c5*c6+c4*s6)
        r21 = s1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)-c1*(s4*c5*c6+c4*s6)
        r31 = -1*s23*(c4*c5*c6-s4*s6)-c23*s5*c6

        r12 = c1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)+s1*(c4*c6-s4*c5*s6)
        r22 = s1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)-c1*(c4*c6-s4*c5*s6)
        r32 = -1*s23*(-1*c4*c5*s6-s4*c6)+c23*s5*s6
        
        r13 = -1*c1*(c23*c4*s5+s23*c5)-s1*s4*s5
        r23 = -1*s1*(c23*c4*s5+s23*c5)+c1*s4*s5
        r33 = s23*c4*s5-c23*c5

        px = c1*(a2*c2+a3*c23-d4*s23)-d3*s1
        py = s1*(a2*c2+a3*c23-d4*s23)+d3*c1
        pz = -1*a3*s23-a2*s2-d4*c23

        expected = np.array([
            [r11, r12, r13, px],
            [r21, r22, r23, py],
            [r31, r32, r33, pz],
            [0, 0, 0, 1],
        ])
        actual = r.forward_kinematics(ths)

        r_expected = np.round(expected, 5)
        r_actual = np.round(actual, 5)

        np.testing.assert_allclose(r_actual, r_expected)


    def test_inverse_reachable(self):
        a2 = 1
        d3 = 1
        a3 = 1
        d4 = 5

        r = ArticulatedRobot([
            (0, 0, 0),
            (-1 * math.pi / 2, 0, 0),
            (0, a2, d3),
            (-1 * math.pi / 2, a3, d4),
            (math.pi / 2, 0, 0),
            (-1 * math.pi / 2, 0, 0),
        ])

        goal = (-1, -1, 4)
        thetas = r.inverse_kinematics(goal)

        # Test with forward kinematics
        calc_pos = r.forward_kinematics(thetas)[:3, -1]
        round_pos = np.round(calc_pos, 1)

        np.testing.assert_allclose(round_pos, goal)

    def test_point_reachable_simple(self):

        r = ArticulatedRobot([
            (math.pi / 2, 0, 0),
            (0, 1, 0),
            (0, 1, 0),
        ])

        self.assertTrue(r.is_position_reachable((0, 0, 0))) # fold back on itself.
        self.assertTrue(r.is_position_reachable((2, 0, 0))) # all 0 thetas
        self.assertTrue(r.is_position_reachable((1 + math.sin(math.pi / 2), 0, math.cos(math.pi / 2)))) # complex
        self.assertFalse(r.is_position_reachable((math.sin(math.pi / 2), 0.1, math.cos(math.pi / 2)))) # invalid y direction
        self.assertFalse(r.is_position_reachable((5, 5, 5))) # outside of workspace

    def test_point_reachable(self):
        a2 = 1
        d3 = 1
        a3 = 1
        d4 = 5

        r = ArticulatedRobot([
            (0, 0, 0),
            (-1 * math.pi / 2, 0, 0),
            (0, a2, d3),
            (-1 * math.pi / 2, a3, d4),
            (math.pi / 2, 0, 0),
            (-1 * math.pi / 2, 0, 0),
        ])

        self.assertTrue(r.is_position_reachable((-1, -1, 4)))


if __name__ == '__main__':
    unittest.main()