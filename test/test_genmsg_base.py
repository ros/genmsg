def test_log():
    from genmsg.base import log
    log("hello", "there")

def test_plog():
    class Foo(object):
        pass
    from genmsg.base import plog
    plog("hello", Foo())
        
def test_exceptions():
    from genmsg import MsgNotFound, MsgSpecException
    try:
        raise MsgNotFound('hello')
    except MsgNotFound:
        pass
    try:
        raise MsgSpecException('hello')
    except MsgSpecException:
        pass    
