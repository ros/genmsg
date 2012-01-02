
genmsg:  generating code from ros .msg format
=============================================

Project ``genmsg`` exists in order to decouple code generation from
.msg format files from the parsing of these files and from
impementation details of the build system (project directory layout,
existence or nonexistence of utilities like ``rospack``, values of
environment variables such as ``ROS_PACKAGE_PATH``): i.e. none of
these are required to be set in any particular way.

Code generators expose a compiler-like interface that make all inputs,
outputs and search paths explicit.  For instance, the invocation of
``gencpp`` for ros message ``nav_msgs/Odometry.msg`` looks like this::

  /ssd/catkin/test/src/gencpp/scripts/gen_cpp.py
  /ssd/catkin/test/src/common_msgs/nav_msgs/msg/Odometry.msg
  -Inav_msgs:/ssd/catkin/test/src/common_msgs/nav_msgs/msg
  -Igeometry_msgs:/ssd/catkin/test/src/common_msgs/geometry_msgs/msg
  -Istd_msgs:/ssd/catkin/test/src/std_msgs/msg
  -p nav_msgs
  -o /ssd/catkin/test/build/gen/cpp/nav_msgs
  -e /ssd/catkin/test/src/gencpp/scripts

where the code generator (the first argument), is a python script
``gen_cpp.py``.  The commandline arguments have the following
meanings:

``/path/to/Some.msg``
     The flagless argument is the path to the
     input ``.msg`` file.

``-I NAMESPACE:/some/path``
     find messages in NAMESPACE in directory /some/path

``-p THIS_NAMESPACE``
     put generated message into namespace THIS_NAMESPACE

``-o /output/dir``
     Generate code into directory :file:`/output/dir`

``-e /path/to/templates``
     Find empy templates in this directory


Code generators may not use any information other than what is
provided on the commandline.


Writing the generator
^^^^^^^^^^^^^^^^^^^^^

Code generators depend on ``genmsg`` to parse the .msg file itself.
They then use the parse tree to generate code in whatever language or
format they prefer.

So far, we believe the most straightforward way to write code
generators is to use the wonderful python templating library `empy
<http://www.alcyone.com/software/empy/>`_.


Hooking in to the build system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generator packages define several macros (below), an use catkin
mechanisms to make the definitions of these macros available, see
:cmake:macro:`catkin_project`.  catkin will generate
calls to them for

* each message
* each service
* once for the overall package

For a generator called ``X``, in a package called ``genX``:

.. cmake:macro:: _generate_msg_X(PACKAGE MESSAGE IFLAGS MSG_DEPS OUTDIR)

   :param PACKAGE: name of package that the generated message MESSAGE
                   is found in.
   :param MESSAGE: full path to ``.msg`` file
   :param IFLAGS: a list of flags in ``-I<package>:/path`` format
   :param MSG_DEPS: a list of ``.msg`` files on which this message depends
   :param OUTDIR: destination directory for generated files

There are two other macros, ``_generate_srv_X``,

.. cmake:macro:: _generate_srv_X(PACKAGE SERVICE IFLAGS MSG_DEPS OUTDIR)

   :param PACKAGE: name of package that the generated message MESSAGE
                   is found in.

   :param SERVICE: full path to ``.srv`` file

   :param IFLAGS: a list of flags in ``-I<package>:/path`` format

   :param MSG_DEPS: a list of ``.msg`` files on which this message
          depends

   :param OUTDIR: destination directory for generated files

and

.. cmake:macro:: _generate_module_X(PACKAGE OUTDIR GENERATED_FILES)

   :param PACKAGE:  name of package

   :param OUTDIR:  destination directory

   :param GENERATED_FILES: Files that were generated (from messages
                           and services) for this package.  Usually
                           used to pass to the ``DEPENDS`` option of
                           cmake's ``add_custom_command()``

   Generate any "module" code necessary, e.g. ``__init__.py`` for
   python or ``module.cpp`` for boost.python bindings.



Examples
^^^^^^^^

Example projects that use this infrastructure are ``gencpp``,
``genpy``, and ``genpybindings``, all found in the github repositories
at http://github.com/ros.

