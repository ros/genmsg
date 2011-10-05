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
#
# Revision $Id: msgs.py 14304 2011-07-13 08:00:40Z kwc $
# $Author: kwc $

from __future__ import print_function

"""
ROS msg library for Python

Implements: U{http://ros.org/wiki/msg}
"""

try:
    from cStringIO import StringIO # Python 2.x
except ImportError:
    from io import StringIO # Python 3.x

import os
import itertools
import sys
import re
import string

from . base import MessageNotFound, MsgSpecException, CONSTCHAR, COMMENT, EXT_MSG, MSG_DIR

#TODOXXX: unit test
def base_msg_type(type_):
    """
    Compute the base data type, e.g. for arrays, get the underlying array item type
    @param type_: ROS msg type (e.g. 'std_msgs/String')
    @type  type_: str
    @return: base type
    @rtype: str
    """
    if type_ is None:
        return None
    if '[' in type_:
        return type_[:type_.find('[')]
    return type_

def resolve_type(type_, package_context):
    """
    Resolve type name based on current package context.

    NOTE: in ROS Diamondback, 'Header' resolves to
    'std_msgs/Header'. In previous releases, it resolves to
    'roslib/Header' (REP 100).

    e.g.::
      resolve_type('String', 'std_msgs') -> 'std_msgs/String'
      resolve_type('String[]', 'std_msgs') -> 'std_msgs/String[]'
      resolve_type('std_msgs/String', 'foo') -> 'std_msgs/String'    
      resolve_type('uint16', 'std_msgs') -> 'uint16'
      resolve_type('uint16[]', 'std_msgs') -> 'uint16[]'
    """
    bt = base_msg_type(type_)
    if bt in BUILTIN_TYPES:
        return type_
    elif bt == HEADER:
        return HEADER_FULL_NAME
    elif SEP in type_:
        return type_
    else:
        return "%s%s%s"%(package_context, SEP, type_)    

#NOTE: this assumes that we aren't going to support multi-dimensional

def parse_type(type_):
    """
    Parse ROS message field type
    :param type_: ROS field type, ``str``
    :returns: base_type, is_array, array_length, ``(str, bool, int)``
    :raises: :exc:`ValueError` If *type_* cannot be parsed
    """
    if not type_:
        raise ValueError("Invalid empty type")
    if '[' in type_:
        var_length = type_.endswith('[]')
        splits = type_.split('[')
        if len(splits) > 2:
            raise ValueError("Currently only support 1-dimensional array types: %s"%type_)
        if var_length:
            return type_[:-2], True, None
        else:
            try:
                length = int(splits[1][:-1])
                return splits[0], True, length
            except ValueError:
                raise ValueError("Invalid array dimension: [%s]"%splits[1][:-1])
    else:
        return type_, False, None
   
################################################################################
# name validation 

def is_valid_msg_type(x):
    """
    @return: True if the name is a syntatically legal message type name
    @rtype: bool
    """
    if not x or len(x) != len(x.strip()):
        return False
    base = base_msg_type(x)
    if not names.is_legal_resource_name(base):
        return False
    #parse array indicies
    x = x[len(base):]
    state = 0
    i = 0
    for c in x:
        if state == 0:
            if c != '[':
                return False
            state = 1 #open
        elif state == 1:
            if c == ']':
                state = 0 #closed
            else:
                try:
                    string.atoi(c)
                except:
                    return False
    return state == 0

def is_valid_constant_type(x):
    """
    :returns: ``True`` if the name is a legal constant type. Only simple types are allowed, ``bool``
    """
    return x in PRIMITIVE_TYPES

def is_valid_msg_field_name(x):
    """
    :returns: ``True`` if the name is a syntatically legal message field name, ``bool``
    """
    return names.is_legal_resource_base_name(x)

# msg spec representation ##########################################

class Constant(object):
    """
    Container class for holding a Constant declaration
    """
    __slots__ = ['type', 'name', 'val', 'val_text']
    
    def __init__(self, type_, name, val, val_text):
        """
        @param type_: constant type
        @type  type_: str 
        @param name: constant name
        @type  name: str
        @param val: constant value
        @type  val: str
        @param val_text: Original text definition of \a val
        @type  val_text: str
        """
        if type is None or name is None or val is None or val_text is None:
            raise ValueError('Constant must have non-None parameters')
        self.type = type_
        self.name = name.strip() #names are always stripped of whitespace
        self.val = val
        self.val_text = val_text

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return False
        return self.type == other.type and self.name == other.name and self.val == other.val

    def __repr__(self):
        return "%s %s=%s"%(self.type, self.name, self.val)

    def __str__(self):
        return "%s %s=%s"%(self.type, self.name, self.val)

