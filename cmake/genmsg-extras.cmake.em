# generated from genmsg/cmake/genmsg-extras.cmake.in

if(_GENMSG_EXTRAS_INCLUDED_)
  return()
endif()
set(_GENMSG_EXTRAS_INCLUDED_ TRUE)

# set destination for langs
set(GENMSG_LANGS_DESTINATION "etc/ros/genmsg")

include(CMakeParseArguments)

# find message generators in all workspaces
set(message_generators "")
foreach(workspace ${CATKIN_WORKSPACES})
  file(GLOB workspace_message_generators
    RELATIVE ${workspace}/${GENMSG_LANGS_DESTINATION}
    ${workspace}/${GENMSG_LANGS_DESTINATION}/gen*)
  list(APPEND message_generators ${workspace_message_generators})
endforeach()
if(message_generators)
  list(SORT message_generators)
endif()

foreach(message_generator ${message_generators})
  find_package(${message_generator} REQUIRED)
  list(FIND CATKIN_MESSAGE_GENERATORS ${message_generator} _index)
  if(_index EQUAL -1)
    list(APPEND CATKIN_MESSAGE_GENERATORS ${message_generator})
  endif()
endforeach()
if(CATKIN_MESSAGE_GENERATORS)
  list(SORT CATKIN_MESSAGE_GENERATORS)
endif()

# disable specific message generators
string(REPLACE ":" ";" _disabled_message_generators "$ENV{ROS_LANG_DISABLE}")
# remove unknown generators from disabled list
foreach(message_generator ${_disabled_message_generators})
  list(FIND CATKIN_MESSAGE_GENERATORS ${message_generator} _index)
  if(_index EQUAL -1)
    list(REMOVE_ITEM _disabled_message_generators ${message_generator})
    message(WARNING "Unknown message generator specified in ROS_LANG_DISABLE: ${message_generator}")
  endif()
endforeach()
if(_disabled_message_generators)
  message(STATUS "Disabling the following message generators: ${_disabled_message_generators}")
  list(REMOVE_ITEM CATKIN_MESSAGE_GENERATORS ${_disabled_message_generators})
endif()
message(STATUS "Using these message generators: ${CATKIN_MESSAGE_GENERATORS}")

macro(_prepend_path ARG_PATH ARG_FILES ARG_OUTPUT_VAR)
  cmake_parse_arguments(ARG "UNIQUE" "" "" ${ARGN})
  if(ARG_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "_prepend_path() called with unused arguments: ${ARG_UNPARSED_ARGUMENTS}")
  endif()
  # todo, check for proper path, slasheds, etc
  set(${ARG_OUTPUT_VAR} "")
  foreach(_file ${ARG_FILES})
    set(_value ${ARG_PATH}/${_file})
    list(FIND ${ARG_OUTPUT_VAR} ${_value} _index)
    if(NOT ARG_UNIQUE OR _index EQUAL -1)
      list(APPEND ${ARG_OUTPUT_VAR} ${_value})
    endif()
  endforeach()
endmacro()

