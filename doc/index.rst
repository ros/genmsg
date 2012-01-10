.. _index:

genmsg:  generating code from ros .msg format
=============================================

Project ``genmsg`` exists in order to decouple code generation from
.msg format files from the parsing of these files and from
impementation details of the build system (project directory layout,
existence or nonexistence of utilities like ``rospack``, values of
environment variables such as ``ROS_PACKAGE_PATH``): i.e. none of
these are required to be set in any particular way.

.. cmake:macro:: add_message_files(DIRECTORY dir FILES file1 [file2...] [PACKAGE pkgname] [NOINSTALL])

   :param DIRECTORY: Directory containing messages.  May be absolute or
     relative to ``CMAKE_CURRENT_SOURCE_DIR``.
   :param FILES:  Files containing messages, relative to `msgdir`
   :param PACKAGE:  Optional alternate packagename (if the current project doesn't match the
     desired namespace for the messages)
   :param NOINSTALL: Do not automatically install the messages to the package's share/ directory.

   Register the listed files as requiring message generation and installation.

.. cmake:macro:: add_service_files(DIRECTORY dir FILES file1 [file2...] [PACKAGE pkgname] [NOINSTALL])

   Same as add_message_files... but for services.

.. cmake:macro:: generate_messages(DEPENDENCIES deps [LANGS lang1 lang2...])

   :param DEPENDENCIES: Names of packages containing messages
      contained by messages in the current package.  Got it?  i.e. if
      one of our messages contains std_msgs.Header, ``std_msgs``
      should appear in this list.
   :param LANGS:  Restrict generation to the listed languages.

   Triggers the generation of message generation targets.  i.e. in
   project ``foo`` with generators ``gencpp`` and ``genpy`` accessible
   in the workspace, triggers creation of targets ``foo_gencpp`` and
   ``foo_genpy``.

.. toctree::

   developer
