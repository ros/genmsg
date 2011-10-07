# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
ROS Service Description Language Spec
Implements http://ros.org/wiki/srv
"""

import os
import sys
import re

try:
    from cStringIO import StringIO # Python 2.x
except ImportError:
    from io import StringIO # Python 3.x

from . import msgs
from . base import SEP, COMMENTCHAR, CONSTCHAR, IODELIM, EXT_SRV, InvalidMsgSpec, log
from . names import is_legal_resource_name, normalize_package_context

# model ##########################################

class SrvSpec(object):
    
    def __init__(self, request, response, text, full_name = '', short_name = '', package = ''):
        self.request = request
        self.response = response
        self.text = text
        self.full_name = full_name
        self.short_name = short_name
        self.package = package
        
    def __eq__(self, other):
        if not other or not isinstance(other, SrvSpec):
            return False
        return self.request == other.request and \
               self.response == other.response and \
               self.text == other.text and \
               self.full_name == other.full_name and \
               self.short_name == other.short_name and \
               self.package == other.package
    
    def __ne__(self, other):
        if not other or not isinstance(other, SrvSpec):
            return True
        return not self.__eq__(other)

    def __repr__(self):
        return "SrvSpec[%s, %s]"%(repr(self.request), repr(self.response))
    
# srv spec loading utilities ##########################################

def load_from_string(msg_context, text, package_context='', full_name='', short_name=''):
    """
    NOTE: this will *not* register the message in the *msg_context*.
    
    :param msg_context: :class:`MsgContext` for finding loaded dependencies
    :param text: .msg text , ``str``
    :param package_context: context to use for msg type name, i.e. the package name,
      or '' to use local naming convention. ``str``
    :returns: :class:`SrvSpec` instance
    :raises :exc:`InvalidMsgSpec` If syntax errors or other problems are detected in file
    """
    package_context = normalize_package_context(package_context)
    
    text_in  = StringIO()
    text_out = StringIO()
    accum = text_in
    for l in text.split('\n'):
        l = l.split(COMMENTCHAR)[0].strip() #strip comments        
        if l.startswith(IODELIM): #lenient, by request
            accum = text_out
        else:
            accum.write(l+'\n')

    # create separate MsgSpec objects for each half of file
    msg_in = msgs.load_from_string(msg_context, text_in.getvalue(), package_context, '%sRequest'%(full_name), '%sRequest'%(short_name))
    msg_out = msgs.load_from_string(msg_context, text_out.getvalue(), package_context, '%sResponse'%(full_name), '%sResponse'%(short_name))
    return SrvSpec(msg_in, msg_out, text, full_name, short_name, package_context)

def load_from_file(msg_context, file_path, package_context='', full_name='', short_name=''):
    """
    Convert the .srv representation in the file to a :class:`SrvSpec` instance.

    NOTE: this will *not* register the message in the *msg_context*.
    
    :param msg_context: :class:`MsgContext` for finding loaded dependencies
    :param file_name: name of file to load from, ``str``
    :param package_context: context to use for type name, i.e. the package name,
      or '' to use local naming convention, ``str``
    :returns: :class:`SrvSpec` instance
    :raise: :exc:`InvalidMsgSpec` If syntax errors or other problems are detected in file
    """
    if package_context:
        log("Load spec from %s into namespace [%s]\n"%(file_path, package_context))
    else:
        log("Load spec from %s\n"%(file_path))
    with open(file_path, 'r') as f:
        text = f.read()
    return load_from_string(msg_context, text, package_context, full_name, short_name)




