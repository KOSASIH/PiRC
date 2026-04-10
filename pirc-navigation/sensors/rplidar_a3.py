#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import serial
import numpy as np

class RPLidarA3(Node):
    def __init__(self):
        super().__init__('rplidar_a3')
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        
        self.ser = serial.Serial('/dev/ttyUSB0', 256000, timeout=1)
        self.timer = self.create_timer(0.1, self.scan_callback)
    
    def scan_callback(self):
        # RPLIDAR A3 protocol
        cmd = bytes([0x88, 0x00, 0x00, 0x00, 0x22])  # Scan command
        self.ser.write(cmd)
        
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'laser'
        scan.angle_min = 0
        scan.angle_max = 2 * np.pi
        scan.angle_increment = 0.0087  # 0.5 degrees
        scan.range_min = 0.15
        scan.range_max = 30.0
        scan.ranges = self.read_scan()
        
        self.scan_pub.publish(scan)
