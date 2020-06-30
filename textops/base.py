# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
"""This module defines base classes for python-textops3"""

import os
import sys
import re
import types
import textops
from addicted import NoAttrDict, NoAttr
import string
import logging
import pprint
import chardet
from collections import Callable, abc
pp = pprint.PrettyPrinter(indent=4)


logger = textops.logger

def activate_debug():
    """Activate debug logging on console

    This function is useful when playing with python-textops3 through a python console.
    It is not recommended to use this function in a real application : use standard logging
    functions instead.
    """
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

class TextOpException(Exception):
    pass

class TextOp(object):
    """Base class for text operations

    All operations must be derived from this class. Subclasses must redefine an ``op()`` method
    that will be called when the operations will be triggered by an input text.
    """
    def __init__(self,*args,**kwargs):
        self.ops = [[self.__class__.__name__, args, kwargs]]
        self.op = None
        self.debug = kwargs.get('debug',False)

    def __getattr__(self,attr):
        if not attr.startswith('_'):
            self.ops.append([attr, (), {}])
            self.op = attr
        else:
            raise AttributeError()
        return self

    def __or__(self,other):
        if not isinstance(other,TextOp):
            raise TextOpException('Please use "|" only between two TextOp or AFTER a string or a list')
        self.ops += other.ops
        return self

    def __ror__(self,text):
        return self._process(text, piped=True)

    def __rrshift__(self,text):
        result = self._process(text, piped=True)
        if isinstance(result, (types.GeneratorType,enumerate)):
            return ListExt(result)
        return result

    def __rshift__(self,other):
        if not isinstance(other,TextOp):
            raise TextOpException('Please use ">>" only between two TextOp or AFTER a string or a list')
        self.ops += other.ops
        return self

    def __str__(self):
        return self.se

    def __iter__(self):
        return iter(self.g)

    def __int__(self):
        return iter(self.i)

    def __float__(self):
        return iter(self.f)

    def __call__(self,*args,**kwargs):
        if self.op:
            self.ops[-1][1] = args
            self.ops[-1][2] = kwargs
            self.op = None
            return self
        else:
            return self._process(args and args[0] or None)

    def _process(self,text=None, piped=False):
        input_text = text
        if self.debug:
            if isinstance(text, types.GeneratorType):
                text = list(text)
            logger.debug('=== TextOps : %r' % self)
            logger.debug(DebugText(text))
        for i,(op,args,kwargs) in enumerate(self.ops):
            if not piped and not i and not input_text and args:
                text = args[0]
                args = args[1:]
            opcls = getattr(textops.ops,op,None)
            if isinstance(opcls,type) and issubclass(opcls, TextOp):
                try:
                    text = opcls.op(text, *args, **kwargs)
                    if self.debug:
                        if isinstance(text, types.GeneratorType):
                            text = list(text)
                        logger.debug('--- Op : %s(%s,%s)',op,args,kwargs)
                        logger.debug(DebugText(text))
                    if text is None:
                         return text
                except TypeError:
                    logger.error('*** bad parameters for %s()' % opcls.__name__)
                    raise
            elif hasattr(text,op):
                text = getattr(text,op)(*args, **kwargs)
            else:
                extext = extend_type(text)
                if hasattr(extext,op):
                    text = getattr(extext,op)(*args, **kwargs)
                elif isinstance(text, (types.GeneratorType,enumerate,list)):
                    text = self._apply_op_gen(text,op,*args, **kwargs)
                else:
                    raise TextOpException('Unknown OP "%s"' % op)

        return extend_type(text)

    def _apply_op_gen(self, text, op, *args, **kwargs):
        for line in text:
            if hasattr(line,op):
                yield getattr(line,op)(*args, **kwargs)
            else:
                extext = extend_type(text)
                if hasattr(extext,op):
                    yield getattr(extext,op)(*args, **kwargs)
                else:
                    raise TextOpException('Unknown OP "%s"' % op)

    def __repr__(self):
        rops = []
        for op,args,kwargs in self.ops:
            opargs = [ '%r' % v if isinstance(v,(str,int,float)) else v for v in args ]
            opargs += [ '%s=%r' % (k,v) for k,v in list(kwargs.items()) ]
            rops.append('%s(%s)' % (op,','.join(map(str,opargs))))
        return '.'.join(rops)

    @classmethod
    def make_gen(cls, text, return_if_none=None):
        if text in [None,NoAttr]:
            return return_if_none
        return cls._tolist(text)

    @property
    def g(self):
        r"""Execute operations, return a generator when possible or a list otherwise

        This is to be used ONLY when the input text has be set as the first argument of the first
        operation.

        Examples:

            >>> echo('hello')
            echo('hello')
            >>> echo('hello').g
            ['hello']
            >>> def mygen(): yield 'hello'
            >>> cut(mygen(),'l')                                # doctest: +ELLIPSIS
            cut(<generator object mygen at ...>,'l')
            >>> cut(mygen(),'l').g                              # doctest: +ELLIPSIS
            <generator object extend_type_gen at ...>
            >>> def mygen(): yield None
            >>> type(echo(None).g)                              # doctest: +ELLIPSIS
            <class 'NoneType'>
        """
        text = self._process()
        return self.make_gen(text)

    @property
    def ge(self):
        r"""Execute operations, return a generator when possible or a list otherwise,
        ( [] if the result is None ).

        This works like :attr:`g` except it returns an empty list if the execution
        result is None.

        Examples:

            >>> echo(None).ge                                    # doctest: +ELLIPSIS
            []
        """
        text = self._process()
        return self.make_gen(text,[])

    @classmethod
    def make_list(cls, text, return_if_none=None):
        if text in [None,NoAttr]:
            return return_if_none
        elif isinstance(text, str):
            return text.splitlines()
        elif isinstance(text, (types.GeneratorType, enumerate)):
            return ListExt(text)
        elif isinstance(text, (int, float)):
            return ListExt([text])
        return text

    @property
    def l(self):
        r"""Execute operations, return a list

        This is to be used ONLY when the input text has be set as the first argument of the first
        operation.

        Examples:

            >>> echo('hello')
            echo('hello')
            >>> echo('hello').l
            ['hello']
            >>> type(echo(None).g)
            <class 'NoneType'>
        """
        text = self._process()
        return self.make_list(text)

    @property
    def le(self):
        r"""Execute operations, returns a list ( [] if the result is None ).

        This works like :attr:`l` except it returns an empty list if the execution
        result is None.

        Examples:

            >>> echo(None).le
            []
        """
        text = self._process()
        return self.make_list(text,[])

    @classmethod
    def make_string(cls, text, join_str='\n', return_if_none=None):
        if text in [None,NoAttr]:
            return return_if_none
        elif isinstance(text, (list,types.GeneratorType,abc.ItemsView,abc.KeysView,abc.ValuesView)):
            return StrExt(join_str.join([ stru(item) for item in text ]))
        return StrExt(text)

    @property
    def s(self):
        r"""Execute operations, return a string (join = newline)

        This is to be used ONLY when the input text has be set as the first argument of the first
        operation. If the result is a list or a generator, it is converted into a string by joinning
        items with a newline.

        Examples:

            >>> echo('hello')
            echo('hello')
            >>> echo('hello').s
            'hello'
            >>> echo(['hello','world']).s
            'hello\nworld'
            >>> type(echo(None).s)
            <class 'NoneType'>
        """
        text = self._process()
        return self.make_string(text)

    @property
    def se(self):
        r"""Execute operations, returns a string ( '' if the result is None ).

        This works like :attr:`s` except it returns an empty string if the execution
        result is None.

        Examples:

            >>> echo(None).se
            ''
        """
        text = self._process()
        return self.make_string(text,return_if_none='')

    @property
    def j(self):
        r"""Execute operations, return a string (join = '')

        This works like :attr:`s` except that joins will be done with an empty string

        Examples:

            >>> echo(['hello','world']).j
            'helloworld'
            >>> type(echo(None).j)
            <class 'NoneType'>
        """
        text = self._process()
        return self.make_string(text,join_str='')

    @property
    def je(self):
        r"""Execute operations, returns a string ( '' if the result is None, join='').

        This works like :attr:`j` except it returns an empty string if the execution
        result is None.

        Examples:

            >>> echo(None).je
            ''
        """
        text = self._process()
        return self.make_string(text,join_str='',return_if_none='')

    @classmethod
    def make_int(cls, text):
        def _to_int(text):
            try:
                return int(float(text))
            except (ValueError, TypeError):
                return 0
        if isinstance(text, str):
            return _to_int(text)
        elif isinstance(text,(list,tuple)):
            return list(map(_to_int,text))
        return text

    @property
    def i(self):
        r"""Execute operations, returns an int.

        Examples:

            >>> echo('1789').i
            1789
            >>> echo('3.14').i
            3
            >>> echo('Tea for 2').i
            0
        """
        text = self._process()
        return self.make_int(text)

    @classmethod
    def make_float(cls, text):
        def _to_float(text):
            try:
                return float(text)
            except (ValueError, TypeError):
                return 0.0
        if isinstance(text, str):
            return _to_float(text)
        elif isinstance(text, (list,tuple)):
            return list(map(_to_float,text))
        return text

    @property
    def f(self):
        r"""Execute operations, returns a float.

        Examples:

            >>> echo('1789').f
            1789.0
            >>> echo('3.14').f
            3.14
            >>> echo('Tea for 2').f
            0.0
        """
        text = self._process()
        return self.make_float(text)

    @property
    def r(self):
        r"""Execute operations, do not convert.

        Examples:

            >>> echo('1789').length().l
            [4]
            >>> echo('1789').length().s
            '4'
            >>> echo('1789').length().r
            4
        """
        return self._process()

    @classmethod
    def consume(cls, text):
        if isinstance(text, types.GeneratorType):
            for i in text:
                pass

    @property
    def n(self):
        r"""Execute operations, do not convert, do not return anything

        If _process() returns a generator, it is consumed

        Examples:

            >>> echo('1789').length().n

        """
        text = self._process()
        self.consume(text)

    @property
    def pp(self):
        r"""Execute operations, return Prettyprint version of the result

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
        >>> print(parse_indented(s).r)
        {'a': 'val1', 'b': {'c': 'val3', 'd': {'e': 'val5', 'f': 'val6'}, 'g': 'val7'}, 'f': 'val8'}
        >>> print(parse_indented(s).pp)
        {   'a': 'val1',
            'b': {'c': 'val3', 'd': {'e': 'val5', 'f': 'val6'}, 'g': 'val7'},
            'f': 'val8'}
        """
        text = self._process()
        return pp.pformat(text)

    @classmethod
    def op(cls,text,*args,**kwargs):
        """ This method must be overriden in derived classes """
        return cls.fn(text,*args,**kwargs)

    @classmethod
    def _tolist(cls,text):
        if isinstance(text, str):
            return str.splitlines(text)
        elif isinstance(text, bytes):
            return bytes.splitlines(text)
        elif isinstance(text, dict):
            return iter(text.items())
        elif isinstance(text, (int,float)):
            return [text]
        return text

    @classmethod
    def _tosublist(cls,text):
        if isinstance(text, str):
            return [ [line] for line in str.splitlines(text) ]
        elif isinstance(text, bytes):
            return [ [line] for line in bytes.splitlines(text) ]
        elif isinstance(text, (int,float,dict)):
            return [[text]]
        elif isinstance(text, list) and (not text or not isinstance(text[0],list)):
            return [text]
        return text

    @classmethod
    def _tostr(cls,text):
        if not isinstance(text, str):
            return '\n'.join(text)
        return text

    @classmethod
    def make_dict(cls, text):
        return DictExt(text)

    def __len__(self):
        text = self._process()
        if isinstance(text, types.GeneratorType):
            return sum(1 for x in text)
        return len(text)

    def __getitem__(self, item):
        lst = self.l
        return lst.__getitem__(item)

