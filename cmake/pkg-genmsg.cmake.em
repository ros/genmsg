#
#  Generated from genmsg/cmake/pkg-genmsg.cmake.em
#
@{
import sys, genmsg, os, genmsg.base
genmsg.base.log_verbose('GENMSG_VERBOSE' in os.environ)
# put this path at the beginning
sys.path.insert(0, genmsg_python_path)
import genmsg.deps, genmsg.gentools

msg_deps = {}
for m in messages:
  msg_deps[m] = genmsg.deps.find_msg_dependencies(pkg_name, m, dep_search_paths)

srv_deps = {}
for s in services:
  srv_deps[s] = genmsg.deps.find_srv_dependencies(pkg_name, s, dep_search_paths)

}@
message(STATUS "@(pkg_name): @(len(messages)) messages")

set(MSG_I_FLAGS "@(';'.join(["-I%s:%s" % (dep, dir) for dep, dir in dep_search_paths.items()]))")

# Find all generators
@[for l in langs.split(';')]@
find_package(@l)
@[end for]@

#better way to handle this?
set (ALL_GEN_OUTPUT_FILES_cpp "")

#
#  langs = @langs
#

@[for l in langs.split(';')]@
### Section generating for lang: @l
### Generating Messages
@[for m in messages]@
_generate_msg_@(l[3:])(@pkg_name
  @m
  "${MSG_I_FLAGS}"
  "@(';'.join(msg_deps[m]).replace("\\","/"))"
  ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
)
@[end for]@

### Generating Services
@[for s in services]
_generate_srv_@(l[3:])(@pkg_name
  @s
  "${MSG_I_FLAGS}"
  "@(';'.join(srv_deps[s]).replace("\\","/"))"
  ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
)
@[end for]@

### Generating Module File
_generate_module_@(l[3:])(@pkg_name
  ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
  "${ALL_GEN_OUTPUT_FILES_@(l[3:])}"
)

add_custom_target(@(pkg_name)_@(l) ALL
  DEPENDS ${ALL_GEN_OUTPUT_FILES_@(l[3:])}
)

@[end for]@
log(1 "@pkg_name: Iflags=${MSG_I_FLAGS}")

@[for l in langs.split(';')]@

if(@(l)_INSTALL_DIR)
install(
  DIRECTORY ${CMAKE_BINARY_DIR}/gen/@(l[3:])/@pkg_name
  DESTINATION ${@(l)_INSTALL_DIR}
)
endif()
@[for d in dependencies]@
add_dependencies(@(pkg_name)_@(l) @(d)_@(l))
@[end for]@# dependencies
@[end for]@# langs
