# Schneider Electric MDrive device server

This a Tango device server written in PyTango for a Schneider Electric MDrive stepper motor controller using the RS485 serial interface.
It consits of a SchneiderMDriveCtrl device server that handles the communication with the RS485 bus and one to many SchneiderMDriveCtrlAxis device servers implementing the actual interface to the stepper axis.

## Party Mode

Configuring the MDriveWith a communication converter and the MDrive units planned to be used in Party Mode at hand, 
perform the following:

* Connect in single mode RS-422 and initiate communication, download any programs if required.
* Assign a device name (DN=”<A-Z, a-z or 0-9>”) i.e., DN=”A”.
* Set the party flag to 1 (PY=1)
* Press CTRL+J to activate party mode
* Type in [Device Name]S and press CTRL+J (saves the DN and party configuration) ie AS CTRL+J
* Remove power and label the drive with the assigned DN.
* Repeat for each system MDrive.

You should also set the ``EM`` (Echo Mode) to 1:

> Don’t echo the information, only send back prompt. CR/LF indicates command accepted (half duplex).

You should also set the ``ES`` (Escape Mode) to 3:

> Escape Flag set to respond to addressable ESC keypress (party mode)

## I/O setting - Homing and Limits

Refer to the settings of the general input/output for limit and homing switches: ``S1-S4``.
The Tango driver automatically detects which inputs are used for positive and negative limit switches and homing switch,
but only at startup.
If you change these settings (do not forget to save them to EEPROM) and restart the Device Server.
If no homing switch is set, the limit switches will be reconfigured as homing switch during runtime.

## Authors

* Daniel Schick



