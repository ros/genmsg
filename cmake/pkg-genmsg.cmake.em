@{
import sys
# put this path at the beginning
sys.path.insert(0, genmsg_python_path)
import genmsg.deps

msg_deps = {}
for m in messages:
  msg_deps[m] = genmsg.deps.find_msg_dependencies(pkg_name, source_path+"/"+m, dep_search_paths)

print "# %s"%msg_deps

srv_deps = {}
for s in services:
  srv_deps[s] = genmsg.deps.find_srv_dependencies(pkg_name, source_path+"/"+s, dep_search_paths)

print "\n# %s"%srv_deps


}

install(FILES
  @(' '.join(messages))
  DESTINATION share/msg/@pkg_name)

install(FILES
  @(' '.join(services))
  DESTINATION share/srv/@pkg_name)

set(MSG_I_FLAGS "@(';'.join(["-I%s:%s" % (dep, dir) for dep, dir in dep_search_paths.items()]))")

#for each lang....

@[for l in langs.split(';')]
find_package(@l)
@[end for]

#better way to handle this?
set (ALL_GEN_OUTPUT_FILES_cpp "")

@[for l in langs.split(';')]

@[for m in messages]
_generate_msg_@(l[3:])(@pkg_name
  @m
  "${MSG_I_FLAGS}"
  "@(';'.join(msg_deps[m]))"
  ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
)
@[end for]

@[for s in services]
_generate_srv_@(l[3:])(@pkg_name
  @s
  "${MSG_I_FLAGS}"
  "@(';'.join(msg_deps[m]))"
  ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
)
@[end for]
@[end for]
log(1 "@pkg_name: Iflags=${MSG_I_FLAGS}")

@[for l in langs.split(';')]

add_custom_target(@(pkg_name)_@(l) ALL
  DEPENDS ${ALL_GEN_OUTPUT_FILES_@(l[3:])}
)

install(
  DIRECTORY ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
  DESTINATION ${@(l)_INSTALL_DIR}
)

@[for d in dependencies]

add_dependencies(@(pkg_name)_@(l) @(d)_@(l))

@[end for]
@[end for]