def _strify_spec(spec, buff=None, indent=''):
    """
    Convert spec into a string representation. Helper routine for MsgSpec.
    :param indent: internal use only, ``str``
    :param buff: internal use only, ``StringIO``
    :returns: string representation of spec, ``str``
    """
    if buff is None:
        buff = StringIO()
    for c in spec.constants:
        buff.write("%s%s %s=%s\n"%(indent, c.type, c.name, c.val_text))
    for type_, name in zip(spec.types, spec.names):
        buff.write("%s%s %s\n"%(indent, type_, name))
        base_type = base_msg_type(type_)
        if not base_type in BUILTIN_TYPES:
            subspec = get_registered(base_type)
            _strify_spec(subspec, buff, indent + '  ')
    return buff.getvalue()

class Field(object):
    """
    Container class for storing information about a single field in a MsgSpec
    
    Contains:
    name
    type
    base_type
    is_array
    array_len
    is_builtin
    is_header
    """
    
    def __init__(self, name, type):
        self.name = name
        self.type = type
        (self.base_type, self.is_array, self.array_len) = parse_type(type)
        self.is_header = is_header_type(self.base_type)
        self.is_builtin = is_builtin(self.base_type)

    def __repr__(self):
        return "[%s, %s, %s, %s, %s]"%(self.name, self.type, self.base_type, self.is_array, self.array_len)

class MsgSpec(object):
    """
    Container class for storing loaded msg description files. Field
    types and names are stored in separate lists with 1-to-1
    correspondence. MsgSpec can also return an md5 of the source text.
    """

    def __init__(self, types, names, constants, text, full_name = '', short_name = '', package = ''):
        """
        :param types: list of field types, in order of declaration, ``[str]]``
        :param names: list of field names, in order of declaration, ``[str]]``
        :param constants: List of :class:`Constant` declarations, ``[Constant]``
        :param text: text of declaration, ``str`
        :raises: :exc:`MsgSpecException` If spec is invalid (e.g. fields with the same name)
        """
        self.types = types
        if len(set(names)) != len(names):
            raise MsgSpecException("Duplicate field names in message: %s"%names)
        self.names = names
        self.constants = constants
        assert len(self.types) == len(self.names), "len(%s) != len(%s)"%(self.types, self.names)
        #Header.msg support
        if (len(self.types)):
            self.header_present = self.types[0] == HEADER_FULL_NAME and self.names[0] == 'header'
        else:
            self.header_present = False
        self.text = text
        self.full_name = full_name
        self.short_name = short_name
        self.package = package
        try:
            self._parsed_fields = [Field(name, type) for (name, type) in zip(self.names, self.types)]
        except ValueError as e:
            raise MsgSpecException("invalid field: %s"%(e))
        
    def fields(self):
        """
        :returns: zip list of types and names (e.g. [('int32', 'x'), ('int32', 'y')], ``[(str,str),]``
        """
        return list(zip(self.types, self.names)) #py3k
    
    def parsed_fields(self):
        """
        :returns: list of :class:`Field` classes, ``[Field,]``
        """
        return self._parsed_fields

    def has_header(self):
        """
        :returns: ``True`` if msg decription contains a 'Header header'
          declaration at the beginning, ``bool``
        """
        return self.header_present
    def __eq__(self, other):
        if not other or not isinstance(other, MsgSpec):
            return False 
        return self.types == other.types and self.names == other.names and \
               self.constants == other.constants and self.text == other.text
    def __ne__(self, other):
        if not other or not isinstance(other, MsgSpec):
            return True
        return not self.__eq__(other)

    def __repr__(self):
        if self.constants:
            return "MsgSpec[%s, %s, %s]"%(repr(self.constants), repr(self.types), repr(self.names))
        else:
            return "MsgSpec[%s, %s]"%(repr(self.types), repr(self.names))        

    def __str__(self):
        return _strify_spec(self)
    
# msg spec loading utilities ##########################################

def reinit():
    """
    Reinitialize roslib.msgs. This API is for message generators
    (e.g. genpy) that need to re-initialize the registration table.
    """
    global _initialized , _loaded_packages
    # unset the initialized state and unregister everything 
    _initialized = False
    del _loaded_packages[:]
    REGISTERED_TYPES.clear()
    _init()
    
# .msg file routines ##############################################################       

def msg_file(package, type_, searchpath):
    """
    Determine the file system path for the specified .msg on path.

    :param package: name of package .msg file is in, ``str``
    :param type_: type name of message, e.g. 'Point2DFloat32', ``str``
    :returns: file path of .msg file in specified package or ``None`` if not found, ``str``
    """
    log("msg_file(%s, %s, %s)" % (package, type_, str(searchpath)))
    assert isinstance(searchpath, list)
    for p in searchpath:
        j = os.path.join(p, "msg", type_ + ".msg")
        if os.path.isfile(j):
            return j