macro(add_message_files)
  cmake_parse_arguments(ARG "NOINSTALL" "DIRECTORY;BASE_DIR" "FILES" ${ARGN})
  if(ARG_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "add_message_files() called with unused arguments: ${ARG_UNPARSED_ARGUMENTS}")
  endif()

  if(NOT ARG_DIRECTORY)
    set(ARG_DIRECTORY "msg")
  endif()

  set(MESSAGE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${ARG_DIRECTORY})
  # override message directory (used by add_action_files())
  if(ARG_BASE_DIR)
    set(MESSAGE_DIR ${ARG_BASE_DIR})
  endif()

  if(NOT IS_DIRECTORY ${MESSAGE_DIR})
    message(FATAL_ERROR "add_message_files() directory not found: ${MESSAGE_DIR}")
  endif()

  if(${PROJECT_NAME}_GENERATE_MESSAGES)
    message(FATAL_ERROR "generate_messages() must be called after add_message_files()")
  endif()

  # if FILES are not passed search message files in the given directory
  # note: ARGV is not variable, so it can not be passed to list(FIND) directly
  set(_argv ${ARGV})
  list(FIND _argv "FILES" _index)
  if(_index EQUAL -1)
    file(GLOB ARG_FILES RELATIVE "${MESSAGE_DIR}" "${MESSAGE_DIR}/*.msg")
    list(SORT ARG_FILES)
  endif()
  _prepend_path(${MESSAGE_DIR} "${ARG_FILES}" FILES_W_PATH)

  list(APPEND ${PROJECT_NAME}_MESSAGE_FILES ${FILES_W_PATH})
  foreach(file ${FILES_W_PATH})
    assert_file_exists(${file} "message file not found")
  endforeach()

  # remember path to messages to resolve them as dependencies
  list(FIND ${PROJECT_NAME}_MSG_INCLUDE_DIRS_DEVELSPACE ${MESSAGE_DIR} _index)
  if(_index EQUAL -1)
    list(APPEND ${PROJECT_NAME}_MSG_INCLUDE_DIRS_DEVELSPACE ${MESSAGE_DIR})
  endif()

  if(NOT ARG_NOINSTALL)
    # ensure that destination variables are initialized
    catkin_destinations()

    list(APPEND ${PROJECT_NAME}_MSG_INCLUDE_DIRS_INSTALLSPACE ${ARG_DIRECTORY})
    install(FILES ${FILES_W_PATH}
      DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${ARG_DIRECTORY})

    _prepend_path("${ARG_DIRECTORY}" "${ARG_FILES}" FILES_W_PATH)
    list(APPEND ${PROJECT_NAME}_INSTALLED_MESSAGE_FILES ${FILES_W_PATH})
  endif()
endmacro()

macro(add_service_files)
  cmake_parse_arguments(ARG "NOINSTALL" "DIRECTORY" "FILES" ${ARGN})
  if(ARG_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "add_service_files() called with unused arguments: ${ARG_UNPARSED_ARGUMENTS}")
  endif()

  if(NOT ARG_DIRECTORY)
    set(ARG_DIRECTORY "srv")
  endif()

  set(SERVICE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${ARG_DIRECTORY})

  if(NOT IS_DIRECTORY ${SERVICE_DIR})
    message(FATAL_ERROR "add_service_files() directory not found: ${SERVICE_DIR}")
  endif()

  if(${PROJECT_NAME}_GENERATE_MESSAGES)
    message(FATAL_ERROR "generate_messages() must be called after add_service_files()")
  endif()

  # if FILES are not passed search service files in the given directory
  # note: ARGV is not variable, so it can not be passed to list(FIND) directly
  set(_argv ${ARGV})
  list(FIND _argv "FILES" _index)
  if(_index EQUAL -1)
    file(GLOB ARG_FILES RELATIVE "${SERVICE_DIR}" "${SERVICE_DIR}/*.srv")
    list(SORT ARG_FILES)
  endif()
  _prepend_path(${SERVICE_DIR} "${ARG_FILES}" FILES_W_PATH)

  list(APPEND ${PROJECT_NAME}_SERVICE_FILES ${FILES_W_PATH})
  foreach(file ${FILES_W_PATH})
    assert_file_exists(${file} "service file not found")
  endforeach()

  if(NOT ARG_NOINSTALL)
    # ensure that destination variables are initialized
    catkin_destinations()

    install(FILES ${FILES_W_PATH}
      DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${ARG_DIRECTORY})

    _prepend_path("${ARG_DIRECTORY}" "${ARG_FILES}" FILES_W_PATH)
    list(APPEND ${PROJECT_NAME}_INSTALLED_SERVICE_FILES ${FILES_W_PATH})
  endif()
endmacro()


