#!/usr/bin/env python3
"""
PiRC CAN Bus - PiCAN3 + SocketCAN + ODrive
"""

import can
import time
import threading

class CANBus:
    def __init__(self, channel='can0', bitrate=1000000):
        # Setup SocketCAN
        os.system(f"sudo ip link set {channel} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {channel} txqueuelen 1000")
        
        self.bus = can.interface.Bus(channel=channel, bustype='socketcan')
        self.odrive_ids = {}
    
    def discover_odrive(self):
        """Auto-discover ODrive motors"""
        msg = can.Message(arbitration_id=0x007, data=[0x00], is_extended_id=False)
        self.bus.send(msg)
        
        while True:
            try:
                response = self.bus.recv(timeout=0.1)
                if response.arbitration_id == 0x008:
                    serial = response.data.hex()
                    self.odrive_ids[serial] = response.arbitration_id
                    print(f"Found ODrive: {serial}")
            except:
                break
    
    def set_odrive_velocity(self, serial, velocity):
        """Set ODrive velocity (RPM)"""
        axis_id = self.odrive_ids.get(serial, 0)
        msg = can.Message(
            arbitration_id=axis_id,
            data=[0x07, 0x00, 0x00, int(velocity), 0, 0, 0, 0],
            is_extended_id=False
        )
        self.bus.send(msg)
    
    def read_odrive_status(self, serial):
        msg = can.Message(arbitration_id=self.odrive_ids[serial], 
                         data=[0x01], is_extended_id=False)
        self.bus.send(msg)
        return self.bus.recv(timeout=0.1)

# Usage
canbus = CANBus()
canbus.discover_odrive()
canbus.set_odrive_velocity('ODRV1', 100)  # 100 RPM