def extend_type(obj):
    if isinstance(obj,bytes):
        if not isinstance(obj,BytesExt):
            return BytesExt(obj)
    elif isinstance(obj,str):
        if not isinstance(obj,StrExt):
            return StrExt(obj)
    elif isinstance(obj, tuple):
        if not isinstance(obj, TupleExt):
            return TupleExt(obj)  # mandatory to have pickle working on DictExt
    elif isinstance(obj,(list,abc.ItemsView,abc.KeysView,abc.ValuesView)):
        if not isinstance(obj,ListExt):
            return ListExt(obj)
    elif isinstance(obj,dict):
        if not isinstance(obj,DictExt):
            return DictExt(obj)
    elif isinstance(obj,types.GeneratorType):
        return extend_type_gen(obj)
    return obj

def extend_type_gen(obj):
    for i in obj:
        yield extend_type(i)

def stru(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8','replace')
    else:
        text = str(text)
    return text

def set_debug(flag):
    """ Change debug level

    It sets logger level to DEBUG if flag is True, otherwise to CRITICAL (no log at all)
    """
    logger.setLevel(flag and logging.DEBUG or logging.CRITICAL)

class WrapOp(TextOp):
    input_argn = 0
    # fn=<to be defined in child class>
    @classmethod
    def op(cls, text, *args,**kwargs):
        args = list(args)
        args.insert(cls.input_argn,text)
        return cls.fn(*args,**kwargs)

class WrapOpStr(TextOp):
    input_argn = 0
    # fn=<to be defined in child class>
    @classmethod
    def op(cls, text, *args,**kwargs):
        args = list(args)
        if isinstance(text, str):
            args.insert(cls.input_argn,text)
            return cls.fn(*args,**kwargs)
        else:
            return wrap_op_str_gen(text, cls.fn, cls.input_argn, args, kwargs)

def wrap_op_str_gen(text, fn, argn, args, kwargs):
    args.insert(argn,None)
    for line in text:
        args[argn] = line
        yield fn(*args,**kwargs)

class WrapOpIter(TextOp):
    input_argn = 0
    # fn=<to be defined in child class>
    @classmethod
    def op(cls, text,*args,**kwargs):
        args = list(args)
        args.insert(cls.input_argn,cls._tolist(text))
        return cls.fn(*args,**kwargs)

def add_textop(class_or_func):
    """Decorator to declare custom function or custom class as a new textops op

    the custom function/class will receive the whole raw input text at once.

    Examples:

        >>> @add_textop
        ... def repeat(text, n, *args,**kwargs):
        ...     return text * n
        >>> 'hello' | repeat(3)
        'hellohellohello'

        >>> @add_textop
        ... class cool(TextOp):
        ...     @classmethod
        ...     def op(cls, text, *args,**kwargs):
        ...         return text + ' is cool.'
        >>> 'textops' | cool()
        'textops is cool.'
    """
    if isinstance(class_or_func,type):
        op = class_or_func
    else:
        op = type(class_or_func.__name__,(TextOp,), {'fn':staticmethod(class_or_func)})

    setattr(textops.ops,class_or_func.__name__,op)
    return op

def add_textop_iter(func):
    r"""Decorator to declare custom *ITER* function as a new textops op

    An *ITER* function is a function that will receive the input text as a *LIST* of lines.
    One have to iterate over this list and generate a result (it can be a list, a generator,
    a dict, a string, an int ...)

    Examples:

        >>> @add_textop_iter
        ... def odd(lines, *args,**kwargs):
        ...     for i,line in enumerate(lines):
        ...         if not i % 2:
        ...             yield line
        >>> s = '''line 1
        ... line 2
        ... line 3'''
        >>> s >> odd()
        ['line 1', 'line 3']
        >>> s | odd().tolist()
        ['line 1', 'line 3']

        >>> @add_textop_iter
        ... def sumsize(lines, *args,**kwargs):
        ...     sum = 0
        ...     for line in lines:
        ...         sum += int(re.search(r'\d+',line).group(0))
        ...     return sum
        >>> '''1492 file1
        ... 1789 file2
        ... 2015 file3''' | sumsize()
        5296
    """
    op = type(func.__name__,(WrapOpIter,), {'fn':staticmethod(func)})
    setattr(textops.ops,func.__name__,op)
    return op

class DebugText(object):
    def __init__(self,text,nblines=20,more_msg='...'):
        self.text = text
        self.nblines = nblines
        self.more_msg = more_msg
    def __repr__(self):
        if isinstance(self.text, str):
            lines = str.splitlines(self.text)
            begin,sep,end = '','',''
        elif isinstance(self.text, str):
            lines = str.splitlines(self.text)
            begin,sep,end = '','',''
        elif isinstance(self.text, dict):
            lines = [ '%s : %s' % item for item in self.text.items() ]
            begin,sep,end = '{',',','}'
        elif isinstance(self.text,(types.GeneratorType,list)):
            lines = self.text
            begin,sep,end = '[',',',']'
        else:
            lines = [repr(self.text)]
            begin,sep,end = '','',''

        out = begin
        for i,line in enumerate(lines):
            if i:
                out += '\n'
            if i == self.nblines:
                out += '%s\n' % self.more_msg
                break
            out += '%s%s' % (line[:120],sep)
        out += end
        return out

def get_attribute_or_textop(obj,name):
    if name.startswith('__'):
        return object.__getattribute__(obj,name)
    op_cls = getattr(textops.ops,name,None)
    if op_cls and isinstance(op_cls,type) and issubclass(op_cls,TextOp):
        def fn(*args,**kwargs):
            debug = kwargs.get('debug',False)
            if debug:
                logger.debug('='*60)
                logger.debug('Before %s(%s,%s):', name,args, kwargs)
                logger.debug('%s', DebugText(obj))
            result = op_cls.op(obj,*args,**kwargs)
            if debug:
                logger.debug('-'*60)
                logger.debug('After %s(%s,%s):', name,args, kwargs)
                logger.debug('%s', DebugText(result))
            return result
    else:
        try:
            fn = object.__getattribute__(obj,name)
        except AttributeError:
            if isinstance(obj,DictExt):
                return NoAttr
            elif isinstance(obj,(StrExt,BytesExt)):
                raise
            def fn(*args,**kwargs):
                return [getattr(str if isinstance(s,str) else str, name)(s,*args,**kwargs) for s in obj]

    if not isinstance(fn, Callable):
        return fn

    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except:
            logger.error('*** Error when calling %s(%s,%s)' % (fn.__name__,args, kwargs))
            raise
        if isinstance(result,types.GeneratorType):
            result = list(result)
        return extend_type(result)
    return wrapper

class BytesExt(bytes):
    """Extend bytes class to gain access to textops as attributes

    Examples:

        >>> b'normal bytes'.cut()
        Traceback (most recent call last):
            ...
        AttributeError: 'bytes' object has no attribute 'cut'

        >>> BytesExt(b'extended bytes').cut()
        [b'extended', b'bytes']
    """
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        """ Convert to ListExt object """
        return ListExt([self])
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__getitem__(*args, **kwargs))
    def __add__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__add__(*args, **kwargs))
    def __mul__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__mul__(*args, **kwargs))
    def __rmul__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__rmul__(*args, **kwargs))
    def __mod__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__mod__(*args, **kwargs))
    def __rmod__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__rmod__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(BytesExt, self).__format__(*args, **kwargs))
    def _ipython_display_(self):
        print(self.__repr__())

