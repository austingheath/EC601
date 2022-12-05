import numpy as np
from .utils import points_share_plane, points_equal_distant

def test_points_equal_distant():
    # 1 point
    p = np.array([(2,1,0)])
    assert points_equal_distant(p)

    # 3 point
    p = np.array([(1,0,0),(0,1,0),(0,0,1)])
    assert points_equal_distant(p)

    # Negation
    p = np.array([(1,0,0),(0,1,0),(3,0,1)])
    assert not points_equal_distant(p)

def test_points_share_plane():
    # 1 point
    p = np.array([(2,1,0)])
    assert points_share_plane(p)

    # 2 points
    p = np.array([(2,1,0), (3,1,0)])
    assert points_share_plane(p)

    # 3 points
    p = np.array([(2,1,8), (2,4,10), (10,1,0)])
    assert points_share_plane(p)

    # Colinear points
    p = np.array([(3,0,0),(5,0,0),(9,0,0),(100,0,0)])
    assert points_share_plane(p)

    # Find noncolinear points
    p = np.array([(0,70,0),(0,-2,0),(-2,0,0),(0,1,0)])
    assert points_share_plane(p)

    # Negation
    p = np.array([(0,3,-90),(0,-2,0),(-2,0,0),(0,1,0)])
    assert not points_share_plane(p)