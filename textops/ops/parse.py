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

class parseg(TextOp):
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, key_update = None, *args,**kwargs):
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

class find_patterns(TextOp):
    stop_when_found = False
    ignore_case = False

    @classmethod
    def op(cls,text, patterns_dict,*args,**kwargs):
        out = {}
        text = cls._tostr(text)
        for attr,pattern in patterns_dict.items():
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


class state_machine(TextOp):
    @classmethod
    def op(cls,text, state_machine_def,*args,**kwargs):
        parser = StateMachineParser()
        if kwargs.get('debug'):
            parser.set_debug(True)
        parser.set_params(state_machine_def)
        out = parser.parse(text)
        return out

STATE_MACHINE_LINE_REPARSE_MAX = 5

re_multiple_tag=re.compile('^_(\d+)(.*)$')
month_name_to_id = {
'jan' : 1,
'janv' : 1,
'feb' : 2,
'feb' : 2,
'fev' : 2,
'fév' : 2,
'mar' : 3,
'mars' : 3,
'avr' : 4,
'apr' : 4,
'may' : 5,
'mai' : 5,
'jun' : 6,
'juin' : 6,
'jul' : 7,
'juil' : 7,
'aug' : 8,
'aou' : 8,
'aout' : 8,
'sep' : 9,
'sept' : 9,
'oct' : 10,
'nov' : 11,
'dec' : 12,
'déc' : 12,
}

class StateMachineLineReparseMAX(Exception): pass
class StateMachineFileParserEOF(Exception): pass

class StateMachinePanic(Exception):
    def __init__(self, msg, parser):
        self.msg = msg
        self.parser = parser
    def __unicode__(self):
        return '%s\nState : %s\nSubAction : %s\nline analysed="%s"' % (self.msg, self.parser.state, self.parser.subaction_name, self.parser.line)

