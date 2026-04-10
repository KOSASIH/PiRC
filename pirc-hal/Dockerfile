FROM ros:humble-ros-base

# PiRC HAL - Hardware Abstraction Layer
RUN apt update && apt install -y \
    python3-smbus \
    python3-ina219 \
    python3-pigpio \
    i2c-tools \
    can-utils \
    ros-humble-micro-ros-agent \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# C++ CAN drivers
RUN apt install -y libsocketcan-dev libcan-utils

# Python HAL
COPY requirements.txt .
RUN pip install -r requirements.txt

# Firmware
COPY firmware/ /opt/pirc-hal/firmware/
COPY . /opt/pirc-hal

WORKDIR /opt/pirc-hal
RUN colcon build --packages-select pirc_hal

CMD ["bash"]
