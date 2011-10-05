SEP = '/'

MSG_DIR = 'msg'
SRV_DIR = 'srv'

EXT_MSG = '.msg'
EXT_SRV = '.srv'

## character that designates a constant assignment rather than a field
CONSTCHAR   = '='
COMMENTCHAR = '#'
IODELIM   = '---'

class MessageNotFound(Exception):
    pass

class MsgSpecException(Exception):
    pass
