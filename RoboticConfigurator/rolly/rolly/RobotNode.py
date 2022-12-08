import uuid
import numpy as np
from dummy.Robot import Robot
from dummy.workspace import find_max_reach, find_min_reach

def create_node(dh_parameters: np.ndarray):
    params = np.array(dh_parameters)
    r = Robot(params)
    return RobotNode(r, uuid.uuid4(), find_min_reach(r), find_max_reach(r))

class RobotNode:
    uuid: str
    min_reach: int
    max_reach: int
    robot: Robot

    def __init__(self, robot: Robot, uuid: str, min_reach: int, max_reach: int):
        self.uuid = uuid
        self.min_reach = min_reach
        self.max_reach = max_reach
        self.robot = robot