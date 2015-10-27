# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This modules provides casting features, that is to force the output type """

from textops import TextOp
import dateutil.parser
from slugify import slugify

class tostr(TextOp):
    r""" Convert the result to a string

    | If the input text is a list or a generator, it will join all the lines with a newline.
    | If the input text is None, None is NOT converted to a string : None is returned

    Returns:
        str or None: converted result as a string

    Examples:

        >>> 'line1\nline2' | tostr()
        'line1\nline2'
        >>> ['line1','line2'] | tostr()
        'line1\nline2'
        >>> ['line1','line2'] | tostr('---')
        'line1---line2'
        >>> type(None | tostr())
        <type 'NoneType'>
        >>> None | tostr(return_if_none='N/A')
        'N/A'
    """
    @classmethod
    def fn(cls, text, join_str='\n', return_if_none=None,*args,**kwargs):
        return TextOp.make_string(text,join_str,return_if_none)

class tostre(TextOp):
    r""" Convert the result to a string

    | If the input text is a list or a generator, it will join all the lines with a newline.
    | If the input text is None, None is converted to an empty string.

    Returns:
        str: converted result as a string

    Examples:

        >>> ['line1','line2'] | tostre()
        'line1\nline2'
        >>> type(None | tostre())
        <class 'textops.base.StrExt'>
        >>> None | tostre()
        ''
    """
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