# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.2'

import os
import sys
import re
from inspect import isclass
from _multiprocessing import flags

class TextOp(object):    
    def __init__(self,*args,**kwargs):
        self.ops = [[self.__class__.__name__, args, kwargs]]
        self.op = None
        print self.ops[0]
    
    def __getattr__(self,attr):
        if not attr.startswith('_'):
            print 'op =',attr
            self.op = attr
        else:
            raise AttributeError()
        return self
    
    def __ror__(self,text):
        return self._process(text)
    
    def __call__(self,*args,**kwargs):
        if self.op:
            print 'op param =',args,kwargs
            self.ops.append([self.op, args, kwargs])
            self.op = None
            return self
        else:
            return self._process(args and args[0] or '')
        
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
                except TypeError:
                    print '*** you did not give the right number of parameters for %s()' % opcls.__name__
                    raise
                    
            else:
                text = getattr(text, op)(*args,**kwargs)
        return text

    def __repr__(self):
        rops = []
        for op,args,kwargs in self.ops:
            opargs = map(repr,args)
            opargs += [ '%s=%r' % (k,v) for k,v in kwargs.items() ]
            rops.append('%s(%s)' % (op,','.join(map(str,opargs))))
        return '.'.join(rops)
    
    @classmethod    
    def op(cls,text,*args,**kwargs):
        return text * 2
        
    @classmethod    
    def tolist(cls,text):
        print 'tolist text :',type(text)
        if not isinstance(text, basestring):
            return text
        return cls.splitlines(text)
    
    @classmethod    
    def splitlines(cls,text):
        prevnl = -1
        while True:
            nextnl = text.find('\n', prevnl + 1)
            if nextnl < 0: break
            yield text[prevnl + 1:nextnl]
            prevnl = nextnl
        yield text[prevnl + 1:]
      
    
def add_specials(cls):
    def make_method(name):
        def method(self, *args, **kw):
            print '__%s__' % name,args,kw
            text = self._process()
            return getattr(text, name)(*args, **kw)
        return method
    _special_names = [
        '__abs__', '__add__', '__and__', '__cmp__', '__coerce__', 
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__', 
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__', 
        '__getslice__', '__gt__', '__hash__', '__hex__', '__le__', '__len__', 
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', 
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__', 
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__', 
        '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__', 
        '__rmul__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', 
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', 
        '__truediv__', '__xor__',
    ]
    for n in _special_names:
        setattr(cls,n,make_method(n))
add_specials(TextOp)
        
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
        for line in cls.tolist(text):
            if regex.search(line):
                if not cls.reverse:
                    yield line
            else:
                if cls.reverse:
                    yield line

class grepi(grep):
    flags = re.IGNORECASE
class grepv(grep):
    reverse = True
class grepvi(grepv):    
    flags = re.IGNORECASE
                
class first(TextOp):                
    @classmethod    
    def op(cls,text,*args,**kwargs):
        print '*** first', args,kwargs
        for line in cls.tolist(text):
            return line
        return ''

class last(TextOp):                
    @classmethod    
    def op(cls,text,*args,**kwargs):
        print '*** last', args,kwargs
        last = ''
        for line in cls.tolist(text):
            last = line
        return last