#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, BatteryState
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
from pirc_hal.hal import MotorDriver, IMU_XKF, PowerMonitor, CANBus

class PiRCHALNode(Node):
    def __init__(self):
        super().__init__('pirc_hal_node')
        
        # HAL Components
        self.motors = MotorDriver()
        self.imu = IMU_XKF()
        self.power = PowerMonitor()
        self.can = CANBus()
        
        # Publishers
        self.imu_pub = self.create_publisher(Imu, '/imu/data_raw', 10)
        self.battery_pub = self.create_publisher(BatteryState, '/battery_state', 10)
        self.odom_pub = self.create_publisher(nav_msgs.msg.Odometry, '/odom', 10)
        
        # Subscribers
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        self.timer = self.create_timer(0.01, self.update_loop)
    
    def cmd_vel_callback(self, msg):
        self.motors.set_speed('left_motor', msg.linear.x * 500)
        self.motors.set_speed('right_motor', msg.linear.x * 500)
        self.motors.set_speed('turn_motor', msg.angular.z * 300)
    
    def update_loop(self):
        # IMU + XKF
        pose = self.imu.update()
        
        # Publish IMU
        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.angular_velocity.z = self.imu.xkf.x[5]
        self.imu_pub.publish(imu_msg)
        
        # Publish Battery
        power_data = self.power.read_power()
        battery_msg = BatteryState()
        battery_msg.header.stamp = self.get_clock().now().to_msg()
        battery_msg.percentage = power_data['battery_percent'] / 100.0
        battery_msg.voltage = power_data['voltage']
        self.battery_pub.publish(battery_msg)

def main():
    rclpy.init()
    node = PiRCHALNode()
    rclpy.spin(node)
    rclpy.shutdown()
