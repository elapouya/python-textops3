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
        return self.process(text)
    
    def __call__(self,*args,**kwargs):
        if self.op:            
            print 'op param =',args,kwargs
            self.ops.append((self.op, args, kwargs))
            self.op = None
            return self
        else:
            return self.process(args[0])
        
    def process(self,text):
        print 'processing...'
        for op in self.ops:
            print op