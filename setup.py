from distutils.core import setup
import os
from setuptools import setup
from detect import __version__

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='detect',
    version=__version__,
    packages=[
        'detect',
        'detect.data',
        'detect.handlers',
        'detect.workers'
    ],
    install_requires=required
)
