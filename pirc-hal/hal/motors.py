#!/usr/bin/env python3
"""
PiRC Motor HAL - TB6600, DRV8876, ODrive
"""

import pigpio
import time
import yaml
from enum import Enum

class MotorType(Enum):
    TB6600 = "tb6600"
    DRV8876 = "drv8876"
    ODRIVE = "odrive"

class MotorDriver:
    def __init__(self, config_path="config/motor_config.yaml"):
        self.pi = pigpio.pi()
        self.motors = self.load_config(config_path)
    
    def load_config(self, path):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config['motors']
    
    def set_speed(self, motor_id, speed, direction=1):
        """Set motor speed (-1000 to 1000)"""
        motor = self.motors[motor_id]
        motor_type = motor['type']
        
        if motor_type == MotorType.TB6600:
            self._tb6600_control(motor, speed, direction)
        elif motor_type == MotorType.DRV8876:
            self._drv8876_control(motor, speed, direction)
        elif motor_type == MotorType.ODRIVE:
            self._odrive_control(motor, speed)
    
    def _tb6600_control(self, motor, speed, direction):
        """TB6600 Stepper Driver (PWM + DIR)"""
        pwm_pin = motor['pwm_pin']
        dir_pin = motor['dir_pin']
        
        # Direction
        self.pi.write(dir_pin, 1 if speed > 0 else 0)
        
        # PWM frequency 1kHz, duty cycle = |speed|/1000
        pwm_freq = 1000
        duty_cycle = abs(speed) / 1000.0
        self.pi.set_PWM_frequency(pwm_pin, pwm_freq)
        self.pi.set_PWM_dutycycle(pwm_pin, int(duty_cycle * 255))
    
    def _drv8876_control(self, motor, speed, direction):
        """DRV8876 H-Bridge (PWM + IN1/IN2)"""
        pwm_pin = motor['pwm_pin']
        in1_pin = motor['in1_pin']
        in2_pin = motor['in2_pin']
        
        pwm_value = abs(speed) / 1000.0 * 255
        
        if speed > 0:
            self.pi.write(in1_pin, 1)
            self.pi.write(in2_pin, 0)
        else:
            self.pi.write(in1_pin, 0)
            self.pi.write(in2_pin, 1)
        
        self.pi.set_PWM_dutycycle(pwm_pin, int(pwm_value))
    
    def _odrive_control(self, motor, speed):
        """ODrive CAN Control"""
        import can
        bus = can.interface.Bus(bustype='socketcan', channel=motor['can_channel'])
        msg = can.Message(
            arbitration_id=0x007,
            data=[0x07, 0x00, 0x00, int(speed*1000), 0, 0, 0, 0],
            is_extended_id=False
        )
        bus.send(msg)
    
    def stop_all(self):
        for motor_id in self.motors:
            self.set_speed(motor_id, 0)

if __name__ == "__main__":
    motors = MotorDriver()
    motors.set_speed('left_motor', 500)
    motors.set_speed('right_motor', 500)
    time.sleep(2)
    motors.stop_all()
