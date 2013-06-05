^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package genmsg
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Forthcoming
-----------
* improve error message for missing message dependencies (`#1 <https://github.com/ros/genmsg/issues/1>`_)
* fix generating duplicate include dirs for multiple add_message_files() invocations which broke generated lisp messages (`#27 <https://github.com/ros/genmsg/issues/27>`_)
* for a complete list of changes see the `commit log <https://github.com/ros/genmsg/compare/0.4.18...groovy-devel>`_

0.4.18 (2013-03-08)
-------------------
* fix handling spaces in folder names (`ros/catkin#375 <https://github.com/ros/catkin/issues/375>`_)
* add targets with _generate_messages_LANG suffix (`#20 <https://github.com/ros/genmsg/issues/20>`_)
* pass all message generation target to EXPORTED_TARGETS (`#26 <https://github.com/ros/genmsg/issues/26>`_)
* improve error messages (`#22 <https://github.com/ros/genmsg/issues/22>`_)
* for a complete list of changes see the `commit log <https://github.com/ros/genmsg/compare/0.4.17...0.4.18>`_

0.4.17 (2013-01-19)
-------------------
* fix bug using ARGV in list(FIND) directly (`#18 <https://github.com/ros/genmsg/issues/18>`_)
* for a complete list of changes see the `commit log <https://github.com/ros/genmsg/compare/0.4.16...0.4.17>`_

0.4.16 (2013-01-13)
-------------------
* hide transitive message dependencies and pull them in automatically (`#15 <https://github.com/ros/genmsg/issues/15>`_)
* for a complete list of changes see the `commit log <https://github.com/ros/genmsg/compare/0.4.15...0.4.16>`_

0.4.15 (2012-12-21)
-------------------
* first public release for Groovy
