^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package genmsg
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.4.26 (2014-10-13)
-------------------
* fix interpreter globals collision with multiple message templates or modules (`#53 <https://github.com/ros/genmsg/issues/53>`_)

0.4.25 (2014-02-25)
-------------------
* remove usage of debug_message() (`#40 <https://github.com/ros/genmsg/issues/40>`_)
* revert "python 3 compatibility" (introduced in 0.4.24)

0.4.24 (2014-01-07)
-------------------
* python 3 compatibility (`#36 <https://github.com/ros/genmsg/issues/36>`_, `#37 <https://github.com/ros/genmsg/issues/37>`_)
* add support for ROS_LANG_DISABLE env variable (`ros/ros#39 <https://github.com/ros/ros/issues/39>`_)
* fix installation of __init__.py from devel space (`#38 <https://github.com/ros/genmsg/issues/38>`_)

0.4.23 (2013-09-17)
-------------------
* fix installation of __init__.py file for packages where name differs from project name (`#34 <https://github.com/ros/genmsg/issues/34>`_)
* rename variable 'config' to not collide with global variable (`#33 <https://github.com/ros/genmsg/issues/33>`_)
* fix service files variable to only contain package relative paths (`#32 <https://github.com/ros/genmsg/issues/32>`_)

0.4.22 (2013-08-21)
-------------------
* make genmsg relocatable (`ros/catkin#490 <https://github.com/ros/catkin/issues/490>`_)
* add warning in case generate_messages() is invoked without any messages and services (`#31 <https://github.com/ros/genmsg/issues/31>`_)
* check if files have been generated before trying to install them (`#31 <https://github.com/ros/genmsg/issues/31>`_)

0.4.21 (2013-07-03)
-------------------
* check for CATKIN_ENABLE_TESTING to enable configure without tests

0.4.20 (2013-06-18)
-------------------
* generate pkg config extra files containing variables which list all message and service files (`#28 <https://github.com/ros/genmsg/issues/28>`_)

0.4.19 (2013-06-06)
-------------------
* improve error message for missing message dependencies (`#1 <https://github.com/ros/genmsg/issues/1>`_)
* fix generating duplicate include dirs for multiple add_message_files() invocations which broke generated lisp messages (`#27 <https://github.com/ros/genmsg/issues/27>`_)

0.4.18 (2013-03-08)
-------------------
* fix handling spaces in folder names (`ros/catkin#375 <https://github.com/ros/catkin/issues/375>`_)
* add targets with _generate_messages_LANG suffix (`#20 <https://github.com/ros/genmsg/issues/20>`_)
* pass all message generation target to EXPORTED_TARGETS (`#26 <https://github.com/ros/genmsg/issues/26>`_)
* improve error messages (`#22 <https://github.com/ros/genmsg/issues/22>`_)

0.4.17 (2013-01-19)
-------------------
* fix bug using ARGV in list(FIND) directly (`#18 <https://github.com/ros/genmsg/issues/18>`_)

0.4.16 (2013-01-13)
-------------------
* hide transitive message dependencies and pull them in automatically (`#15 <https://github.com/ros/genmsg/issues/15>`_)

0.4.15 (2012-12-21)
-------------------
* first public release for Groovy
