# Software License Agreement (BSD License)
#
# Copyright (c) 2009, Willow Garage, Inc.
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

import os
import sys

import random

def test_bare_msg_type():
    import genmsg.msgs    
    tests = [(None, None), ('String', 'String'), ('std_msgs/String', 'std_msgs/String'),
             ('String[10]', 'String'), ('string[10]', 'string'), ('std_msgs/String[10]', 'std_msgs/String'),
             ]
    for val, res in tests:
      assert res == genmsg.msgs.bare_msg_type(val)

PKG = 'genmsg'

def test_resolve_type():
    from genmsg.msgs import resolve_type, bare_msg_type
    for t in ['string', 'string[]', 'string[14]', 'int32', 'int32[]']:
        bt = bare_msg_type(t)
        t == resolve_type(t, PKG)
      
    assert 'foo/string' == resolve_type('foo/string', PKG)
    assert 'std_msgs/Header' == resolve_type('Header', 'roslib')
    assert 'std_msgs/Header' == resolve_type('std_msgs/Header', 'roslib')
    assert 'std_msgs/Header' == resolve_type('Header', 'stereo_msgs')
    assert 'std_msgs/String' == resolve_type('String', 'std_msgs')
    assert 'std_msgs/String' == resolve_type('std_msgs/String', 'std_msgs')
    assert 'std_msgs/String' == resolve_type('std_msgs/String', PKG) 
    assert 'std_msgs/String[]' == resolve_type('std_msgs/String[]', PKG)
    
def test_parse_type():
    import genmsg.msgs
    tests = [
        ('a', ('a', False, None)),
        ('int8', ('int8', False, None)),      
        ('std_msgs/String', ('std_msgs/String', False, None)),
        ('a[]', ('a', True, None)),
        ('int8[]', ('int8', True, None)),      
        ('std_msgs/String[]', ('std_msgs/String', True, None)),
        ('a[1]', ('a', True, 1)),
        ('int8[1]', ('int8', True, 1)),      
        ('std_msgs/String[1]', ('std_msgs/String', True, 1)),
        ('a[11]', ('a', True, 11)),
        ('int8[11]', ('int8', True, 11)),      
        ('std_msgs/String[11]', ('std_msgs/String', True, 11)),
        ]
    for val, res in tests:
        assert res == genmsg.msgs.parse_type(val)
      
    fail = ['a[1][2]', 'a[][]', '', None, 'a[', 'a[[1]', 'a[1]]']
    for f in fail:
        try:
            genmsg.msgs.parse_type(f)
            assert False, "should have failed on %s"%f
        except ValueError as e:
            pass

def test_Constant():
    import genmsg.msgs    
    vals = [random.randint(0, 1000) for i in xrange(0, 3)]
    type_, name, val = [str(x) for x in vals]
    x = genmsg.msgs.Constant(type_, name, val, str(val))
    assert type_ == x.type
    assert name == x.name
    assert val == x.val
    assert x == genmsg.msgs.Constant(type_, name, val, str(val))

    assert 1 != x
    assert x != genmsg.msgs.Constant('baz', name, val, str(val))
    assert x != genmsg.msgs.Constant(type_, 'foo', val, str(val))
    assert x != genmsg.msgs.Constant(type_, name, 'foo', 'foo')

    # tripwire
    assert repr(x)
    assert str(x)
    
    try:
        genmsg.msgs.Constant(None, name, val, str(val))
        assert False, "should have raised"
    except: pass
    try:
        genmsg.msgs.Constant(type_, None, val, str(val))
        assert False, "should have raised"        
    except: pass
    try:
        genmsg.msgs.Constant(type_, name, None, 'None')
        assert False, "should have raised"        
    except: pass
    try:
        genmsg.msgs.Constant(type_, name, val, None)
        assert False, "should have raised"        
    except: pass
    
    try:
        x.foo = 'bar'
        assert False, 'Constant should not allow arbitrary attr assignment'
    except: pass
    
