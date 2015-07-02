# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.3'

import os
import sys
import re
from inspect import isclass

class TextOp(object):
    def __init__(self,*args,**kwargs):
        self.ops = [[self.__class__.__name__, args, kwargs]]
        self.op = None
        print self.ops[0]

    def __getattr__(self,attr):
        if not attr.startswith('_'):
            self.ops.append([attr, (), {}])
            print 'op =',attr
            self.op = attr
        else:
            raise AttributeError()
        return self

    def __ror__(self,text):
        return self._process(text)

    def __iter__(self):
        return iter(self.g)

    def __call__(self,*args,**kwargs):
        if self.op:
            print 'op param =',args,kwargs
            self.ops[-1][1] = args
            self.ops[-1][2] = kwargs
            self.op = None
            return self
        else:
            return self._process(args and args[0] or None)

    def _process(self,text=None):
        print 'processing...'
        if text is None:
            args = self.ops[0][1]
            if args:
                text = args[0]
        for op,args,kwargs in self.ops:
            print '%%%',op,args,kwargs
            opcls = globals().get(op)
            print '°°°',opcls,type(opcls)
            if isclass(opcls) and issubclass(opcls, TextOp):
                try:
                    text = opcls.op(text, *args, **kwargs)
                    if text is None:
                         return text
                except TypeError:
                    print '*** you did not give the right number of parameters for %s()' % opcls.__name__
                    raise

            else:
                print '*** TextOp "%s" does not exist.' % op
        return text

    def __repr__(self):
        rops = []
        for op,args,kwargs in self.ops:
            opargs = map(repr,args)
            opargs += [ '%s=%r' % (k,v) for k,v in kwargs.items() ]
            rops.append('%s(%s)' % (op,','.join(map(str,opargs))))
        return '.'.join(rops)

    @property
    def gen(self):
        return self._tolist(self._process())

    @property
    def list(self):
        text = self._process()
        if isinstance(text, basestring):
            return text.splitlines()
        elif not isinstance(text, list):
            return list(text)
        return text

    @property
    def str(self):
        text = self._process()
        if isinstance(text, basestring):
            return text
        elif not isinstance(text, list):
            return '\n'.join(list(text))
        return '\n'.join(text)

    @property
    def int(self):
        text = self._process()
        try:
            return int(text)
        except ValueError:
            return 0

    @property
    def float(self):
        text = self._process()
        try:
            return float(text)
        except ValueError:
            return 0.0

    @classmethod
    def op(cls,text,*args,**kwargs):
        return text * 2

    @classmethod
    def _tolist(cls,text):
        print 'tolist text :',type(text)
        if not isinstance(text, basestring):
            return text
        return cls._splitlines(text)

    @classmethod
    def _splitlines(cls,text):
        prevnl = -1
        while True:
            nextnl = text.find('\n', prevnl + 1)
            if nextnl < 0: break
            yield text[prevnl + 1:nextnl]
            prevnl = nextnl
        yield text[prevnl + 1:]


class length(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        print '*** length'
        return len(text)

class grep(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
        print '*** grep', args,kwargs
        regex = re.compile(pattern,cls.flags)
        for line in cls._tolist(text):
            if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                yield line

class grepi(grep): flags = re.IGNORECASE
class grepv(grep): reverse = True
class grepvi(grepv): flags = re.IGNORECASE

class grepc(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
        print '*** grepc', args,kwargs
        regex = re.compile(pattern,cls.flags)
        count = 0
        for line in cls._tolist(text):
            if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                count += 1
        return count

class grepci(grepc): flags = re.IGNORECASE
class grepcv(grepc): reverse = True
class grepcvi(grepcv): flags = re.IGNORECASE


class first(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        print '*** first', args,kwargs
        for line in cls._tolist(text):
            return line
        return ''

class last(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        print '*** last', args,kwargs
        last = ''
        for line in cls._tolist(text):
            last = line
        return last

class gcat(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        print '*** gcat', args,kwargs
        with open(text) as fh:
            for line in fh:
                yield line

class cat(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        return open(text).read()

class StrOp(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, basestring):
            return cls.fn(text,*args,**kwargs)
        elif isinstance(text, list):
            return [ cls.fn(line,*args,**kwargs) for line in text ]
        return cls.gop(text)
    def gop(cls,text):
        for line in text:
            yield cls.fn(line,*args,**kwargs)

class upper(StrOp): fn = str.upper
class lower(StrOp): fn = str.lower
class capitalize(StrOp): fn = str.capitalize
class replace(StrOp): fn = str.replace
class expandtabs(StrOp): fn = str.expandtabs
class split(StrOp): fn = str.split
class strip(StrOp): fn = str.strip




