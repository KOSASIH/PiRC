import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import torch

class YOLO10Detector:
    def __init__(self, model_path="models/yolo10n.pt"):
        self.model = YOLO(model_path)
        self.model.fuse()
        self.byte_tracker = sv.ByteTrack()
        self.class_names = self.model.names
        
    def predict(self, frame):
        results = self.model(frame, verbose=False, conf=0.25)
        detections = sv.Detections.from_ultralytics(results[0])
        tracks = self.byte_tracker.update_with_detections(detections)
        return tracks
