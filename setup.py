from setuptools import setup, find_packages

setup(
    name="tangods_schneidermdrive",
    version="0.0.1",
    description="This a Tango device server written in PyTango for a Schneider Electric MDrive stepper motor controller using the RS485 serial interface.",
    author="Daniel Schick",
    author_email="dschick@mbi-berlin.de",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["SchneiderMDrive = tangods_schneidermdrive:main"]
    },
    license="MIT",
    packages=["tangods_schneidermdrive"],
    install_requires=["pytango", "pyserial"],
    url="https://github.com/MBI-Div-b/pytango-SchneiderMDrive",
    keywords=[
        "tango device",
        "tango",
        "pytango",
    ],
)
