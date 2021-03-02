#!/usr/bin/python3 -u
# coding: utf8
# SchneiderMDriveCtrl
from tango import DevState, AttrWriteType, DispLevel
from tango.server import Device, attribute, command, device_property
import time
import sys
import serial


class SchneiderMDriveCtrl(Device):
    # device properties
    Port = device_property(
        dtype="str",
        default_value="/dev/ttySchneider",
    )

    Baudrate = device_property(
        dtype="int",
        default_value=9600,
    )

    # device attributes
    port = attribute(
        dtype="str",
        label="port",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    baudrate = attribute(
        dtype="int",
        label="baudrate",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    __ACK = '\r\n'

    def init_device(self):
        self.info_stream("init_device()")
        self.set_state(DevState.OFF)
        self.get_device_properties(self.get_device_class())
        # open serial
        try:
            self.serial = serial.Serial(self.Port, self.Baudrate, timeout=3)
            self.set_state(DevState.ON)
            self.info_stream("connected to port {:s} with baudrate {:d}".format(
                self.Port, self.Baudrate))
        except Exception:
            self.error_stream("failed to open {:s}".format(self.Port))
            sys.exit(255)

    def delete_device(self):
        self.close()

    # attribute read/write methods
    def read_port(self):
        return self.Port

    def read_baudrate(self):
        return int(self.Baudrate)

    @command
    def close(self):
        try:
            self.serial.close()
            self.set_state(DevState.OFF)
            self.info_stream("closed connection on {:s}".format(self.Port))
        except Exception:
            self.warn_stream("could not close connection on {:s}".format(self.Port))

    @command(dtype_in=str, dtype_out=bool)
    def write(self, cmd):
        self.debug_stream("write command: {:s}".format(cmd))
        cmd = cmd + '\n'
        self.serial.write(cmd.encode("utf-8"))
        self.serial.flush()
        time.sleep(0.02)  # 20ms wait time
        res = self.serial.readline().decode("utf-8")
        if self.__ACK in res:
            return True
        else:
            # no acknowledgment in response
            return False

    @command(dtype_out=str)
    def read(self):
        res = self.serial.readline().decode("utf-8").rstrip(self.__ACK)
        self.debug_stream("read response: {:s}".format(res))
        return res

    @command(dtype_in=str, dtype_out=str)
    def write_read(self, cmd):
        if self.write(cmd):
            return self.read()
        else:
            return 'error'


if __name__ == "__main__":
    SchneiderMDriveCtrl.run_server()
