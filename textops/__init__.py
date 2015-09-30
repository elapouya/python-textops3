# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.9'

import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

from base import TextOp, WrapOpIter, WrapOpYield, add_textop, add_textop_iter, \
                 add_textop_yield, StrExt, UnicodeExt, ListExt, DictExt, NoAttrDict, NoAttr, \
                 activate_debug
import ops
from ops import *