function(get_all_msg_file_deps ros_pkg msg_file)
  # function to parse the message file and determine the
  # list of message files that it depends on (recursively)
  #
  # ros_pkg - the ROS package name containing the message
  # msg_file - the full path to the message file (.msg, .srv, etc)
  #
  # The function will set the variable:
  #   ${msg_file}_MSG_FILE_DEPS - a list of message files that
  #                               ${msg_file} depends on
  #

  # list of built in ROS message types
  set(BUILT_IN_MSG_TYPES
    bool
    int8
    uint8
    int16
    uint16
    int32
    uint32
    int64
    uint64
    float32
    float64
    string
    time
    duration
  )

  # initialize the return variables
  set(${msg_file}_MSG_FILE_DEPS PARENT_SCOPE)

  # read message contents and split by line
  file(READ ${msg_file} contents)
  string(REGEX REPLACE ";" "\\\\;" contents "${contents}")
  string(REGEX REPLACE "\n" ";" contents "${contents}")

  foreach(line ${contents})

    # if the line is a comment or blank skip it
    string(STRIP "${line}" line_strip)
    if(NOT line_strip STREQUAL ""
       AND NOT line_strip STREQUAL "---"
       AND NOT line_strip MATCHES "^#")

      # convert the line to a cmake array (split by white space)
      string(REGEX REPLACE " +" ";" line_strip "${line_strip}")

      # the first element of the array is the message type
      list(GET line_strip 0 msg_field_type)
      # remove and array notation, it is irrelevant
      string(REPLACE "[]" "" msg_field_type "${msg_field_type}")

      # if the type is a built in type skip it
      list(FIND BUILT_IN_MSG_TYPES ${msg_field_type} is_built_in)
      if(is_built_in STREQUAL "-1")
        # the message is not built in

        # Header is a special case and can be listed without the package
        if(${msg_field_type} STREQUAL "Header"
            OR ${msg_field_type} STREQUAL "std_msgs/Header")
          set(msg_field_pkg_name "std_msgs")
          set(msg_field_short_name "Header")
        else()
          # extract the ROS package and message type from the full type name
          string(FIND ${msg_field_type} "/" slash_index)
          if(slash_index STREQUAL "-1")
            # no slash, it is a message in this package
            set(msg_field_pkg_name ${ros_pkg})
            set(msg_field_short_name ${msg_type})
          else()
            math(EXPR index_after_slash "${slash_index} + 1")
            string(SUBSTRING ${msg_field_type} 0 ${slash_index} msg_field_pkg_name)
            string(SUBSTRING ${msg_field_type} ${index_after_slash} -1 msg_field_short_name)
          endif()

        endif()

        # check to verify the message file exists and get the list of its dependencies
        set(${msg_field_short_name}_MSG_FILE_FOUND FALSE)
        foreach(inc_dir ${${msg_field_pkg_name}_MSG_INCLUDE_DIRS})
          set(msg_field_file "${inc_dir}/${msg_field_short_name}.msg")

          if(EXISTS ${msg_field_file})

            set(${msg_field_short_name}_MSG_FILE_FOUND TRUE)

            list(APPEND ${msg_file}_MSG_FILE_DEPS "${msg_field_file}")

            get_all_msg_file_deps(${msg_field_pkg_name} ${msg_field_file})

            if(NOT "${${msg_field_file}_MSG_FILE_DEPS}" STREQUAL "")
              list(APPEND ${msg_file}_MSG_FILE_DEPS "${${msg_field_file}_MSG_FILE_DEPS}")
            endif()
            set(${msg_file}_MSG_FILE_DEPS "${${msg_file}_MSG_FILE_DEPS}" PARENT_SCOPE)

          endif()
        endforeach()

        if(${msg_field_short_name}_MSG_FILE_FOUND EQUAL FALSE)
          message(FATAL_ERROR "Unable to find dependant message file ${msg_type}:"
                              "searched in ${${msg_field_pkg_name}_MSG_INCLUDE_DIRS}")
        endif()

      endif()
    endif()
  endforeach()
