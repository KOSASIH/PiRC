#!/usr/bin/env python3
"""
PiRC IMU XKF - Extended Kalman Filter Fusion
MPU9250 + Wheel Odometry
"""

import numpy as np
from filterpy.kalman import ExtendedKalmanFilter
import smbus2
import time
import math

class IMU_XKF:
    def __init__(self):
        self.bus = smbus2.SMBus(1)  # I2C bus 1
        self.setup_mpu9250()
        self.xkf = self.setup_xkf()
        self.wheel_odom = np.array([0.0, 0.0])  # [left_wheel, right_wheel]
    
    def setup_mpu9250(self):
        # MPU9250 Init
        self.bus.write_byte_data(0x68, 0x6B, 0x00)  # Wake up
        self.bus.write_byte_data(0x68, 0x1B, 0x00)  # Gyro range
        self.bus.write_byte_data(0x68, 0x1C, 0x00)  # Accel range
    
    def setup_xkf(self):
        kf = ExtendedKalmanFilter(dim_x=6, dim_z=6, dim_u=2)  # [x,y,theta,vx,vy,w]
        
        # State transition
        kf.F = np.eye(6)
        kf.F[0,3] = 0.1  # vx -> x
        kf.F[1,4] = 0.1  # vy -> y
        kf.F[2,5] = 0.1  # w -> theta
        
        # Measurement
        kf.H = np.eye(6)
        
        # Process noise
        kf.Q = np.diag([0.01, 0.01, 0.001, 0.1, 0.1, 0.01])
        
        # Measurement noise
        kf.R = np.diag([0.1, 0.1, 0.01, 1.0, 1.0, 0.1])
        
        kf.x = np.zeros(6)  # Initial state
        kf.P *= 10  # Initial covariance
        
        return kf
    
    def read_imu(self):
        """Read MPU9250 accel + gyro"""
        # Raw data (simplified)
        accel_x = self.bus.read_byte_data(0x68, 0x3B) / 16384.0
        accel_y = self.bus.read_byte_data(0x68, 0x3D) / 16384.0
        gyro_z = self.bus.read_byte_data(0x68, 0x47) / 131.0
        
        return np.array([accel_x, accel_y, gyro_z])
    
    def predict(self, u):
        """Predict step with wheel odometry"""
        self.xkf.predict(u=u)
    
    def update(self):
        """Update with IMU"""
        z = self.read_imu()
        self.xkf.update(z)
        return self.xkf.x  # [x, y, theta, vx, vy, w]
    
    def get_pose(self):
        return self.xkf.x[:3]  # x, y, theta

# Usage
imu = IMU_XKF()
while True:
    pose = imu.update()
    print(f"Pose: x={pose[0]:.2f}, y={pose[1]:.2f}, yaw={math.degrees(pose[2]):.1f}°")
    time.sleep(0.01)
