# -*- coding: utf-8 -*-
'''
Created : 2015-08-24

@author: Eric Lapouyade
'''

from textops import TextOp, NoAttr
import textops
import string
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
import copy
from datetime import datetime

class ParsingError(Exception):
    pass

class mgrep(TextOp):
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,patterns_dict,col_or_key = None, *args,**kwargs):
        for k,pattern in patterns_dict.items():
            if isinstance(pattern,basestring):
                patterns_dict[k] = re.compile(pattern,cls.flags)
        dct = {}
        for line in cls._tolist(text):
            for k,regex in patterns_dict.items():
                try:
                    if isinstance(line,basestring):
                        if bool(regex.search(line)) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                    elif col_or_key is None:
                        if bool(regex.search(str(line))) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                    else:
                        if bool(regex.search(line[col_or_key])) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                except (ValueError, TypeError, IndexError, KeyError):
                    pass
        return dct

class mgrepi(mgrep): flags = re.IGNORECASE
class mgrepv(mgrep): reverse = True
class mgrepvi(mgrepv): flags = re.IGNORECASE

class parseg(TextOp):
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, *args,**kwargs):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if cls.ignore_case else 0)
        out = []
        for line in cls._tolist(text):
            m = pattern.match(line)
            if m:
                out.append(m.groupdict())
        return out

class parsegi(parseg): ignore_case = True

class parsek(TextOp):
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, key_name = 'key', key_update = None, *args,**kwargs):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if cls.ignore_case else 0)
        out = []
        for line in cls._tolist(text):
            m = pattern.match(line)
            if m:
                dct = m.groupdict()
                key = dct.get(key_name)
                if key:
                    if key_update:
                        key = key_update(key)
                    out.append(key)
        return out

class parseki(parsek): ignore_case = True

class parsekv(TextOp):
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, key_name = 'key', key_update = None, *args,**kwargs):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.I if cls.ignore_case else 0)
        out = {}
        for line in cls._tolist(text):
            m = pattern.match(line)
            if m:
                dct = m.groupdict()
                key = dct.get(key_name)
                if key:
                    if key_update is None:
                        key_norm = re.sub(r'\s+','_',key.strip())
                    else:
                        key_norm = key_update(key)
                    out.update({ key_norm : dct })
        return out

class parsekvi(parsekv): ignore_case = True

class find_pattern(TextOp):
    ignore_case = False

    @classmethod
    def op(cls,text, pattern, *args,**kwargs):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern, re.M | (re.I if cls.ignore_case else 0))
        text = cls._tostr(text)
        m = pattern.search(text)
        if m :
            grps = m.groups()
            return grps[0] if grps else NoAttr
        return NoAttr

class find_patterni(find_pattern): ignore_case=True

class find_patterns(TextOp):
    stop_when_found = False
    ignore_case = False

    @classmethod
    def op(cls,text, patterns,*args,**kwargs):
        out = {}
        text = cls._tostr(text)
        if isinstance(patterns, dict):
            patterns = patterns.items()
        for attr,pattern in patterns:
            if isinstance(pattern,basestring):
                pattern = re.compile(pattern, re.M | (re.I if cls.ignore_case else 0))
            if pattern:
                m = pattern.search(text)
                if m :
                    tmp_groupdict = m.groupdict() or dict([('group%s' % k,v) for k,v in enumerate(m.groups())])
                    groupdict = {}
                    for grp, val in tmp_groupdict.items():
                        if grp[:3] == 'INT':
                            try:
                                groupdict[grp[3:]] = int(val)
                            except ValueError:
                                groupdict[grp[3:]] = 0
                        else:
                            groupdict[grp] = val
                    groupdict = cls.pre_store(groupdict)
                    if len(groupdict) == 1:
                        out.update({ attr : groupdict.popitem()[1] })
                    else:
                        out.update({ attr : groupdict })
                    if cls.stop_when_found:
                        break
        return out

    @classmethod
    def pre_store(self,groupdict):
        return groupdict

class find_patternsi(find_patterns): ignore_case=True


class find_first_pattern(find_patterns):
    stop_when_found = True

    @classmethod
    def op(cls,text, patterns,*args,**kwargs):
        data = find_patterns.op(text, dict([('pat%s' % k,v) for k,v in enumerate(patterns)]))
        if not data:
            return NoAttr
        return data.popitem()[1]

class find_first_patterni(find_patterns): ignore_case=True

def index_normalize(index_val):
    index_val = index_val.lower().strip()
    index_val = re.sub(r'\W','_',index_val)
    index_val = re.sub('_+','_',index_val)
    index_val = re.sub('_$','',index_val)
    return index_val

