import cv2
import numpy as np
from orb_slam3 import System  # pip install orb_slam3_ros

class ORBSLAM3:
    def __init__(self, vocab_file="models/ORBvoc.txt"):
        self.system = System(vocab_file, "models/mono_rpi.yaml", "mono")
    
    def track(self, frame):
        """Track monocular SLAM"""
        current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        pose = self.system.trackMonocular(current_frame, int(time.time()*1000))
        return pose
    
    def project_points(self, pose):
        """Project 3D map points to 2D"""
        # Simplified projection
        points_3d = np.random.rand(8, 3) * 10  # Map points
        K = np.array([[640, 0, 320], [0, 640, 240], [0, 0, 1]])
        R, t = pose[:3,:3], pose[:3,3]
        points_2d = K @ (R @ points_3d.T + t[:, np.newaxis])
        return points_2d.T
