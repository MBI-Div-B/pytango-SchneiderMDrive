#!/usr/bin/python3 -u
from tango.server import run
from SchneiderMDriveAxis import SchneiderMDriveAxis
from SchneiderMDriveCtrl import SchneiderMDriveCtrl

run([SchneiderMDriveCtrl, SchneiderMDriveAxis])