def test_MsgSpec():
    def sub_test_MsgSpec(types, names, constants, text, has_header):
        m = MsgSpec(types, names, constants, text)
        assert m.types == types
        assert m.names == names
        assert m.text == text
        assert has_header == m.has_header()
        assert m.constants == constants
        assert zip(types, names) == m.fields()
        assert m == MsgSpec(types, names, constants, text)
        return m
    
    from genmsg import MsgSpec
    # allow empty msg
    empty = sub_test_MsgSpec([], [], [], '', False)
    assert [] == empty.fields()

    # one-field
    one_field = sub_test_MsgSpec(['int32'], ['x'], [], 'int32 x', False)
    # make sure that equals tests every declared field
    assert one_field == MsgSpec(['int32'], ['x'], [], 'int32 x')
    assert one_field != MsgSpec(['uint32'], ['x'], [], 'int32 x')
    assert one_field != MsgSpec(['int32'], ['y'], [], 'int32 x')
    assert one_field != MsgSpec(['int32'], ['x'], [], 'uint32 x')
    # test against __ne__ as well
    assert one_field != MsgSpec(['int32'], ['x'], [], 'uint32 x')
    #test strify
    assert "int32 x" == str(one_field).strip()
    
    # test variations of multiple fields and headers
    two_fields = sub_test_MsgSpec(['int32', 'string'], ['x', 'str'], [], 'int32 x\nstring str', False)
    one_header = sub_test_MsgSpec(['std_msgs/Header'], ['header'], [], 'Header header', True)
    header_and_fields = sub_test_MsgSpec(['std_msgs/Header', 'int32', 'string'], ['header', 'x', 'str'], [], 'Header header\nint32 x\nstring str', True)
    embed_types = sub_test_MsgSpec(['std_msgs/Header', 'std_msgs/Int32', 'string'], ['header', 'x', 'str'], [], 'Header header\nstd_msgs/Int32 x\nstring str', True)
    #test strify
    assert "int32 x\nstring str" == str(two_fields).strip()

    # types and names mismatch
    try:
        MsgSpec(['int32', 'int32'], ['intval'], [], 'int32 intval\int32 y')
        assert False, "types and names must align"
    except: pass

    # test (not) equals against non msgspec
    assert not (one_field == 1)
    assert one_field != 1
    #TODO: test flatten

    # test that repr doesn't throw an error
    [repr(x) for x in [empty, one_field, one_header, two_fields, embed_types]]

def test_reinit():
    import genmsg.msgs    
    genmsg.msgs._initialized = False
    genmsg.msgs.reinit()
    assert genmsg.msgs._initialized
    # test repeated initialization
    genmsg.msgs.reinit()    

def test___convert_val():
    from genmsg.msgs import _convert_val
    from genmsg import InvalidMsgSpec
    assert 0. == _convert_val('float32', '0.0')
    assert 0. == _convert_val('float64', '0.0')
    
    assert 'fo o' == _convert_val('string', '   fo o ')

    assert 1 == _convert_val('byte', '1')
    assert 1 == _convert_val('char', '1')
    assert 1 == _convert_val('int8', '1')
    assert 12 == _convert_val('int16', '12')
    assert -13 == _convert_val('int32', '-13')
    assert 14 == _convert_val('int64', '14')
    assert 0 == _convert_val('uint8', '0')
    assert 18 == _convert_val('uint16', '18')
    assert 19 == _convert_val('uint32', '19')
    assert 20 == _convert_val('uint64', '20')

    width_fail = [('int8', '129'), ('uint8', '256'),
                  ('int16', '35536'), ('uint16', '-1'),('uint16', '65536'),
                  ('int32', '3000000000'),('int32', '-2700000000'),
                  ('uint32', '-1'),('uint32', '41000000000'),
                  ('uint64', '-1')]
    for t, v in width_fail:
        try:
            _convert_val(t, v)
            assert False, "should have failed width check: %s, %s"%(t, v)
        except InvalidMsgSpec:
            pass
    type_fail = [('int32', 'f'), ('float32', 'baz')]
    for t, v in type_fail:
        try:
            _convert_val(t, v)
            assert False, "should have failed type check: %s, %s"%(t, v)
        except ValueError:
            pass
    try:
        _convert_val('foo', '1')
        assert False, "should have failed invalid type"
    except InvalidMsgSpec:
        pass
    
def test_load_from_string():
    # make sure Header -> std_msgs/Header conversion works
    from genmsg.msgs import load_from_string, MsgContext
    context = MsgContext.create_default()
    msgspec = load_from_string(context, "Header header", package_context='test_pkg', full_name='test_pkg/HeaderTest', short_name='HeaderTest')
    print msgspec
    assert msgspec.has_header()
    assert msgspec.types == ['std_msgs/Header']
    assert msgspec.names == ['header']
    assert msgspec.constants == []
    assert msgspec.short_name == 'HeaderTest'
    
