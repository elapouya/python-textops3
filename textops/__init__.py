# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

__version__ = '0.0.4'

import os
import sys
import re
from inspect import isclass

class TextOp(object):
    def __init__(self,*args,**kwargs):
        self.ops = [[self.__class__.__name__, args, kwargs]]
        self.op = None

    def __getattr__(self,attr):
        if not attr.startswith('_') and attr in globals():
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
        for op,args,kwargs in self.ops:
            opcls = globals().get(op)
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
        elif not isinstance(text, list):
            return list(text)
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
        elif isinstance(text, basestring):
            return text
        elif not isinstance(text, list):
            return '\n'.join(list(text))
        return '\n'.join(text)

    @property
    def s(self):
        text = self._process()
        return self.make_string(text)

    @property
    def se(self):
        text = self._process()
        return self.make_string(text,'')

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

    @classmethod
    def op(cls,text,*args,**kwargs):
        return cls.fn(text)

    @classmethod
    def _tolist(cls,text):
        if not isinstance(text, basestring):
            return text
        return text.splitlines()

class tostr(TextOp): fn = TextOp.make_string
class tostre(TextOp): fn = classmethod(lambda cls,text: TextOp.make_string(text,''))
class tolist(TextOp): fn = TextOp.make_list
class toliste(TextOp): fn = classmethod(lambda cls,text: TextOp.make_list(text,[]))
class toint(TextOp): fn = TextOp.make_int
class tofloat(TextOp): fn = TextOp.make_float
class length(TextOp): fn = classmethod(lambda cls,text: len(text))
class echo(TextOp): fn = classmethod(lambda cls,text: text)

class cat(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        with open(text) as fh:
            for line in fh:
                yield line.rstrip('\r\n')

class catq(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        try:
            with open(text) as fh:
                for line in fh:
                    yield line.rstrip('\r\n')
        except (IOError,TypeError):
            pass

class cats(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        return open(text).read()

class catsq(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        try:
            return open(text).read()
        except (IOError,TypeError):
            return None

class grep(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,pattern,*args,**kwargs):
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
        if text is None:
            return 0
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
        for line in cls._tolist(text):
            return line
        return ''

class last(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        last = ''
        for line in cls._tolist(text):
            last = line
        return last

class head(TextOp):
    @classmethod
    def op(cls,text,lines,*args,**kwargs):
        for i,line in enumerate(cls._tolist(text)):
            if i >= lines:
                break
            yield line

class tail(TextOp):
    @classmethod
    def op(cls,text,lines,*args,**kwargs):
        buffer = []
        for line in cls._tolist(text):
            buffer.append(line)
            if len(buffer) > lines:
                buffer.pop(0)
        for line in buffer:
            yield line

class sed(TextOp):
    flags = 0
    @classmethod
    def op(cls,text,pat,repl,*args,**kwargs):
        if isinstance(pat, basestring):
            pat = re.compile(pat,cls.flags)
        for line in cls._tolist(text):
            yield pat.sub(repl,line)

class sedi(sed): flags = re.IGNORECASE

class between(TextOp):
    flags = 0
    @classmethod
    def _build_regex_list(cls,string_or_list):
        if string_or_list is None:
            return []
        elif isinstance(string_or_list, basestring):
            lst = [string_or_list]
        else:
            lst = list(string_or_list)
        return [ re.compile(pat,cls.flags) if isinstance(pat, basestring) else pat for pat in lst ]

    @classmethod
    def op(cls, text, begin, end, get_begin=False, get_end=False,*args,**kwargs):
        begin = cls._build_regex_list(begin)
        end = cls._build_regex_list(end)

        state = 0 if begin else 1

        for line in cls._tolist(text):
            if state == 0:
                if begin[0].search(line):
                    begin.pop(0)
                if not begin:
                    if get_begin:
                        yield line
                    state = 1
            elif state == 1:
                if end[0].search(line):
                    end.pop(0)
                if not end:
                    if get_end:
                        yield line
                    break
                else:
                    yield line

class betweeni(between): flags = re.IGNORECASE

class cut(TextOp):
    @classmethod
    def split(cls, text, sep):
        return text.split(sep)

    @classmethod
    def op(cls, text, col, sep=None, not_present_value='', *args,**kwargs):
        if isinstance(col,(list,tuple)):
            nbcol = len(col)
            for line in cls._tolist(text):
                line_cols = cls.split(line,sep)
                nblinecol = len(line_cols)
                yield [ line_cols[c] if c < nblinecol else not_present_value for c in col ]
        else:
            for line in cls._tolist(text):
                line_cols = cls.split(line,sep)
                nblinecol = len(line_cols)
                if col < nblinecol:
                    yield line_cols[col]
                else:
                    yield not_present_value

class cutre(cut):
    @classmethod
    def split(cls, text, sep):
        if hasattr(sep,'match'):
            return sep.split(text)
        return re.split(sep,text)

class cutca(cut):
    @classmethod
    def split(cls, text, sep):
        if hasattr(sep,'match'):
            m = sep.match(text)
        else:
            m = re.match(sep,text)
        return m.groups() if m else []

class StrOp(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, basestring):
            return cls.fn(text,*args,**kwargs)
        elif isinstance(text, list):
            return [ cls.fn(line,*args,**kwargs) for line in text ]
        return cls.gop(text,*args,**kwargs)
    @classmethod
    def gop(cls,text,*args,**kwargs):
        for line in text:
            yield cls.fn(line,*args,**kwargs)

class upper(StrOp): fn = str.upper
class lower(StrOp): fn = str.lower
class capitalize(StrOp): fn = str.capitalize
class replace(StrOp): fn = str.replace
class expandtabs(StrOp): fn = str.expandtabs
class split(StrOp): fn = str.split
class strip(StrOp): fn = str.strip



