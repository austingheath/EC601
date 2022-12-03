import numpy as np
from RobotNode import create_node

r = create_node(np.array([[0,0,0]]))
print(r.max_reach)