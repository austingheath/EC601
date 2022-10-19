from typing import List, Tuple
import numpy as np 

# An articualted robot is a 1..N jointed "arm" robot
# that might contain rotary and prismatic joints.
class ArticulatedRobot:

    # DH Parameters
    # Tuple of three numbers per joint.
    # Assume the joints are all rotary joints for now.
    # alpha_i-1, a_i-1, d_i
    #
    # Brief info:
    #
    # a_i = the distance from Z_i to Z_i+1 measured along X_i
    # alpha_i = the angle from Z_i to Z_i+1 measured about X_i
    # d_i = the distance from X_i-1 to X_i measured along Z_i
    # theta_i = the angle from X_i-1 to X_i measured about Z_i
    dh_parameters: np.array

    # Just the length of the list of DH Parameters
    num_joints: int

    def __init__(self, dh_parameters: List[Tuple[float]]) -> None:
        self.dh_parameters = np.array(dh_parameters)
        self.num_joints = len(dh_parameters)
        pass

    # Determines if the provided point exists in the
    # reachable workspace of the robot
    def point_is_reachable(point: Tuple[float]) -> bool:
        (x, y, z) = point
        pass

    # Determines if the provided point and orientation exists
    # in the dextrous workspace of the robot
    def orientation_is_reachable() -> bool:
        pass

    # Calculate forward kinematics given joint angles.
    # Returns the translation vector 0^T{N}
    def forward_kinematics(self, angles: Tuple[float]) -> np.array:
        if len(angles) is not self.num_joints:
            raise Exception("There must be a provided angle for each joint")

        np_angles = np.array(angles).reshape((len(angles), 1))
        full_dh = np.concatenate((self.dh_parameters, np_angles), axis=1)

        # TODO: Try and vectorize this operation later
        translations = self.__build_t_matrix(full_dh[0])
        for i in range(1, full_dh.shape[0]):
            t_matrix = self.__build_t_matrix(full_dh[i])
            translations = np.dot(translations, t_matrix)
        
        return translations
    
    # Full DH: alpha_i-1, a_i-1, d_i, theta_i
    def __build_t_matrix(self, full_dh: Tuple[float]) -> np.array:
        (al_i, a_i, d_i, th_i) = full_dh

        return np.array([
            [np.cos(th_i), -1 * np.sin(th_i), 0, a_i],
            [np.sin(th_i) * np.cos(al_i), np.cos(th_i) * np.cos(al_i), -1 * np.sin(al_i), -1 * np.sin(al_i) * d_i],
            [np.sin(th_i) * np.sin(al_i), np.cos(th_i) * np.sin(al_i), np.cos(al_i), np.cos(al_i) * d_i],
            [0, 0, 0, 1],
        ])

robot = ArticulatedRobot(
    [
        (0, 0, 0),
        (-90, 0, 0),
        (0, 1, 1),
        (-90, 1, 1),
        (90, 0, 0),
        (-90, 0, 0),
    ]
)

robot.forward_kinematics((0, 0, 0, 0, 0, 0))