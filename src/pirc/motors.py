"""GPIO Motor Control Plugin"""
import RPi.GPIO as GPIO
import asyncio

class MotorPlugin:
    def __init__(self, left_pin=17, right_pin=18):
        self.left_pin = left_pin
        self.right_pin = right_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([left_pin, right_pin], GPIO.OUT)
    
    async def __call__(self, state):
        """Plugin interface - called every 50Hz tick"""
        # PWM simulation
        GPIO.output(self.left_pin, state.motors.get("left", 0) > 0)
        GPIO.output(self.right_pin, state.motors.get("right", 0) > 0)