endfunction()


macro(configure_pkg_genmsg context_in file_out)
  set(messages_str ${ARG_MESSAGES})
  set(services_str ${ARG_SERVICES})
  set(pkg_name ${PROJECT_NAME})
  set(dependencies_str ${ARG_DEPENDENCIES})
  set(langs ${GEN_LANGS})
  set(dep_include_paths_str ${MSG_INCLUDE_DIRS})
  set(package_has_static_sources ${package_has_static_sources})

  # total number of message and service files
  list(LENGTH messages_str n_messages)
  list(LENGTH services_str n_services)

  # create msg include flags variable
  set(MSG_I_FLAGS)
  foreach(dep ${${pkg_name}_ALL_MSG_DEPENDENCIES})
    foreach(msgdir ${${dep}_MSG_INCLUDE_DIRS})
      list(APPEND MSG_I_FLAGS "-I${dep}:${msgdir}")
    endforeach()
  endforeach()

  # determine message dependencies
  foreach(m ${messages_str})
    get_all_msg_file_deps(${pkg_name} ${m})
  endforeach()
  foreach(m ${services_str})
    get_all_msg_file_deps(${pkg_name} ${m})
  endforeach()

  # start generating pkg-genmsg cmake file
  file(WRITE ${file_out}
    "# generated from genmsg/cmake/genmsg-extras.cmake\n"
    "\n"
    "message(STATUS \"${pkg_name}: ${n_messages} messages, ${n_services} services\")\n"
    "\n"
    "set(MSG_I_FLAGS \"${MSG_I_FLAGS}\")\n"
    "\n"
    "# Find all generators\n"
  )
  foreach(l ${langs})
    file(APPEND ${file_out}
      "find_package(${l} REQUIRED)\n"
    )
  endforeach()

  # add target for whole package generate messages
  file(APPEND ${file_out}
    "\n"
    "add_custom_target(${pkg_name}_generate_messages ALL)\n"
    "\n"
    "#\n"
    "#  langs = ${langs}\n"
    "#\n"
    "\n"
  )

  # write language specific generate message commands
  foreach(l ${langs})
    # get the short version of the lang (- gen)
    string(SUBSTRING ${l} 3 -1 l_short)

    file(APPEND ${file_out}
      "### Section generating for lang: ${l}\n"
      "### Generating Messages\n"
    )

    # message generation macro
    foreach(m ${messages_str})
      file(APPEND ${file_out}
        "_generate_msg_${l_short}(${pkg_name}\n"
        "  \"${m}\"\n"
        "  \"\${MSG_I_FLAGS}\"\n"
        "  \"${${m}_MSG_FILE_DEPS}\"\n"
        "  \${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name}\n"
        ")\n"
        "\n"
      )

      # add configure file for each message to re-trigger cmake configuration
      #   after any message file changes (see bug #41)
      get_filename_component(m_filename ${m} NAME)
      file(APPEND ${file_out}
        "configure_file(${m} \${CMAKE_CURRENT_BINARY_DIR}/${m_filename}.reconf)\n\n"
      )
    endforeach()

    file(APPEND ${file_out}
      "### Generating Services\n"
    )

    # service generation macro
    foreach(m ${services_str})
      file(APPEND ${file_out}
        "_generate_srv_${l_short}(${pkg_name}\n"
        "  \"${m}\"\n"
        "  \"\${MSG_I_FLAGS}\"\n"
        "  \"${${m}_MSG_FILE_DEPS}\"\n"
        "  ${CATKIN_DEVEL_PREFIX}/${${l}_INSTALL_DIR}/${pkg_name}\n"
        ")\n"
        "\n"
      )

      # add configure file for each message to re-trigger cmake configuration
      #   after any message file changes (see bug #41)
      get_filename_component(m_filename ${m} NAME)
      file(APPEND ${file_out}
        "configure_file(${m} \${CMAKE_CURRENT_BINARY_DIR}/${m_filename}.reconf)\n\n"
      )
    endforeach()

    # genrate module file
    file(APPEND ${file_out}
      "### Generating Module File\n"
      "_generate_module_${l_short}(${pkg_name}\n"
      "  \${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name}\n"
      "  \"\${ALL_GEN_OUTPUT_FILES_${l_short}}\"\n"
      ")\n"
      "\n"
      "add_custom_target(${pkg_name}_generate_messages_${l_short}\n"
      "  DEPENDS \${ALL_GEN_OUTPUT_FILES_${l_short}}\n"
      ")\n"
      "add_dependencies(${pkg_name}_generate_messages ${pkg_name}_generate_messages_${l_short})\n"
      "\n"
      "# target for backward compatibility\n"
      "add_custom_target(${pkg_name}_${l})\n"
      "add_dependencies(${pkg_name}_${l} ${pkg_name}_generate_messages_${l_short})\n"
      "\n"
      "# register target for catkin_package(EXPORTED_TARGETS)\n"
      "list(APPEND \${PROJECT_NAME}_EXPORTED_TARGETS ${pkg_name}_generate_messages_${l_short})\n"
      "\n"
    )

  endforeach()

  file(APPEND ${file_out}
    "\n"
    "debug_message(2 \"${pkg_name}: Iflags=\${MSG_I_FLAGS}\")\n"
    "\n"
    "\n"
  )

  # write language specific install rules
  foreach(l ${langs})
    # get the short version of the lang (- gen)
    string(SUBSTRING ${l} 3 -1 l_short)

    file(APPEND ${file_out}
      "if(${l}_INSTALL_DIR AND EXISTS \${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name})\n"
    )

    if("${l}" STREQUAL "genpy")
      file(APPEND ${file_out}
        "  install(CODE \"execute_process(COMMAND \\\"${PYTHON_EXECUTABLE}\\\" -m compileall \\\"\${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name}\\\")\")\n"
      )
    endif()

    file(APPEND ${file_out}
      "  # install generated code\n"
      "  install(\n"
      "    DIRECTORY \${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name}\n"
      "    DESTINATION \${${l}_INSTALL_DIR}\n"
    )
    if("${l}" STREQUAL "genpy" AND "${package_has_static_sources}" STREQUAL "TRUE")
      file(APPEND ${file_out}
        "    PATTERN \"__init__.py\" EXCLUDE\n"
        "    PATTERN \"__init__.pyc\" EXCLUDE\n"
        "  )\n"
        "  install(\n"
        "    DIRECTORY \${CATKIN_DEVEL_PREFIX}/\${${l}_INSTALL_DIR}/${pkg_name}\n"
        "    DESTINATION \${${l}_INSTALL_DIR}\n"
        "    FILES_MATCHING\n"
        "    REGEX \"/${pkg_name}/.+/__init__.pyc?\$\"\n"
      )
    endif()
    file(APPEND ${file_out}
      "  )\n"
    )

    file(APPEND ${file_out}
      "endif()\n"
    )

    foreach(d ${dependencies_str})
      file(APPEND ${file_out}
        "add_dependencies(${pkg_name}_generate_messages_${l_short} ${d}_generate_messages_${l_short})\n"
      )
    endforeach()

    file(APPEND ${file_out}
      "\n"
    )

  endforeach()

