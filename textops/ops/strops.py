# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This module gathers text operations to be run on a string """

from textops import TextOp
import re
import types

class PyStrWrapper(object):
    """ This is a help to be able to use python string method with piped notation """

    def __getattr__(self,attr):
        if not attr.startswith('_'):
            op = TextOp()
            op.ops=[[attr, (), {}]]
            op.op = attr
        else:
            raise AttributeError()
        return op

strop = PyStrWrapper()

class length(TextOp):
    r""" Returns the length of a string, list or generator

    Returns:
        int: length of the string

    Examples:

        >>> s='this is a string'
        >>> s | length()
        16
        >>> s=StrExt(s)
        >>> s.length()
        16
        >>> ['a','b','c'] | length()
        3
        >>> def mygenerator():yield 3; yield 2
        >>> mygenerator() | length()
        2
    """
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, types.GeneratorType):
            return reduce(lambda x,y:x+1,text,0)
        return len(text)

class echo(TextOp):
    r""" identity operation

    it returns the same text, except that is uses textops Extended classes (StrExt, ListExt ...).
    This could be usefull in some cases to access str methods (upper, replace, ...) just after a pipe.

    Returns:
        int: length of the string

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

class splitln(TextOp):
    r""" Transforms a string with newlines into a list of lines

    It uses python str.splitlines() : newline separator can be \\n or \\r or both. They are removed
    during the process.

    Returns:
        list: The splitted text

    Example:

        >>> s='this is\na multi-line\nstring'
        >>> s | splitln()
        ['this is', 'a multi-line', 'string']
    """
    @classmethod
    def op(cls,text,*args,**kwargs):
        return cls._tolist(text)

class matches(TextOp):
    r""" Tests whether a pattern is present or not

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
    r""" Search a pattern

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
    r""" Extract columns from a string or a list of strings

    This works like the unix shell command 'cut'. It uses :meth:`str.split` function.

        * if the input is a simple string, cut() will return a list of strings
          representing the splitted input string.
        * if the input is a list of strings or a string with newlines, cut() will return
          a list of list of strings : each line of the input will splitted and put in a list.
        * if only one column is extracted, one level of list is removed.

    Args:
        sep (str): a string as a column separator, default is None : this means 'any kind of spaces'
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        not_present_value (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='col1 col2 col3'
        >>> s | cut()
        ['col1', 'col2', 'col3']
        >>> s | cut(col=1)
        'col2'
        >>> s | cut(col='1,2,10',not_present_value='N/A')
        ['col2', 'col3', 'N/A']
        >>> s='col1.1 col1.2 col1.3\ncol2.1 col2.2 col2.3'
        >>> s | cut()
        [['col1.1', 'col1.2', 'col1.3'], ['col2.1', 'col2.2', 'col2.3']]
        >>> s | cut(col=1)
        ['col1.2', 'col2.2']
        >>> s | cut(col='0,1')
        [['col1.1', 'col1.2'], ['col2.1', 'col2.2']]
        >>> s | cut(col=[1,2])
        [['col1.2', 'col1.3'], ['col2.2', 'col2.3']]
        >>> s='col1.1 | col1.2 |  col1.3\ncol2.1 | col2.2 | col2.3'
        >>> s | cut()
        [['col1.1', '|', 'col1.2', '|', 'col1.3'], ['col2.1', '|', 'col2.2', '|', 'col2.3']]
        >>> s | cut(sep=' | ')
        [['col1.1', 'col1.2', ' col1.3'], ['col2.1', 'col2.2', 'col2.3']]
    """
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
    r""" Extract columns from a string or a list of strings with re.split()

    This works like the unix shell command 'cut'. It uses :func:`re.split` function.

        * if the input is a simple string, cutre() will return a list of strings
          representing the splitted input string.
        * if the input is a list of strings or a string with newlines, cut() will return
          a list of list of strings : each line of the input will splitted and put in a list.
        * if only one column is extracted, one level of list is removed.

    Args:
        sep (str or re.RegexObject): a regular expression string or object as a column separator
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        not_present_value (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='col1.1 | col1.2 | col1.3\ncol2.1 | col2.2 | col2.3'
        >>> print s
        col1.1 | col1.2 | col1.3
        col2.1 | col2.2 | col2.3
        >>> s | cutre(r'\s+')
        [['col1.1', '|', 'col1.2', '|', 'col1.3'], ['col2.1', '|', 'col2.2', '|', 'col2.3']]
        >>> s | cutre(r'[\s|]+')
        [['col1.1', 'col1.2', 'col1.3'], ['col2.1', 'col2.2', 'col2.3']]
        >>> s | cutre(r'[\s|]+','0,2,4','-')
        [['col1.1', 'col1.3', '-'], ['col2.1', 'col2.3', '-']]
        >>> mysep = re.compile(r'[\s|]+')
        >>> s | cutre(mysep)
        [['col1.1', 'col1.2', 'col1.3'], ['col2.1', 'col2.2', 'col2.3']]
    """
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            return sep.split(text)
        return re.split(sep,text)

class cutca(cut):
    r""" Extract columns from a string or a list of strings through pattern capture

    This works like :class:`textops.cutre` except it needs a pattern having parenthesis to capture column.

        * if the input is a simple string, cutca() will return a list of strings
          representing the splitted input string.
        * if the input is a list of strings or a string with newlines, cut() will return
          a list of list of strings : each line of the input will splitted and put in a list.
        * if only one column is extracted, one level of list is removed.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        not_present_value (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutca(r'[^-]*-([^-]*)-[^=]*=([^=]*)=[^_]*_([^_]*)_')
        ['col1', 'col2', 'col3']
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cutca(r'[^-]*-([^-]*)-[^=]*=([^=]*)=[^_]*_([^_]*)_','0,2,4','not present')
        [['col1', 'col3', 'not present'], ['col11', 'col33', 'not present']]
    """
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groups() if m else []

class cutdct(cut):
    r""" Extract columns from a string or a list of strings through pattern capture

    This works like :class:`textops.cutca` except it needs a pattern having *named* parenthesis to capture column.

        * if the input is a simple string, cutca() will return a list of strings
          representing the splitted input string.
        * if the input is a list of strings or a string with newlines, cut() will return
          a list of list of strings : each line of the input will splitted and put in a list.
        * if only one column is extracted, one level of list is removed.

    Args:
        sep (str or re.RegexObject): a regular expression string or object
            having *named* capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        not_present_value (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='item="col1" count="col2" price="col3"'
        >>> s | cutdct(r'item="(?P<item>[^"]*)" count="(?P<i_count>[^"]*)" price="(?P<i_price>[^"]*)"')
        {'item': 'col1', 'i_price': 'col3', 'i_count': 'col2'}
        >>> s='item="col1" count="col2" price="col3"\nitem="col11" count="col22" price="col33"'
        >>> s | cutdct(r'item="(?P<item>[^"]*)" count="(?P<i_count>[^"]*)" price="(?P<i_price>[^"]*)"') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [{'item': 'col1', 'i_price': 'col3', 'i_count': 'col2'},...
        {'item': 'col11', 'i_price': 'col33', 'i_count': 'col22'}]
    """
    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groupdict() if m else {}

class cutkv(cut):
    r""" Extract columns from a string or a list of strings through pattern capture

    This works like :class:`textops.cutdct` except it return a dict where the key is the one captured with the
    name given in parameter 'key_name', and where the value is the full dict of captured values.
    The interest is to merge informations into a bigger dict : see ``merge_dicts()``

    Args:
        sep (str or re.RegexObject): a regular expression string or object
            having *named* capture parenthesis
        key_name (str) : specify the named capture to use as the key for the returned dict
            Default value is 'key'

    Note:
        ``key_name=`` must be specified (not a positionnal parameter)

    Returns:
        A dict or a list of dict

    Examples:

        >>> s='item="col1" count="col2" price="col3"'
        >>> pattern=r'item="(?P<item>[^"]*)" count="(?P<i_count>[^"]*)" price="(?P<i_price>[^"]*)"'
        >>> s | cutkv(pattern,key_name='item')
        {'col1': {'item': 'col1', 'i_price': 'col3', 'i_count': 'col2'}}
        >>> s='item="col1" count="col2" price="col3"\nitem="col11" count="col22" price="col33"'
        >>> s | cutkv(pattern,key_name='item')                                                         # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [{'col1': {'item': 'col1', 'i_price': 'col3', 'i_count': 'col2'}},...
        {'col11': {'item': 'col11', 'i_price': 'col33', 'i_count': 'col22'}}]

    """
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