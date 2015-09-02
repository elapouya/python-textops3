# -*- coding: utf-8 -*-
'''
Created : 2015-08-24

@author: Eric Lapouyade
'''

from textops import TextOp, NoAttr, slugify
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
import copy
from datetime import datetime

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
    def op(cls,text, patterns_dict):
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
    def op(cls,text, patterns):
        data = find_patterns.op(text, dict([('pat%s' % k,v) for k,v in enumerate(patterns)]))
        if not data:
            return NoAttr
        return data.popitem()[1]

class find_first_patterni(find_patterns): ignore_case=True

class parse_with_state_machine(TextOp):
    @classmethod
    def op(cls,text, state_machine_def):
        parser = StateMachineParser()
        parser.set_params(state_machine_def)
        out = parser.parse(text)
        return

def index_normalize(index_val,trans_index=None):
    return slugify(index_val)

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
        trans_index = params.get('trans_index',TRANS_INDEX)
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
        index_val = index_normalize(index_val_org,trans_index)
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

        if store_current_index and self.current_index:
            data = data[self.current_index]
            if isinstance(data, list):
                data = data[-1]

        if not overwrite and index_val in data:
            if type(data[index_val]) is not list:
                data[index_val] = [data[index_val],]
            data[index_val].append(groupdict)
        else:
            if not isinstance(data, NoneAttr):
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
        index_list = params.get('index')
        trans_index = params.get('trans_index',TRANS_INDEX)
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
        for index in index_list:
            index_val = index_normalize(groupdict.pop(index),trans_index)
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
        if not index:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "cpus")',self)
        index_parts = index.split('.')
        base = index_parts[:-1]
        last = index_parts[-1]
        dest = self.data
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
        if not index:
            raise StateMachinePanic('data_collect_params["index"] doit contenir un clef non nulle (ex : "cpus")',self)
        index_parts = index.split('.')
        base = index_parts[:-1]
        last = index_parts[-1]
        dest = self.data
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

    def handle_subaction(self,subaction):
        if subaction:
            if 'if_set' not in subaction or self.parser.get(subaction['if_set'],False):
                pattern = subaction['pattern']
                m = pattern.match(self.line)
                if m :
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
        m = pattern.match(self.line)
        if m :
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
        return self.data

    def make_stats(self):
        if self.stats_fields:
            self.data['stats'] = {}
            for k,fields in self.stats_fields.items():
                if k in self.data:
                    self.data['stats'][k] = dictExt.list_stats(self.data[k],fields)
            self.post_stats()
