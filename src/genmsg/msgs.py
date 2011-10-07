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
import traceback

from . base import MsgNotFound, InvalidMsgSpec, CONSTCHAR, COMMENTCHAR, EXT_MSG, MSG_DIR, SEP, log
from . names import is_legal_resource_name, is_legal_resource_base_name, package_resource_name, resource_name

#TODOXXX: unit test
def bare_msg_type(msg_type):
    """
    Compute the bare data type, e.g. for arrays, get the underlying array item type
    
    :param msg_type: ROS msg type (e.g. 'std_msgs/String'), ``str``
    :returns: base type, ``str``
    """
    if msg_type is None:
        return None
    if '[' in msg_type:
        return msg_type[:msg_type.find('[')]
    return msg_type

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
    bt = bare_msg_type(type_)
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
    base = bare_msg_type(x)
    if not is_legal_resource_name(base):
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
    return is_legal_resource_base_name(x)

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

def strify_spec(msg_context, spec, buff=None, indent=''):
    """
    Convert spec into a string representation. 
    :param msg_context: :class:`MsgContext` for looking up message types
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
        base_type = bare_msg_type(type_)
        if not base_type in BUILTIN_TYPES:
            package, base_type = package_resource_name(base_type)
            subspec = msg_context.get_registered(base_type)
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
        :raises: :exc:`InvalidMsgSpec` If spec is invalid (e.g. fields with the same name)
        """
        self.types = types
        if len(set(names)) != len(names):
            raise InvalidMsgSpec("Duplicate field names in message: %s"%names)
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
            raise InvalidMsgSpec("invalid field: %s"%(e))
        
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
        return self.text
    
# msg spec loading utilities ##########################################

def reinit():
    """
    Reinitialize roslib.msgs. This API is for message generators
    (e.g. genpy) that need to re-initialize the registration table.
    """
    global _initialized
    # unset the initialized state and unregister everything 
    _initialized = False
    REGISTERED_TYPES.clear()
    _initialized = True    
    
# .msg file routines ##############################################################       

def get_msg_file(package, base_type, search_path):
    """
    Determine the file system path for the specified .msg on path.

    :param package: name of package .msg file is in, ``str``
    :param base_type: type name of message, e.g. 'Point2DFloat32', ``str``
    :param search_path: dictionary mapping message namespaces to a directory locations

    :returns: file path of .msg file in specified package, ``str``
    :raises: :exc:`MsgNotFound` If message cannot be located.
    """
    log("msg_file(%s, %s, %s)" % (package, base_type, str(search_path)))
    if not isinstance(search_path, dict):
        raise ValueError("search_path must be a dictionary of {namespace: dirpath}")
    if not package in search_path:
        raise MsgNotFound("Cannot locate message [%s]: unknown package [%s]"%(base_type, package))
    else:
        path = os.path.join(search_path[package], "%s.msg"%(base_type))
        if os.path.isfile(path):
            return path
        else:
            raise MsgNotFound("Cannot locate message [%s] in package [%s]"%(base_type, package))

