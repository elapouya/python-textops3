# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import re

class length(TextOp): fn = classmethod(lambda cls,text: len(text))
class echo(TextOp): fn = classmethod(lambda cls,text: text)

class cut(TextOp):
    @classmethod
    def split(cls, text, sep):
        return text.split(sep)

    @classmethod
    def op(cls, text, col, sep=None, not_present_value='', *args,**kwargs):
        if isinstance(col,(list,tuple)):
            nbcol = len(col)
            for line in cls._tolist(text):
                line_cols = cls.split(line,sep)
                nblinecol = len(line_cols)
                yield [ line_cols[c] if c < nblinecol else not_present_value for c in col ]
        else:
            for line in cls._tolist(text):
                line_cols = cls.split(line,sep)
                nblinecol = len(line_cols)
                if col < nblinecol:
                    yield line_cols[col]
                else:
                    yield not_present_value

class cutre(cut):
    @classmethod
    def split(cls, text, sep):
        if hasattr(sep,'match'):
            return sep.split(text)
        return re.split(sep,text)

class cutca(cut):
    @classmethod
    def split(cls, text, sep):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groups() if m else []

class splitln(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
	return cls._tolist(text)

class StrOp(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, basestring):
            return cls.fn(text,*args,**kwargs)
        elif isinstance(text, list):
            return [ cls.fn(line,*args,**kwargs) for line in text ]
        return cls.gop(text,*args,**kwargs)
    @classmethod
    def gop(cls,text,*args,**kwargs):
        for line in text:
            yield cls.fn(line,*args,**kwargs)

class upper(StrOp): fn = str.upper
class lower(StrOp): fn = str.lower
class capitalize(StrOp): fn = str.capitalize
class replace(StrOp): fn = str.replace
class expandtabs(StrOp): fn = str.expandtabs
class split(StrOp): fn = str.split
class strip(StrOp): fn = str.strip
