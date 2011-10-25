cmake_minimum_required(VERSION 2.8)
find_package(ros_cmake)

add_subdirectory(src)

install_cmake_infrastructure(genmsg 
  VERSION 1.3.1 
  INCLUDE_DIRS include 
  CFG_EXTRAS genmsg-extras.cmake
)
