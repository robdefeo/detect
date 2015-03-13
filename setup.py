from distutils.core import setup
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='detect',
    version='0.0.4',
    packages=[
        'detect',
        'detect.data',
        'detect.handlers',
        'detect.workers'
    ],
    install_requires=required
)
