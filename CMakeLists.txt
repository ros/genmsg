cmake_minimum_required(VERSION 2.8)
find_package(rosbuild)

add_subdirectory(src)

install_cmake_infrastructure(genmsg 
  VERSION 0.0.1 
  INCLUDE_DIRS include 
  CFG_EXTRAS genmsg-extras.cmake
)
