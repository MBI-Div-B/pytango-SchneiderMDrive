#!/usr/bin/python3 -u
# coding: utf8
# SchneiderMDriveAxis
from tango import Database, DevFailed, AttrWriteType, DevState, DeviceProxy, DispLevel
from tango.server import device_property
from tango.server import Device, attribute, command
import sys
from enum import IntEnum

class MovementUnit(IntEnum):
    step = 0
    mm = 1
    inch = 2
    degree = 3


class SchneiderMDriveAxis(Device):
    # device properties
    CtrlDevice = device_property(
        dtype="str",
        default_value="domain/family/member",
    )

    Axis = device_property(
        dtype="str",
        default_value="X",
    )

    position = attribute(
        dtype=int,
        format="%8d",
        label="position",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.OPERATOR,
    )

    velocity = attribute(
        dtype=int,
        format="%8d",
        label="velocity",
        unit="steps/s",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    acceleration = attribute(
        dtype=int,
        format="%8d",
        label="acceleration",
        unit="steps/s^2",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    hold_current = attribute(
        dtype=int,
        label="hold current",
        unit="%",
        min_value=0,
        max_value=100,
        format="%3d",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    run_current = attribute(
        dtype=int,
        label="run current",
        unit="%",
        min_value=0,
        max_value=100,
        format="%3d",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    micro_steps = attribute(
        dtype="int",
        label="micro steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc="""Step resolution 1 to 256
1 = Full step
2 = Half step
4 = 1/4 step
8 = 1/8 step
16 = 1/16 step
32 = 1/32 step
64 = 1/64 step
128 = 1/128 step
256 = 1/256 step"""
    )

    movement_unit = attribute(
        dtype=MovementUnit,
        label="unit",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc="Allowed unit values are step, mm, inch, degree"
    )

    hw_limit_minus = attribute(
        dtype="bool",
        label="HW limit -",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    hw_limit_plus = attribute(
        dtype="bool",
        label="HW limit +",
        access=AttrWriteType.READ,
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

        self.info_stream("axis part number: {:s}".format(self.write_read('PR PN')))
        self.info_stream("axis serial number: {:s}".format(self.write_read('PR SN')))

    def delete_device(self):
        self.set_state(DevState.OFF)

    def dev_state(self):
        self.__HW_Limit_Minus = bool(int(self.write_read('PR I1')))
        self.__HW_Limit_Plus = bool(int(self.write_read('PR I2')))
        self.debug_stream("HW limit-: {0}".format(self.__HW_Limit_Minus))
        self.debug_stream("HW limit+: {0}".format(self.__HW_Limit_Plus))

        is_moving = bool(int(self.write_read('PR MV')))

        if is_moving:
            self.set_status("Device is MOVING")
            self.debug_stream("device is: MOVING")
            return DevState.MOVING
        else:
            self.set_status("Device in ON")
            self.debug_stream("device is: ON")
            return DevState.ON

    # attribute read/write methods
    def read_position(self):
        return int(self.write_read("PR P"))

    def write_position(self, value):
        self.write("MA {:d}".format(value))

    def read_velocity(self):
        return int(self.write_read("PR VM"))

    def write_velocity(self, value):
        self.write("VM={:d}".format(value))

    def read_acceleration(self):
        return int(self.write_read("PR A"))

    def write_acceleration(self, value):
        self.write("A={:d}".format(value))
        # set deceleration to same value
        self.write("D={:d}".format(value))

    def read_run_current(self):
        return int(self.write_read("PR RC"))

    def write_run_current(self, value):
        self.write("RC={:d}".format(value))

    def read_hold_current(self):
        return int(self.write_read("PR HC"))

    def write_hold_current(self, value):
        self.write("HC={:d}".format(value))

    def read_micro_steps(self):
        return int(self.write_read("PR MS"))

    def write_micro_steps(self, value):
        if value not in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            return "input not in [1, 2, 4, 8, 16, 32, 64, 128, 256]"
        self.write("MS={:d}".format(value))

    def read_movement_unit(self):
        return self.__Unit

    def write_movement_unit(self, value):
        if value == 1:
            self.__Unit = MovementUnit.step
        elif value == 2:
            self.__Unit = MovementUnit.mm
        elif value == 3:
            self.__Unit = MovementUnit.inch
        elif value == 4:
            self.__Unit = MovementUnit.degree
        self.set_display_unit()

    def read_hw_limit_minus(self):
        return self.__HW_Limit_Minus

    def read_hw_limit_plus(self):
        return self.__HW_Limit_Plus

    # internal methods
    def set_display_unit(self):
        attributes = [b"position"]
        for attr in attributes:
            ac3 = self.get_attribute_config_3(attr)
            ac3[0].unit = self.__Unit.name.encode("utf-8")
            # if (1/self.__Steps_Per_Unit % 1) == 0.0:
            #     ac3[0].format = b"%8d"
            # else:
            #     ac3[0].format = b"%8.3f"
            self.set_attribute_config_3(ac3)

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

    @command(dtype_in=int, doc_in="position")
    def set_position(self, value):
        self.write("P={:d}".format(value))

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
    @command(dtype_out=str)
    def save_to_eeprom(self):
        self.write("S")
        self.info_stream("parameters saved to EEPROM")
        return "parameters saved to EEPROM"


if __name__ == "__main__":
    SchneiderMDriveAxis.run_server()
