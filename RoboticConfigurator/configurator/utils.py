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
    points = np.unique(points, axis=0)
    if len(points.shape) != 2 or points.shape[1] != 3:
        raise Exception("Must list each point in 3d space (x,y,z)")

    # 3 points define a plane
    if points.shape[0] == 1 or points.shape[0] == 2 or points.shape[0] == 3:
        return True

    # find 3 points that aren't colinear
    bk = False
    for i in range(0, len(points)):
        for j in range(0, len(points)):
            for k in range(0, len(points)):
                if i == j or i == k or j == k:
                    continue
                
                pts = np.array([points[i], points[j], points[k]])
                ab = pts[1]-pts[0]
                ac = pts[2]-pts[0]
                cross = np.cross(ab, ac)
                norm = np.linalg.norm(cross)

                if norm != 0:
                    # calc equation of plane
                    p_eq = np.append(cross, -1 * cross.dot(pts[0]))
                    plane_pts = pts
                    bk = True
                    break
            if bk:
                break
        if bk:
            break

    if not bk:
        return True

    rem_points = np.append(points, np.ones((len(points), 1)), axis=1)
    all_act = rem_points.dot(p_eq)
    rem_act = np.append(plane_pts, np.ones((len(plane_pts), 1)), axis=1).dot(p_eq)
    
    ex = rem_act[0] * np.ones(len(all_act))

    return np.allclose(ex, all_act, atol=0.4)


