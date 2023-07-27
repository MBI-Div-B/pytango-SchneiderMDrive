from .SchneiderMDriveCtrl import SchneiderMDriveCtrl
from .SchneiderMDriveAxis import SchneiderMDriveAxis


def main():
    import sys
    import tango.server

    args = ["SchneiderMDrive"] + sys.argv[1:]
    tango.server.run(
        (
            SchneiderMDriveCtrl,
            SchneiderMDriveAxis,
        ),
        args=args,
    )
