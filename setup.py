#!/usr/bin/env python

from distutils.core import setup

import sys
sys.path.insert(0, 'src')

from genmsg import __version__

setup(name='genmsg',
      version= __version__,
      packages=['genmsg'],
      package_dir = {'':'src'},
      scripts = [],
      author = "Ken Conley, Josh Faust, Troy Straszheim", 
      author_email = "kwc@willowgarage.com",
      url = "http://www.ros.org/wiki/genmsg",
      download_url = "http://pr.willowgarage.com/downloads/genmsg/", 
      keywords = ["ROS"],
      classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: BSD License" ],
      description = "ROS msg/srv generation", 
      long_description = """\
Library and scripts for generating ROS message data structures in Python, C++, and Lisp.
""",
      license = "BSD"
      )