class state_pattern(TextOp):
    """ states and patterns parser

    The states_patterns_desc to give looks like this :

    ((<if state1>,<goto state1>,<pattern1>,<out data path1>,<out filter1>),
    ...
    (<if stateN>,<patternN>,<goto stateN>,<out data pathN>))
    <if state> is a string telling on what state(s) the pattern must be searched, one can specify several states with comma separated string or a tupple.
        if <if state> is empty, the pattern will be searched for all lines
        Note : at the beginning, the state is 'top'
    <goto state> is a string corresponding to the new state if the pattern matches. use an empty string to not change the current state
    <pattern> is a string or a re.regex to match a line of text. one should use named groups for selecting data : (?P<key1>pattern)
    <out data path> is a string with '.' separator or a tuple telling where to place the groupdict from pattern maching process,
        The syntax is :
        '%(contextgroupkey1)s.%(contextgroupkey2)s. ... .%(contextgroupkeyN)s'
        or
        ('%(contextgroupkey1)s','%(contextgroupkey2)s', ... ,'%(contextgroupkeyN)s')
        Where contextgroup is the dictionnary of all merged groupdict from previous pattern maching process.
        instead of %(contextgroupkeyN)s, one can use a simple string to put data in a not changing key.
        It will put the groupdict (merged if alread present) into {'key1_value':{'key2_value':{'keyN_value' : groupdict }}}
        instead of %(contextgroupkeyN)s, one can use the string '[]' :  the groupdict will be appended in a list
        ie : {'key1_value':{'key2_value':[groupdict,...] }}}
    <out filter> could be :
        None : no filter is applied, the pattern groupdict is stored
        a string : used as a format string with context group dict, the formatted string is stored
        a callable : to calculate the value to be stored

    """

    @classmethod
    def op(cls,text, states_patterns_desc, reflags=0, autostrip=True,**kwargs):
        """ Parse the text

            Do not use this method directly, butter use this syntax :

            >>> "mytext to parse" | states_patterns(<states_patterns_desc>)

            Args:
                text (str or list or gen) :  the text to parse
                states_patterns_desc (tupple) : the patterns to find at some state values
                reflags : re flags, ie re.I or re.M or re.I | re.M
                autostrip : before being stored, groupdict keys and values are stripped
            Returns:
                dict : parsed data from text
        """
        state = 'top'
        root_data = {}
        groups_context = {}
        states_patterns = []

        #check states_patterns_desc is a correct tuple/list of tuples/lists
        if not isinstance(states_patterns_desc,(list,tuple)):
            raise ParsingError('states_patterns_desc must contains a tuple/list of tuples/lists')
        if not states_patterns_desc or not states_patterns_desc[0]:
            raise ParsingError('states_patterns_desc must not be empty')
        if not isinstance(states_patterns_desc[0],(list,tuple)):
            raise ParsingError('states_patterns_desc must contains a tuple/list of tuples/lists : one level of parenthesis or a coma is missing somewhere.')
        if len(states_patterns_desc[0]) != 5:
            raise ParsingError('states_patterns_desc subtuple must contain 5 elements : ifstate, gotostate, pattern, datapath and outfilter')

        #normalizing states_patterns_desc :
        for ifstate, gotostate, pattern, datapath, outfilter in states_patterns_desc:
            if not ifstate:
                ifstate = ()
            else:
                if isinstance(ifstate, basestring):
                    ifstate = ifstate.split(',')
            if isinstance(pattern, basestring):
                pattern = re.compile(pattern,reflags)
            if isinstance(datapath, basestring):
                if not datapath:
                    datapath = []
                else:
                    datapath = datapath.split('.')
            states_patterns.append((ifstate, gotostate, pattern, datapath, outfilter))

        # parse the text
        for line in cls._tolist(text):
            for ifstate, gotostate, pattern, datapath, outfilter in states_patterns:
                if not ifstate or state in ifstate:
                    m=pattern.match(line)
                    if m:
                        if datapath is not None:
                            g = m.groupdict()
                            if autostrip:
                                g = dict([ (k,v.strip()) for k,v in m.groupdict().items() ])
                            groups_context.update(g)
                            data = root_data
                            for p in datapath:
                                p = p.format(**groups_context)
                                prev_data = data
                                if p[-2:] == '[]':
                                    p = p[:-2]
                                    p = index_normalize(p)
                                    if p not in data:
                                        data[p] = []
                                    data = data[p]
                                else:
                                    p = index_normalize(p)
                                    if p not in data:
                                        data[p] = {}
                                    data = data[p]

                            if callable(outfilter):
                                g=outfilter(g)
                            elif isinstance(outfilter, basestring):
                                g=outfilter.format(**groups_context)

                            if isinstance(data,list):
                                data.append(g)
                            else:
                                if isinstance(g,dict):
                                    data.update(g)
                                else:
                                    prev_data[p] = g
                        if gotostate:
                            state = gotostate
                        break
        return root_data
