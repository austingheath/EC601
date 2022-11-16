

from typing import List, Tuple
import numpy as np

# Boundaries
min_num_joints = 1
max_num_joints = 7
max_joint_len = 1000 # mm
allowed_alphas = np.radians([0, 90, -90])

def smart_search(positions: List[Tuple[int]]):
    if len(positions) == 0:
        raise Exception("You must provide at least one position")

    for pos in positions:
        if len(pos) != 3:
            raise Exception("Each position must be a coordinate point: (x, y, z)")

    # sort by distance
    positions.sort(key=np.linalg.norm)

    furthest = positions[-1]
    closest = positions[0]

    # Block points that lay way outside the releastic bounds
    # In the future, device prismatic joints (maybe) to handle these cases.
    if furthest > max_joint_len * max_num_joints:
        raise Exception("A point provided is way to far from the origin for a feasible kinematic chain.")

class RobotNode:
    robot_dh: List[Tuple[float]]
    max_reach: float
    min_reach: float

def build_graph_brute():
    all_robots = []

    for n_joints in range(min_num_joints, max_num_joints + 1):
        for alpha in allowed_alphas:
            for a_len in range(0, max_joint_len):
                for d_len in range(0, max_joint_len):
                    dh_params = []

                    for _ in range(n_joints):
                        dh = (alpha, a_len, d_len)
                        dh_params.append(dh)

                    robot_node = RobotNode()
                    robot_node.robot_dh = dh_params

                    all_robots.append(robot_node)
