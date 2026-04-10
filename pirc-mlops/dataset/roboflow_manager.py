#!/usr/bin/env python3
from roboflow import Roboflow
import os
from pathlib import Path

class RoboflowManager:
    def __init__(self, api_key):
        self.rf = Roboflow(api_key=api_key)
        self.workspace = self.rf.workspace()
    
    def download_dataset(self, project_name, version, dataset_path="./datasets"):
        project = self.workspace.project(project_name)
        dataset = project.version(version).download("yolov8", dataset_path)
        return dataset.location
    
    def create_project(self, name, classes):
        """Create new Roboflow project"""
        project = self.workspace.create_project(
            name=name,
            project_type="object-detection",
            classes=classes
        )
        return project.url

# Usage
rf = RoboflowManager("YOUR_ROBOFLOW_API_KEY")
dataset_path = rf.download_dataset("robot-detection-v2", 1)
print(f"Dataset ready: {dataset_path}")
