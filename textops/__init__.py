# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.5'

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

from base import TextOp, StrExt, ListExt, DictExt, NoAttrDict, NoAttr
import ops
from ops import *
