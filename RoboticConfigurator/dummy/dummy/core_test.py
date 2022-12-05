import math
import numpy as np
from .core import convert_euler_to_rot, convert_rot_matrix_euler, forward_kinematics, inverse_kinematics
from .Robot import Robot

def test_fk():
    a2 = 1
    d3 = 1
    a3 = 1
    d4 = 5

    r = Robot(np.array([
        (0, 0, 0),
        (-1 * math.pi / 2, 0, 0),
        (0, a2, d3),
        (-1 * math.pi / 2, a3, d4),
        (math.pi / 2, 0, 0),
        (-1 * math.pi / 2, 0, 0),
    ]))

    # set joints
    ths = (
        math.pi / 2,
        math.pi / 2,
        math.pi / 2,
        math.pi / 2,
        math.pi / 2,
        math.pi,
    )
    c_ths = np.cos(ths).tolist()
    s_ths = np.sin(ths).tolist()

    (c1, c2, c3, c4, c5, c6) = c_ths
    (s1, s2, s3, s4, s5, s6) = s_ths

    # calculate actual joints manually
    c23 = c2*c3-s2*s3
    s23 = c2*s3+s2*c3

    r11 = c1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)+s1*(s4*c5*c6+c4*s6)
    r21 = s1*(c23*(c4*c5*c6-s4*s6)-s23*s5*c6)-c1*(s4*c5*c6+c4*s6)
    r31 = -1*s23*(c4*c5*c6-s4*s6)-c23*s5*c6

    r12 = c1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)+s1*(c4*c6-s4*c5*s6)
    r22 = s1*(c23*(-1*c4*c5*s6-s4*c6)+s23*s5*s6)-c1*(c4*c6-s4*c5*s6)
    r32 = -1*s23*(-1*c4*c5*s6-s4*c6)+c23*s5*s6
    
    r13 = -1*c1*(c23*c4*s5+s23*c5)-s1*s4*s5
    r23 = -1*s1*(c23*c4*s5+s23*c5)+c1*s4*s5
    r33 = s23*c4*s5-c23*c5

    px = c1*(a2*c2+a3*c23-d4*s23)-d3*s1
    py = s1*(a2*c2+a3*c23-d4*s23)+d3*c1
    pz = -1*a3*s23-a2*s2-d4*c23

    expected = np.array([
        [r11, r12, r13, px],
        [r21, r22, r23, py],
        [r31, r32, r33, pz],
        [0, 0, 0, 1],
    ])
    actual = forward_kinematics(r, ths)

    r_expected = np.round(expected, 5)
    r_actual = np.round(actual, 5)

    np.testing.assert_allclose(r_actual, r_expected)

def test_ik_position_reachable():
    a2 = 1
    d3 = 1
    a3 = 1
    d4 = 5

    r = Robot(np.array([
        (0, 0, 0),
        (-1 * math.pi / 2, 0, 0),
        (0, a2, d3),
        (-1 * math.pi / 2, a3, d4),
        (math.pi / 2, 0, 0),
        (-1 * math.pi / 2, 0, 0),
    ]))

    t_goal = np.array([
        [0, 0, -1, -1],
        [0, -1, 0, -1],
        [-1, 0, 0, 4],
        [0, 0, 0, 1]
    ])

    thetas = inverse_kinematics(r, target_position=t_goal[:3,-1], tolerance_threshold=0.01, restart_threshold=100)

    # Test with forward kinematics
    calc_pos = forward_kinematics(r, thetas)[:3, -1]
    round_pos = np.round(calc_pos, 1)

    np.testing.assert_allclose(round_pos, t_goal[:3,-1])

def test_convert_rot_matrix_euler():
    rot_m1 = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ])

    rot_m2 = np.array([
        [0, 0, 1],
        [1, 0, 0],
        [0, 1, 0],
    ])

    rot_m3 = np.array([
        [0, 0, 1],
        [0, 1, 0],
        [-1, 0, 0],
    ])

    np.testing.assert_allclose(convert_rot_matrix_euler(rot_m1), np.array((0,0,0)))
    np.testing.assert_allclose(convert_rot_matrix_euler(rot_m2), np.array((math.pi/2,0,math.pi/2)))
    np.testing.assert_allclose(convert_rot_matrix_euler(rot_m3), np.array((0,math.pi/2,0)))

def test_convert_euler_to_rot():
    e1 = np.array((0,0,0))
    rot1 = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ])

    e2 = np.array((math.pi/2,0,math.pi/2))
    rot2 = np.array([
        [0, 0, 1],
        [1, 0, 0],
        [0, 1, 0],
    ])

    e3 = np.array((0,math.pi/2,0))
    rot3 = np.array([
        [0, 0, 1],
        [0, 1, 0],
        [-1, 0, 0],
    ])

    np.testing.assert_allclose(rot1, np.round(convert_euler_to_rot(e1),2))
    np.testing.assert_allclose(rot2, np.round(convert_euler_to_rot(e2),2))
    np.testing.assert_allclose(rot3, np.round(convert_euler_to_rot(e3),2))