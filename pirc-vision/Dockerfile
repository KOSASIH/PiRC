FROM nvcr.io/nvidia/l4t-pytorch:r35.4.1-pth2.1-py3

# PiRC Vision - Multi-Accelerator
RUN apt update && apt install -y \
    libopencv-dev=4.9.0+dfsg-5ubuntu1 \
    libdepthai-dev \
    libgoogle-glog-dev \
    libeigen3-dev \
    libatlas-base-dev \
    libtbb-dev \
    libpng-dev \
    libjpeg-dev \
    libopenexr-dev \
    libgflags-dev \
    && rm -rf /var/lib/apt/lists/*

# Coral Edge TPU
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" \
    | tee /etc/apt/sources.list.d/coral-edgetpu.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt update && apt install -y libedgetpu1-std

# Install Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# DepthAI pipeline
COPY depthai_pipeline.py .
RUN python3 -c "import depthai; print('DepthAI OK')"

# Copy source
COPY . /opt/pirc-vision
WORKDIR /opt/pirc-vision

EXPOSE 8554 8080
CMD ["python3", "main.py"]