class StrExt(str):
    """Extend str class to gain access to textops as attributes

    Examples:

        >>> 'normal string'.cut()
        Traceback (most recent call last):
            ...
        AttributeError: 'str' object has no attribute 'cut'

        >>> StrExt('extended string').cut()
        ['extended', 'string']
    """
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        """ Convert to ListExt object """
        return ListExt([self])
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__getitem__(*args, **kwargs))
    def __add__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__add__(*args, **kwargs))
    def __mul__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__mul__(*args, **kwargs))
    def __rmul__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__rmul__(*args, **kwargs))
    def __mod__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__mod__(*args, **kwargs))
    def __rmod__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__rmod__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(StrExt, self).__format__(*args, **kwargs))
    def _ipython_display_(self):
        print(self.__repr__())


class TupleExt(tuple):
    """Extend tuple class to gain access to textops as attributes

    In addition, all tuple items are extended on-the-fly when accessed

    Examples:

        >>> ('normal','list').grep('t')
        Traceback (most recent call last):
            ...
        AttributeError: 'tuple' object has no attribute 'grep'

        >>> TupleExt(('extended','list')).grep('t')
        ['extended', 'list']

        Note: grep() returns a list
    """
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_tuple(self):
        """ Convert to TupleExt object """
        return self
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,key,*args, **kwargs):
        try:
            return extend_type(super().__getitem__(key,*args, **kwargs))
        except IndexError:
            return NoAttr
    def __add__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__add__(*args, **kwargs))
    def __mul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__mul__(*args, **kwargs))
    def __iadd__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__iadd__(*args, **kwargs))
    def __imul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__imul__(*args, **kwargs))
    def __rmul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__rmul__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__format__(*args, **kwargs))
    def __iter__(self):
        return TupleExtIterator(self)
    def _ipython_display_(self):
        print(self.__repr__())