class StateMachineParser(object):
    """ StateMachineParser by E.Lapouyade """
    stats_fields = {}
    single_pass = True

    def __init__(self):
        self.debug = False
        self.debug_trace = []

    def set_debug(self, level):
        self.debug = level

    def debug_collect(self,extras=None):
        self.debug_trace.append({'line':self.line, 'state':self.state, 'subaction':self.subaction_name, 'data':copy.deepcopy(self.data), 'parser':copy.deepcopy(self.parser), 'groupdict':self.groupdict, 'extras':extras})

    def debug_dump(self):
        pp.pprint(self.debug_trace)

    def debug_data(self):
        return self.debug_trace

    def strip_blank_pre_store(self,subaction, groupdict):
        for k,v in groupdict.items():
            if type(v) == str:
                groupdict[k] = v.replace(' ','')

    def post_parse(self):
        pass

    def post_stats(self):
        pass

    def data_collect(self, subaction, groupdict):
        if 'data_collect' in subaction:
            try:
                method_name = subaction['data_collect']
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
            else:
                method(subaction, groupdict)

        else:
            self.default_data_collect(subaction, groupdict)

    def default_data_collect(self, subaction, groupdict):
        for grp, val in groupdict.items():
            if grp[:6] == 'PARSER':
                self.parser[grp[6:]] = val
            elif grp[:7] == 'DATATAB':
                datatab_name = grp[7:]
                if datatab_name not in self.data:
                    self.data[datatab_name] = []
                self.data[datatab_name].append(val)
            elif grp[:7] == 'DATAINT':
                self.data[grp[7:]] = int(val)
            elif grp[:9] == 'DATAFLOAT':
                self.data[grp[9:]] = float(val)
            elif grp[:4] == 'DATA':
                self.data[grp[4:]] = val

    def datetime_pre_store(self,subaction, groupdict):
        if 'year' not in groupdict or 'month' not in groupdict or 'day' not in groupdict:
            return groupdict
        index = subaction['data_collect_params'].get('datetime_index','datetime')
        month = month_name_to_id.get(groupdict['month'].lower())
        if not month:
            try:
                month = int(groupdict['month'])
            except:
                month = 1
        date = datetime(int(groupdict['year']),month,int(groupdict['day']),int(groupdict.get('hour',12)),int(groupdict.get('minute',0)),int(groupdict.get('second',0)))
        del groupdict['year']
        del groupdict['month']
        del groupdict['day']
        if 'hour' in groupdict: del groupdict['hour']
        if 'minute' in groupdict: del groupdict['minute']
        if 'second' in groupdict: del groupdict['second']
        groupdict[index] = date
        return groupdict

    def auto_type_pre_store(self,subaction, groupdict):
        out_dict={}
        for grp, val in groupdict.items():
            if grp[:6] == 'PARSER':
                self.parser[grp[6:]] = val
            elif grp[:7] == 'DATATAB':
                datatab_name = grp[7:]
                if datatab_name not in groupdict:
                    out_dict[datatab_name] = [val,]
                else:
                    out_dict[datatab_name] = groupdict[datatab_name] + [val,]
            elif grp[:7] == 'DATAINT':
                out_dict[grp[7:]] = int(val)
            elif grp[:9] == 'DATAFLOAT':
                self.data[grp[9:]] = float(val)
            elif grp[:4] == 'DATA':
                out_dict[grp[4:]] = val
            else:
                out_dict[grp] = val

        return out_dict

    def store_index_dict(self, subaction, groupdict):
        if 'data_collect_params' not in subaction:
            raise StateMachinePanic("store_index_dict nécessite la clef qui servira d'index dans self.data ('index' dans le dict data_collect_params)",self)
        params = subaction['data_collect_params']
        index = params.get('index','')
        overwrite = params.get('overwrite',False)
        forcelist = params.get('forcelist',False)
        dataset = params.get('dataset')
        store_in_dataset = params.get('store_in_dataset')
        store_current_index = params.get('store_current_index')
        store_in_path = params.get('store_in_path')
        if not index:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "mount_point")',self)

        method_name = params.get('pre_store_func',None)
        if method_name:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
            else:
                groupdict = method(subaction, groupdict)

        index_val_org = groupdict.pop(index)
        index_val = index_normalize(index_val_org)
        if len(groupdict) == 1 and not params.get('keep_dict'):
            groupdict = groupdict.popitem()[1]
        else:
            groupdict[index] = index_val_org

        data = self.dataset.get(store_in_dataset,self.data)
        if dataset:
            dataset_name = dataset or 'dataset'
            if dataset_name not in data:
                data[dataset_name] = {}
            data = data[dataset_name]

        if store_in_path:
            for p in store_in_path:
                index = p.format(**self.groups_context)
                if index not in data:
                    data[index] = {}
                data = data[index]

        if store_current_index and self.current_index:
            data = data[self.current_index]
            if isinstance(data, list):
                data = data[-1]

        if not overwrite and index_val in data:
            if type(data[index_val]) is not list:
                data[index_val] = [data[index_val],]
            data[index_val].append(groupdict)
        else:
            if not isinstance(data, NoAttr):
                if overwrite == 'merge' and index_val in data:
                    if isinstance(groupdict,dict):
                        data[index_val].update(groupdict)
                else:
                    if forcelist:
                        data[index_val] = [groupdict,]
                    else:
                        data[index_val] = groupdict
        if not store_current_index or not self.current_index:
            self.current_index = index_val
        if dataset:
            self.dataset[dataset] = data[index_val]

    def store_multi_index_dict(self, subaction, groupdict):
        if 'data_collect_params' not in subaction:
            raise StateMachinePanic("store_multi_index_dict nécessite une liste d'indexation (overwrite des index implicite)",self)
        params = subaction['data_collect_params']
        store_in_path = params.get('store_in_path')
        index_list = params.get('index')
        overwrite = params.get('overwrite',False)
        if not index_list:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "(index1,index2,)")',self)

        method_name = subaction['data_collect_params'].get('pre_store_func',None)
        if method_name:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
            else:
                groupdict = method(subaction, groupdict)

        dct = self.data

        if store_in_path:
            for p in store_in_path:
                index = p.format(**self.groups_context)
                if index not in dct:
                    dct[index] = {}
                dct = dct[index]

        for index in index_list:
            index_val = index_normalize(groupdict.pop(index))
            if index_val not in dct:
                dct[index_val] = {}
            prev_dct=dct
            dct=dct[index_val]
        if len(groupdict) == 1 and not params.get('keep_dict'):
            if not overwrite:
                if not dct:
                    prev_dct[index_val] = []
                prev_dct[index_val].append(groupdict.popitem()[1])
            else:
                prev_dct[index_val] = groupdict.popitem()[1]
        else:
            if not overwrite:
                if not dct:
                    prev_dct[index_val] = []
                prev_dct[index_val].append(groupdict)
            else:
                dct.update(groupdict)

    def store_current_index(self, subaction, groupdict):
        if self.current_index:
            if 'data_collect_params' in subaction:
                method_name = subaction['data_collect_params'].get('pre_store_func',None)
                if method_name:
                    try:
                        method = getattr(self, method_name)
                    except AttributeError:
                        raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
                    else:
                        groupdict = method(subaction, groupdict)
            self.data[self.current_index].update(groupdict)

    def store_dict_in_tab(self, subaction, groupdict):
        if 'data_collect_params' not in subaction:
            raise StateMachinePanic('store_dict_in_tab nécessite la clef où sera stocké le tableau de dict ("index" dans le dict data_collect_params)',self)
        index = subaction['data_collect_params'].get('index','')
        store_in_path = subaction['data_collect_params'].params.get('store_in_path')
        if not index:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "cpus")',self)
        index_parts = index.split('.')
        base = index_parts[:-1]
        last = index_parts[-1]
        dest = self.data

        if store_in_path:
            for p in store_in_path:
                index = p.format(**self.groups_context)
                if index not in dest:
                    dest[index] = {}
                dest = dest[index]

        if subaction['data_collect_params'].get('store_current_index') and self.current_index:
            dest = self.data[self.current_index]
        for d in base:
            if d not in dest:
                dest[d] = {}
            dest=dest[d]
        if last not in dest:
            dest[last] = []
        dest=dest[last]

        method_name = subaction['data_collect_params'].get('pre_store_func',None)
        if method_name:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
            else:
                groupdict = method(subaction, groupdict)

        if type(groupdict) == list:
            dest += groupdict
        else:
            if len(groupdict) == 1 and not subaction['data_collect_params'].get('keep_dict'):
                groupdict = groupdict.popitem()[1]
                if subaction['data_collect_params'].get('uniq'):
                    if groupdict not in dest:
                        dest.append(groupdict)
                else:
                    dest.append(groupdict)
            else:
                dest.append(groupdict)

    # Cas où il y a plusieurs enregistrement sur une même ligne
    # la syntaxe est alors pour le tag du groupdir : <chiffre><tag>, ainsi on a 1freq ... 2freq qui sera splité en 2 dict avec les 2 valeurs de freq
    def store_dict_in_tab_split(self, subaction, groupdict):
        if 'data_collect_params' not in subaction:
            raise StateMachinePanic('store_dict_in_tab nécessite la clef où sera stocké le tableau de dict ("index" dans le dict data_collect_params)',self)
        index = subaction['data_collect_params'].get('index','')
        store_in_path = subaction['data_collect_params'].params.get('store_in_path')
        if not index:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "cpus")',self)
        index_parts = index.split('.')
        base = index_parts[:-1]
        last = index_parts[-1]
        dest = self.data

        if store_in_path:
            for p in store_in_path:
                index = p.format(**self.groups_context)
                if index not in dest:
                    dest[index] = {}
                dest = dest[index]

        for d in base:
            if d not in dest:
                dest[d] = {}
            dest=dest[d]
        if last not in dest:
            dest[last] = []
        dest=dest[last]

        #lecture du groupdict et répartition des tag:
        split_dict={}
        global_dict={}
        for k,v in groupdict.items():
            m=re_multiple_tag.match(k)
            if m:
                n = int(m.group(1))
                tag = m.group(2)
                if n not in split_dict:
                    split_dict[n]={}
                split_dict[n][tag] = v
            else:
                global_dict[k] = v

        method_name = subaction['data_collect_params'].get('pre_store_func',None)
        if method_name:
            try:
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__), self)
        for v in split_dict.values():
            groupdict = v
            groupdict.update(global_dict)
            if method_name:
                groupdict = method(subaction, groupdict)
            if type(groupdict) == list:
                dest += groupdict
            else:
                dest.append(groupdict)

    def goto_state(self, subaction, groupdict):
        if 'goto_state_func' in subaction:
            try:
                method_name = subaction['goto_state_func']
                method = getattr(self, method_name)
            except AttributeError:
                raise StateMachinePanic('Pas de methode "%s" pour %s' % (method_name, self.__class__),self)
            else:
                method(subaction, groupdict)
        elif 'goto_state' in groupdict :
            new_state = groupdict['goto_state']
            if new_state in self.state_actions:
                self.state = new_state
        else:
            self.state = subaction.get('goto_state', self.state)
        self.line_reparse = subaction.get('line_reparse', False)


    def read_next_line(self):
        if self.line_reparse:
            self.line_reparse = False
            self.line_reparse_cptr += 1
            if self.line_reparse_cptr > STATE_MACHINE_LINE_REPARSE_MAX:
                raise StateMachineLineReparseMAX
        else:
            self.line = self.text_iter.next().rstrip()
            self.line_reparse_cptr = 0
            self.lineno += 1

    def update_groups_context(self,dct):
        self.groups_context.update(dct)

    def handle_subaction(self,subaction):
        if subaction:
            if 'if_set' not in subaction or self.parser.get(subaction['if_set'],False):
                pattern = subaction['pattern']
                if isinstance(pattern,basestring):
                    pattern = re.compile(pattern)
                    subaction['pattern'] = pattern

                m = pattern.match(self.line)
                if m :
                    self.update_groups_context(m.groupdict())
                    self.groupdict = m.groupdict() or { str(self.lineno) : m.group(0)}
                    self.subaction_name = subaction.get('name', 'Unknown')
                    self.data_collect(subaction, self.groupdict)
                    if 'set_flag' in subaction:
                        self.parser.update(subaction['set_flag'])
                    if subaction.get('exit',False):
                        if self.debug:
                            self.debug_collect()
                        raise StateMachineFileParserEOF
                    self.goto_state(subaction, self.groupdict)
                    return True
        return False

    def many_select_action(self, params):
        self.read_next_line()
        self.groupdict = None
        self.subaction_name = None
        for subaction in params:
            if self.handle_subaction(subaction):
                break

        if self.debug:
            self.debug_collect()
        return True

    def indirect_select_action(self, params):
        self.read_next_line()
        self.groupdict = None
        self.subaction_name = None
        pattern = params['first_look']
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern)
            params['first_look'] = pattern
        m = pattern.match(self.line)
        if m :
            self.update_groups_context(m.groupdict())
            subaction = params['indirect_subactions'].get(m.group(1).lower())
            self.handle_subaction(subaction)

        if self.debug:
            self.debug_collect()
        return True

    def in_order_select_action(self, params):
        try:
            if self.state not in self.state_vars:
                self.state_vars[self.state] = iter(params)
            itr = self.state_vars[self.state]
            subaction = itr.next()
            try:
                while True:
                    self.read_next_line()
                    if self.handle_subaction(subaction):
                        break
                    self.groupdict = None
                    if self.debug:
                        self.debug_collect()
            except StopIteration:
                raise StateMachineFileParserEOF
        except StopIteration:
            if self.state == "top":
                raise StateMachineFileParserEOF
            else:
                self.state = "top"
            return False
        return True

    def set_params(self,state_actions):
        self.state_actions = state_actions

    def parse_init(self):
        self.state = "top"
        self.state_vars = {}
        self.data = {}
        self.parser = {}
        self.line_reparse = False
        self.line_reparse_cptr = 0
        self.remember_groupdict = {}
        self.bank_list = []
        self.lineno = 0
        self.current_index = None
        self.dataset = {}
        self.groups_context = {}

    def parse(self,text,attr=None):
        self.parse_init()
        if isinstance(text,basestring):
             text = text.splitlines()
        self.text_iter = iter(text)

        try:
            while True:
                for i in range(10):
                    action_desc = self.state_actions.get(self.state)
                    if not action_desc:
                        raise StateMachinePanic("Unknown state : %s" % self.state,self)
                    method = getattr(self, action_desc.get('action_type','many_select_action'), None)
                    method_params = action_desc['action_params']
                    if method(method_params): break
                if self.state == 'eof':
                    raise StateMachineFileParserEOF
        except (StopIteration, StateMachineFileParserEOF):
            self.post_parse()

        # On efface le fichier de l'object sinon il n'est pas pickable

        self.make_stats()
        if self.debug:
            textops.logger.debug('State machine final data : %s',pp.pformat(self.data))
        return self.data

    def make_stats(self):
        if self.stats_fields:
            self.data['stats'] = {}
            for k,fields in self.stats_fields.items():
                if k in self.data:
                    self.data['stats'][k] = dictExt.list_stats(self.data[k],fields)
            self.post_stats()
