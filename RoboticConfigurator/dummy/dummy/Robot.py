from typing import List, Tuple
import numpy as np

class Robot:
    dh_parameters: np.ndarray
    num_joints: int

    def __init__(self, dh_parameters: np.ndarray) -> None:
        """
        dh_parameters: A list of tuples with length equal to the number of joints. 
            The tuples should contain three numbers and represent the DH paramters
            for that paricular joint: (alpha_i-1, a_i-1, d_i).
        """
        dh_parameters = np.array(dh_parameters)

        if len(dh_parameters.shape) != 2 or dh_parameters.shape[1] != 3:
            raise Exception("DH parameters must be a list of 3 length tuples.")

        if len(dh_parameters) > 7:
            raise Exception("DH parameters must have 7 DOF or less.")
        
        for params in dh_parameters:
            if params[1] < 0 or params[2] < 0:
                raise Exception("a_i-1 and d_i must be positive")
 
        self.dh_parameters = np.array(dh_parameters)
        self.num_joints = len(dh_parameters)

    