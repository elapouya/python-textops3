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
from functools import reduce

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
        <class 'str'>
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
        >>> print('OK' if state.matches(r'good|not_present|charging') else 'CRITICAL')
        OK
        >>> state=StrExt('looks like all is good')
        >>> print('OK' if state.matches(r'good|not_present|charging') else 'CRITICAL')
        CRITICAL
        >>> print('OK' if state.matches(r'.*(good|not_present|charging)') else 'CRITICAL')
        OK
        >>> state=StrExt('Error')
        >>> print('OK' if state.matches(r'good|not_present|charging') else 'CRITICAL')
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
        >>> print('OK' if state.searches(r'good|not_present|charging') else 'CRITICAL')
        OK
        >>> state=StrExt('looks like all is good')
        >>> print('OK' if state.searches(r'good|not_present|charging') else 'CRITICAL')
        OK
        >>> print('OK' if state.searches(r'.*(good|not_present|charging)') else 'CRITICAL')
        OK
        >>> state=StrExt('Error')
        >>> print('OK' if state.searches(r'good|not_present|charging') else 'CRITICAL')
        CRITICAL

    """
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
        return re.search(pattern,text,*args,**kwargs)



class StrOp(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if ( ( isinstance(text, str) and '\n' in text ) or
             (isinstance(text, bytes) and b'\n' in text) ):
            text = cls._tolist(text)
        if isinstance(text, (str,bytes)):
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

        default (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='col1 col2 col3'
        >>> s | cut()
        ['col1', 'col2', 'col3']
        >>> s | cut(col=1)
        'col2'
        >>> s | cut(col='1,2,10',default='N/A')
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
    sep_is_regex = False
    flags = 0

    @classmethod
    def split(cls, text, sep, maxsplit=-1,*args,**kwargs):
        return text.split(sep,maxsplit)

    @classmethod
    def fn(cls, text, sep=None, col=None, default='', *args,**kwargs):
        if cls.sep_is_regex:
            if isinstance(sep, str):
                sep = re.compile(sep,cls.flags)
        if isinstance(col, str):
            col = [int(i) for i in col.split(',')]
        if isinstance(col,(list,tuple)):
            nbcol = len(col)
            line_cols = cls.split(text,sep, *args,**kwargs)
            nblinecol = len(line_cols)
            return [ line_cols[c] if c < nblinecol else default for c in col ]
        else:
            line_cols = cls.split(text,sep, *args,**kwargs)
            if line_cols is None:
                return default
            nblinecol = len(line_cols)
            if col == None:
                return line_cols
            elif col < nblinecol:
                return line_cols[col]
            else:
                return default

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

        default (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='col1.1 | col1.2 | col1.3\ncol2.1 | col2.2 | col2.3'
        >>> print(s)
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
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, maxsplit=0, *args,**kwargs):
        return sep.split(text,maxsplit)

class cutca(cut):
    r""" Extract columns from a string or a list of strings through pattern capture

    This works like :class:`textops.cutre` except it needs a pattern having parenthesis to capture column.
    It uses :func:`re.match` for capture, this means the pattern must start at line beginning.

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

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutca(r'[^-]*-([^-]*)-[^=]*=([^=]*)=[^_]*_([^_]*)_')
        ['col1', 'col2', 'col3']
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cutca(r'[^-]*-([^-]*)-[^=]*=([^=]*)=[^_]*_([^_]*)_','0,2,4','not present')
        [['col1', 'col3', 'not present'], ['col11', 'col33', 'not present']]
    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        m = sep.match(text)
        return m.groups() if m else []

class cutm(cut):
    r""" Extract exactly one column by using :func:`re.match`

    It returns the matched pattern. Beware : the pattern must match the beginning of the line.
    One may use capture parenthesis to only return a part of the found pattern.

        * if the input is a simple string, :class:`textops.cutm` will return a strings
          representing the captured substring.
        * if the input is a list of strings or a string with newlines, :class:`textops.cutm` will
          return a list of captured substring.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutm(r'[^=]*=[^=]*=')
        '-col1- =col2='
        >>> s | cutm(r'=[^=]*=')
        ''
        >>> s | cutm(r'[^=]*=([^=]*)=')
        'col2'
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cutm(r'[^-]*-([^-]*)-')
        ['col1', 'col11']
        >>> s | cutm(r'[^-]*-(badpattern)-',default='-')
        ['-', '-']
    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        m = sep.match(text)
        if not m:
            return None
        g = m.groups()
        if not g:
            return m.group(0)
        return g[0]

class cutmi(cutm):
    r""" Extract exactly one column by using :func:`re.match` (case insensitive)

    This works like :class:`textops.cutm` except it is case insensitive.

        * if the input is a simple string, :class:`textops.cutmi` will return a strings
          representing the captured substring.
        * if the input is a list of strings or a string with newlines, :class:`textops.cutmi` will
          return a list of captured substring.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutm(r'.*(COL\d+)',default='no found')
        'no found'
        >>> s='-col1- =col2= _col3_'
        >>> s | cutmi(r'.*(COL\d+)',default='no found')  #as .* is the longest possible, only last column is extracted
        'col3'
    """
    flags = re.IGNORECASE

class cuts(cut):
    r""" Extract exactly one column by using :func:`re.search`

    This works like :class:`textops.cutm` except it searches the first occurence of the pattern in
    the string. One may use capture parenthesis to only return a part of the found pattern.

        * if the input is a simple string, :class:`textops.cuts` will return a strings
          representing the captured substring.
        * if the input is a list of strings or a string with newlines, :class:`textops.cuts` will
          return a list of captured substring.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cuts(r'_[^_]*_')
        '_col3_'
        >>> s | cuts(r'_([^_]*)_')
        'col3'
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cuts(r'_([^_]*)_')
        ['col3', 'col33']
    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        m = sep.search(text)
        if not m:
            return None
        g = m.groups()
        if not g:
            return m.group(0)
        return g[0]

