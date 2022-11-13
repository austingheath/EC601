import math
import string
from typing import List, Tuple
import numpy as np 

"""
ArticulatedRobot

Represents a simple kinematic robot chain
with only rotary joints. Prismatic joints
can be added with ease later.

Assume actuators are placed along the z
axis at the common normal (the point where
the x axis and z axis intersect - the origin).
"""
class ArticulatedRobot:

    """
    DH Parameters

    Tuple of three numbers per joint.
    Assume the joints are all rotary joints for now.
    alpha_i-1, a_i-1, d_i
    
    Brief description:
    a_i = the distance from Z_i to Z_i+1 measured along X_i
    alpha_i = the angle from Z_i to Z_i+1 measured about X_i
    d_i = the distance from X_i-1 to X_i measured along Z_i
    theta_i = the angle from X_i-1 to X_i measured about Z_i
    """
    dh_parameters: np.array

    num_joints: int

    reachable_radius: float

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
        self.reachable_radius = self.__reachable_radius()

    def is_position_reachable(self, target_position: Tuple[float]) -> bool:
        if len(target_position) != 3:
            raise Exception("Position must be a vector (x,y,z) given in base coordinates")

        # First, do a quick check and make sure the point is within
        # the spherical workspace of the robot.
        dist_origin = np.linalg.norm(np.array(target_position))
        if dist_origin > self.reachable_radius:
            return False

        # Next, it's necessary to solve the IK problem
        ths = self.inverse_kinematics(target_position)

        return True

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

    Inverse kinematic solution methods are explored here:
    http://graphics.cs.cmu.edu/nsp/course/15-464/Spring11/handouts/iksurvey.pdf

    Arguments:
        target_position: (x, y, z) tuple relative to the base (0) frame
        solver_method: The method used to calculate the inverse kinematics. Valid methods are: 
            - "jacobian_transpose"
            - More to come. Defaults to "jacobian_transpose"

    Output:
        A set of joint angles that gets the robot within 0.01 of the specified point
    """
    def inverse_kinematics(self, target_position: Tuple[float], solver_method: string = "jacobian_transpose") -> np.array:
        if len(target_position) != 3:
            raise Exception("Position must be a vector (x,y,z) given in base coordinates")

        # select the algorithm
        if solver_method == "jacobian_transpose":
            solver = self.__jacobian_transpose_solver
        else:
            raise Exception("The algorithm provided is not supported.")

        # set constants
        allowed_err = 0.01
        max_displacement = 0.05
        d_th_threshold = math.radians(5) # limit to 5 degrees

        # start calculation at theta = 0
        ths = np.zeros(self.num_joints)
        pos = self.forward_kinematics(ths)[:3, -1]
        err = target_position - pos

        while np.linalg.norm(err) > allowed_err:
            # clamp error so we make small iterative changes
            mag_e = np.linalg.norm(err)
            if mag_e > max_displacement:
                err = max_displacement * (err / np.linalg.norm(err))

            # caculate change in theta
            d_th = solver(ths, err)

            # calculate alpha using the method from
            # https://cseweb.ucsd.edu/classes/wi17/cse169-a/slides/CSE169_09.pdf
            a = d_th_threshold / max(d_th_threshold, np.amax(abs(d_th)))

            # update theta
            ths = ths + a * d_th

            # recalc position and error
            pos = self.forward_kinematics(ths)[:3, -1]
            err = target_position - pos

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
    This function calculates an upper bound. To calcualte the actual reach,
    one would need to use gradient decent and maximize the distance formula.

    Output:
        A float representing the maximum reach of the robot measured from frame 0
    """
    def __reachable_radius(self) -> float:
        radius = 0
        for param in self.dh_parameters:
            radius += np.linalg.norm(param[1:])
        
        return radius

        