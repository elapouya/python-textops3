# -*- coding: utf-8 -*-
'''
Created : 2015-04-03

@author: Eric Lapouyade
'''

from textops import TextOp
import re
import subprocess
import sys
import os

class ListOpError(Exception):
    pass

class cat(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        for path in cls._tolist(text):
            if os.path.isfile(path) or os.path.islink(path):
                with open(path) as fh:
                    for line in fh:
                        yield line.rstrip('\r\n')

class run(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        for cmd in cls._tolist(text):
            if isinstance(text, basestring):
                p=subprocess.Popen(['sh','-c',cmd],stdout=subprocess.PIPE)
            else:
                p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
            while p.returncode is None:
                (stdout, stderr) = p.communicate()
                for line in stdout.splitlines():
                    yield line

class grep(TextOp):
    flags = 0
    reverse = False
    pattern = ''
    @classmethod
    def op(cls,text,pattern=None,col_or_key = None, *args,**kwargs):
        if pattern is None:
            pattern = cls.pattern
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
    pattern = ''
    exit_on_found = False
    @classmethod
    def op(cls,text,pattern=None,col_or_key = None,*args,**kwargs):
        if text is None:
            return 0
        if pattern is None:
            pattern = cls.pattern
        regex = re.compile(pattern,cls.flags)
        count = 0
        for line in cls._tolist(text):
            try:
                if isinstance(line,basestring):
                    if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
                        if cls.exit_on_found:
                            break
                elif col_or_key is None:
                    if bool(regex.search(str(line))) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
                        if cls.exit_on_found:
                            break
                else:
                    if bool(regex.search(line[col_or_key])) != cls.reverse:  # kind of XOR with cls.reverse
                        count += 1
                        if cls.exit_on_found:
                            break
            except (ValueError, TypeError, IndexError, KeyError):
                pass
        if cls.exit_on_found:
            return bool(count)
        return count

class grepci(grepc): flags = re.IGNORECASE
class grepcv(grepc): reverse = True
class grepcvi(grepcv): flags = re.IGNORECASE

class haspattern(grepc): exit_on_found = True
class haspatterni(haspattern): flags = re.IGNORECASE

class rmblank(grepv): pattern = r'^\s*$'

class formatitems(TextOp):
    @classmethod
    def op(cls,items,format_str='{0} : {1}\n',join_str = '', *args,**kwargs):
        return join_str.join([format_str.format(k,v) for k,v in items ])

class formatdicts(TextOp):
    @classmethod
    def op(cls,items,format_str='{key} : {val}\n',join_str = '',*args,**kwargs):
        return join_str.join([format_str.format(**dct) for dct in items ])

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
    boundaries = False
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
    def op(cls, text, begin, end, get_begin=None, get_end=None,*args,**kwargs):
        if get_begin is None:
            get_begin = cls.boundaries
        if get_end is None:
            get_end = cls.boundaries
        begin = cls._build_regex_list(begin)
        end = cls._build_regex_list(end)

        state = 0 if begin else 1

        for line in cls._tolist(text):
            if state == 0 and begin:
                if begin[0].search(line):
                    begin.pop(0)
                if not begin:
                    if get_begin:
                        yield line
                    state = 1
            elif state == 1 and end:
                if end[0].search(line):
                    end.pop(0)
                if not end:
                    if get_end:
                        yield line
                    break
                else:
                    yield line
            else:
                yield line

class betweeni(between): flags = re.IGNORECASE
class betweenb(between): boundaries = True
class betweenbi(betweenb): flags = re.IGNORECASE

class range(TextOp):
    flags = 0

    @classmethod
    def op(cls, text, begin, end, *args,**kwargs):
        state = 0

        for line in cls._tolist(text):
            if line >= begin and line < end:
                yield line

class before(between):
    @classmethod
    def op(cls, text, pattern, get_end=False,*args,**kwargs):
        return between.op(text,None,pattern,get_end=get_end)

class beforei(before): flags = re.IGNORECASE

class after(between):
    @classmethod
    def op(cls, text, pattern, get_begin=False,*args,**kwargs):
        return between.op(text,pattern,None,get_begin=get_begin)

class afteri(after): flags = re.IGNORECASE

class mapfn(TextOp):
    @classmethod
    def op(cls, text, map_fn, *args,**kwargs):
        for line in cls._tolist(text):
            yield map_fn(line)

class iffn(TextOp):
    @classmethod
    def op(cls, text, filter_fn=None, *args,**kwargs):
        if filter_fn is None:
            filter_fn = lambda x:x
        for line in cls._tolist(text):
            if filter_fn(line):
                yield line

class mapif(TextOp):
    @classmethod
    def op(cls, text, map_fn, filter_fn=None,*args,**kwargs):
        if filter_fn is None:
            filter_fn = lambda x:x
        for line in cls._tolist(text):
            if filter_fn(line):
                yield map_fn(line)

class doreduce(TextOp):
    @classmethod
    def op(cls, text, reduce_fn, *args, **kwargs):
        return reduce(reduce_fn, cls._tolist(text))

class merge_dicts(TextOp):
    @classmethod
    def op(cls,text,*args,**kwargs):
        out = {}
        for dct in cls._tolist(text):
            if isinstance(dct, dict):
                out.update(dct)
        return out

class span(TextOp):
    @classmethod
    def op(cls, text, nbcols, fill_str='', *args,**kwargs):
        fill_list = [fill_str] * nbcols
        for sublist in cls._tolist(text):
            yield (sublist+fill_list)[:nbcols]

class slice(TextOp):
    @classmethod
    def op(cls, text, begin=0, end=sys.maxsize, step = 1, fill_str=None, *args,**kwargs):
        for sublist in cls._tolist(text):
            yield sublist[begin:end:step]

class subitem(TextOp):
    @classmethod
    def op(cls, text, n, *args,**kwargs):
        for sublist in cls._tolist(text):
            yield sublist[n]

class subitems(TextOp):
    @classmethod
    def op(cls, text, ntab, *args,**kwargs):
        if isinstance(ntab,basestring):
            ntab = [ int(n) for n in ntab.split(',') ]
        for sublist in cls._tolist(text):
            yield [ sublist[n] for n in ntab ]

class uniq(TextOp):
    @classmethod
    def op(cls, text, *args,**kwargs):
        s=[]
        for line in cls._tolist(text):
            if line not in s:
                s.append(line)
                yield line