class cutsi(cuts):
    r""" Extract exactly one column by using :func:`re.search` (case insensitive)

    This works like :class:`textops.cuts` except it is case insensitive.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cuts(r'_(COL[^_]*)_')
        ''
        >>> s='-col1- =col2= _col3_'
        >>> s | cutsi(r'_(COL[^_]*)_')
        'col3'
    """
    flags = re.IGNORECASE

class cutsa(cut):
    r""" Extract all columns having the specified pattern.

    It uses :func:`re.finditer` to find all occurences of the pattern.

        * if the input is a simple string, :class:`textops.cutfa` will return a list of found strings.
        * if the input is a list of strings or a string with newlines, :class:`textops.cutfa` will
          return a list of list of found string.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutsa(r'col\d+')
        ['col1', 'col2', 'col3']
        >>> s | cutsa(r'col(\d+)')
        ['1', '2', '3']
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cutsa(r'col\d+')
        [['col1', 'col2', 'col3'], ['col11', 'col22', 'col33']]
    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        cols=[]
        for m in sep.finditer(text):
            g = m.groups()
            cols.append(g[0] if g else m.group(0))
        return cols

class cutsai(cutsa):
    r""" Extract all columns having the specified pattern. (case insensitive)

    It works like :class:`textops.cutsa` but is case insensitive if the pattern is given as a string.

    Args:
        sep (str or re.RegexObject): a regular expression string or object having capture parenthesis
        col (int or list of int or str) : specify one or many columns you want to get back,
            You can specify :

            * an int as a single column number (starting with 0)
            * a list of int as the list of colmun
            * a string containing a comma separated list of int
            * None (default value) for all columns

        default (str): A string to display when requesting a column that does not exist

    Returns:
        a list of strings or a list of list of strings

    Examples:

        >>> s='-col1- =col2= _col3_'
        >>> s | cutsa(r'COL\d+')
        []
        >>> s | cutsai(r'COL\d+')
        ['col1', 'col2', 'col3']
        >>> s | cutsai(r'COL(\d+)')
        ['1', '2', '3']
        >>> s=['-col1- =col2= _col3_','-col11- =col22= _col33_']
        >>> s | cutsai(r'COL\d+')
        [['col1', 'col2', 'col3'], ['col11', 'col22', 'col33']]
    """
    flags = re.IGNORECASE

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

        default (str): A string to display when requesting a column that does not exist

    Returns:
        A string, a list of strings or a list of list of strings

    Examples:

        >>> s='item="col1" count="col2" price="col3"'
        >>> s | cutdct(r'item="(?P<item>[^"]*)" count="(?P<i_count>[^"]*)" price="(?P<i_price>[^"]*)"')
        {'item': 'col1', 'i_count': 'col2', 'i_price': 'col3'}
        >>> s='item="col1" count="col2" price="col3"\nitem="col11" count="col22" price="col33"'
        >>> s | cutdct(r'item="(?P<item>[^"]*)" count="(?P<i_count>[^"]*)" price="(?P<i_price>[^"]*)"') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [{'item': 'col1', 'i_count': 'col2', 'i_price': 'col3'},
        {'item': 'col11', 'i_count': 'col22', 'i_price': 'col33'}]
    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, *args,**kwargs):
        m = sep.match(text)
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
        {'col1': {'item': 'col1', 'i_count': 'col2', 'i_price': 'col3'}}
        >>> s='item="col1" count="col2" price="col3"\nitem="col11" count="col22" price="col33"'
        >>> s | cutkv(pattern,key_name='item')                                                         # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [{'col1': {'item': 'col1', 'i_count': 'col2', 'i_price': 'col3'}},
        {'col11': {'item': 'col11', 'i_count': 'col22', 'i_price': 'col33'}}]

    """
    sep_is_regex = True

    @classmethod
    def split(cls, text, sep, key_name = 'key', *args,**kwargs):
        # Use named 'key_name' parameter, not postionnal
        m = sep.match(text)
        if m:
            dct = m.groupdict()
            kv = dct.get(key_name)
            if kv:
                return { kv : dct }
        return {}