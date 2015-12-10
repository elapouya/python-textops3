# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade

__version__ = '0.1.8'
__author__ = 'Eric Lapouyade'
__copyright__ = 'Copyright 2015, python-textops project'
__credits__ = ['Eric Lapouyade']
__license__ = 'LGPL'
__maintainer__ = 'Eric Lapouyade'
__status__ = 'Beta'

import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

from base import TextOp, WrapOp, WrapOpIter, WrapOpStr, add_textop, add_textop_iter, \
                 StrExt, UnicodeExt, ListExt, DictExt, NoAttrDict, NoAttr, \
                 DefaultDict, string_formatter, vformat, dformat, activate_debug, pp
import ops
from ops import *
