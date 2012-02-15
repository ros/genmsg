cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(catkin REQUIRED)

install(
  FILES
  cmake/pkg-genmsg.cmake.em
  cmake/pkg-genmsg.context.in
  cmake/import_check.py
  DESTINATION share/${PROJECT_NAME}/cmake)

catkin_stack()
catkin_project(genmsg
  VERSION 0.0.1
  CFG_EXTRAS genmsg-extras.cmake
)

install(FILES cmake/generator.cmake.in DESTINATION share/genmsg/cmake)
install(FILES stack.yaml DESTINATION share/${PROJECT_NAME})

catkin_export_python()