endmacro()

macro(configure_msg_include_dirs file_out)
  get_filename_component(file_out_dir ${file_out} PATH)
  make_directory(${file_out_dir})
  if(DEVELSPACE)
    file(WRITE ${file_out}
      "set(${PROJECT_NAME}_MSG_INCLUDE_DIRS ${PKG_MSG_INCLUDE_DIRS})\n"
      "set(${PROJECT_NAME}_MSG_DEPENDENCIES ${ARG_DEPENDENCIES})\n"
    )
  else()
    file(WRITE ${file_out}
      "_prepend_path(\"\${${PROJECT_NAME}_DIR}/..\" \"${PKG_MSG_INCLUDE_DIRS}\" ${PROJECT_NAME}_MSG_INCLUDE_DIRS UNIQUE)\n"
      "set(${PROJECT_NAME}_MSG_DEPENDENCIES ${ARG_DEPENDENCIES})\n"
    )
  endif()
endmacro()

macro(generate_messages)
  cmake_parse_arguments(ARG "" "" "DEPENDENCIES;LANGS" ${ARGN})

  if(${PROJECT_NAME}_GENERATE_MESSAGES)
    message(FATAL_ERROR "generate_messages() must only be called once per project'")
  endif()

  if(ARG_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "generate_messages() called with unused arguments: ${ARG_UNPARSED_ARGUMENTS}")
  endif()

  if(${PROJECT_NAME}_CATKIN_PACKAGE)
    message(FATAL_ERROR "generate_messages() must be called before catkin_package() in project '${PROJECT_NAME}'")
  endif()

  set(ARG_MESSAGES ${${PROJECT_NAME}_MESSAGE_FILES})
  set(ARG_SERVICES ${${PROJECT_NAME}_SERVICE_FILES})
  set(ARG_DEPENDENCIES ${ARG_DEPENDENCIES})

  if(ARG_LANGS)
    set(GEN_LANGS ${ARG_LANGS})
  else()
    set(GEN_LANGS ${CATKIN_MESSAGE_GENERATORS})
  endif()

