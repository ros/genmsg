cmake_minimum_required(VERSION 2.8.3)
project(genmsg)
find_package(catkin REQUIRED)

catkin_package(CFG_EXTRAS genmsg-extras.cmake)

install(
  FILES
  cmake/pkg-genmsg.cmake.em
  cmake/pkg-genmsg.context.in
  cmake/pkg-msg-extras.cmake.in
  cmake/pkg-msg-paths.cmake.em
  cmake/pkg-msg-paths.context.in
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/cmake)

catkin_python_setup()

if(CATKIN_ENABLE_TESTING)
  catkin_add_nosetests(test)
endif()
