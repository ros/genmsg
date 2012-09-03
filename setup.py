#!/usr/bin/env python

from __future__ import print_function
from distutils.core import setup
import sys
from xml.etree.ElementTree import ElementTree

try:
    root = ElementTree(None, 'stack.xml')
    version = root.findtext('version')
except Exception as e:
    print('Could not extract version from your stack.xml:\n%s' % e, file=sys.stderr)
    sys.exit(-1)

sys.path.insert(0, 'src')

setup(name = 'genmsg',
      version = version,
      packages = ['genmsg'],
      package_dir = {'': 'src'},
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
