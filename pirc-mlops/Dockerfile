FROM nvcr.io/nvidia/pytorch:24.09-py3

# PiRC MLOps - Production Training Environment
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y \
    git wget curl vim htop \
    label-studio \
    roboflow \
    && rm -rf /var/lib/apt/lists/*

# Python ML Stack
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Ray + Distributed Training
RUN pip install "ray[tune]"==2.10.0 optuna==3.6.1 wandb==0.17.0

# Model Zoo
COPY model_zoo/ /opt/pirc-mlops/model_zoo/
RUN python /opt/pirc-mlops/model_zoo/download_models.py

# Label Studio
EXPOSE 8080 8081 9090
WORKDIR /workspace
COPY . /workspace

CMD ["tail", "-f", "/dev/null"]