@[if DEVELSPACE]@
  # cmake dir in develspace
  set(genmsg_CMAKE_DIR "@(CMAKE_CURRENT_SOURCE_DIR)/cmake")
@[else]@
  # cmake dir in installspace
  set(genmsg_CMAKE_DIR "@(PKG_CMAKE_DIR)")
@[end if]@

  # ensure that destination variables are initialized
  catkin_destinations()

  # generate devel space config of message include dirs for project
  set(DEVELSPACE TRUE)
  set(INSTALLSPACE FALSE)
  set(PKG_MSG_INCLUDE_DIRS "${${PROJECT_NAME}_MSG_INCLUDE_DIRS_DEVELSPACE}")
  configure_msg_include_dirs(${CATKIN_DEVEL_PREFIX}/share/${PROJECT_NAME}/cmake/${PROJECT_NAME}-msg-paths.cmake)
  # generate and install config of message include dirs for project
  set(DEVELSPACE FALSE)
  set(INSTALLSPACE TRUE)
  set(PKG_MSG_INCLUDE_DIRS "${${PROJECT_NAME}_MSG_INCLUDE_DIRS_INSTALLSPACE}")
  configure_msg_include_dirs(${CMAKE_CURRENT_BINARY_DIR}/catkin_generated/installspace/${PROJECT_NAME}-msg-paths.cmake)
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/catkin_generated/installspace/${PROJECT_NAME}-msg-paths.cmake
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/cmake)

  # generate devel space pkg config extra defining variables with all processed message and service files
  set(PKG_MSG_FILES "${${PROJECT_NAME}_MESSAGE_FILES}")
  set(PKG_SRV_FILES "${${PROJECT_NAME}_SERVICE_FILES}")
  configure_file(
    ${genmsg_CMAKE_DIR}/pkg-msg-extras.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/catkin_generated/${PROJECT_NAME}-msg-extras.cmake.develspace.in
    @@ONLY)
  # generate install space pkg config extra defining variables with all processed and installed message and service files
  set(PKG_MSG_FILES "${${PROJECT_NAME}_INSTALLED_MESSAGE_FILES}")
  set(PKG_SRV_FILES "${${PROJECT_NAME}_INSTALLED_SERVICE_FILES}")
  configure_file(
    ${genmsg_CMAKE_DIR}/pkg-msg-extras.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/catkin_generated/${PROJECT_NAME}-msg-extras.cmake.installspace.in
    @@ONLY)
  # register pkg config files as cmake extra file for the project
  list(APPEND ${PROJECT_NAME}_CFG_EXTRAS ${CMAKE_CURRENT_BINARY_DIR}/catkin_generated/${PROJECT_NAME}-msg-extras.cmake)

  # find configuration containing include dirs for projects in all devel- and installspaces
  set(workspaces ${CATKIN_WORKSPACES})
  list(FIND workspaces ${CATKIN_DEVEL_PREFIX} _index)
  if(_index EQUAL -1)
    list(INSERT workspaces 0 ${CATKIN_DEVEL_PREFIX})
  endif()

  set(pending_deps ${PROJECT_NAME} ${ARG_DEPENDENCIES})
  set(handled_deps "")
  set(${PROJECT_NAME}_ALL_MSG_DEPENDENCIES ${pending_deps})
  while(pending_deps)
    list(GET pending_deps 0 dep)
    list(REMOVE_AT pending_deps 0)
    list(APPEND handled_deps ${dep})

    if(NOT ${dep}_FOUND AND NOT ${dep}_SOURCE_DIR)
      message(FATAL_ERROR "Messages depends on unknown pkg: ${dep} (Missing find_package(${dep}?))")
    endif()

    unset(_dep_msg_paths_file CACHE)
    set(filename "share/${dep}/cmake/${dep}-msg-paths.cmake")
    find_file(_dep_msg_paths_file ${filename} PATHS ${workspaces}
      NO_DEFAULT_PATH NO_CMAKE_FIND_ROOT_PATH)
    if("${_dep_msg_paths_file}" STREQUAL "_dep_msg_paths_file-NOTFOUND")
      message(FATAL_ERROR "Could not find '${filename}' (searched in '${workspaces}').")
    endif()
    include(${_dep_msg_paths_file})
    unset(_dep_msg_paths_file CACHE)

    # explicitly set message include dirs for current project since information from pkg-msg-paths.cmake is not yet available
    if(${dep} STREQUAL ${PROJECT_NAME})
      set(${dep}_MSG_INCLUDE_DIRS ${${PROJECT_NAME}_MSG_INCLUDE_DIRS_DEVELSPACE})
    endif()
    foreach(path ${${dep}_MSG_INCLUDE_DIRS})
      list(APPEND MSG_INCLUDE_DIRS "${dep}")
      list(APPEND MSG_INCLUDE_DIRS "${path}")
    endforeach()

    # add transitive msg dependencies
    if(NOT ${dep} STREQUAL ${PROJECT_NAME})
      foreach(recdep ${${dep}_MSG_DEPENDENCIES})
        set(all_deps ${handled_deps} ${pending_deps})
        list(FIND all_deps ${recdep} _index)
        if(_index EQUAL -1)
          list(APPEND pending_deps ${recdep})
          list(APPEND ${PROJECT_NAME}_ALL_MSG_DEPENDENCIES ${recdep})
        endif()
      endforeach()
    endif()
  endwhile()

  # mark that generate_messages() was called in order to detect wrong order of calling with catkin_python_setup()
  set(${PROJECT_NAME}_GENERATE_MESSAGES TRUE)
  # check if catkin_python_setup() installs an __init__.py file for a package with the current project name
  # in order to skip the installation of a generated __init__.py file
  set(package_has_static_sources ${${PROJECT_NAME}_CATKIN_PYTHON_SETUP_HAS_PACKAGE_INIT})

  configure_pkg_genmsg(${genmsg_CMAKE_DIR}/pkg-genmsg.context.in
    ${CMAKE_CURRENT_BINARY_DIR}/cmake/${PROJECT_NAME}-genmsg.cmake)
  include(${CMAKE_CURRENT_BINARY_DIR}/cmake/${PROJECT_NAME}-genmsg.cmake)
endmacro()
