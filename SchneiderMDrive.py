#!/usr/bin/python3 -u
from tango.server import run
from tango import Database
import os
from SchneiderMDriveAxis import SchneiderMDriveAxis
from SchneiderMDriveCtrl import SchneiderMDriveCtrl

TANGO_HOST = os.environ['TANGO_HOST']
print('Trying to connect to TANGO_HOST: {:s}'.format(TANGO_HOST))

try:
    db = Database()
    print('Connection established!')
except Exception:
    print('Could not connect to TANGO database')
    exit(255)

print('Run SchneiderMDriveCtrl & SchneiderMDriveAxis')
run([SchneiderMDriveCtrl, SchneiderMDriveAxis])
