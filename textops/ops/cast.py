# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import dateutil.parser
from slugify import slugify

class tostr(TextOp):
    @classmethod 
    def fn(cls, text, join_str='\n', return_if_none=None,*args,**kwargs):
        return TextOp.make_string(text,join_str,return_if_none)

class tostre(TextOp):
    @classmethod 
    def fn(cls, text, join_str='\n', return_if_none='',*args,**kwargs):
        return TextOp.make_string(text,join_str,return_if_none)
    
class tolist(TextOp):
    @classmethod 
    def fn(cls, text, return_if_none=None,*args,**kwargs):
        return TextOp.make_list(text,return_if_none)

class toliste(TextOp):
    @classmethod 
    def fn(cls, text, return_if_none=[],*args,**kwargs):
        return TextOp.make_list(text,return_if_none)

class toint(TextOp):
    @classmethod 
    def fn(cls, text,*args,**kwargs):
        return TextOp.make_int(text)

class tofloat(TextOp):
    @classmethod 
    def fn(cls, text,*args,**kwargs):
        return TextOp.make_float(text)

class todatetime(TextOp):
    @classmethod 
    def fn(cls, text,*args,**kwargs):
        return dateutil.parser.parse(text)

class toslug(TextOp):
    @classmethod 
    def fn(cls, text,*args,**kwargs):
        return slugify(text)