import sys
from cx_Freeze import setup, Executable

includefiles = ['theme.json', 'Montserrat-Regular.ttf', 'PTSApp-Icon.png']

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"], "include_files": includefiles}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "PTSApp",
        version = "0.1",
        description = "PTSApp",
        options = {"build_exe": build_exe_options},
        executables = [Executable("PTSApp.py", base=base)])