def _validate_TestString(msgspec):
    assert ['caller_id', 'orig_caller_id', 'data'] == msgspec.names, msgspec.names
    assert ['string', 'string', 'string'] == msgspec.types, msgspec.types

def test_load_from_file():
    from genmsg.msgs import load_from_file, MsgContext
    test_d = get_test_dir()
    test_ros_dir = os.path.join(test_d, 'test_ros', 'msg')
    test_string_path = os.path.join(test_ros_dir, 'TestString.msg')

    msg_context = MsgContext.create_default()
    load_from_file(msg_context, test_string_path, package_context='test_ros', full_name='test_ros/TestString', short_name='TestString')
    # not supposed to register
    assert not msg_context.is_registered_full('test_ros/TestString'), msg_context
    assert not msg_context.is_registered('test_ros', 'TestString')    
    
def test_load_from_string_TestString():
    from genmsg.msgs import load_from_string, MsgContext

    test_d = get_test_dir()
    test_ros_dir = os.path.join(test_d, 'test_ros', 'msg')
    test_string_path = os.path.join(test_ros_dir, 'TestString.msg')
    with open(test_string_path) as f:
        text = f.read()

    msg_context = MsgContext.create_default()
    _validate_TestString(load_from_string(msg_context, text, 'test_ros', 'test_ros/TestString', 'TestString'))
    # not supposed to register
    assert not msg_context.is_registered_full('test_ros/TestString'), msg_context
    assert not msg_context.is_registered('test_ros', 'TestString')    

def test_load_by_type():
    test_d = get_test_dir()
    test_ros_dir = os.path.join(test_d, 'test_ros', 'msg')
    test_string_path = os.path.join(test_ros_dir, 'TestString.msg')
    search_path = {
        'test_ros': test_ros_dir,
        }
    from genmsg.msgs import load_by_type, MsgContext
    msg_context = MsgContext.create_default()
    msgspec = load_by_type(msg_context, 'test_ros/TestString', search_path)
    _validate_TestString(msgspec)
    # not supposed to register
    assert not msg_context.is_registered_full('test_ros/TestString'), msg_context
    assert not msg_context.is_registered('test_ros', 'TestString')    
    
def get_test_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))

def test_get_msg_file():
    from genmsg.msgs import get_msg_file, MsgNotFound
    test_d = get_test_dir()
    test_ros_dir = os.path.join(test_d, 'test_ros', 'msg')
    test_string_path = os.path.join(test_ros_dir, 'TestString.msg')
    search_path = {
        'test_ros': test_ros_dir,
        }
    assert test_string_path == get_msg_file('test_ros', 'TestString', search_path)
    try:
        get_msg_file('test_ros', 'Bad', search_path)
        assert False, "should have raised"
    except MsgNotFound:
        pass
    try:
        get_msg_file('bad_pkg', 'TestString', search_path)
        assert False, "should have raised"
    except MsgNotFound:
        pass

def test_is_valid_msg_type():
    import genmsg.msgs
    vals = [
        #basic
        'F', 'f', 'Foo', 'Foo1',
        'std_msgs/String',
        # arrays
        'Foo[]', 'Foo[1]', 'Foo[10]',
        ]
    for v in vals:
        assert genmsg.msgs.is_valid_msg_type(v), "genmsg.msgs.is_valid_msg_type should have returned True for '%s'"%v
 
    # bad cases
    vals = [None, '', '#', '%', 'Foo%', 'Woo Woo',
            '/', '/String', 
            'Foo[f]', 'Foo[1d]', 'Foo[-1]', 'Foo[1:10]', 'Foo[', 'Foo]', 'Foo[]Bar']
    for v in vals:
        assert not genmsg.msgs.is_valid_msg_type(v), "genmsg.msgs.is_valid_msg_type should have returned False for '%s'"%v
      
def test_is_valid_constant_type():
    import genmsg.msgs
    valid = ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', \
             'uint64', 'float32', 'float64', 'char', 'byte', 'string']
    invalid = [
        'std_msgs/String', '/', 'String',
        'time', 'duration','header',
    ]
    for v in valid:
        assert genmsg.msgs.is_valid_constant_type(v), "genmsg.msgs.is_valid_constant_type should have returned True for '%s'"%v
    for v in invalid:
        assert not genmsg.msgs.is_valid_constant_type(v), "genmsg.msgs.is_valid_constant_type should have returned False for '%s'"%v
