# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.2'

import os
import sys
import re

class TextOp(object):
    
    def __init__(self,*args,**kwargs):
        self.ops = [(self.__class__.__name__, args, kwargs)]
        self.op = None
        self.text = args and args[0] or ''
        print self.ops[0]
    
    def __getattr__(self,attr):
        if not attr.startswith('_'):
            print 'op =',attr
            self.op = attr
        else:
            raise AttributeError()
        return self
    
    def __ror__(self,text):
        self.text = text
        return self._process()
    
    def __call__(self,*args,**kwargs):
        if self.op:
            print 'op param =',args,kwargs
            self.ops.append((self.op, args, kwargs))
            self.op = None
            return self
        else:
            if args or kwargs:
                self.ops[0][1] = args
                self.ops[0][2] = kwargs
            self._process()
            return self.text
        
    @staticmethod    
    def op(text,*args,**kwargs):
        return text
        
    def _process(self):
        print 'processing...'
        for op,args,kwargs in self.ops:
            print '%%%',op,args,kwargs
            opcls = globals().get(op)
            print '°°°',opcls
            if issubclass(opcls, TextOp):
                self.text = opcls.op(self.text, *args, **kwargs)
            else:
                self.text = getattr(self.text, op)(*args,**kwargs)

    def __iter__(self):
        print '__iter__'
        self._process()
        return iter(self.text)
    
    def __unicode__(self):
        print '__unicode__'
        return 'unicode'    
        
    def __str__(self):
        print '__str__'
        self._process()
        return self.text    
        
    def __int__(self):
        print '__int__'
        self._process()
        return int(self.text)

    def __repr__(self):
        print '__repr__'
        return '__repr__'    
        
    def __add__(self,obj):
        print '__add__'
        return '__add__'    
        
    def __radd__(self,o):
        print '__radd__'
        return '__radd__'    
        
    def __iadd__(self,o):
        print '__iadd__'
        return '__iadd__'    
        
    def __mul__(self,o):
        print '__mul__'
        return '__mul__'    
        
    def __rmul__(self,o):
        print '__rmul__'
        return '__rmul__'    
        
    def __imul__(self,o):
        print '__imul__'
        return '__imul__'    
        
    def __len__(self):
        print '__len__'
        self._process()
        return len(self.text)    

class length(TextOp):    
    @staticmethod    
    def op(text,*args,**kwargs):
        print '*** length'
        return len(text)
    