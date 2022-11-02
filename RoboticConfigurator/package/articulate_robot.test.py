import math
from articulated_robot import ArticulatedRobot
import unittest
import numpy as np

class TestArticulatedRobot(unittest.TestCase):
    def test_forward(self):
        r = ArticulatedRobot([
            (0, 1, 1),
        ])

        # Finish test
        res = r.forward_kinematics([math.pi / 2])
        print(res)


if __name__ == '__main__':
    unittest.main()