class TupleExtIterator(object):
    def __init__(self, obj):
        self.obj = obj
        self.index = -1
        self.len = len(obj)

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index < self.len:
            # Will call extend_type() because __getitem__ do it :
            return self.obj[self.index]
        else:
            raise StopIteration


class ListExt(list):
    """Extend list class to gain access to textops as attributes

    In addition, all list items (dict, list, str, bytes) are extended on-the-fly when accessed

    Examples:

        >>> ['normal','list'].grep('t')
        Traceback (most recent call last):
            ...
        AttributeError: 'list' object has no attribute 'grep'

        >>> ListExt(['extended','list']).grep('t')
        ['extended', 'list']
    """
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        """ Convert to ListExt object """
        return self
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,key,*args, **kwargs):
        try:
            return extend_type(super(ListExt, self).__getitem__(key,*args, **kwargs))
        except IndexError:
            return NoAttr
    def __add__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__add__(*args, **kwargs))
    def __mul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__mul__(*args, **kwargs))
    def __iadd__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__iadd__(*args, **kwargs))
    def __imul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__imul__(*args, **kwargs))
    def __rmul__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__rmul__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__format__(*args, **kwargs))
    def __iter__(self):
        return ListExtIterator(self)
    def _ipython_display_(self):
        print(self.__repr__())

