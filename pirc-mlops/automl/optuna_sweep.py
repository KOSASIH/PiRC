#!/usr/bin/env python3
import optuna
import wandb
from ultralytics import YOLO

def objective(trial):
    config = {
        'imgsz': trial.suggest_categorical('imgsz', [416, 640, 800]),
        'lr0': trial.suggest_float('lr0', 1e-5, 1e-2, log=True),
        'momentum': trial.suggest_float('momentum', 0.6, 0.98),
        'batch_size': trial.suggest_categorical('batch_size', [8, 16, 32])
    }
    
    wandb.init(project="PiRC-Optuna", config=config)
    
    model = YOLO('yolov10n.pt')
    results = model.train(
        data='coco8.yaml',
        epochs=30,
        **config,
        project='optuna_sweeps',
        name=f"trial_{trial.number}",
        device=0
    )
    
    mAP = results.results_dict['metrics/mAP50(B)']
    wandb.log({"mAP50": mAP})
    
    return mAP

def main():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)
    
    print("Best trial:", study.best_trial.params)
    wandb.log(study.best_trial)

if __name__ == "__main__":
    main()
