cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(rosbuild)

install(DIRECTORY src/genmsg
  DESTINATION lib/python
  FILES_MATCHING PATTERN *.py
  )

install(
  FILES
  cmake/pkg-genmsg.cmake.em
  cmake/pkg-genmsg.context.in
  DESTINATION share/cmake/${PROJECT_NAME})

install_cmake_infrastructure(genmsg
  VERSION 0.0.1
  CFG_EXTRAS genmsg-extras.cmake
  PYTHONPATH src
)
