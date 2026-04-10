#!/usr/bin/env python3
import ray
from ray import tune
from ray.tune.integration.wandb import WandbLoggerCallback
import torch.nn as nn
from ultralytics import YOLO

def objective(config):
    """Ray Tune objective function"""
    model = YOLO('yolov10n.pt')
    
    results = model.train(
        data='coco8.yaml',  # Small dataset for tuning
        epochs=50,
        imgsz=config['imgsz'],
        lr0=config['lr0'],
        momentum=config['momentum'],
        weight_decay=config['weight_decay'],
        batch=config['batch_size'],
        device='cuda',
        project='ray_tune',
        name=tune.get_trial_name(),
        exist_ok=True,
        verbose=False
    )
    
    # Report metrics
    tune.report(
        mAP50=results.results_dict['metrics/mAP50(B)'],
        loss=results.results_dict['train/box_loss']
    )

def main():
    ray.init()
    
    scheduler = tune.schedulers.ASHAScheduler(
        max_t=50,
        grace_period=10,
        reduction_factor=2
    )
    
    tuner = tune.Tuner(
        objective,
        param_space={
            'imgsz': tune.choice([416, 640, 800]),
            'lr0': tune.loguniform(1e-5, 1e-2),
            'momentum': tune.uniform(0.6, 0.98),
            'weight_decay': tune.loguniform(1e-5, 1e-2),
            'batch_size': tune.choice([8, 16, 32])
        },
        run_config=tune.RunConfig(
            metric="mAP50",
            mode="max",
            scheduler=scheduler,
            num_samples=100,
            callbacks=[WandbLoggerCallback(project="PiRC-RayTune")]
        )
    )
    
    results = tuner.fit()
    print("Best config:", results.get_best_result().config)

if __name__ == "__main__":
    main()
