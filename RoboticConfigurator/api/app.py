from flask import Flask, request
import numpy as np
from rolly.search import search

app = Flask(__name__)

@app.post("/api/robots/create")
def robot_create():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
    else:
        return {
            "error": True,
            "message": "Content is not supported."
        }

    try:
        points = np.array(json['points'])
        orientations = np.array(json['orientations'])
        euler_seq = json['orientationSequence']
    except KeyError:
        return {
            "error": True,
            "message": "Please specify points, orientations, and orientationSequence"
        }

    print(points, orientations)

    try:
        robot_node = search(points_only=points, orientations_only=orientations, euler_seq=euler_seq)
    except Exception as inst:
        return {
            "error": True,
            "message": inst.args[0]
        }

    return {
        "error": False,
        "robot_dh": robot_node.robot.dh_parameters,
        "num_joints": robot_node.robot.num_joints,
    }