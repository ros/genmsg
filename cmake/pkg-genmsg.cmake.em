@{
import sys
sys.path.append(genmsg_python_path)
import genmsg.deps

msg_deps = {}
for m in messages:
  msg_deps[m] = genmsg.deps.find_msg_dependencies(pkg_name, source_path+"/"+m, dep_search_paths)

print "# %s"%msg_deps

}

install(FILES
  @(' '.join(messages))
  DESTINATION share/msg/@pkg_name)

set(MSG_I_FLAGS "@
@[for dep,dir in dep_search_paths.items()]@
-I@dep:@dir@
@[end for]@
")

#for each lang....

find_package(gencpp)

#better way to handle this?
set (ALL_GEN_OUTPUT_FILES_cpp "")

@[for m in messages]
_generate_msg_cpp(@pkg_name
  @m
  "${MSG_I_FLAGS}"
  "@(';'.join(msg_deps[m]))"
  ${CMAKE_CURRENT_BINARY_DIR}/gen/cpp/@pkg_name
)
@[end for]

log(1 "@pkg_name: Iflags=${MSG_I_FLAGS}")
log(1 "@pkg_name: Output Files=${ALL_GEN_OUTPUT_FILES_cpp}")

add_custom_target(@(pkg_name)_gencpp ALL
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)

@[for d in dependencies]
add_dependencies(@(pkg_name)_gencpp @(d)_gencpp)
@[end for]

install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/gen/cpp/@pkg_name
  DESTINATION include
)