def _convert_val(type_, val):
    """
    Convert constant value declaration to python value. Does not do
    type-checking, so ValueError or other exceptions may be raised.
    
    :param type_: ROS field type, ``str``
    :param val: string representation of constant, ``str``
    :raises: :exc:`ValueError` If unable to convert to python representation
    :raises: :exc:`MsgSpecException` If value exceeds specified integer width
    """
    if type_ in ['float32','float64']:
        return float(val)
    elif type_ in ['string']:
        return val.strip() #string constants are always stripped 
    elif type_ in ['int8', 'uint8', 'int16','uint16','int32','uint32','int64','uint64', 'char', 'byte']:
        # bounds checking
        bits = [('int8', 8), ('uint8', 8), ('int16', 16),('uint16', 16),\
                ('int32', 32),('uint32', 32), ('int64', 64),('uint64', 64),\
                ('byte', 8), ('char', 8)]
        b = [b for t, b in bits if t == type_][0]
        import math
        if type_[0] == 'u' or type_ == 'char':
            lower = 0
            upper = int(math.pow(2, b)-1)
        else:
            upper = int(math.pow(2, b-1)-1)   
            lower = -upper - 1 #two's complement min
        val = int(val) #python will autocast to long if necessary
        if val > upper or val < lower:
            raise MsgSpecException("cannot coerce [%s] to %s (out of bounds)"%(val, type_))
        return val
    elif type_ == 'bool':
        # TODO: need to nail down constant spec for bool
        return True if eval(val) else False
    raise MsgSpecException("invalid constant type: [%s]"%type_)
        
def load_by_type(msgtype, includepath, package_context=''):
    """
    Load message specification for specified type

    :param package_context: package name to use for the type name or
      '' to use the local (relative) naming convention, ``str``
    :returns: Message type name and message specification, ``(str, MsgSpec)``
    :raises: :exc:`MessageNotFound`
    """
    assert isinstance(includepath, list)

    log("load_by_type(%s, %s, %s)" % (msgtype, str(includepath), package_context))
    pkg, basetype = rosidl.names.package_resource_name(msgtype)
    pkg = pkg or package_context # convert '' -> local package
    
    log("pkg", pkg)
    m_f = msg_file(pkg, basetype, includepath)
    log("m_f", m_f)
    if m_f is None:
        raise MessageNotFound(msgtype)
    return load_from_file(m_f, pkg)

def load_from_string(text, package_context='', full_name='', short_name=''):
    """
    Load message specification from a string.
    :param text: .msg text , ``str``
    :param package_context: package name to use for the type name or
        '' to use the local (relative) naming convention., ``str``
    :returns: :class:`MsgSpec` specification
    :raises: :exc:`MsgSpecException` If syntax errors or other problems are detected in file
    """
    types = []
    names = []
    constants = []
    for orig_line in text.split('\n'):
        l = orig_line.split(COMMENTCHAR)[0].strip() #strip comments
        if not l:
            continue #ignore empty lines
        splits = [s for s in [x.strip() for x in l.split(" ")] if s] #split type/name, filter out empties
        type_ = splits[0]
        if not is_valid_msg_type(type_):
            raise MsgSpecException("%s is not a legal message type"%type_)
        if CONSTCHAR in l:
            if not is_valid_constant_type(type_):
                raise MsgSpecException("%s is not a legal constant type"%type_)
            if type_ == 'string':
                # strings contain anything to the right of the equals sign, there are no comments allowed
                idx = orig_line.find(CONSTCHAR)
                name = orig_line[orig_line.find(' ')+1:idx]
                val = orig_line[idx+1:]
            else:
                splits = [x.strip() for x in ' '.join(splits[1:]).split(CONSTCHAR)] #resplit on '='
                if len(splits) != 2:
                    raise MsgSpecException("Invalid declaration: %s"%l)
                name = splits[0]
                val = splits[1]
            try:
                val_converted  = _convert_val(type_, val)
            except Exception as e:
                raise MsgSpecException("Invalid declaration: %s"%e)
            constants.append(Constant(type_, name, val_converted, val.strip()))
        else:
            if len(splits) != 2:
                raise MsgSpecException("Invalid declaration: %s"%l)
            name = splits[1]
            if not is_valid_msg_field_name(name):
                raise MsgSpecException("%s is not a legal message field name"%name)
            if package_context and not SEP in type_:
                if type_ == HEADER:
                    type_ == HEADER_FULL_NAME
                elif not base_msg_type(type_) in BUILTIN_TYPES:
                    #print "rewrite", type_, "to", "%s/%s"%(package_context, type_)
                    type_ = "%s/%s"%(package_context, type_)
            types.append(type_)
            names.append(name)
    return MsgSpec(types, names, constants, text, full_name, short_name, package_context)

