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
from . base import SEP, COMMENTCHAR, CONSTCHAR, IODELIM, EXT_SRV, MsgSpecException, log
from . names import is_legal_resource_name

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

def load_from_string(text, package_context='', full_name='', short_name=''):
    """
    :param text: .msg text , ``str``
    :param package_context: context to use for msg type name, i.e. the package name,
      or '' to use local naming convention. ``str``
    :returns: Message type name and :class:`MsgSpec` message specification
    :raises :exc:`MsgSpecException` If syntax errors or other problems are detected in file
    """
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
    msg_in = msgs.load_from_string(text_in.getvalue(), package_context, '%sRequest'%(full_name), '%sRequest'%(short_name))
    msg_out = msgs.load_from_string(text_out.getvalue(), package_context, '%sResponse'%(full_name), '%sResponse'%(short_name))
    return SrvSpec(msg_in, msg_out, text, full_name, short_name, package_context)

def load_from_file(file_name, package_context=''):
    """
    Convert the .srv representation in the file to a :class:`SrvSpec` instance.

    :param file_name: name of file to load from, ``str``
    :param package_context: context to use for type name, i.e. the package name,
      or '' to use local naming convention, ``str``
    :returns: Message type name and message specification, ``(str, SrvSpec)``
    :raise: :exc:`MsgSpecException` If syntax errors or other problems are detected in file
    """
    if package_context:
        log("Load spec from %s into namespace [%s]\n"%(file_name, package_context))
    else:
        log("Load spec from %s\n"%(file_name))
    base_file_name = os.path.basename(file_name)
    type_ = base_file_name[:-len(EXT_SRV)]
    base_type_ = type_
    # determine the type name
    if package_context:
        while package_context.endswith(SEP):
            package_context = package_context[:-1] #strip message separators
        type_ = "%s%s%s"%(package_context, SEP, type_)
    if not is_legal_resource_name(type_):
        raise MsgSpecException("%s: %s is not a legal service type name"%(file_name, type_))
    
    with  open(file_name, 'r') as f:
        text = f.read()
        return (type_, load_from_string(text, package_context, type_, base_type_))




