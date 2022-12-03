import math

import numpy as np

def points_equal_distant(points: np.ndarray) -> bool:
    if points.shape[0] == 0:
        return True

    if points.shape[1] != 3:
        raise Exception("Points must be in 3d space (x,y,z)")

    dist = np.linalg.norm(points[0])
    for p in points:
        if not math.isclose(np.linalg.norm(p), dist):
            return False
    
    return True

def points_share_plane(points: np.ndarray) -> bool:
    if points.shape[1] != 3:
        raise Exception("Points must be in 3d space (x,y,z)")

    f_x = True
    f_y = True
    f_z = True
    for p in points:
        (x, y, z) = p
        f_x = math.isclose(points[0][0], x)
        f_y = math.isclose(points[0][1], y)
        f_z = math.isclose(points[0][2], z)

        if not f_x and not f_y and not f_z:
            return False

    return True

