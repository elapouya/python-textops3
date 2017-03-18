# -*- coding: utf-8 -*-
#
# Created : 2015-08-14
#
# @author: Eric Lapouyade
#

""" This module gathers text operations that are wrapped from standard python functions """

from textops import TextOp, WrapOp, WrapOpStr, WrapOpIter
import re

class dosort(WrapOpIter):
    r"""Sort input text

    Return a new sorted list from the input text. The sorting is done on a by-line/list item basis.

    Args:
        cmp(callable): specifies a custom comparison function of two arguments (iterable elements)
            which should return a negative, zero or positive number depending on whether the first
            argument is considered smaller than, equal to, or larger than the second argument, ex:
            ``cmp=lambda x,y: cmp(x.lower(), y.lower())``. The default value is None.
        key(callable): specifies a function of one argument that is used to extract a comparison key
            from each list element, ex: ``key=str.lower``.
            The default value is None (compare the elements directly).
        reverse(bool): If set to True, then the list elements are sorted as if each comparison
            were reversed.

    Returns:
        generator: The sorted input text

    Examples:
        >>> 'a\nd\nc\nb' | dosort().tolist()
        ['a', 'b', 'c', 'd']
        >>> 'a\nd\nc\nb' >> dosort()
        ['a', 'b', 'c', 'd']
        >>> 'a\nd\nc\nb' >> dosort(reverse=True)
        ['d', 'c', 'b', 'a']
        >>> 'a\nB\nc' >> dosort()
        ['B', 'a', 'c']
        >>> 'a\nB\nc' >> dosort(cmp=lambda x,y:cmp(x.lower(),y.lower()))
        ['a', 'B', 'c']
        >>> [('a',3),('c',1),('b',2)] >> dosort()
        [('a', 3), ('b', 2), ('c', 1)]
        >>> [('a',3),('c',1),('b',2)] >> dosort(key=lambda x:x[1])
        [('c', 1), ('b', 2), ('a', 3)]
        >>> [{'k':3},{'k':1},{'k':2}] >> dosort(key=lambda x:x['k'])
        [{'k': 1}, {'k': 2}, {'k': 3}]
    """
    fn=sorted

class doreverse(WrapOpIter):
    r"""reverse input text

    Return a new reversed list from the input text. This is done on a by-line/list item basis.

    Returns:
        generator: The reversed input text

    Examples:
        >>> list(['a','b','c','d'] | doreverse())
        ['d', 'c', 'b', 'a']
    """
    fn=reversed

class getmax(WrapOpIter):
    r"""get the max value

    Return the largest item/line from the input.

    Args:
        key(callable): specifies a function of one argument that is used to extract a comparison key
            from each list element, ex: ``key=str.lower``.

    Returns:
        object: The largest item/line

    Examples:
        >>> 'E\nc\na' | getmax()
        'c'
        >>> 'E\nc\na' >> getmax()
        'c'
        >>> 'E\nc\na' >> getmax(key=str.lower)
        'E'
    """
    fn=max

class getmin(WrapOpIter):
    r"""get the min value

    Return the smallest item/line from the input.

    Args:
        key(callable): specifies a function of one argument that is used to extract a comparison key
            from each list element, ex: ``key=str.lower``.

    Returns:
        object: The smallest item/line

    Examples:
        >>> 'c\nE\na' | getmin()
        'E'
        >>> 'c\nE\na' >> getmin()
        'E'
        >>> 'c\nE\na' >> getmin(key=str.lower)
        'a'
    """
    fn=min

class alltrue(WrapOpIter):
    r"""Return True if all elements of the input are true

    Returns:
        bool: True if all elements of the input are true

    Examples:
        >>> '\n\n' | alltrue()
        False
        >>> 'a\n\n' | alltrue()
        False
        >>> 'a\nb\n' | alltrue()
        True
        >>> 'a\nb\nc' | alltrue()
        True
        >>> ['',''] >> alltrue()
        False
        >>> ['1','2'] >> alltrue()
        True
        >>> [True,False] >> alltrue()
        False
        >>> [True,True] >> alltrue()
        True
    """
    fn=all

class anytrue(WrapOpIter):
    r"""Return True if any element of the input is true

    Returns:
        bool: True if any element of the input is true

    Examples:
        >>> '\n\n' | anytrue()
        False
        >>> 'a\n\n' | anytrue()
        True
        >>> 'a\nb\n' | anytrue()
        True
        >>> 'a\nb\nc' | anytrue()
        True
        >>> [0,0] >> anytrue()
        False
        >>> [0,1] >> anytrue()
        True
        >>> [1,2] >> anytrue()
        True
        >>> [False,False] >> anytrue()
        False
        >>> [True,False] >> anytrue()
        True
        >>> [True,True] >> anytrue()
        True
    """
    fn=any

class linenbr(WrapOpIter):
    r"""Enumerate input text lines

    add a column to the input text with the line number within.

    Args:
        start(int): starting number (default : 0)

    Returns:
        generator: input text with line numbering

    Examples:
        >>> 'a\nb\nc' >> linenbr()
        [(0, 'a'), (1, 'b'), (2, 'c')]
        >>> 'a\nb\nc' | linenbr(1).tolist()
        [(1, 'a'), (2, 'b'), (3, 'c')]
    """
    fn=enumerate

class resub(WrapOpStr):
    r"""Substitute a regular expression within a string or a list of strings

    It uses :func:`re.sub` to replace the input text.

    Args:
        pattern (str): Split string by the occurrences of pattern
        repl (str): Replacement string. 
        count (int): the maximum number of pattern occurrences to be replaced
        flags (int): regular expression flags (re.I etc...). Only available in Python 2.7+    

    Returns:
        str or list: The replaced text

    Examples:
        >>> 'Words, words, words.' | resub('[Ww]ords','Mots')
        'Mots, Mots, Mots.'
        >>> ['Words1 words2', 'words', 'words.' ] >> resub('[Ww]ords','Mots',1)
        ['Mots1 words2', 'Mots', 'Mots.']
    """
    input_argn = 2
    fn = staticmethod(re.sub)
    