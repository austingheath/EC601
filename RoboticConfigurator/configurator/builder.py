import math
from intervaltree import Interval, IntervalTree
import numpy as np

from RobotNode import create_node
from dummy.core import inverse_kinematics

# Boundaries
min_num_joints = 3
max_num_joints = 7
max_dh_param_size = 1000 # mm
dh_param_step_size = 10
allowed_alphas = np.radians([0, 90, -90])

"""
Just points: 
- 1 Joint: Points equal distance from center and lie on a plane [allowed_alphas] degrees 
    from the base z origin
- 2 Joints: Points all lie on a plane which is either [allowed_alphas] degrees from 
    from the base z origin
- 3 Joints: Otherwise, 3 joints enough for any point

Just orientation:
- 1 Joint: If only one of pitch, yaw, or roll changes - 1 joint enough
- 2 Joints: If only two of pitch, yaw, or roll changes - 2 joints enough
- 3 Joints: Otherwise, 3 joints enough for any orientation

Points & orientation:
- 1 Joint: All points equal distance from center, and all lie on one of the [allowed_alphas] planes
    from origin and all orientations match exactly the required angle to reach the corresponding point 
- 2 Joints: All points share a plane that is either [allowed_alphas] degrees from
    origin and all orientations 

Future work:
- If points / desired workspace looks more like a rectangular prism, use a cartesian robot
- If desired workspaces looks like a cylinder, use a rotory + prismatic
- Etc.
"""

def search(
    points: np.ndarray = np.array([]), 
    orientations: np.ndarray = np.array([]), 
    points_and_orientations: np.ndarray = np.array([])):
    
    if points.shape[0] == 0 and orientations.shape[0] == 0 and points_and_orientations.shape[0] == 0:
        raise Exception("At least one search parameter must be provided")

    # Only points provided
    if orientations.shape[0] == 0 and points_and_orientations.shape[0] == 0:
        # Check if points share a plane [allowed_alphas] from base z

        # Check if points equidistant from center
        i = 0


def build_graph_brute():
    all_robots = []

    r_set = set()

    target_point = (155, 1250, 240)
    radi = np.linalg.norm(target_point)

    for n_joints in range(min_num_joints, max_num_joints + 1):
        for alpha in allowed_alphas:
            for a_len in range(0, max_dh_param_size, dh_param_step_size):
                for d_len in range(0, max_dh_param_size, dh_param_step_size):
                    dh_params = []

                    for _ in range(n_joints):
                        dh = (alpha, a_len, d_len)
                        dh_params.append(dh)

                    node = create_node(dh_params)
                    r = (int(node.min_reach), int(node.max_reach))

                    print(radi, r)
                    if radi < node.min_reach or radi > node.max_reach:
                        continue

                    print("trying", dh_params)
                    try:
                        thetas = inverse_kinematics(node.robot, target_position=target_point, tolerance_threshold=10, restart_threshold=100)
                        print("ROBOT FOUND: ", dh_params)
                        return
                    except Exception:
                        continue

build_graph_brute()