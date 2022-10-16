# Given a set of parameters, determine the articulated robot
# build_robot(...inputs) = output
# 
# Version 0.1.0
# 
# Inputs
# - reach_position: Position the robot must "touch" from a origin specified in world coordinates
#   (x, y, z)
#
# Assumptions
# - Only 1 rotary joint and 1 link
# - No prismatic joints
# - Weightless joint actuators and links
# - No offset for joints
# 
# Output
# - Robot object that contains a single joint's length and the number of joints

import math

class ArticulatedRobot:
    def __init__(self, num_joints, joint_length):
        if num_joints <= 0:
            raise Exception("Robot must contain more than 0 joints")

        self.num_joints = num_joints;
        self.joint_length = joint_length;

    def build_robot(reach_position):
        (x, y, z) = reach_position

        joint_length = math.sqrt(x**2 + y**2 + z**2)

        return Robot(1, joint_length);

print(Robot.build_robot((0, 0, 2)).joint_length)


