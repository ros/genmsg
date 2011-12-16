cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(catkin REQUIRED)

install(
  FILES
  cmake/pkg-genmsg.cmake.em
  cmake/pkg-genmsg.context.in
  cmake/import_check.py
  DESTINATION share/${PROJECT_NAME}/cmake)

install_cmake_infrastructure(genmsg
  VERSION 0.0.1
  CFG_EXTRAS genmsg-extras.cmake
  PYTHONPATH src
)

catkin_package(genmsg)
enable_python(genmsg)

sphinx(${CMAKE_CURRENT_SOURCE_DIR}/doc ${CMAKE_CURRENT_BINARY_DIR}/doc)
