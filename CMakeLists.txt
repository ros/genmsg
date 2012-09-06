cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(catkin REQUIRED)

catkin_stack()
catkin_project(genmsg
  CFG_EXTRAS genmsg-extras.cmake)

install(
  FILES
  cmake/pkg-genmsg.cmake.em
  cmake/pkg-genmsg.context.in
  cmake/pkg-msg-paths.cmake.in
  DESTINATION ${CATKIN_PROJECT_SHARE_DESTINATION}/cmake)

catkin_python_setup()

catkin_add_nosetests(${PROJECT_SOURCE_DIR})
