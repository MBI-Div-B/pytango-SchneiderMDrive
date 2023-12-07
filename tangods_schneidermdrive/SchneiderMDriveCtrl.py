#!/usr/bin/python3 -u
# coding: utf8
# SchneiderMDriveCtrl
from tango import DevState, AttrWriteType, DispLevel
from tango.server import Device, attribute, command, device_property
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

    __ACK = "\r\n"

    def init_device(self):
        super().init_device()
        self.set_state(DevState.INIT)
        self.info_stream("init_device()")
        # open serial
        try:
            self.serial = serial.Serial(self.Port, self.Baudrate, timeout=3)
            self.set_state(DevState.ON)
            self.info_stream(
                "connected to port {:s} with baudrate {:d}".format(
                    self.Port, self.Baudrate
                )
            )
        except Exception:
            self.error_stream("failed to open {:s}".format(self.Port))
            self.set_state(DevState.FAULT)
            return

    def delete_device(self):
        self.serial.close()
        self.set_state(DevState.OFF)
        self.info_stream("closed connection on {:s}".format(self.Port))

    @command(dtype_in=str, dtype_out=bool)
    def write(self, cmd):
        self.debug_stream("write command: {:s}".format(cmd))
        cmd = cmd + "\n"
        self.serial.write(cmd.encode("utf-8"))
        res = ""
        while not self.__ACK in res:
            self.serial.flush()
            line = self.serial.readline().decode("utf-8")
            res += line

    @command(dtype_out=str)
    def read(self):
        res = self.serial.readline().decode("utf-8").rstrip(self.__ACK)
        self.debug_stream("read response: {:s}".format(res))
        return res

    @command(dtype_in=str, dtype_out=str)
    def write_read(self, cmd):
        self.write(cmd)
        return self.read()


if __name__ == "__main__":
    SchneiderMDriveCtrl.run_server()
