# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This modules provides casting features, that is to force the output type """

from textops import TextOp, pp, stru
import dateutil.parser
from slugify import slugify

class tostr(TextOp):
    r""" Convert the result to a string

    | If the input text is a list or a generator, it will join all the lines with a newline.
    | If the input text is None, None is NOT converted to a string : None is returned

    Args:
        join_str (str): the join string to apply on list or generator (Default : newline)
        return_if_none (str): the object to return if the input text is None (Default : None)

    Returns:
        str or None: converted result as a string

    Examples:

        >>> 'line1\nline2' | tostr()
        'line1\nline2'
        >>> ['line1','line2'] | tostr()
        'line1\nline2'
        >>> ['line1','line2'] | tostr('---')
        'line1---line2'
        >>> def g(): yield 'hello';yield 'world'
        ...
        >>> g()|tostr()
        'hello\nworld'
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

    Args:
        join_str (str): the join string to apply on list or generator (Default : newline)
        return_if_none (str): the object to return if the input text is None (Default : empty string)

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
    r""" Convert the result to a list

    | If the input text is a string, it is put in a list.
    | If the input text is a list : nothing is done.
    | If the input text is a generator : it is converted into a list

    Args:
        return_if_none (str): the object to return if the input text is None (Default : None)

    Returns:
        str: converted result as a string

    Examples:
        >>> 'hello' | tolist()
        ['hello']
        >>> ['hello','world'] | tolist()
        ['hello', 'world']
        >>> type(None|tolist())
        <type 'NoneType'>
        >>> def g(): yield 'hello'
        ...
        >>> g()|tolist()
        ['hello']
    """
    @classmethod
    def fn(cls, text, return_if_none=None,*args,**kwargs):
        return TextOp.make_list(text,return_if_none)

class toliste(TextOp):
    r""" Convert the result to a list

    | If the input text is a string, it is put in a list.
    | If the input text is a list : nothing is done.
    | If the input text is a generator : it is converted into a list

    Args:
        return_if_none (str): the object to return if the input text is None (Default : empty list)

    Returns:
        str: converted result as a string

    Examples:
        >>> 'hello' | toliste()
        ['hello']
        >>> type(None|toliste())
        <class 'textops.base.ListExt'>
        >>> None|toliste()
        []
    """
    @classmethod
    def fn(cls, text, return_if_none=[],*args,**kwargs):
        return TextOp.make_list(text,return_if_none)

class toint(TextOp):
    r""" Convert the result to an integer

    Returns:
        str or list: converted result as an int or list of int

    Examples:
        >>> '53' | toint()
        53
        >>> 'not an int' | toint()
        0
        >>> '3.14' | toint()
        3
        >>> '3e3' | toint()
        3000
        >>> ['53','not an int','3.14'] | toint()
        [53, 0, 3]
    """
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return TextOp.make_int(text)

class tofloat(TextOp):
    r""" Convert the result to a float

    Returns:
        str or list: converted result as an int or list of int

    Examples:
        >>> '53' | tofloat()
        53.0
        >>> 'not a float' | tofloat()
        0.0
        >>> '3.14' | tofloat()
        3.14
        >>> '3e3' | tofloat()
        3000.0
        >>> ['53','not an int','3.14'] | tofloat()
        [53.0, 0.0, 3.14]
    """
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return TextOp.make_float(text)

class todatetime(TextOp):
    r""" Convert the result to a datetime python object

    Returns:
        datetime: converted result as a datetime python object

    Examples:
        >>> '2015-10-28' | todatetime()
        datetime.datetime(2015, 10, 28, 0, 0)
        >>> '2015-10-28 22:33:00' | todatetime()
        datetime.datetime(2015, 10, 28, 22, 33)
        >>> '2015-10-28 22:33:44' | todatetime()
        datetime.datetime(2015, 10, 28, 22, 33, 44)
        >>> '2014-07-08T09:02:21.377' | todatetime()
        datetime.datetime(2014, 7, 8, 9, 2, 21, 377000)
        >>> '28-10-2015' | todatetime()
        datetime.datetime(2015, 10, 28, 0, 0)
        >>> '10-28-2015' | todatetime()
        datetime.datetime(2015, 10, 28, 0, 0)
        >>> '10-11-2015' | todatetime()
        datetime.datetime(2015, 10, 11, 0, 0)
    """
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return dateutil.parser.parse(text)

class toslug(TextOp):
    r""" Convert a string to a slug

    Returns:
        str: a slug

    Examples:
        >>> 'this is my article' | toslug()
        'this-is-my-article'
        >>> 'this%%% is### my___article' | toslug()
        'this-is-my-article'
    """
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return slugify(text)

class todict(TextOp):
    r"""Converts list or 2 items-tuples into dict
    
    Returns:
        dict: Converted result as a dict

    Examples:
        
    >>> [ ('a',1), ('b',2), ('c',3) ] | echo().todict()
    {'a': 1, 'c': 3, 'b': 2}
    """         
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return TextOp.make_dict(text)


class tonull(TextOp):
    r"""Consume generator if any and then return nothing (aka None)

    Examples:

    >>> [ 1,2,3 ] | echo().tonull()

    """
    @classmethod
    def fn(cls, text, *args, **kwargs):
        TextOp.consume(text)

class pretty(TextOp):
    r"""Pretty format the input text
    
    Returns:
        str: Converted result as a pretty string ( uses :meth:`pprint.PrettyPrinter.pformat` )

    Examples:
        
    >>> s = '''
    ... a:val1
    ... b:
    ...     c:val3
    ...     d:
    ...         e ... : val5
    ...         f ... :val6
    ...     g:val7
    ... f: val8'''
    >>> print s | parse_indented()
    {'a': 'val1', 'b': {'c': 'val3', 'd': {'e': 'val5', 'f': 'val6'}, 'g': 'val7'}, 'f': 'val8'}
    >>> print s | parse_indented().pretty()
    {   'a': 'val1',
        'b': {   'c': 'val3', 'd': {   'e': 'val5', 'f': 'val6'}, 'g': 'val7'},
        'f': 'val8'}
    """         
    @classmethod
    def fn(cls, text,*args,**kwargs):
        return pp.pformat(text)
