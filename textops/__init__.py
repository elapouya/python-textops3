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
    
    def __getattr__(self,attr):
        print 'op =',attr
        self.op = attr
        return self
    
    def __ror__(self,text):
        return self._process(text)
    
    def __call__(self,*args,**kwargs):
        if self.op:            
            print 'op param =',args,kwargs
            self.ops.append((self.op, args, kwargs))
            self.op = None
            return self
        else:
            return self._process(args[0])
        
    def _process(self,text):
        print 'processing...'
        for op,args,kwargs in self.ops:
            text = getattr(text, op)(*args,**args)
        return text    

    def __iter__(self):
        print '__iter__'
        return iter(['my iter'])
    
    def __unicode__(self):
        print '__unicode__'
        return 'unicode'    
        
    def __str__(self):
        print '__str__'
        return '__str__'    
        
    def __int__(self):
        print '__int__'
        return '__int__'    
        
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
        return 23    