import math
from typing import Tuple
import numpy as np
from scipy.spatial.transform import Rotation as R

from .Robot import Robot

supported_solver_methods = ["jacobian_transpose", "jacobian_psuedo"]

def forward_kinematics(robot: Robot, thetas: np.ndarray):
    to_joint = len(thetas)

    if to_joint > robot.num_joints:
        raise Exception("The number of joint angles cannot exceed the number of joints")
    if to_joint <= 0:
        raise Exception("The number of joint angles must be greater than 0")

    np_angles = np.array(thetas).reshape((len(thetas), 1))
    full_dh = np.concatenate((robot.dh_parameters[:to_joint,:], np_angles), axis=1)

    translations = build_t_matrix(full_dh[0])
    for i in range(1, full_dh.shape[0]):
        if i >= to_joint:
            break

        t_matrix = build_t_matrix(full_dh[i])
        translations = np.dot(translations, t_matrix)
    
    return translations

def inverse_kinematics(
    robot: Robot,
    target_position: np.ndarray = None,
    target_orientation: np.ndarray = None,
    solver_method: str = "jacobian_transpose", 
    allowed_pos_error: float = 0.1,
    allowed_ori_error: float = 0.1,
    restart_threshold: int = 1) -> np.array:

    if target_position is None and target_orientation is None:
        raise Exception("Either target_position or target_orientation must be specified")

    if target_position is not None and len(target_position) != 3:
        raise Exception("Position must be a vector (x,y,z) given in base coordinates")

    if target_orientation is not None and (target_orientation.shape[0] != 3 or target_orientation.shape[1] != 3):
        raise Exception("Orientation must be specified as 3x3 rotation matrix")

    if allowed_pos_error <= 0 or allowed_ori_error <= 0:
        raise Exception("allowed_pos_error/allowed_ori_error must be a value larger than 0")

    if restart_threshold < 0:
        raise Exception("restart_threshold must be greater than or equal to 0")

    if solver_method not in supported_solver_methods:
        raise Exception("The solver method provided is not supported.")

    # build target translation matrix
    if target_position is None:
        target_position = np.zeros(3)
        disable_position = True
    else:
        target_position = np.array(target_position)
        disable_position = False

    if target_orientation is None:
        target_orientation = np.zeros((3, 3))
        disable_orientation = True
    else:
        target_orientation = np.array(target_orientation)
        disable_orientation = False

    target_translation = assemble_t_matrix(target_orientation, target_position)

    # set constants
    d_th_threshold = math.radians(5) # limit to 5 degrees
    err_sim_count_threshold = 100

    # start calculation at theta = 0
    ths = np.zeros(robot.num_joints)
    actual = forward_kinematics(robot, ths)
    err = err_between_t(
        target_translation, 
        actual, 
        disable_position=disable_position,
        disable_orientation=disable_orientation)

    (prev_pos_err, prev_ori_err) = (math.inf, math.inf)

    err_sim_counter = 0
    restart_counter = 0

    while True:
        (pos_err, ori_err) = np.round((np.linalg.norm(err[:3]), np.linalg.norm(err[3:])), 5)

        # finish if within threshold
        if pos_err <= allowed_pos_error and ori_err <= allowed_ori_error: 
            break

        # check if err changed
        if (pos_err > allowed_pos_error and pos_err >= prev_pos_err) or (ori_err > allowed_ori_error and ori_err >= prev_ori_err):
            err_sim_counter += 1

        # if error hasn't changed in a while, we might be in a local minima
        # or a singularity
        if err_sim_counter >= err_sim_count_threshold:
            if restart_counter > restart_threshold:
                raise Exception("Unable to meet the tolerance threshold")

            # restart with random thetas
            ths = np.random.normal(0, math.pi, robot.num_joints)
            actual = forward_kinematics(robot, ths)
            err = err_between_t(
                target_translation, 
                actual, 
                disable_position=disable_position,
                disable_orientation=disable_orientation)
            (prev_pos_err, prev_ori_err) = (math.inf, math.inf)

            err_sim_counter = 0
            restart_counter += 1
            continue

        # calculate change in theta
        match solver_method:
            case "jacobian_transpose":
                # caculate jacobian
                j = calc_geometric_jacobian(robot, ths)

                # calculate inverse of jacobian as the transpose
                j_tp = np.transpose(j)

                # calculate change in theta
                scaled_err = 0.05 * err
                d_th = j_tp.dot(scaled_err)
            case "jacobian_psuedo":
                # caculate jacobian
                j = calc_geometric_jacobian(robot, ths)

                # calculate psuedoinverse
                j_tp = np.linalg.pinv(j)

                # calculate change in theta
                scaled_err = 0.05 * err
                d_th = j_tp.dot(scaled_err)
            case _:
                raise Exception("The solver method provided is not supported.")
        
        # calculate alpha using the method from
        # https://cseweb.ucsd.edu/classes/wi17/cse169-a/slides/CSE169_09.pdf
        # a = d_th_threshold / max(d_th_threshold, np.amax(abs(d_th)))

        # update theta
        # ths = ths + a * d_th

        # recalc pose and error
        actual = forward_kinematics(robot, ths)
        err = err_between_t(
            target_translation, 
            actual, 
            disable_position=disable_position,
            disable_orientation=disable_orientation,
            solver_method=solver_method)

        # set previous error
        (prev_pos_err, prev_ori_err) = (pos_err, ori_err)

    return ths

