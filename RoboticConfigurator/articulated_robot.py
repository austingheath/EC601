from typing import Tuple
import numpy as np 

# An articualted robot is a 1..N jointed "arm" robot
# that might contain rotary and prismatic joints.
class ArticulatedRobot:

    # a_i = the distance from Z_i to Z_i+1 measured along X_i
    # alpha_i = the angle from Z_i to Z_i+1 measured about X_i
    # d_i = the distance from X_i-1 to X_i measured along Z_i
    # theta_i = the angle from X_i-1 to X_i measured about Z_i

    def __init__(self) -> None:
        pass

    # Determines if the provided point exists in the
    # reachable workspace of the robot
    def point_is_reachable(point: Tuple[float]) -> bool:
        (x, y, z) = point

    # Determines if the provided point and orientation exists
    # in the dextrous workspace of the robot
    def orientation_is_reachable() -> bool:
        pass
    
    def inverse_kinematics():
        pass
