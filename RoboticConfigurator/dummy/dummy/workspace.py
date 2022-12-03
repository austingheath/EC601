import math
import numpy as np

from .core import forward_kinematics
from .Robot import Robot

def find_max_reach(robot: Robot) -> float:
    """
    Find the max reach of the robot.
    This implementation will always overestimate or equal the actual max reach.
    """

    sum = 0
    for dh in robot.dh_parameters:
        sum += np.max(dh[1:3])

    return sum

def find_min_reach(robot: Robot) -> float:
    """
    Find the min reach of the robot.
    This implementation will always underestimate or equal the actual min reach.
    """

    dh = [np.min(dh[1:3]) for dh in robot.dh_parameters]
    
    queue = []
    r = math.inf

    if len(dh) > 1:
        queue.append((0, dh[0]))
    else:
        r = dh[0]

    while len(queue) > 0:
        c = queue.pop()
        dh_i = c[0] + 1

        n_dh = dh[dh_i]

        lt = abs(c[1] - n_dh) # left
        rt = c[1] + n_dh # right

        if dh_i < len(dh) - 1:
            queue.append((dh_i, lt))
            queue.append((dh_i, rt))
        else:
            r = min([lt, rt, r])

    return r

def estimate_workspace(robot: Robot, num_angles_per_joint: int = 8) -> np.ndarray:
    v_angles = np.linspace(0., 2*math.pi, num_angles_per_joint)
    points = set()

    if robot.num_joints == 1:
        points.add((0, 0, 0))
        return np.array(points)

    for i in range(robot.num_joints - 1, -1, -1):
        thetas = []

        for angle in v_angles:
            point = forward_kinematics(robot, thetas)
