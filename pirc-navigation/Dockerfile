FROM osrf/ros2:humble-desktop

# PiRC Navigation - Nav2 + MPC + Behavior Trees
RUN apt update && apt install -y \
    ros-humble-nav2-bringup \
    ros-humble-navigation2 \
    ros-humble-slam-toolbox \
    ros-humble-rplidar-ros \
    ros-humble-realsense2-camera \
    ros-humble-py-trees \
    ros-humble-behavior-msgs \
    python3-casadi \
    python3-ompl \
    libsbpl-dev \
    && rm -rf /var/lib/apt/lists/*

# CasADi + ACADO
RUN pip install casadi==3.6.3 ompl-py py-trees==2.4.4

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source
COPY . /opt/pirc-navigation
WORKDIR /opt/pirc-navigation

# Build BehaviorTree.CPP
RUN mkdir -p bt_ws/src && \
    cd bt_ws/src && \
    git clone https://github.com/BehaviorTree/BehaviorTree.CPP.git && \
    cd .. && colcon build

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "pirc_navigation", "navigation_launch.py"]
