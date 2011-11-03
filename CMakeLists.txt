cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(rosbuild)

install(DIRECTORY src/genmsg
  DESTINATION lib/python
  FILES_MATCHING PATTERN *.py
  )

install_cmake_infrastructure(genmsg 
  VERSION 0.0.1 
  INCLUDE_DIRS include
  CFG_EXTRAS genmsg-extras.cmake
  PYTHON_PATH src
)
