#!/usr/bin/env python
"""
The pozyx ranging demo (c) Pozyx Labs
please check out https://www.pozyx.io/Documentation/Tutorials/getting_started/Python
This demo requires one (or two) pozyx shields. It demonstrates the 3D orientation and the functionality
to remotely read register data from a pozyx device. Connect one of the Pozyx devices with USB and run this script.
This demo reads the following sensor data:
- pressure
- acceleration
- magnetic field strength
- angular velocity
- the heading, roll and pitch
- the quaternion rotation describing the 3D orientation of the device. This can be used to transform from the body coordinate system to the world coordinate system.
- the linear acceleration (the acceleration excluding gravity)
- the gravitational vector
The data can be viewed in the Processing sketch orientation_3D.pde
"""
from time import time

from pypozyx import *
from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import SimpleUDPClient


class Orientation3D(object):
    """Reads out all sensor data from either a local or remote Pozyx"""

    def __init__(self, pozyx, osc_udp_client, remote_id=None):
        self.pozyx = pozyx
        self.remote_id = remote_id

        self.osc_udp_client = osc_udp_client

    def setup(self):
        """There is no specific setup functionality"""
        self.current_time = time()

    def loop(self):
        """Gets new IMU sensor data"""
        sensor_data = SensorData()
        calibration_status = SingleRegister()
        if self.remote_id is not None or self.pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
            status = self.pozyx.getAllSensorData(sensor_data, self.remote_id)
            status &= self.pozyx.getCalibrationStatus(calibration_status, self.remote_id)
            if status == POZYX_SUCCESS:
                return self.publishSensorData(sensor_data, calibration_status)

    def publishSensorData(self, sensor_data, calibration_status):
        """Makes the OSC sensor data package and publishes it"""

        print("*" * 25)
        print(sensor_data.acceleration)
        print(sensor_data.linear_acceleration)
        print(sensor_data.angular_vel)
        print(sensor_data.euler_angles)
        print(sensor_data.gravity_vector)
        print(sensor_data.magnetic)
        print(sensor_data.quaternion)
        print(sensor_data.temperature)
        print("*" * 25)

        return {"x-value-acceleration": sensor_data.acceleration.data[0],
                "y-value-acceleration": sensor_data.acceleration.data[1],
                "z-value-acceleration": sensor_data.acceleration.data[2],
                "x-value-acceleration-linear": sensor_data.linear_acceleration.data[0],
                "y-value-acceleration-linear": sensor_data.linear_acceleration.data[1],
                "z-value-acceleration-linear": sensor_data.linear_acceleration.data[2],
                "x-value-angular-velocity": sensor_data.angular_vel.data[0],
                "y-value-angular-velocity": sensor_data.angular_vel.data[1],
                "z-value-angular-velocity": sensor_data.angular_vel.data[2],
                "heading-value-euler": sensor_data.euler_angles.data[0],
                "roll-value-euler": sensor_data.euler_angles.data[1],
                "pitch-value-euler": sensor_data.euler_angles.data[2],
                "x-value-gravity-vector": sensor_data.gravity_vector.data[0],
                "y-value-gravity-vector": sensor_data.gravity_vector.data[1],
                "z-value-gravity-vector": sensor_data.gravity_vector.data[2],
                "x-value-magnetic": sensor_data.magnetic.data[0],
                "y-value-magnetic": sensor_data.magnetic.data[1],
                "z-value-magnetic": sensor_data.magnetic.data[2],
                "w-value-quaternion": sensor_data.quaternion.data[0],
                "x-value-quaternion": sensor_data.quaternion.data[1],
                "y-value-quaternion": sensor_data.quaternion.data[2],
                "z-value-quaternion": sensor_data.quaternion.data[3],
                "temperature": sensor_data.temperature
                }

    def addSensorData(self, sensor_data):
        """Adds the sensor data to the OSC message"""
        #self.msg_builder.add_arg(sensor_data.pressure)
        self.addComponentsOSC(sensor_data.acceleration)
        self.addComponentsOSC(sensor_data.magnetic)
        self.addComponentsOSC(sensor_data.angular_vel)
        self.addComponentsOSC(sensor_data.euler_angles)
        self.addComponentsOSC(sensor_data.quaternion)
        self.addComponentsOSC(sensor_data.linear_acceleration)
        self.addComponentsOSC(sensor_data.gravity_vector)

    def addComponentsOSC(self, component):
        """Adds a sensor data component to the OSC message"""
        for data in component.data:
            self.msg_builder.add_arg(float(data))

    def addCalibrationStatus(self, calibration_status):
        """Adds the calibration status data to the OSC message"""
        self.msg_builder.add_arg(calibration_status[0] & 0x03)
        self.msg_builder.add_arg((calibration_status[0] & 0x0C) >> 2)
        self.msg_builder.add_arg((calibration_status[0] & 0x30) >> 4)
        self.msg_builder.add_arg((calibration_status[0] & 0xC0) >> 6)

if __name__ == '__main__':
    # shortcut to not have to find out the port yourself
    serial_port = get_serial_ports()[1].device

    remote_id = 0x6166                    # remote device network ID
    remote = True                         # whether to use a remote device
    if not remote:
        remote_id = None

    ip = "127.0.0.1"
    network_port = 8888

    pozyx = PozyxSerial(serial_port)
    osc_udp_client = SimpleUDPClient(ip, network_port)
    o = Orientation3D(pozyx, osc_udp_client, remote_id)
    o.setup()
    while True:
        o.loop()