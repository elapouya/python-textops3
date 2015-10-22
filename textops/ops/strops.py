# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This module gathers text operations to be run on a string """

from textops import TextOp
import re

class length(TextOp):
    """ Returns the length of a string

    Returns:
        int: length of the string

    Examples:

        >>> s='this is a string'
        >>> s | length()
        16
        >>> s=StrExt(s)
        >>> s.length()
        16
    """
    fn = staticmethod(lambda text: len(text))

class echo(TextOp):
    """ identity operation

    it returns the same text, except that is uses textops Extended classes (StrExt, ListExt ...).
    This could be usefull in some cases to access str methods (upper, replace, ...) just after a pipe.

    Returns:
        int: length of the string

    Note:
        ``strop`` is a shortcut for ``echo()``

    Examples:

        >>> s='this is a string'
        >>> type(s)
        <type 'str'>
        >>> t=s | echo()
        >>> type(t)
        <class 'textops.base.StrExt'>
        >>> s.upper()
        'THIS IS A STRING'
        >>> s | upper()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        NameError: name 'upper' is not defined
        >>> s | echo().upper()
        'THIS IS A STRING'
        >>> s | strop.upper()
        'THIS IS A STRING'
    """
    fn = staticmethod(lambda text: text)

strop = echo()

class splitln(TextOp):
    """ Transforms a string with newlines into a list of lines

    It uses python str.splitlines() : newline separator can be \\\\n or \\\\r or both. They are removed
    during the process.

    Returns:
        list: The splitted text

    Example:

        >>> s='this is\\na multi-line\\nstring'
        >>> s | splitln()
        ['this is', 'a multi-line', 'string']
    """
    @classmethod
    def op(cls,text,*args,**kwargs):
        return cls._tolist(text)

class matches(TextOp):
    """ Tests whether a pattern is present or not

    Uses re.match() to match a pattern against the string.

    Args:
        pattern (str): a regular expression string

    Returns:
        re.RegexObject: The pattern found

    Note:
        Be careful : the pattern is tested from the beginning of the string, the pattern is NOT searched somewhere in the middle of the string.

    Examples:

        >>> state=StrExt('good')
        >>> print 'OK' if state.matches(r'good|not_present|charging') else 'CRITICAL'
        OK
        >>> state=StrExt('looks like all is good')
        >>> print 'OK' if state.matches(r'good|not_present|charging') else 'CRITICAL'
        CRITICAL
        >>> print 'OK' if state.matches(r'.*(good|not_present|charging)') else 'CRITICAL'
        OK
        >>> state=StrExt('Error')
        >>> print 'OK' if state.matches(r'good|not_present|charging') else 'CRITICAL'
        CRITICAL

    """
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
        return re.match(pattern,text,*args,**kwargs)

class searches(TextOp):
    """ Search a pattern

    Uses re.search() to find a pattern in the string.

    Args:
        pattern (str): a regular expression string

    Returns:
        re.RegexObject: The pattern found

    Examples:

        >>> state=StrExt('good')
        >>> print 'OK' if state.searches(r'good|not_present|charging') else 'CRITICAL'
        OK
        >>> state=StrExt('looks like all is good')
        >>> print 'OK' if state.searches(r'good|not_present|charging') else 'CRITICAL'
        OK
        >>> print 'OK' if state.searches(r'.*(good|not_present|charging)') else 'CRITICAL'
        OK
        >>> state=StrExt('Error')
        >>> print 'OK' if state.searches(r'good|not_present|charging') else 'CRITICAL'
        CRITICAL

    """
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
        return re.search(pattern,text,*args,**kwargs)



class StrOp(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, basestring) and '\n' in text:
            text = cls._tolist(text)
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
    def split(cls, text, sep, *args,**kwargs):
        return text.split(sep)

    @classmethod
    def fn(cls, text, sep=None, col=None, not_present_value='', *args,**kwargs):
        if isinstance(col, basestring):
            col = [int(i) for i in col.split(',')]
        if isinstance(col,(list,tuple)):
            nbcol = len(col)
            line_cols = cls.split(text,sep, *args,**kwargs)
            nblinecol = len(line_cols)
            return [ line_cols[c] if c < nblinecol else not_present_value for c in col ]
        else:
            line_cols = cls.split(text,sep, *args,**kwargs)
            nblinecol = len(line_cols)
            if col == None:
                return line_cols
            elif col < nblinecol:
                return line_cols[col]
            else:
                return not_present_value

class cutre(cut):
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            return sep.split(text)
        return re.split(sep,text)

class cutca(cut):
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groups() if m else []

class cutdct(cut):
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groupdict() if m else {}

class cutkv(cut):
    @classmethod
    def split(cls, text, sep, key_name = 'key', *args,**kwargs):
        # Use named 'key_name' parameter, not postionnal
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        if m:
            dct = m.groupdict()
            kv = dct.get(key_name)
            if kv:
                return { kv : dct }
        return {}