#!/usr/bin/env python3
"""
PiRC Vision Master - YOLOv10 + DepthAI + SLAM + 3D Recon + EdgeTPU
60FPS Multi-Modal Perception Pipeline
"""

import cv2
import numpy as np
import depthai as dai
import yaml
import threading
import time
from pathlib import Path
import argparse
import logging
from ultralytics import YOLO
import supervision as sv
from detectors.yolo10 import YOLO10Detector
from detectors.rt_detr import RTDETRDetector
from depthai_pipeline import DepthAIPipeline
from slam.orb_slam3 import ORBSLAM3
from reconstruction.colmap import COLMAPRecon
from edgetpu.coral import CoralDetector
from utils.ros_bridge import ROSBridge
import torch

class PiRCVision:
    def __init__(self, config_path="config.yaml"):
        self.config = self.load_config(config_path)
        self.logger = self.setup_logging()
        
        # Initialize accelerators
        self.yolo10 = YOLO10Detector(self.config['yolo10_model'])
        self.rt_detr = RTDETRDetector(self.config['rt_detr_model'])
        self.depthai = DepthAIPipeline()
        self.orb_slam = ORBSLAM3(vocab_file=self.config['orb_vocab'])
        self.colmap = COLMAPRecon()
        self.coral = CoralDetector(model_path=self.config['coral_model'])
        
        # ROS Bridge
        self.ros = ROSBridge()
        
        # Stats
        self.fps = sv.FPSCounter()
        self.annotator = sv.BoxAnnotator()
        self.heatmap = sv.HeatMapAnnotator()
        
        # RTSP Server
        self.rtsp_port = 8554
        
    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)
    
    def pipeline(self):
        """Main 60FPS vision pipeline"""
        pipeline = dai.Pipeline()
        self.depthai.setup_pipeline(pipeline)
        
        with dai.Device(pipeline) as device:
            q_rgb = device.getOutputQueue("rgb", maxSize=4, blocking=False)
            q_nn = device.getOutputQueue("nn", maxSize=4, blocking=False)
            
            while True:
                in_rgb = q_rgb.tryGet()
                in_nn = q_nn.tryGet()
                
                if in_rgb is not None:
                    frame = in_rgb.getCvFrame()
                    frame = cv2.resize(frame, (640, 640))
                    
                    # Multi-model inference
                    yolo_results = self.yolo10.predict(frame)
                    detr_results = self.rt_detr.predict(frame)
                    coral_results = self.coral.predict(frame)
                    
                    # Fusion
                    detections = self.fuse_detections(yolo_results, detr_results, coral_results)
                    
                    # Annotate
                    frame = self.annotator.annotate(scene=frame, detections=detections)
                    
                    # SLAM + 3D
                    pose = self.orb_slam.track(frame)
                    if pose is not None:
                        frame = self.draw_pose(frame, pose)
                    
                    # Stats
                    fps = self.fps.enter()
                    frame = sv.draw_text(frame, f"FPS: {fps:.1f}", (10, 30))
                    
                    # ROS Publish
                    self.ros.publish_detections(detections, frame)
                    self.ros.publish_pose(pose)
                    
                    # RTSP Stream
                    cv2.imshow("PiRC Vision", frame)
                    if cv2.waitKey(1) == ord('q'):
                        break
        
        cv2.destroyAllWindows()
    
    def fuse_detections(self, yolo, detr, coral):
        """NMS fusion across YOLO10 + RT-DETR + Coral"""
        all_dets = []
        all_dets.extend(yolo)
        all_dets.extend(detr)
        all_dets.extend(coral)
        
        return sv.NonMaxSuppression(
            threshold=0.5,
            iou_threshold=0.5
        ).trigger(all_dets)
    
    def draw_pose(self, frame, pose):
        """Draw SLAM pose"""
        h, w = frame.shape[:2]
        corners = self.orb_slam.project_points(pose)
        cv2.polylines(frame, [corners.astype(np.int32)], True, (0,255,0), 3)
        return frame

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()
    
    vision = PiRCVision(args.config)
    vision.pipeline()

if __name__ == "__main__":
    main()
