#!/usr/bin/env python3
"""
PiRC MLOps Training Pipeline
YOLOv10 + RT-DETR + AutoML + W&B + Roboflow
"""

import wandb
import torch
import argparse
import yaml
from pathlib import Path
import os
from ultralytics import YOLO
from transformers import TrainingArguments, Trainer
import ray
from ray import tune
import optuna

class PiRCTrainer:
    def __init__(self, config_path, project_name="PiRC-Robotics"):
        self.config = self.load_config(config_path)
        wandb.init(project=project_name, config=self.config)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def load_config(self, path):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def train_yolo10(self):
        """YOLOv10 Training with W&B"""
        model = YOLO(self.config['model_path'])
        
        results = model.train(
            data=self.config['dataset_path'],
            epochs=self.config['epochs'],
            imgsz=self.config['imgsz'],
            batch=self.config['batch_size'],
            device=self.device,
            project='wandb/runs',
            name=wandb.run.name,
            exist_ok=True,
            plots=True,
            save_period=10
        )
        
        # Log metrics to W&B
        wandb.log({
            'mAP50': results.results_dict['metrics/mAP50(B)'],
            'mAP50-95': results.results_dict['metrics/mAP50-95(B)'],
            'precision': results.results_dict['metrics/precision(B)'],
            'recall': results.results_dict['metrics/recall(B)']
        })
        
        model.export(format='onnx')  # Export for deployment
        wandb.save("best.pt")
        return model
    
    def train_rt_detr(self):
        """RT-DETR Training"""
        from transformers import RTDETRForRealTimeDetection, RTDETRImageProcessor
        
        model = RTDETRForRealTimeDetection.from_pretrained(self.config['model_name'])
        processor = RTDETRImageProcessor.from_pretrained(self.config['model_name'])
        
        training_args = TrainingArguments(
            output_dir=f"wandb/{wandb.run.name}",
            num_train_epochs=self.config['epochs'],
            per_device_train_batch_size=self.config['batch_size'],
            gradient_accumulation_steps=4,
            learning_rate=2e-5,
            logging_steps=10,
            save_steps=500,
            report_to="wandb",
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=self.config['train_dataset'],
            eval_dataset=self.config['val_dataset'],
            tokenizer=processor,
        )
        
        trainer.train()
        wandb.log(trainer.evaluate())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/yolo10.yaml')
    parser.add_argument('--model', choices=['yolo10', 'rt_detr'], default='yolo10')
    args = parser.parse_args()
    
    trainer = PiRCTrainer(args.config)
    if args.model == 'yolo10':
        trainer.train_yolo10()
    else:
        trainer.train_rt_detr()

if __name__ == "__main__":
    main()
