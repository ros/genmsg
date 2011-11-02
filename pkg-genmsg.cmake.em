@{
import sys
sys.path.append(genmsg_python_path)
import genmsg.deps

#paths = {'std_msgs':'/u/mkjargaard/repositories/mkjargaard/dist-sandbox/std_msgs/msg'}                                          
#file = '/u/mkjargaard/repositories/mkjargaard/dist-sandbox/quux_msgs/msg/QuuxString.msg'                                        

msg_deps = {}
for m in messages:
  msg_deps[m] = find_msg_dependencies(pkg_name, source_path+"/"+m, dep_search_paths)

print "# %s"%msg_deps

}

install(FILES
  msg/String.msg
  msg/ColorRGBA.msg
  DESTINATION share/msg/std_msgs)

set(MSG_I_FLAGS "")

#for each lang....

find_package(gencpp)

_generate_msg_cpp(std_msgs
  msg/String.msg
  ${MSG_I_FLAGS}
  ""
  ${CMAKE_CURRENT_BINARY_DIR}/gen/cpp/std_msgs
)
_generate_msg_cpp(std_msgs
  msg/ColorRGBA.msg
  ${MSG_I_FLAGS}
  ""
  ${CMAKE_CURRENT_BINARY_DIR}/gen/cpp/std_msgs
)
