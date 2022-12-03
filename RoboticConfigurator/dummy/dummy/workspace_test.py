import numpy as np

from .Robot import Robot
from .workspace import find_max_reach, find_min_reach

def test_max():
    r1 = Robot([
        (0, 0, 0),
        (0, 1, 2),
        (0, 1, 2),
    ])
    r2 = Robot([
        (0, 3, 5),
        (0, 1, 2),
        (0, 1, 2),
    ])

    np.testing.assert_almost_equal(find_max_reach(r1), 4)
    np.testing.assert_almost_equal(find_max_reach(r2), 9)

def test_min():
    r1 = Robot([
        (0, 0, 0),
        (0, 1, 2),
        (0, 1, 2),
    ])

    r2 = Robot([
        (0, 3, 5),
        (0, 1, 2),
        (0, 1, 2),
    ])

    r3 = Robot([
        (0, 0, 0),
    ])

    np.testing.assert_almost_equal(find_min_reach(r1), 0)
    np.testing.assert_almost_equal(find_min_reach(r2), 1)
    np.testing.assert_almost_equal(find_min_reach(r3), 0)