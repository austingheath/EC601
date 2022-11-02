from typing import List, Tuple
import numpy as np 

"""
ArticulatedRobot

Represents a simple kinematic robot chain
with only rotary joints. Prismatic joints
can be added with ease later.
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

    def __init__(self, dh_parameters: List[Tuple[float]]) -> None:
        self.dh_parameters = np.array(dh_parameters)
        self.num_joints = len(dh_parameters)

    """
    Calculate forward kinematics of the robot.

    Arguments:
        joint_angles: The angle (in radians) of each joint
        [optional] to_joint: If provided, only the forward kinematics up 
            to the specified joint will be calculated.

    Output:
        Returns the translation vector from base frame 0 
        to the last linkage's frame N
    """
    def forward_kinematics(self, joint_angles: Tuple[float], to_joint = None) -> np.array:
        if to_joint is None and len(joint_angles) != self.num_joints:
            raise Exception("Please provide an angle for each joint")
        elif to_joint is not None and len(joint_angles) > self.num_joints:
            raise Exception("to_joint must be less than or equal to the number of joints")
        elif to_joint is not None and to_joint < 1:
            raise Exception("to_joint must be greater than or equal to 1")

        if to_joint is None:
            to_joint = self.num_joints

        np_angles = np.array(joint_angles).reshape((len(joint_angles), 1))
        full_dh = np.concatenate((self.dh_parameters, np_angles), axis=1)

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

    This function makes use of the Jacobian transpose to
    solve the inverse kinematics problem. This was chosen since it is simple
    and efficient to calculate. There are issues with it, however, since this function
    is not expected to control a robot, but rather decide whether a point is reachable,
    it is sufficient for now.

    Other inverse kinematic solution methods are explored here:
    http://graphics.cs.cmu.edu/nsp/course/15-464/Spring11/handouts/iksurvey.pdf

    Arguments:
        target_position: (x, y, z) tuple relative to the base (0) frame

    Output:
        A set of joint angles that gets the robot within 0.01 of the specified point
    """
    def inverse_kinematics(self, target_position: Tuple[float]) -> np.array:
        if len(target_position) != 3:
            raise Exception("Position must be a vector (x,y,z) given in base coordinates")

        allowed_err = 0.01
        max_displacement = 0.05

        # start calculation at theta = 0
        ths = np.zeros(self.num_joints)

        pos = self.forward_kinematics(ths)[:3, -1]
        err = target_position - pos

        while np.linalg.norm(err) > allowed_err:
            # clamp error so we make small iterative changes
            mag_e = np.linalg.norm(err)
            if mag_e > max_displacement:
                err = max_displacement * (err / np.linalg.norm(err))

            # caculate jacobian
            j = self.calc_jacobian(ths, pos)

            j_tp = np.transpose(jac)
            a_com = j.dot(j_tp).dot(e)
            a = np.dot(e, a_com) / np.dot(a_com, a_com)

            # calculate delta theta using the Jacobian transpose
            d_th = a * j_tp.dot(e)

            # update theta
            ths = ths + d_th

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
    
    Output:
        The jacobian of the robot given the joint angles.
        An 6xN np.array, where N is the number of joints
    """
    def calc_jacobian(self, joint_angles: np.array, final_pos: np.array = None):
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

        for i in range(1, self.num_joints + 1):
            # TODO optimize this so it doesn't have to recalculate the intermediate
            # translation matrices each time
            t_mat = self.forward_kinematics(joint_angles, to_joint=i)
            r_mat = t_mat[:3, :3]
            p_vec = t_mat[:3, -1]

            w_por = np.dot(r_mat, mlt)
            v_por = np.cross(w_por, final_pos - p_vec)

            fin = np.concatenate((v_por, w_por))

            jacobian.append(fin)

        return np.array(jacobian)

    
    """
    T matrix construction for link i

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
