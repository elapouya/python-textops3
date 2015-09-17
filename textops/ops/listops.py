# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import re
import subprocess

class ListOpError(Exception):
    pass

class cat(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        with open(text) as fh:
            for line in fh:
                yield line

class run(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        if isinstance(text, basestring):
            p=subprocess.Popen(['sh','-c',text],stdout=subprocess.PIPE)
        else:
            p=subprocess.Popen(text,stdout=subprocess.PIPE)
        status = None
        while status is None:
            status=p.poll()
            if status is None:
                yield p.stdout.readline()

class grep(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,pattern,col_or_key = None, *args,**kwargs):
        regex = re.compile(pattern,cls.flags)
        for line in cls._tolist(text):
            try:
                if isinstance(line,basestring):
                    if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                        yield line
                elif col_or_key is None:
                    if bool(regex.search(str(line))) != cls.reverse:  # kind of XOR with cls.reverse
                        yield line
                else:
                    if bool(regex.search(line[col_or_key])) != cls.reverse:  # kind of XOR with cls.reverse
                        yield line
            except (ValueError, TypeError, IndexError, KeyError):
                pass

class grepi(grep): flags = re.IGNORECASE
class grepv(grep): reverse = True
class grepvi(grepv): flags = re.IGNORECASE

class grepc(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,pattern,col_or_key = None,*args,**kwargs):
        if text is None:
            return 0
        regex = re.compile(pattern,cls.flags)
        count = 0
        for line in cls._tolist(text):
            try:
                if isinstance(line,basestring):
                    if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
                elif col_or_key is None:
                    if bool(regex.search(str(line))) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
                else:
                    if bool(regex.search(line[col_or_key])) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
            except (ValueError, TypeError, IndexError, KeyError):
                pass
        return count

class grepci(grepc): flags = re.IGNORECASE
class grepcv(grepc): reverse = True
class grepcvi(grepcv): flags = re.IGNORECASE

class formatitems(TextOp):
    @classmethod
    def op(cls,items,format_str='{0} : {1}\n',*args,**kwargs):
        return ''.join([format_str.format(k,v) for k,v in items ])

class formatdicts(TextOp):
    @classmethod
    def op(cls,items,format_str='{key} : {val}\n',*args,**kwargs):
        return ''.join([format_str.format(**dct) for dct in items ])

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

class merge_dicts(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        out = {}
        for dct in cls._tolist(text):
            if isinstance(dct, dict):
                out.update(dct)
        return out