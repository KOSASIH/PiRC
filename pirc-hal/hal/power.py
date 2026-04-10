#!/usr/bin/env python3
"""
PiRC Power Monitor - INA219 I2C
"""

import smbus2
from ina219 import INA219
from ina219 import DeviceRangeError
import time

class PowerMonitor:
    def __init__(self, i2c_address=0x40):
        self.bus = smbus2.SMBus(1)
        self.ina = INA219(self.bus, 0x40)
        self.ina.configure()
    
    def read_power(self):
        """Read voltage, current, power"""
        try:
            voltage = self.ina.voltage()
            current = self.ina.current()
            power = self.ina.power()
            return {
                'voltage': voltage,
                'current': current / 1000.0,  # mA
                'power': power / 1000.0,     # W
                'battery_percent': self._calc_battery(voltage)
            }
        except DeviceRangeError:
            return {'error': 'Out of range'}
    
    def _calc_battery(self, voltage):
        # 3S LiPo: 9.0V (empty) - 12.6V (full)
        if voltage > 12.6: return 100
        if voltage < 9.0: return 0
        return (voltage - 9.0) / 3.6 * 100
    
    def is_low_battery(self, threshold=20):
        data = self.read_power()
        return data.get('battery_percent', 0) < threshold

# Usage
power = PowerMonitor()
while True:
    stats = power.read_power()
    print(f"Battery: {stats['battery_percent']:.1f}% | {stats['voltage']:.2f}V | {stats['current']:.1f}A")
    time.sleep(1)
