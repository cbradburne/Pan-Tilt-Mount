"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['PTSApp.py']
APP_NAME = "PTSApp"
DATA_FILES = ['theme.json', 'Montserrat-Regular.ttf', 'Roboto-Regular.ttf', 'PTSApp-Icon.png']

OPTIONS = {
    'iconfile': 'PTSApp-Icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Controller for Pan / Tilt / Slider camera mount.",
        'CFBundleIdentifier': "com.metabradders.osx.ptsapp",
        'CFBundleVersion': "1.0",
        'CFBundleShortVersionString': "1.0",
        'NSHumanReadableCopyright': "Copyright © 2021, Colin Bradburne, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
