# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import re

class length(TextOp): fn = classmethod(lambda cls,text: len(text))
class echo(TextOp): fn = classmethod(lambda cls,text: text)

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

class cut(StrOp):
    @classmethod
    def split(cls, text, sep):
        return text.split(sep)

    @classmethod
    def fn(cls, text, sep=None, col=None, not_present_value='', *args,**kwargs):
        if isinstance(col,(list,tuple)):
            nbcol = len(col)
            line_cols = cls.split(text,sep)
            nblinecol = len(line_cols)
            return [ line_cols[c] if c < nblinecol else not_present_value for c in col ]
        else:
            line_cols = cls.split(text,sep)
            nblinecol = len(line_cols)
            if col == None:
                return line_cols
            elif col < nblinecol:
                return line_cols[col]
            else:
                return not_present_value

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

class cutcan(cut):
    @classmethod
    def split(cls, text, sep):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groupdict() if m else []

class upper(StrOp): fn = str.upper
class lower(StrOp): fn = str.lower
class capitalize(StrOp): fn = str.capitalize
class replace(StrOp): fn = str.replace
class expandtabs(StrOp): fn = str.expandtabs
class split(StrOp): fn = str.split
class strip(StrOp): fn = str.strip
