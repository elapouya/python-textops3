# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import dateutil.parser
from slugify import slugify

class tostr(TextOp): fn = TextOp.make_string
class tostre(TextOp): fn = classmethod(lambda cls,text: TextOp.make_string(text,''))
class tolist(TextOp): fn = TextOp.make_list
class toliste(TextOp): fn = classmethod(lambda cls,text: TextOp.make_list(text,[]))
class toint(TextOp): fn = TextOp.make_int
class tofloat(TextOp): fn = TextOp.make_float
class todatetime(TextOp): fn = classmethod(lambda cls,text: dateutil.parser.parse(text))
class toslug(TextOp): fn = classmethod(lambda cls,text: slugify(text))
