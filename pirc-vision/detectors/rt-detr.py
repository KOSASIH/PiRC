from transformers import RTDETRImageProcessor, RTDETRForRealTimeDetection
import torch
import supervision as sv
import numpy as np

class RTDETRDetector:
    def __init__(self, model_path="models/rt-detr-resnet50.pt"):
        self.processor = RTDETRImageProcessor.from_pretrained(model_path)
        self.model = RTDETRForRealTimeDetection.from_pretrained(model_path)
        self.model.eval()
        self.class_names = self.model.config.id2label
        
    def predict(self, frame):
        inputs = self.processor(images=frame, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        target_sizes = torch.tensor([frame.shape[:2]])
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]
        
        boxes = results["boxes"].cpu().numpy()
        scores = results["scores"].cpu().numpy()
        labels = results["labels"].cpu().numpy()
        
        return sv.Detections(
            xyxy=boxes,
            confidence=scores,
            class_id=labels
        )
