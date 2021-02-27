#!/usr/bin/python3 -u
# coding: utf8
# SchneiderMDriveAxis
from tango import Database, DevFailed, AttrWriteType, DevState, DeviceProxy, DispLevel
from tango.server import device_property
from tango.server import Device, attribute, command
import sys


class SchneiderMDriveAxis(Device):
    # device properties
    CtrlDevice = device_property(
        dtype="str",
        default_value="tango://localhost:10000/rsxs/SchneiderMDriveCtrl/1#dbase=no",
    )

    Axis = device_property(
        dtype="str",
        default_value="X",
    )

    position = attribute(
        dtype="float",
        format="%8.3f",
        label="position",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.OPERATOR,
    )

    def init_device(self):
        super().init_device()
        self.info_stream("init_device()")

        self.info_stream("module axis: {:s}".format(self.Axis))

        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream("ctrl. device: {:s}".format(self.CtrlDevice))
        except DevFailed as df:
            self.error_stream("failed to create proxy to {:s}".format(df))
            sys.exit(255)

        # check if the CrlDevice ON, if not open the serial port
        if str(self.ctrl.state()) == "OFF":
            self.ctrl.open()
            self.info_stream("controller sucessfully opened")
        else:
            self.info_stream("controller was already open")

    def delete_device(self):
        self.set_state(DevState.OFF)

    def dev_state(self):
#         answer = self._send_cmd("SE")
#         if (self.Axis == 0):
#             if self.__Inverted:
#                 self.__HW_Limit_Minus = bool(int(answer[2]) & self.__LIM_PLUS)
#                 self.__HW_Limit_Plus = bool(int(answer[2]) & self.__LIM_MINUS)
#             else:
#                 self.__HW_Limit_Minus = bool(int(answer[2]) & self.__LIM_MINUS)
#                 self.__HW_Limit_Plus = bool(int(answer[2]) & self.__LIM_PLUS)
#             moving = not(bool(int(answer[1]) & 1))
#         else:
#             if self.__Inverted:
#                 self.__HW_Limit_Minus = bool(int(answer[6]) & self.__LIM_PLUS)
#                 self.__HW_Limit_Plus = bool(int(answer[6]) & self.__LIM_MINUS)
#             else:
#                 self.__HW_Limit_Minus = bool(int(answer[6]) & self.__LIM_MINUS)
#                 self.__HW_Limit_Plus = bool(int(answer[6]) & self.__LIM_PLUS)
#             moving = not(bool(int(answer[5]) & 1))
#         self.debug_stream("HW limit-: {0}".format(self.__HW_Limit_Minus))
#         self.debug_stream("HW limit+: {0}".format(self.__HW_Limit_Plus))
#         if moving is False:
#             self.set_status("Device in ON")
#             self.debug_stream("device is: ON")
#             return DevState.ON
#         else:
#             self.set_status("Device is MOVING")
#             self.debug_stream("device is: MOVING")
#             return DevState.MOVING
        pass

    # attribute read/write methods
    def read_position(self):
        return float(self.write_read("PR P"))

    def write_position(self, value):
        self.write("MA {:.4f}".format(value))

    # commands
    @command(dtype_in=str, doc_in="enter a command")  
    def write(self, cmd):
        cmd = str(self.Axis) + cmd
        res = self.ctrl.write(cmd)
        if not res:
            self.set_state(DevState.FAULT)
            self.warn_stream("command not acknowledged from controller "
                             "-> Fault State")

    @command(dtype_in=str, dtype_out=str, doc_in="enter a command", doc_out="response")  
    def write_read(self, cmd):
        cmd = str(self.Axis) + cmd
        res = self.ctrl.write_read(cmd)
        if res == "error":
            self.set_state(DevState.FAULT)
            self.warn_stream("command not acknowledged from controller "
                             "-> Fault State")
            return ""
        else:
            return res

#     @command(dtype_in=float, doc_in="position")
#     def set_position(self, value):
#         if self.__Inverted:
#             value = -1*value
#         self.send_cmd("P20S{:.4f}".format(value))
# 
#     @command
#     def jog_plus(self):
#         if self.__Inverted:
#             self.send_cmd("L-")
#         else:
#             self.send_cmd("L+")
#         self.set_state(DevState.MOVING)
# 
#     @command
#     def jog_minus(self):
#         if self.__Inverted:
#             self.send_cmd("L+")
#         else:
#             self.send_cmd("L-")
#         self.set_state(DevState.MOVING)
# 
#     @command
#     def homing_plus(self):
#         if self.__Inverted:
#             self.send_cmd("0-")
#         else:
#             self.send_cmd("0+")
#         self.set_state(DevState.MOVING)
# 
#     @command
#     def homing_minus(self):
#         if self.__Inverted:
#             self.send_cmd("0+")
#         else:
#             self.send_cmd("0-")
#         self.set_state(DevState.MOVING)
# 
#     @command
#     def stop(self):
#         self.send_cmd("S")
#         self.set_state(DevState.ON)
# 
#     @command
#     def abort(self):
#         self.send_cmd("SN")
#         self.set_state(DevState.ON)
# 
#     @command(dtype_out=str)
#     def write_to_eeprom(self):
#         self.send_cmd("SA")
#         self.info_stream("parameters written to EEPROM")
#         return "parameters written to EEPROM"


if __name__ == "__main__":
    SchneiderMDriveAxis.run_server()

