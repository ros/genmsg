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
@[for m in messages]@
  @m
@[end for]@
  DESTINATION share/msg/@pkg_name)

set(MSG_I_FLAGS "@
@[for dep,dir in msg_deps.items()]@
 -I@dep:@dir@
@[end for]
")

#for each lang....

find_package(gencpp)

#better way to handle this?
set (ALL_GEN_OUTPUT_FILES_cpp "")

@[for m in messages]
_generate_msg_cpp(@pkg_name
  @m
  ${MSG_I_FLAGS}
  "@dependencies_str"
  ${CMAKE_CURRENT_BINARY_DIR}/gen/cpp/@pkg_name
)
@[end for]

message(STATUS ${ALL_GEN_OUTPUT_FILES_cpp)

add_custom_target(@pkg_name_gencpp ALL
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)

