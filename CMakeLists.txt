cmake_minimum_required(VERSION 2.8)
project(genmsg)
find_package(rosbuild)

add_subdirectory(src)

set(THINGS "HEHEHHEHHEHEHEE")
em_expand(em_context.py.in ${CMAKE_CURRENT_SOURCE_DIR}/doit.em)

install_cmake_infrastructure(genmsg 
  VERSION 0.0.1 
  INCLUDE_DIRS include
  CFG_EXTRAS genmsg-extras.cmake
  PYTHON_PATH src
)
