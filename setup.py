from distutils.core import setup
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='getter',
    version='0.0.2',
    packages=[
        'detect',
        'detect.data',
        'detect.workers',
        'detect.handlers'
    ],
    install_requires=required
)