def _convert_val(type_, val):
    """
    Convert constant value declaration to python value. Does not do
    type-checking, so ValueError or other exceptions may be raised.
    
    :param type_: ROS field type, ``str``
    :param val: string representation of constant, ``str``
    :raises: :exc:`ValueError` If unable to convert to python representation
    :raises: :exc:`InvalidMsgSpec` If value exceeds specified integer width
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
            raise InvalidMsgSpec("cannot coerce [%s] to %s (out of bounds)"%(val, type_))
        return val
    elif type_ == 'bool':
        # TODO: need to nail down constant spec for bool
        return True if eval(val) else False
    raise InvalidMsgSpec("invalid constant type: [%s]"%type_)
        
def load_by_type(msg_context, msg_type, search_path, package_context=''):
    """
    Load message specification for specified type.

    NOTE: this will *not* register the message in the *msg_context*.
    
    :param msg_context: :class:`MsgContext` for finding loaded dependencies
    :param search_path: dictionary mapping message namespaces to a directory locations
    :param package_context: (optional) package name to resolve
      relative type names.

    :returns: Message type name and :class:`MsgSpec` instance, ``(str, MsgSpec)``
    :raises: :exc:`MsgNotFound` If message cannot be located.
    """
    log("load_by_type(%s, %s, %s)" % (msg_type, str(search_path), package_context))
    if not isinstance(search_path, dict):
        raise ValueError("search_path must be a dictionary of {namespace: dirpath}")

    pkg, base_type = package_resource_name(msg_type)
    pkg = pkg or package_context # convert '' -> local package
    
    log("pkg", pkg)
    file_path = get_msg_file(pkg, base_type, search_path)
    log("file_path", file_path)
    if file_path is None:
        raise MsgNotFound(msg_type)
    return load_from_file(msg_context, file_path, package_context=pkg, full_name=msg_type, short_name=base_type)

def _load_constant_line(orig_line, line_splits):
    """
    :raises: :exc:`InvalidMsgSpec`
    """
    field_type = line_splits[0]
    if not is_valid_constant_type(field_type):
        raise InvalidMsgSpec("%s is not a legal constant type"%field_type)

    if field_type == 'string':
        # strings contain anything to the right of the equals sign, there are no comments allowed
        idx = orig_line.find(CONSTCHAR)
        name = orig_line[orig_line.find(' ')+1:idx]
        val = orig_line[idx+1:]
    else:
        line_splits = [x.strip() for x in ' '.join(line_splits[1:]).split(CONSTCHAR)] #resplit on '='
        if len(line_splits) != 2:
            raise InvalidMsgSpec("Invalid constant declaration: %s"%l)
        name = line_splits[0]
        val = line_splits[1]

    try:
        val_converted = _convert_val(field_type, val)
    except Exception as e:
        raise InvalidMsgSpec("Invalid constant value: %s"%e)
    return Constant(field_type, name, val_converted, val.strip())

def _load_field_line(orig_line, line_splits, package_context):
    """
    :returns: (field_type, name) tuple, ``(str, str)``
    :raises: :exc:`InvalidMsgSpec`
    """
    log("_load_field_line", orig_line, line_splits, package_context)
    if len(line_splits) != 2:
        raise InvalidMsgSpec("Invalid declaration: %s"%(orig_line))
    field_type, name = line_splits
    if not is_valid_msg_field_name(name):
        raise InvalidMsgSpec("%s is not a legal message field name"%name)
    if package_context and not SEP in field_type:
        if field_type == HEADER:
            field_type = HEADER_FULL_NAME
        elif not bare_msg_type(field_type) in BUILTIN_TYPES:
            field_type = "%s/%s"%(package_context, field_type)
    elif field_type == HEADER:
        field_type = HEADER_FULL_NAME
    return field_type, name

def load_from_string(msg_context, text, package_context='', full_name='', short_name=''):
    """
    Load message specification from a string.

    NOTE: this will *not* register the message in the *msg_context*.
    
    :param msg_context: :class:`MsgContext` for finding loaded dependencies
    :param text: .msg text , ``str``
    :param package_context: package name to use for the type name or
        '' to use the local (relative) naming convention., ``str``
    :returns: :class:`MsgSpec` specification
    :raises: :exc:`InvalidMsgSpec` If syntax errors or other problems are detected in file
    """
    log("load_from_string", text, package_context, full_name, short_name)
    types = []
    names = []
    constants = []
    for orig_line in text.split('\n'):
        l = orig_line.split(COMMENTCHAR)[0].strip() #strip comments
        if not l:
            continue #ignore empty lines
        line_splits = [s for s in [x.strip() for x in l.split(" ")] if s] #split type/name, filter out empties
        if CONSTCHAR in l:
            print("LINE", l)
            constants.append(_load_constant_line(orig_line, line_splits))
        else:
            field_type, name = _load_field_line(orig_line, line_splits, package_context)
            types.append(field_type)
            names.append(name)
    return MsgSpec(types, names, constants, text, full_name, short_name, package_context)

def load_from_file(msg_context, file_path, package_context='', full_name='', short_name=''):
    """
    Convert the .msg representation in the file to a :class:`MsgSpec` instance.

    NOTE: this will *not* register the message in the *msg_context*.
    
    :param file_path: path of file to load from, ``str``
    :param package_context: package name to prepend to type name or
        '' to use local (relative) naming convention, ``str``
    :returns: :class:`MsgSpec` instance
    :raises: :exc:`InvalidMsgSpec`: if syntax errors or other problems are detected in file
    """
    if package_context:
        log("Load spec from", file_path, "into package [%s]"%package_context)
    else:
        log("Load spec from", file_path)

    with open(file_path, 'r') as f:
        text = f.read()
    try:
        return load_from_string(msg_context, text, package_context, full_name, short_name)
    except InvalidMsgSpec as e:
        log(traceback.format_exc())
        raise InvalidMsgSpec('%s: %s'%(file_path, e))

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

REGISTERED_TYPES = { } 

class MsgContext(object):

    def __init__(self):
        self._registered_packages = {}
        
    @staticmethod
    def create_default():
        context = MsgContext()
        # register builtins (needed for serialization).  builtins have no package.
        context.register('', TIME, load_from_string(context, TIME_MSG))
        context.register('', DURATION, load_from_string(context, DURATION_MSG))
        return context
        
    def register(self, package, base_type, msgspec):
        if package not in self._registered_packages:
            self._registered_packages[package] = {}
        self._registered_packages[package][base_type] = msgspec

    def is_registered_full(self, full_msg_type):
        full_msg_type = bare_msg_type(full_msg_type)
        package, base_type = package_resource_name(full_msg_type)
        return self.is_registered(package, base_type)
        
    def is_registered(self, package, base_type, default_package=''):
        """
        :param package: package name of type, or ``None`` if package name not specified
        :param base_type: base type name of message
        :param default_package: default package namespace to resolve
          in.  May be overridden by special types.
          
        :returns: ``True`` if :class:`MsgSpec` instance has been loaded for the requested type.
        """
        # support for HEADER type
        if not package:
            if base_type == HEADER:
                package = 'std_msgs'
            else:
                package = default_package

        if package in self._registered_packages:
            return base_type in self._registered_packages
        else:
            return False

    def get_registered(self, package, base_type):
        if self.is_regisered(self, package, base_type):
            return self._registered_packages[package][base_type]
        else:
            return False

    def get_registered_full(self, full_msg_type):
        full_msg_type = bare_msg_type(full_msg_type)
        package, base_type = package_resource_name(full_msg_type)
        return self.get_registered(package, base_type)

    def __str__(self):
        return str(self._registered_packages)
