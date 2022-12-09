import math
import numpy as np
from scipy.spatial.transform import Rotation as R

from dummy.core import inverse_kinematics, x_rot_matrix

from .RobotNode import RobotNode, create_node
from .utils import points_equal_distant, points_share_plane

# Boundaries
min_num_joints = 1
max_num_joints = 6
max_dh_param_size = 1000 # mm
dh_param_step_size = 100
allowed_alphas = np.radians([90, -90, 0])
ik_tolerance_threshold = 100 # get within mm

alpha_rots = [x_rot_matrix(a) for a in np.unique(np.abs(allowed_alphas), axis=0)]
allowed_alpha_uvs_z = np.round(np.array([a.dot(np.array((0,0,1))) for a in alpha_rots]))
allowed_alpha_uvs_x = np.round(np.array([a.dot(np.array((1,0,0))) for a in alpha_rots]))

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
    points_only: np.ndarray = np.array([]), 
    orientations_only: np.ndarray = np.array([]), 
    points_with_orientation: dict = dict(),
    euler_seq: str = "xyz") -> RobotNode:
    
    verify_search_input(points_only, orientations_only, points_with_orientation)
    
    points = np.unique(np.array(points_only), axis=0)
    orientations = np.unique(np.array(orientations_only), axis=0)

    orientation_mats = np.array([R.from_euler(euler_seq, o).as_matrix() for o in orientations])
    
    start_search = max_num_joints

    print("Beginning optimization...")

    # Only points provided
    if orientations.shape[0] == 0 and len(points_with_orientation) == 0:
        max_norm = np.max(np.linalg.norm(points))

        # determine max point size
        for s in range(6, 2, -1):
            ln = s * max_dh_param_size
            if max_norm > ln:
                start_search = s + 1
                break
            else:
                start_search = s

        # determine if we can go lower than 3 joints
        if start_search == 3:
            # Check if points share a plane [allowed_alphas] from base z
            shared = points_share_plane(points)
            if shared:
                for plane_z in allowed_alpha_uvs_z:
                    for plane_x in allowed_alpha_uvs_x:
                        ext_pts = np.append(points, [plane_z, plane_x, (0,0,0)], axis=0)
                        if points_share_plane(ext_pts):
                            print(ext_pts)
                            start_search = 2
                            break

            # Check if points equidistant from center and on a plane [allowed_alphas] from base z
            if start_search == 2 and points_equal_distant(points):
                start_search = 1
        
    # Only orientations provided
    if points.shape[0] == 0 and len(points_with_orientation) == 0:
        start_search = 3

        # get unit vectors
        unit_ori = np.round(np.array([o_m.dot(np.array((0,0,1))) for o_m in orientation_mats]))

        # check only 1 angle change
        for uv in allowed_alpha_uvs_z:
            comb = np.append(unit_ori, [uv], axis=0)
            unq = np.unique(comb, axis=0)

            if unq.shape[0] == 1:
                start_search = 1
                break

        # check only 2 angles change
        if start_search != 1:
            for i in range(allowed_alpha_uvs_z.shape[0]):
                for k in range(allowed_alpha_uvs_z.shape[1]):
                    if i == k:
                        continue

                    comb = np.append(unit_ori, [allowed_alpha_uvs_z[i], allowed_alpha_uvs_z[k]], axis=0)
                    unq = np.unique(comb, axis=0)

                    if unq.shape[0] == 2:
                        start_search = 2
                        break

    # TODO setup optimization for points & orientation
    
    print("Starting search with", start_search, "joint(s)")
    return begin_search(start_search, points, orientations, points_with_orientation)

def verify_search_input(points_only: np.ndarray, orientations_only: np.ndarray, points_with_orientation: dict):
    if points_only.shape[0] == 0 and orientations_only.shape[0] == 0 and len(points_with_orientation) == 0:
        raise Exception("At least one search parameter must be provided")

    # check dictionary
    for key in points_with_orientation.keys():
        ori = points_with_orientation.get(key)
        if type(key) is not tuple or len(key) != 3 or not isinstance(ori, np.ndarray) or ori.shape[0] != 3:
            raise Exception("Keys must be (x,y,z) tuples and values in points_with_orientation must be euler ZYX orientations in radians")

    # check points and orientations
    if points_only.shape[0] > 0 and points_only.shape[1] != 3:
        raise Exception("Points must be (x,y,z) vectors")

    if orientations_only.shape[0] > 0 and orientations_only.shape[1] != 3:
        raise Exception("Orientations must be ZYX euler vectors")

def begin_search(
    starting_num_joints: int,
    points_only: np.ndarray,
    orientations_only: np.ndarray,
    points_with_orientation: dict) -> RobotNode:

    if len(points_with_orientation) > 0:
        all_points = np.unique(np.append(points_only, list(points_with_orientation.keys()), axis=0))
    else:
        all_points = points_only
    
    for n_joints in range(starting_num_joints, max_num_joints + 1):
        for alpha in allowed_alphas:
            for a_len in range(0, max_dh_param_size, dh_param_step_size):
                # Skip if only d_len value changes
                if math.isclose(alpha, 0) and math.isclose(a_len, 0):
                    continue

                for d_len in range(0, max_dh_param_size, dh_param_step_size):
                    # generate DH params
                    dh_params = []

                    for _ in range(n_joints):
                        dh = (alpha, a_len, d_len)
                        dh_params.append(dh)

                    # create robot
                    robot_node = create_node(dh_params)

                    # check workspace first
                    skip = False
                    for point in all_points:
                        radi = np.linalg.norm(point)

                        if radi < robot_node.min_reach or radi > robot_node.max_reach:
                            skip = True
                            break
                    
                    if skip:
                        continue

                    # Then check inverse
                    print("Trying", dh_params)
                    for point in all_points:
                        try:
                            thetas = inverse_kinematics(robot_node.robot, target_position=point, allowed_pos_error=10, restart_threshold=100, solver_method="jacobian_psuedo")
                        except Exception:
                            skip = True
                            break
                    
                    if not skip:
                        return robot_node
                    
    raise Exception("Could not find robot")

                    
