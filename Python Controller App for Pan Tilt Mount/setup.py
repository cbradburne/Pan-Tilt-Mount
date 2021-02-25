"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['PTSApp.py']
DATA_FILES = ['theme.json', 'Montserrat-Regular.ttf', 'PTSApp-Icon.png']
OPTIONS = {'iconfile': 'PTSApp-Icon.icns'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
