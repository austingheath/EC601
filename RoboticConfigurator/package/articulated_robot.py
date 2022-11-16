import math
import string
from typing import List, Tuple
import numpy as np 

class ArticulatedRobot:

    """
    DH Parameters:
    a_i = the distance from Z_i to Z_i+1 measured along X_i
    alpha_i = the angle from Z_i to Z_i+1 measured about X_i
    d_i = the distance from X_i-1 to X_i measured along Z_i
    theta_i = the angle from X_i-1 to X_i measured about Z_i
    """
    dh_parameters: np.array

    num_joints: int

    max_reach: float
    min_reach: float

    """
    ArticulatedRobot

    Represents a simple kinematic robot chain with only rotary joints. Prismatic joints
    can be added with ease later.

    Assume actuators are placed along the z axis at the common normal (the point where
    the x axis and z axis intersect - the origin).
    DH Parameters

    Arguments:
        dh_parameters: A list of tuples with length equal to the number of joints. 
            The tuples should contain three numbers and represent the DH paramters
            for that paricular joint: (alpha_i-1, a_i-1, d_i).
    """
    def __init__(self, dh_parameters: List[Tuple[float]]) -> None:
        if len(dh_parameters) > 7:
            raise Exception("DH parameters must have 7 DOF or less.")
        
        if len(dh_parameters) == 0:
            raise Exception("DH parameters cannot be empty.")

        for params in dh_parameters:
            if len(params) != 3:
                raise Exception("Each set of DH paramters should contain 3 numbers")

        self.dh_parameters = np.array(dh_parameters)
        self.num_joints = len(dh_parameters)

        # Set radius last. Method relies on fully initialized class.
        self.max_reach = self.__max_reach()
        self.min_reach = self.__min_reach()

    """
    Given a position (x,y,z), see if the robot can reach it.

    While rare, it is possible to get false negatives (a point is reachable, 
    but this function returned False).

    This is WIP: Make this function smarter and faster. Utilize different inverse kinematic
    solvers, different thresholds, etc.

    Arguments:
        target_position: (x, y, z) tuple relative to the base (0) frame,
        [optional] within_distance: If the robot can get within the distance specified, then
            the position is considered reachable. Defaults to 0.1

    Output:
        True if the position is reachable, False if it is not.
    """
    def is_position_reachable(self, target_position: Tuple[float], within_distance: float = 0.1) -> bool:
        if len(target_position) != 3:
            raise Exception("Position must be a vector (x,y,z) given in base coordinates")

        if within_distance <= 0:
            raise Exception("within_distance must be positive.")

        # First, do a quick check and make sure the point is within
        # the spherical workspace of the robot.
        dist_origin = np.linalg.norm(np.array(target_position))
        if dist_origin > self.max_reach:
            return False

        # Next, it's necessary (and sufficient) to solve the IK problem
        try:
            self.inverse_kinematics(target_position, tolerance_threshold=0.1, restart_threshold=100)
            return True
        except Exception:
            return False

    """
    Calculate forward kinematics of the robot up to the provided
    joint angles.

    Arguments:
        joint_angles: The angle (in radians) of each joint. The first (0 index) element
            corresponds to the first joint. Calulate up to joint i by only providing the
            angles up to joint i

    Output:
        Returns the translation vector from base frame 0 
        to the last linkage's frame N
    """
    def forward_kinematics(self, joint_angles: Tuple[float]) -> np.array:
        to_joint = len(joint_angles)

        if to_joint > self.num_joints:
            raise Exception("The number of joint angles cannot exceed the number of joints")
        if to_joint <= 0:
            raise Exception("The number of joint angles must be greater than 0")

        np_angles = np.array(joint_angles).reshape((len(joint_angles), 1))
        full_dh = np.concatenate((self.dh_parameters[:to_joint,:], np_angles), axis=1)

        translations = self.__build_t_matrix(full_dh[0])
        for i in range(1, full_dh.shape[0]):
            if i >= to_joint:
                break

            t_matrix = self.__build_t_matrix(full_dh[i])
            translations = np.dot(translations, t_matrix)
        
        return translations

    """
    Calculate the inverse kinematics
    Given a point, find a set of thetas that will make the robot reach that point.

    Other methods include:

    Jacobian Pseudoinverse
    Cyclic Coordinate Descent
    Levenberg-Marquardt damped least squares
    Quasi-Newton, conjugate gradient, Newton-Raphson
    Neural networks

    Arguments:
        target_position: (x, y, z) tuple relative to the base (0) frame
        [optional] solver_method: The method used to calculate the inverse kinematics. Valid methods are: 
            - "jacobian_transpose"
            - More to come. Defaults to "jacobian_transpose"
        [optional] tolerance_threshold: The allowed error distance from the current position and the target
            position. Defaults to 0.10
        [optional] restart_threshold: The number of times the algorithm will restart if it is unable to 
            reduce error by a particular tolerance. Defaults to 1

    Output:
        A set of joint angles that gets the robot within 0.10 of the specified point
    """
    def inverse_kinematics(
        self, 
        target_position: Tuple[float], 
        solver_method: string = "jacobian_transpose", 
        tolerance_threshold: float = 0.01,
        restart_threshold: int = 1) -> np.array:

        if len(target_position) != 3:
            raise Exception("Position must be a vector (x,y,z) given in base coordinates")

        if tolerance_threshold <= 0:
            raise Exception("tolerance_threshold must be a value larger than 0")

        if restart_threshold < 0:
            raise Exception("restart_threshold must be greater than or equal to 0")

        # select the algorithm
        if solver_method == "jacobian_transpose":
            solver = self.__jacobian_transpose_solver
        else:
            raise Exception("The solver method provided is not supported.")

        # set constants
        clamp_threshold = 0.05
        d_th_threshold = math.radians(5) # limit to 5 degrees
        err_th_threshold = 0.01
        err_sim_count_threshold = 10

        # start calculation at theta = 0
        ths = np.zeros(self.num_joints)
        pos = self.forward_kinematics(ths)[:3, -1]
        err = target_position - pos
        err_sim_counter = 0
        restart_counter = 0

        while np.linalg.norm(err) > tolerance_threshold:
            # caculate change in theta
            d_th = solver(ths, self.__clamp_err(err, clamp_threshold))

            # calculate alpha using the method from
            # https://cseweb.ucsd.edu/classes/wi17/cse169-a/slides/CSE169_09.pdf
            a = d_th_threshold / max(d_th_threshold, np.amax(abs(d_th)))

            # update theta
            ths = ths + a * d_th

            # recalc position and error
            pos = self.forward_kinematics(ths)[:3, -1]
            next_err = target_position - pos

            # check if err changed
            if np.linalg.norm(err - next_err) < err_th_threshold:
                err_sim_counter += 1
            else:
                err_sim_counter = 0

            # if error hasn't changed in a while, we might be in a local minima
            if err_sim_counter >= err_sim_count_threshold:
                if restart_counter + 1 > restart_threshold:
                    raise Exception("Unable to meet the tolerance threshold", pos)

                # restart with random thetas
                ths = np.random.normal(0, math.pi, self.num_joints)
                pos = self.forward_kinematics(ths)[:3, -1]
                next_err = target_position - pos
                err_sim_counter = 0
                restart_counter += 1

            err = next_err

        return ths

    """
    Calculate the full jacobian
    We only need to handle rotary joints in the construction. This function
    does not consider prismatic joints.
    
    Arguments:
        joint_angles: Full set of joint angle values for the robot
        [optional] final_pos: The final_pos of the robot given the joint_angles.
            Provide to avoid recalculating it
        [optional] linear_only: returns the jacobian with only the linear velocities
            filled in, resulting in a 3xN np.array.
    
    Output:
        The jacobian of the robot given the joint angles.
        Unless linear_only is True returns a 6xN np.array, where N is the number of joints.
    """
    def calc_jacobian(self, joint_angles: np.array, final_pos: np.array = None, linear_only: bool = False):
        if joint_angles.shape[0] != self.num_joints:
            raise Exception("Please provide an angle for each joint")

        if final_pos is not None and len(final_pos) != 3:
            raise Exception("final_pos must be a four length vector (x, y, z)")

        mlt = np.array([0, 0, 1])

        if final_pos is None:
            final_pos = self.forward_kinematics(joint_angles)[:3, -1]

        jacobian = []

        init_col_rot = np.cross(mlt, final_pos)
        init_col = np.concatenate((init_col_rot, mlt))

        jacobian.append(init_col)

        for i in range(1, self.num_joints):
            # TODO optimize this so it doesn't have to recalculate the intermediate
            # translation matrices each time
            t_mat = self.forward_kinematics(joint_angles[:i])
            r_mat = t_mat[:3, :3]
            p_vec = t_mat[:3, -1]

            w_por = np.dot(r_mat, mlt)
            v_por = np.cross(w_por, final_pos - p_vec)

            fin = np.concatenate((v_por, w_por))

            jacobian.append(fin)

        np_jac = np.array(jacobian).transpose()
        if linear_only is True:
            return np_jac[:3, :]

        return np_jac
    
    """
    T matrix construction for link i for "modified" DH parameters

    Parameters:
        full_dh: Tuple of the 4 DH parameters for link i
            (al_i-1, a_i-1, d_i, th_i)

    Output:
        A 4x4 translation matrix to get from link i-1 to i
    """
    def __build_t_matrix(self, full_dh: Tuple[float]) -> np.array:
        (al_i, a_i, d_i, th_i) = full_dh

        return np.array([
            [np.cos(th_i), -1 * np.sin(th_i), 0, a_i],
            [np.sin(th_i) * np.cos(al_i), np.cos(th_i) * np.cos(al_i), -1 * np.sin(al_i), -1 * np.sin(al_i) * d_i],
            [np.sin(th_i) * np.sin(al_i), np.cos(th_i) * np.sin(al_i), np.cos(al_i), np.cos(al_i) * d_i],
            [0, 0, 0, 1],
        ])

    """
    A utility function for clamping the error
    Reduces jitter by enforcing an upper bound on the error

    Arguments:
        err: A (x, y, z) vector representing the error in each dimension
        [optional] clamp_threshold: Float defining the upper bound.
            Defaults to 0.05
    """
    def __clamp_err(self, err, clamp_threshold: float = 0.05):
        if clamp_threshold <= 0:
            raise Exception("clamp_threshold must be greater than 0")

        # clamp error so we make small iterative changes
        mag_e = np.linalg.norm(err)
        if mag_e > clamp_threshold:
            err = clamp_threshold * (err / np.linalg.norm(err))

        return err

    """
    Calculates the expected change in theta with the jacobian transpose.
    This is one of many methods to iteratively generate the change in theta.

    Arguments:
        prev_ths: The previous thetas used to calculate the last end effector
        position in an iterative IK solver
        prev_err: The previous error between the expected position and the
        current position of the end effector, derived from using prev_ths.

    Output:
        The change in thetas (delta theta) to be added to the previous
        thetas in an IK solver.

    """
    def __jacobian_transpose_solver(self, prev_ths: np.array, prev_err: np.array):
        # caculate jacobian
        j = self.calc_jacobian(prev_ths, linear_only=True)

        # calculate inverse of jacobian as the transpose
        j_tp = np.transpose(j)

        # calculate change in theta
        d_th = j_tp.dot(prev_err)

        return d_th

    """
    Calculates an upperbound on the max reach of the robot from the DH parameters.

    THIS IS NOT THE EXACT MAX REACH (yet). 
    This function calculates an upper bound. To calculate the actual reach,
    one would need to use gradient decent and maximize the distance formula.

    Output:
        A float representing the maximum reach of the robot measured from frame 0
    """
    def __max_reach(self) -> float:
        radius = 0
        for param in self.dh_parameters:
            radius += np.linalg.norm(param[1:])
        
        return radius

    """
    Calculates a lowerbound on the min reach of the robot from the DH parameters.

    THIS IS NOT THE MIN REACH (yet)
    This function assumes the closest the robot can get to the center
    is the length of the first joint. This is VERY incorrect, but a good starting point.

    Output:
        A float representing the minimum reach of the robot measured from frame 0
    """
    def __min_reach(self) -> float:
        return np.linalg.norm(self.dh_parameters[0][1:])
        