class ListExtIterator(object):
    def __init__(self, obj):
        self.obj = obj
        self.index = -1
        self.len = len(obj)
    def __iter__(self):
        return self
    def __next__(self):
        self.index += 1
        if self.index < self.len:
            # Will call extend_type() because __getitem__ do it :
            return self.obj[self.index]
        else:
            raise StopIteration

class DictExt(NoAttrDict):
    """Extend dict class with new features

    New features are :

        * Access to textops operations with attribute notation
        * All dict values (dict, list, str, bytes) are extended on-the-fly when accessed
        * Access to dict values with attribute notation
        * Add a key:value in the dict with attribute notation (one level at a time)
        * Returns NoAttr object when a key is not in the Dict
        * add modification on-the-fly :meth:`amend` and rendering to string :meth:`render`

    Note:

        ``NoAttr`` is a special object that returns always ``NoAttr`` when accessing to any attribute.
        it behaves like ``False`` for testing, ``[]`` in foor-loops. The goal is to be able
        to use very long expression with dotted notation without being afraid to get an exception.

    Examples:

        >>> {'a':1,'b':2}.items().grep('a')
        Traceback (most recent call last):
            ...
        AttributeError: 'dict_items' object has no attribute 'grep'

        >>> DictExt({'a':1,'b':2}).items().grep('a')
        [('a', 1)]

        >>> d = DictExt({ 'this' : { 'is' : { 'a' : {'very deep' : { 'dict' : 'yes it is'}}}}})
        >>> print(d.this['is'].a['very deep'].dict)
        yes it is
        >>> d.not_a_valid_key
        NoAttr
        >>> d['not_a_valid_key']
        NoAttr
        >>> d.not_a_valid_key.and_i.can.put.things.after.without.exception
        NoAttr
        >>> for obj in d.not_a_valid_key.objects:
        ...     do_things(obj)
        ... else:
        ...     print('no object')
        no object

        >>> d = DictExt()
        >>> d.a = DictExt()
        >>> d.a.b = 'this is my logging data'
        >>> print(d)
        {'a': {'b': 'this is my logging data'}}

        >>> d = { 'mykey' : 'myval' }
        >>> d['mykey']
        'myval'
        >>> type(d['mykey'])
        <class 'str'>
        >>> d = DictExt(d)
        >>> d['mykey']
        'myval'
        >>> type(d['mykey'])
        <class 'textops.base.StrExt'>

        >>> d=DictExt()
        >>> d[0]=[]
        >>> d
        {0: []}
        >>> d[0].append(3)
        >>> d
        {0: [3]}
        >>> type(d[0])
        <class 'textops.base.ListExt'>

    """
    def __getattribute__(self, name):
        if dict.__contains__(self,name):
            return dict.__getitem__(self,name)
        return get_attribute_or_textop(self,name)

    @property
    def as_list(self):
        """ Convert to ListExt object """
        return ListExt([self])

    def amend(self,*args, **kwargs):
        """ Modify on-the-fly a dictionary

        The method will generate a new extended dictionary and update it with given params

        Examples:

            >>> s = '''soft:textops
            ... count:32591'''
            >>> s | parse_indented()
            {'soft': 'textops', 'count': '32591'}
            >>> s | parse_indented().amend(date='2015-11-19')
            {'soft': 'textops', 'count': '32591', 'date': '2015-11-19'}
        """
        return DictExt(self,*args, **kwargs)
    def render(self,format_string,defvalue='-'):
        """ Render a DictExt as a string

        It uses the fonction :func:`dformat` to format the dictionary

        Args:
            format_string (str): Same format string as for :meth:`str.format`
            defvalue (str or callable): the default value to display when the data is not in the dict

        Examples:

            >>> d = DictExt({'count': '32591', 'date': '2015-11-19', 'soft': 'textops'})
            >>> d.render('On {date}, "{soft}" has been downloaded {count} times')
            'On 2015-11-19, "textops" has been downloaded 32591 times'
            >>> d.render('On {date}, "{not_in_dict}" has been downloaded {count} times','?')
            'On 2015-11-19, "?" has been downloaded 32591 times'
        """
        return dformat(format_string,self,defvalue)
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(DictExt, self).__getitem__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(DictExt, self).__format__(*args, **kwargs))

