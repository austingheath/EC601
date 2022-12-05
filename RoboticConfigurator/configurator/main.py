import numpy as np
from RobotNode import create_node
from search import search

points = np.array([(0, 200, 0)])

robot_node = search(points_only=points)
print("Robot found!", robot_node.robot.dh_parameters)