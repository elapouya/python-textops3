# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

import os
import sys
import re
import types
import textops
from addicted import NoAttrDict, NoAttr
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)


logger = textops.logger

def activate_debug():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

class TextOp(object):
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

    def __ror__(self,text):
        return self._process(text)

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

    def _process(self,text=None):
        if text is None:
            args = self.ops[0][1]
            if args:
                text = args[0]
                self.ops[0][1] = []
                self.ops[0][2] = {}
        if self.debug:
            if isinstance(text, types.GeneratorType):
                text = list(text)
            logger.debug('=== TextOps : %r' % self)
            logger.debug(DebugText(text))
        for op,args,kwargs in self.ops:
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
            else:
                if isinstance(text,basestring):
                    text = object.__getattribute__(text,op)(*args, **kwargs)
                else:
                    text = self._apply_op_gen(text,op,*args, **kwargs)

        return extend_type(text)

    def _apply_op_gen(self, text, op, *args, **kwargs):
        for line in text:
            yield object.__getattribute__(line,op)(*args, **kwargs)

    def __repr__(self):
        rops = []
        for op,args,kwargs in self.ops:
            opargs = map(repr,args)
            opargs += [ '%s=%r' % (k,v) for k,v in kwargs.items() ]
            rops.append('%s(%s)' % (op,','.join(map(str,opargs))))
        return '.'.join(rops)

    @classmethod
    def make_gen(cls, text, return_if_none=None):
        if text is None:
            return return_if_none
        return cls._tolist(text)

    @property
    def g(self):
        text = self._process()
        return self.make_gen(text)

    @property
    def ge(self):
        text = self._process()
        return self.make_gen(text,[])

    @classmethod
    def make_list(cls, text, return_if_none=None):
        if text is None:
            return return_if_none
        elif isinstance(text, basestring):
            return text.splitlines()
        elif isinstance(text, types.GeneratorType):
            return ListExt(text)
        return text

    @property
    def l(self):
        text = self._process()
        return self.make_list(text)

    @property
    def le(self):
        text = self._process()
        return self.make_list(text,[])

    @classmethod
    def make_string(cls, text, return_if_none=None):
        if text is None:
            return return_if_none
        elif isinstance(text, (list,types.GeneratorType)):
            return StrExt(''.join(text))
        return StrExt(text)

    @property
    def s(self):
        text = self._process()
        return self.make_string(text)

    @property
    def se(self):
        text = self._process()
        return self.make_string(text,'')

    @classmethod
    def make_string_nl(cls, text, return_if_none=None):
        if text is None:
            return return_if_none
        elif isinstance(text, (list,types.GeneratorType)):
            return StrExt('\n'.join(text))
        return StrExt(text)

    @property
    def snl(self):
        text = self._process()
        return self.make_string_nl(text)

    @property
    def senl(self):
        text = self._process()
        return self.make_string_nl(text,'')

    @classmethod
    def make_int(cls, text):
        try:
            return int(float(text))
        except (ValueError, TypeError):
            return 0

    @property
    def i(self):
        text = self._process()
        return self.make_int(text)

    @classmethod
    def make_float(cls, text):
        try:
            return float(text)
        except (ValueError, TypeError):
            return 0.0

    @property
    def f(self):
        text = self._process()
        return self.make_float(text)

    @property
    def r(self):
        return self._process()

    @property
    def pp(self):
        text = self._process()
        return pp.pformat(text)

    @classmethod
    def op(cls,text,*args,**kwargs):
        return cls.fn(text)

    @classmethod
    def _tolist(cls,text):
        if isinstance(text, dict):
            return text.iteritems()
        if not isinstance(text, basestring):
            return text
        return str.splitlines(text)

    @classmethod
    def _tostr(cls,text):
        if not isinstance(text, basestring):
            return '\n'.join(text)
        return text

def extend_type(obj):
    if isinstance(obj,unicode):
        if not isinstance(obj,UnicodeExt):
            return UnicodeExt(obj)
    elif isinstance(obj,basestring):
        if not isinstance(obj,StrExt):
            return StrExt(obj)
    elif isinstance(obj,(list,tuple)):
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

def set_debug(flag):
    logger.setLevel(flag and logging.DEBUG or logging.CRITICAL)

class WrapOpIter(TextOp):
    # fn=<to be defined in child class>
    @classmethod
    def op(cls, text,*args,**kwargs):
        return cls.fn(cls._tolist(text), *args,**kwargs)

class WrapOpYield(TextOp):
    # fn=<to be defined in child class>
    @classmethod
    def op(cls, text,*args,**kwargs):
        for line in cls.fn(cls._tolist(text), *args,**kwargs):
            yield line

def add_textop(func):
    setattr(textops.ops,func.__name__,type(func.__name__,(TextOp,), {'fn':staticmethod(func)}))
    return func

def add_textop_iter(func):
    setattr(textops.ops,func.__name__,type(func.__name__,(WrapOpIter,), {'fn':staticmethod(func)}))
    return func

def add_textop_yield(func):
    setattr(textops.ops,func.__name__,type(func.__name__,(WrapOpYield,), {'fn':staticmethod(func)}))
    return func

class DebugText(object):
    def __init__(self,text,nblines=20,more_msg='...'):
        self.text = text
        self.nblines = nblines
        self.more_msg = more_msg
    def __repr__(self):
        if isinstance(self.text,basestring):
            nbchars = self.nblines * 80
            if len(self.text) > nbchars:
                return self.text[:nbchars] + self.more_msg
            else:
                return self.text
        out = '['
        for i,line in enumerate(self.text):
            if i == self.nblines:
                logger.debug(self.more_msg)
                break
            out += '%s,\n' % line
        out += ']'
        return out

def get_attribute_or_textop(obj,name):
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
            def fn(*args,**kwargs):
                return map(lambda s:getattr(str, name)(s,*args,**kwargs),obj)

    if not callable(fn):
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

class UnicodeExt(unicode):
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        return ListExt([self])
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__getitem__(*args, **kwargs))
    def __add__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__add__(*args, **kwargs))
    def __mul__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__mul__(*args, **kwargs))
    def __rmul__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__rmul__(*args, **kwargs))
    def __mod__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__mod__(*args, **kwargs))
    def __rmod__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__rmod__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(UnicodeExt, self).__format__(*args, **kwargs))

class StrExt(str):
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
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

class ListExt(list):
    def __getattribute__(self, name):
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        return self
    def __getslice__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__getslice__(*args, **kwargs))
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(ListExt, self).__getitem__(*args, **kwargs))
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

class ListExtIterator(object):
    def __init__(self, obj):
        self.obj = obj
        self.index = -1
        self.len = len(obj)
    def __iter__(self):
        return self
    def next(self):
        self.index += 1
        if self.index < self.len:
            # Will call extend_type() because __getitem__ do it :
            return self.obj[self.index]
        else:
            raise StopIteration

class DictExt(NoAttrDict):
    def __getattribute__(self, name):
        if dict.has_key(self,name):
            return self[name]
        return get_attribute_or_textop(self,name)
    @property
    def as_list(self):
        return ListExt([self])
    def __getitem__(self,*args, **kwargs):
        return extend_type(super(DictExt, self).__getitem__(*args, **kwargs))
    def __format__(self,*args, **kwargs):
        return extend_type(super(DictExt, self).__format__(*args, **kwargs))