def load_from_file(file_path, package_context=''):
    """
    Convert the .msg representation in the file to a :class:`MsgSpec` instance.
    This does *not* register the object.
    :param file_path: path of file to load from, ``str``
    :param package_context: package name to prepend to type name or
        '' to use local (relative) naming convention, ``str``
    :returns: Message type name and message specification, ``(str, MsgSpec)``
    :raises: :exc:`MsgSpecException`: if syntax errors or other problems are detected in file
    """
    if package_context:
        log("Load spec from", file_path, "into package [%s]"%package_context)
    else:
        log("Load spec from", file_path)

    file_name = os.path.basename(file_path)
    type_ = file_name[:-len(EXT_MSG)]
    base_type_ = type_
    # determine the type name
    if package_context:
        while package_context.endswith(SEP):
            package_context = package_context[:-1] #strip message separators
        type_ = "%s%s%s"%(package_context, SEP, type_)
    if not names.is_legal_resource_name(type_):
        raise MsgSpecException("%s: [%s] is not a legal type name"%(file_path, type_))
    
    f = open(file_path, 'r')
    try:
        try:
            text = f.read()
            return (type_, load_from_string(text, package_context, type_, base_type_))
        except MsgSpecException as e:
            raise MsgSpecException('%s: %s'%(file_name, e))
    finally:
        f.close()

# data structures and builtins specification ###########################

# adjustable constants, in case we change our minds
HEADER   = 'Header'
TIME     = 'time'
DURATION = 'duration'
HEADER_FULL_NAME = 'std_msgs/Header'

def is_header_type(msg_type):
    """
    :param msg_type: message type name, ``str``
    :returns: ``True`` if *msg_type* refers to the ROS Header type, ``bool``
    """
    # for backwards compatibility, include roslib/Header. REP 100
    return msg_type in [HEADER, HEADER_FULL_NAME, 'roslib/Header']
       
# time and duration types are represented as aggregate data structures
# for the purposes of serialization from the perspective of
# roslib.msgs. genmsg_py will do additional special handling is required
# to convert them into rospy.msg.Time/Duration instances.

## time as msg spec. time is unsigned 
TIME_MSG     = "uint32 secs\nuint32 nsecs"
## duration as msg spec. duration is just like time except signed
DURATION_MSG = "int32 secs\nint32 nsecs"

## primitive types are those for which we allow constants, i.e. have  primitive representation
PRIMITIVE_TYPES = ['int8','uint8','int16','uint16','int32','uint32','int64','uint64','float32','float64',
                   'string',
                   'bool',
                   # deprecated:
                   'char','byte']
BUILTIN_TYPES = PRIMITIVE_TYPES + [TIME, DURATION]

def is_builtin(msg_type_name):
    """
    @param msg_type_name: name of message type
    @type  msg_type_name: str
    @return: True if msg_type_name is a builtin/primitive type
    @rtype: bool
    """
    return msg_type_name in BUILTIN_TYPES

## extended builtins are builtin types that can be represented as MsgSpec instances
EXTENDED_BUILTINS = { TIME : load_from_string(TIME_MSG), DURATION: load_from_string(DURATION_MSG) }

REGISTERED_TYPES = { } 
_loaded_packages = [] #keep track of packages so that we only load once (note: bug #59)

def is_registered(msg_type_name):
    """
    :param msg_type_name: name of message type, ``str``
    :returns: ``True`` if msg spec for specified msg type name is
      registered. NOTE: builtin types are not registered, ``bool``
    """
    return msg_type_name in REGISTERED_TYPES

def get_registered(msg_type_name, default_package=None):
    """
    :param msg_type_name: name of message type, ``str``
    :returns: :class:`MsgSpec` for msg type name
    """
    # support for HEADER type
    if is_header_type(msg_type_name):
        msg_type_name = HEADER_FULL_NAME
    if msg_type_name in REGISTERED_TYPES:
        return REGISTERED_TYPES[msg_type_name]
    elif default_package:
        # if msg_type_name has no package specifier, try with default package resolution
        p, n = names.package_resource_name(msg_type_name)
        if not p:
            return REGISTERED_TYPES[names.resource_name(default_package, msg_type_name)]
    raise KeyError(msg_type_name)

def register(msg_type_name, msg_spec):
    """
    Load MsgSpec into the type dictionary
    
    :param msg_type_name: name of message type, ``str``
    :param msg_spec: :class:`MsgSpec` instance to load
    """
    log("Register msg %s"%msg_type_name)
    REGISTERED_TYPES[msg_type_name] = msg_spec