def calc_jacobian(robot: Robot, thetas: np.ndarray, final_pos: np.ndarray = None, j_type: str = "geometric"):
    if thetas.shape[0] != robot.num_joints:
        raise Exception("Please provide an angle for each joint")

    if final_pos is not None and len(final_pos) != 3:
        raise Exception("final_pos must be a four length vector (x, y, z)")

    if j_type not in ["geometric", "analytical"]:
        raise Exception("Jacobian type must be geometric or analytical") 

    mlt = np.array([0, 0, 1])

    if final_pos is None:
        final_pos = forward_kinematics(robot, thetas)[:3, -1]

    jacobian = []

    init_col_rot = np.cross(mlt, final_pos)
    init_col = np.concatenate((init_col_rot, mlt))

    jacobian.append(init_col)

    for i in range(1, robot.num_joints):
        # TODO optimize this so it doesn't have to recalculate the intermediate
        # translation matrices each time
        t_mat = forward_kinematics(robot, thetas[:i])
        r_mat = t_mat[:3, :3]
        p_vec = t_mat[:3, -1]

        w_por = np.dot(r_mat, mlt)
        v_por = np.cross(w_por, final_pos - p_vec)

        fin = np.concatenate((v_por, w_por))

        jacobian.append(fin)

    g_jac = np.array(jacobian).transpose()

    if j_type == "geometric":
        return g_jac

    # Continue calculating the analytical jacobian

    return np_jac

def build_t_matrix(full_dh: np.ndarray) -> np.ndarray:
    """
    Create the translation matrix from one set of DH paramters.
    Assumes the previous origin is (0,0,0).
    """

    if len(full_dh) != 4:
        raise Exception("All four DH parameters must be present to build the T matrix")

    (al_i, a_i, d_i, th_i) = full_dh

    return np.array([
        [np.cos(th_i), -1 * np.sin(th_i), 0, a_i],
        [np.sin(th_i) * np.cos(al_i), np.cos(th_i) * np.cos(al_i), -1 * np.sin(al_i), -1 * np.sin(al_i) * d_i],
        [np.sin(th_i) * np.sin(al_i), np.cos(th_i) * np.sin(al_i), np.cos(al_i), np.cos(al_i) * d_i],
        [0, 0, 0, 1],
    ])

def err_between_t(
    target_translation: np.ndarray,
    actual_translation: np.ndarray, 
    disable_position: bool = False, 
    disable_orientation: bool = False,
    solver_method: str = "jacobian_transpose", 
    ):
    if disable_position and disable_orientation:
        raise Exception("Must calculate error for either position or orientation")

    if solver_method not in supported_solver_methods:
        raise Exception("The solver method provided is not supported.")

    pos_err = np.zeros(3)
    rot_err = np.zeros(3)

    act_pos = actual_translation[:3, -1]
    act_rot = actual_translation[:3, :3]

    ex_pos = target_translation[:3, -1]
    ex_rot = target_translation[:3, :3]

    # Calculate error in position
    if not disable_position:
        pos_err = ex_pos - act_pos

    # Calculate error in orientation
    if not disable_orientation:
        match solver_method:
            case "jacobian_transpose":
                # Get diff in terms of a rot matrix
                rot_diff = act_rot.transpose() * ex_rot

                # Translate diff to angle-axis representation
                rot_err = R.from_matrix(rot_diff).as_rotvec()

            case "jacobian_psuedo":
                # Get diff in terms of a rot matrix
                rot_diff = act_rot.transpose() * ex_rot

                # Translate diff to angle-axis representation
                rot_err = R.from_matrix(rot_diff).as_rotvec()

    return np.concatenate((pos_err, rot_err))

def assemble_t_matrix(rotation_matrix: np.ndarray, position_vector: np.ndarray):
    """
    Creates the full translation matrix from a rotation matrix and position vector.
    """

    res = np.concatenate((rotation_matrix, np.array([position_vector]).transpose()), axis=1)
    return np.concatenate((res, np.array([(0, 0, 0, 1)])))

def x_rot_matrix(theta: float) -> np.ndarray:
    """
    Create elementary matrix for rotation around X axis
    """
    return np.array([
        (1,0,0),
        (0,math.cos(theta),-1*math.sin(theta)),
        (0,math.sin(theta),math.cos(theta)),
    ])

def y_rot_matrix(theta: float) -> np.ndarray:
    """
    Create elementary matrix for rotation around Y axis
    """
    return np.array([
        (math.cos(theta),0,math.sin(theta)),
        (0,1,0),
        (-1*math.sin(theta),0,math.cos(theta)),
    ])

def z_rot_matrix(theta: float) -> np.ndarray:
    """
    Create elementary matrix for rotation around Z axis
    """
    return np.array([
        (math.cos(theta), -1*math.sin(theta),0),
        (math.sin(theta),math.cos(theta),0),
        (0,0,1)
    ])