class DefaultDict(dict):
    def __init__(self,defvalue,*args,**kwargs):
        self.defvalue = defvalue
        super(DefaultDict,self).__init__(*args,**kwargs)
    def __getitem__(self,key):
        try:
            return super(DefaultDict,self).__getitem__(key)
        except KeyError:
            if isinstance(self.defvalue, Callable):
                return self.defvalue(key)
            return self.defvalue

class DefaultList(list):
    def __init__(self,defvalue,*args,**kwargs):
        self.defvalue = defvalue
        super(DefaultList,self).__init__(*args,**kwargs)
    def __getitem__(self,key):
        try:
            return super(DefaultList,self).__getitem__(key)
        except IndexError:
            if isinstance(self.defvalue, Callable):
                return self.defvalue(key)
            return self.defvalue

def dictmerge(*dict_args):
    """Merge as many dicts you want

    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    Args:
        *dict_args (dict): List of dicts

    Returns:
        dict: a new merged dict

    Examples:

        >>> dictmerge({'a':1,'b':2},{'b':3,'c':4})
        {'a': 1, 'b': 3, 'c': 4}

    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

string_formatter = string.Formatter()
vformat = string_formatter.vformat

def dformat(format_str,dct,defvalue='-'):
    """ Formats a dictionary, manages unkown keys

    It works like :meth:`string.Formatter.vformat` except that it accepts only a dict
    for values and a defvalue for not matching keys. Defvalue can be a callable that will
    receive the requested key as argument and return a string

    Args:
        format_string (str): Same format string as for :meth:`str.format`
        dct (dict) : the dict to format
        defvalue (str or callable): the default value to display when the data is not in the dict

    Examples:

        >>> d = {'count': '32591', 'soft': 'textops'}
        >>> dformat('{soft} : {count} dowloads',d)
        'textops : 32591 dowloads'
        >>> dformat('{software} : {count} dowloads',d,'N/A')
        'N/A : 32591 dowloads'
        >>> dformat('{software} : {count} dowloads',d,lambda k:'unknown_tag_%s' % k)
        'unknown_tag_software : 32591 dowloads'
    """
    return vformat(format_str,(),DefaultDict(defvalue,dct))

def eformat(format_str,lst,dct,defvalue='-'):
    """ Formats a list and a dictionary, manages unkown keys

    It works like :meth:`string.Formatter.vformat` except that it accepts a defvalue for not matching keys.
    Defvalue can be a callable that will receive the requested key as argument and return a string

    Args:
        format_string (str): Same format string as for :meth:`str.format`
        lst (dict) : the list to format
        dct (dict) : the dict to format
        defvalue (str or callable): the default value to display when the data is not in the dict

    Examples:

        >>> d = {'count': '32591', 'soft': 'textops'}
        >>> l = ['Eric','Guido']
        >>> eformat('{0} => {soft} : {count} dowloads',l,d)
        'Eric => textops : 32591 dowloads'
        >>> eformat('{2} => {software} : {count} dowloads',l,d,'N/A')
        'N/A => N/A : 32591 dowloads'
        >>> eformat('{2} => {software} : {count} dowloads',l,d,lambda k:'unknown_tag_%s' % k)
        'unknown_tag_2 => unknown_tag_software : 32591 dowloads'
    """
    return vformat(format_str,DefaultList(defvalue,lst),DefaultDict(defvalue,dct))


def decode_bytes(byte_string, encoding=None):
    """Returns a decoded string from a byte string.
    It can test several encodings, will try to detect encoding if it does not
    work and have a ascii/'replace' fallback.
    One can give standard python3 string, in which case, no action is done

    Args:

        byte_string (bytes): string to decode to python3 standard string
        encoding (str, list, tuple): ending(s) to use. if a list/tuple is given,
            will use the first that does not raise exception
            default : 'utf-8'

    Examples:

        >>> b = 'éric'.encode('utf-16')
        >>> print(b.hex())
        fffee900720069006300
        >>> decode_bytes(b)
        'éric'
        >>> decode_bytes(b,'utf-16')
        'éric'
        >>> decode_bytes(b,('utf-16','utf-32'))
        'éric'

    Returns:

        a python3 standard string
    """
    if not isinstance(byte_string, bytes):
        return byte_string
    if not encoding:
        encoding = ('utf-8',)
    if isinstance(encoding, str):
        encoding = (encoding,)
    for enc in encoding:
        try:
            s = byte_string.decode(enc)
            return s
        except UnicodeDecodeError:
            pass
    # If given encoding does not work try to detect it :
    detected_encoding = chardet.detect(byte_string)
    if detected_encoding['confidence'] >= 0.5:
        try:
            s = byte_string.decode(detected_encoding['encoding'])
            return s
        except UnicodeDecodeError:
            pass
    # Fallback : ascii + replace unkown chars
    s = byte_string.decode('ascii','replace')
    return s


# NoAttr.as_list must return an empty ListExt() not a simple list
# This customize noattr module for textops.
from noattr import NoAttrType
def _as_list(self):
    return ListExt()
NoAttrType.as_list=property(_as_list)
