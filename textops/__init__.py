# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade

__version__ = '3.0.5'
__author__ = 'Eric Lapouyade'
__copyright__ = 'Copyright 2018, python-textops3 project'
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

# Do not use .base instead of textops.base otherwise readthedocs.org cannot see base.py module.
from textops.base import TextOp, WrapOp, WrapOpIter, WrapOpStr, add_textop, add_textop_iter, \
    StrExt, BytesExt, ListExt, DictExt, NoAttrDict, NoAttr, DefaultList, \
    DefaultDict, string_formatter, dictmerge, vformat, dformat, eformat, \
    stru, activate_debug, pp, extend_type, extend_type_gen, decode_bytes
from . import ops
from .ops import *
