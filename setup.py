#!/usr/bin/env python

from setuptools import setup

setup(
    name='ros_genmsg',
    version='0.5.8',
    description='Standalone Python library for generating ROS message and service data structures for various languages.',
    url='http://github.com/ros/genmsg',
    author='Troy Straszheim, Morten Kjaergaard, Ken Conley',
    maintainer_email='dthomas@osrfoundation.org',
    license='BSD',
    packages=['genmsg'],
    package_dir={'': 'src'},
)

