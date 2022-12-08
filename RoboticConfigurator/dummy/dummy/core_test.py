import math
import numpy as np
from .core import forward_kinematics, inverse_kinematics
from .Robot import Robot

# def test_fk():
#     a2 = 1
#     d3 = 1
#     a3 = 1
#     d4 = 5

#     r = Robot(np.array([
#         (0, 0, 0),
#         (-1 * math.pi / 2, 0, 0),
#         (0, a2, d3),
#         (-1 * math.pi / 2, a3, d4),
#         (math.pi / 2, 0, 0),
#         (-1 * math.pi / 2, 0, 0),
#     ]))

#     # set joints
#     ths = (
#         math.pi / 2,
#         math.pi / 2,
#         math.pi / 2,
#         math.pi / 2,
#         math.pi / 2,
#         math.pi,
#     )
#     c_ths = np.cos(ths).tolist()
#     s_ths = np.sin(ths).tolist()

#     (c1, c2, c3, c4, c5, c6) = c_ths
#     (s1, s2, s3, s4, s5, s6) = s_ths

#     # calculate actual joints manually
#     c23 = c2*c3-s2*s3
#     s23 = c2*s3+s2*c3

#     r11 = c1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)+s1*(s4*c5*c6+c4*s6)
#     r21 = s1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)-c1*(s4*c5*c6+c4*s6)
#     r31 = -1*s23*(c4*c5*c6-s4*s6)-c23*s5*c6

#     r12 = c1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)+s1*(c4*c6-s4*c5*s6)
#     r22 = s1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)-c1*(c4*c6-s4*c5*s6)
#     r32 = -1*s23*(-1*c4*c5*s6-s4*c6)+c23*s5*s6
    
#     r13 = -1*c1*(c23*c4*s5+s23*c5)-s1*s4*s5
#     r23 = -1*s1*(c23*c4*s5+s23*c5)+c1*s4*s5
#     r33 = s23*c4*s5-c23*c5

#     px = c1*(a2*c2+a3*c23-d4*s23)-d3*s1
#     py = s1*(a2*c2+a3*c23-d4*s23)+d3*c1
#     pz = -1*a3*s23-a2*s2-d4*c23

#     expected = np.array([
#         [r11, r12, r13, px],
#         [r21, r22, r23, py],
#         [r31, r32, r33, pz],
#         [0, 0, 0, 1],
#     ])
#     actual = forward_kinematics(r, ths)

#     r_expected = np.round(expected, 5)
#     r_actual = np.round(actual, 5)

#     np.testing.assert_allclose(r_actual, r_expected)

def test_ik_position_simple():
    # Robot can only reach coordinates on x-y plane
    r = Robot(np.array([
        (0,0,0),
        (0,1,0),
        (0,1,0),
    ]))

    tg = np.array([
        [0, 1, 0, 0],
        [-1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]])

    thetas = inverse_kinematics(
        r, 
        target_position=tg[:3, -1], 
        target_orientation=tg[:3,:3], 
        allowed_pos_error=0.1, 
        restart_threshold=100, 
        solver_method="jacobian_psuedo")

    act = forward_kinematics(r, np.array(thetas))

    print(thetas)
    
    print(np.round(act))

    np.testing.assert_allclose(0, 1)

# def test_ik_position_reachable():
#     a2 = 1
#     d3 = 1
#     a3 = 1
#     d4 = 5

#     r = Robot(np.array([
#         (0, 0, 0),
#         (-1 * math.pi / 2, 0, 0),
#         (0, a2, d3),
#         (-1 * math.pi / 2, a3, d4),
#         (math.pi / 2, 0, 0),
#         (-1 * math.pi / 2, 0, 0),
#     ]))

#     t_goal = np.array([
#         [0, 0, -1, -1],
#         [0, -1, 0, -1],
#         [-1, 0, 0, 4],
#         [0, 0, 0, 1]
#     ])

#     thetas = inverse_kinematics(r, target_position=t_goal[:3,-1], tolerance_threshold=0.01, restart_threshold=100)

#     # Test with forward kinematics
#     calc_pos = forward_kinematics(r, thetas)[:3, -1]
#     round_pos = np.round(calc_pos, 1)

#     np.testing.assert_allclose(round_pos, t_goal[:3,-1])
