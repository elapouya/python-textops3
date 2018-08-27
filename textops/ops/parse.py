# -*- coding: utf-8 -*-
#
# Created : 2015-08-24
#
# @author: Eric Lapouyade
#
""" This module gathers parsers to handle whole input text"""

from textops import TextOp, NoAttr, dformat, pp, stru
import textops
import types
import string
import re
import copy
from datetime import datetime
import collections

logger = textops.logger

def index_normalize(index_val):
    """Normalize dictionary calculated key

    When parsing, keys within a dictionary may come from the input text. To ensure there is no
    space or other special caracters, one should use this function. This is useful because
    DictExt dictionaries can be access with a dotted notation that only supports ``A-Za-z0-9_`` chars.

    Args:
        index_val (str): The candidate string to a dictionary key.

    Returns:
        str: A normalized string with only ``A-Za-z0-9_`` chars

    Examples:
        >>> index_normalize('this my key')
        'this_my_key'
        >>> index_normalize('this -my- %key%')
        'this_my_key'

    """
    index_val = index_val.lower().strip()
    index_val = re.sub(r'^\W*','',index_val)
    index_val = re.sub(r'\W*$','',index_val)
    index_val = re.sub(r'\W+','_',index_val)
    index_val = re.sub('_+','_',index_val)
    return index_val

def context_key_not_found(key):
    return 'UNKNOWN_CONTEXT_KEY_%s' % key

class ParsingError(Exception):
    pass

class mgrep(TextOp):
    r"""Multiple grep

    This works like :class:`textops.grep` except that it can do several greps in a single command.
    By this way, you can select many patterns in a big file.

    Args:
        patterns_dict (dict): a dictionary where all patterns to search are in values.
        key (int or str): test only one column or one key (optional)

    Returns:
        dict: A dictionary where the keys are the same as for ``patterns_dict``, the values will
            contain the :class:`textops.grep` result for each corresponding patterns.

    Examples:
        >>> logs = '''
        ... error 1
        ... warning 1
        ... warning 2
        ... info 1
        ... error 2
        ... info 2
        ... '''
        >>> t = logs | mgrep({
        ... 'errors' : r'^err',
        ... 'warnings' : r'^warn',
        ... 'infos' : r'^info',
        ... })
        >>> print(t)  #doctest: +NORMALIZE_WHITESPACE
        {'errors': ['error 1', 'error 2'],
        'warnings': ['warning 1', 'warning 2'],
        'infos': ['info 1', 'info 2']}

        >>> s = '''
        ... Disk states
        ... -----------
        ... name: c1t0d0s0
        ... state: good
        ... fs: /
        ... name: c1t0d0s4
        ... state: failed
        ... fs: /home
        ...
        ... '''
        >>> t = s | mgrep({
        ... 'disks' : r'^name:',
        ... 'states' : r'^state:',
        ... 'fss' : r'^fs:',
        ... })
        >>> print(t)  #doctest: +NORMALIZE_WHITESPACE
        {'disks': ['name: c1t0d0s0', 'name: c1t0d0s4'],
        'states': ['state: good', 'state: failed'],
        'fss': ['fs: /', 'fs: /home']}
        >>> dict(zip(t.disks.cutre(': *',1),zip(t.states.cutre(': *',1),t.fss.cutre(': *',1))))
        {'c1t0d0s0': ('good', '/'), 'c1t0d0s4': ('failed', '/home')}
    """
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,patterns_dict,key = None, *args,**kwargs):
        for k,pattern in list(patterns_dict.items()):
            if isinstance(pattern,str):
                patterns_dict[k] = re.compile(pattern,cls.flags)
        dct = {}
        for line in cls._tolist(text):
            for k,regex in list(patterns_dict.items()):
                try:
                    if isinstance(line,str):
                        if bool(regex.search(stru(line))) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                    elif key is None:
                        if bool(regex.search(stru(line))) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                    else:
                        if bool(regex.search(stru(line[key]))) != cls.reverse:  # kind of XOR with cls.reverse
                            dct.setdefault(k,[]).append(line)
                except (ValueError, TypeError, IndexError, KeyError):
                    pass
        return dct

class mgrepi(mgrep):
    r"""same as mgrep but case insensitive

    This works like :class:`textops.mgrep`, except it is case insensitive.

    Args:
        patterns_dict (dict): a dictionary where all patterns to search are in values.
        key (int or str): test only one column or one key (optional)

    Returns:
        dict: A dictionary where the keys are the same as for ``patterns_dict``, the values will
            contain the :class:`textops.grepi` result for each corresponding patterns.

    Examples:
        >>> 'error 1' | mgrep({'errors':'ERROR'})
        {}
        >>> 'error 1' | mgrepi({'errors':'ERROR'})
        {'errors': ['error 1']}
    """
    flags = re.IGNORECASE

class mgrepv(mgrep):
    r"""Same as mgrep but exclusive

    This works like :class:`textops.mgrep`, except it searches lines that DOES NOT match patterns.

    Args:
        patterns_dict (dict): a dictionary where all patterns to exclude are in values().
        key (int or str): test only one column or one key (optional)

    Returns:
        dict: A dictionary where the keys are the same as for ``patterns_dict``, the values will
            contain the :class:`textops.grepv` result for each corresponding patterns.

    Examples:
        >>> logs = '''error 1
        ... warning 1
        ... warning 2
        ... error 2
        ... '''
        >>> t = logs | mgrepv({
        ... 'not_errors' : r'^err',
        ... 'not_warnings' : r'^warn',
        ... })
        >>> print(t                                         )#doctest: +NORMALIZE_WHITESPACE
        {'not_warnings': ['error 1', 'error 2'], 'not_errors': ['warning 1', 'warning 2']}
    """
    reverse = True

class mgrepvi(mgrepv):
    r"""Same as mgrepv but case insensitive

    This works like :class:`textops.mgrepv`, except it is case insensitive.

    Args:
        patterns_dict (dict): a dictionary where all patterns to exclude are in values().
        key (int or str): test only one column or one key (optional)

    Returns:
        dict: A dictionary where the keys are the same as for ``patterns_dict``, the values will
            contain the :class:`textops.grepvi` result for each corresponding patterns.

    Examples:
        >>> logs = '''error 1
        ... WARNING 1
        ... warning 2
        ... ERROR 2
        ... '''
        >>> t = logs | mgrepv({
        ... 'not_errors' : r'^err',
        ... 'not_warnings' : r'^warn',
        ... })
        >>> print(t                                         )#doctest: +NORMALIZE_WHITESPACE
        {'not_warnings': ['error 1', 'WARNING 1', 'ERROR 2'],
        'not_errors': ['WARNING 1', 'warning 2', 'ERROR 2']}
        >>> t = logs | mgrepvi({
        ... 'not_errors' : r'^err',
        ... 'not_warnings' : r'^warn',
        ... })
        >>> print(t                                         )#doctest: +NORMALIZE_WHITESPACE
        {'not_warnings': ['error 1', 'ERROR 2'], 'not_errors': ['WARNING 1', 'warning 2']}
    """
    flags = re.IGNORECASE

class sgrep(TextOp):
    r"""Switch grep

    This works like :class:`textops.mgrep` except that it returns a list of lists.
    ``sgrep`` dispatches lines matching a pattern to the list corresponding to the pattern order.
    If a line matches the third pattern, it will be dispatched to the third returned list.
    If N patterns are given to search, it will return N+1 lists, where the last list will be filled
    of lines that does not match any pattern in the given patterns list.
    The patterns list order is important : only the first
    matching pattern will be taken in account.
    One can consider that ``sgrep`` works like a **switch()** :
    it will do for each line a kind of ::

        if pattern1 matches:
            put line in list1
        elif pattern2 matches:
            put line in list2
        elif patternN matches:
            put line in listN
        else:
            put line in listN+1

    Args:
        patterns (list): a list of patterns to search.
        key (int or str): test only one column or one key (optional)

    Returns:
        list: a list of lists (nb patterns + 1)

    Examples:
        >>> logs = '''
        ... error 1
        ... warning 1
        ... warning 2
        ... info 1
        ... error 2
        ... info 2
        ... '''
        >>> t = logs | sgrep(('^err','^warn'))
        >>> print(t                                         )#doctest: +NORMALIZE_WHITESPACE
        [['error 1', 'error 2'], ['warning 1', 'warning 2'], ['', 'info 1', 'info 2']]
    """
    flags = 0
    reverse = False
    @classmethod
    def op(cls,text,patterns,key = None, *args,**kwargs):
        patterns = [ re.compile(pattern,cls.flags) if isinstance(pattern,str) else pattern for pattern in patterns ]
        lst = [ [] for i in range(len(patterns)+1) ] # surtout pas faire [] * (len(patterns)+1)
        for line in cls._tolist(text):
            for i,regex in enumerate(patterns):
                try:
                    if isinstance(line,str):
                        if bool(regex.search(stru(line))) != cls.reverse:  # kind of XOR with cls.reverse
                            lst[i].append(line)
                            break
                    elif key is None:
                        if bool(regex.search(stru(line))) != cls.reverse:  # kind of XOR with cls.reverse
                            lst[i].append(line)
                            break
                    else:
                        if bool(regex.search(stru(line[key]))) != cls.reverse:  # kind of XOR with cls.reverse
                            lst[i].append(line)
                            break
                except (ValueError, TypeError, IndexError, KeyError):
                    pass
            else:
                lst[-1].append(line)
        return lst

class sgrepi(sgrep):
    r"""Switch grep case insensitive

    This works like :class:`textops.sgrep` but is case insensitive
    """
    flags = re.IGNORECASE

class sgrepv(sgrep):
    r"""Switch grep reversed

    This works like :class:`textops.sgrep` except that it tests that patterns DOES NOT match the line.
    """
    reverse = True

class sgrepvi(sgrepv):
    r"""Switch grep reversed case insensitive

    This works like :class:`textops.sgrepv` but is case insensitive
    """
    flags = re.IGNORECASE

class parseg(TextOp):
    r"""Find all occurrences of one pattern, return MatchObject groupdict

    Args:
        pattern (str): a regular expression string (case sensitive)

    Returns:
        list: A list of dictionaries (MatchObject groupdict)

    Examples:
        >>> s = '''name: Lapouyade
        ... first name: Eric
        ... country: France'''
        >>> s | parseg(r'(?P<key>.*):\s*(?P<val>.*)')         #doctest: +NORMALIZE_WHITESPACE
        [{'key': 'name', 'val': 'Lapouyade'},
        {'key': 'first name', 'val': 'Eric'},
        {'key': 'country', 'val': 'France'}]
    """
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, *args,**kwargs):
        if isinstance(pattern,str):
            pattern = re.compile(pattern, re.I if cls.ignore_case else 0)
        out = []
        for line in cls._tolist(text):
            m = pattern.match(line)
            if m:
                out.append(m.groupdict())
        return out

class parsegi(parseg):
    r"""Same as parseg but case insensitive

    Args:
        pattern (str): a regular expression string (case insensitive)

    Returns:
        list: A list of dictionaries (MatchObject groupdict)

    Examples:
        >>> s = '''Error: System will reboot
        ... Notice: textops rocks
        ... Warning: Python must be used without moderation'''
        >>> s | parsegi(r'(?P<level>error|warning):\s*(?P<msg>.*)')         #doctest: +NORMALIZE_WHITESPACE
        [{'level': 'Error', 'msg': 'System will reboot'},
        {'level': 'Warning', 'msg': 'Python must be used without moderation'}]
    """
    ignore_case = True

class parsek(TextOp):
    r"""Find all occurrences of one pattern, return one Key

    One have to give a pattern with named capturing parenthesis, the function will return a list
    of value corresponding to the specified key. It works a little like :class:`textops.parseg`
    except that it returns from the groupdict, a value for a specified key ('key' be default)

    Args:
        pattern (str): a regular expression string.
        key_name (str): The key to get ('key' by default)
        key_update (callable): function to convert the found value

    Returns:
        list: A list of values corrsponding to `MatchObject groupdict[key]`

    Examples:
        >>> s = '''Error: System will reboot
        ... Notice: textops rocks
        ... Warning: Python must be used without moderation'''
        >>> s | parsek(r'(?P<level>Error|Warning):\s*(?P<msg>.*)','msg')
        ['System will reboot', 'Python must be used without moderation']
    """
    ignore_case = False
    @classmethod
    def op(cls,text, pattern, key_name = 'key', key_update = None, *args,**kwargs):
        if isinstance(pattern,str):
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

class parseki(parsek):
    r"""Same as parsek but case insensitive

    It works like :class:`textops.parsek` except the pattern is case insensitive.

    Args:
        pattern (str): a regular expression string.
        key_name (str): The key to get ('key' by default)
        key_update (callable): function to convert the found value

    Returns:
        list: A list of values corrsponding to `MatchObject groupdict[key]`

    Examples:
        >>> s = '''Error: System will reboot
        ... Notice: textops rocks
        ... Warning: Python must be used without moderation'''
        >>> s | parsek(r'(?P<level>error|warning):\s*(?P<msg>.*)','msg')
        []
        >>> s | parseki(r'(?P<level>error|warning):\s*(?P<msg>.*)','msg')
        ['System will reboot', 'Python must be used without moderation']
    """
    ignore_case = True

class parsekv(TextOp):
    r"""Find all occurrences of one pattern, returns a dict of groupdicts

    It works a little like :class:`textops.parseg` except that it returns a dict of dicts :
    values are MatchObject groupdicts, keys are a value in the groupdict at a specified key
    (By default : 'key'). Note that calculated keys are normalized (spaces are replaced by
    underscores)

    Args:
        pattern (str): a regular expression string.
        key_name (str): The key name to optain the value that will be the key of the groupdict
            ('key' by default)
        key_update (callable): function to convert/normalize the calculated key.
            If ``None``, the keys is normalized.
            If not ``None`` but not callable ,the key is unchanged.
        val_name (str): instead of storing the groupdict, on can choose to select
            the value at the key ``val_name`. (by default, None : means the whole groupdict)

    Returns:
        dict: A dict of MatchObject groupdicts

    Examples:
        >>> s = '''name: Lapouyade
        ... first name: Eric
        ... country: France'''
        >>> s | parsekv(r'(?P<key>.*):\s*(?P<val>.*)')         #doctest: +NORMALIZE_WHITESPACE
        {'name': {'key': 'name', 'val': 'Lapouyade'},
        'first_name': {'key': 'first name', 'val': 'Eric'},
        'country': {'key': 'country', 'val': 'France'}}
        >>> s | parsekv(r'(?P<item>.*):\s*(?P<val>.*)','item',str.upper)         #doctest: +NORMALIZE_WHITESPACE
        {'NAME': {'item': 'name', 'val': 'Lapouyade'},
        'FIRST NAME': {'item': 'first name', 'val': 'Eric'},
        'COUNTRY': {'item': 'country', 'val': 'France'}}
        >>> s | parsekv(r'(?P<key>.*):\s*(?P<val>.*)',key_update=0)         #doctest: +NORMALIZE_WHITESPACE
        {'name': {'key': 'name', 'val': 'Lapouyade'},
        'first name': {'key': 'first name', 'val': 'Eric'},
        'country': {'key': 'country', 'val': 'France'}}
        >>> s | parsekv(r'(?P<key>.*):\s*(?P<val>.*)',val_name='val')         #doctest: +NORMALIZE_WHITESPACE
        {'name': 'Lapouyade', 'first_name': 'Eric', 'country': 'France'}
    """
    ignore_case = False
    val_name = None
    @classmethod
    def op(cls,text, pattern, key_name = 'key', key_update = None, val_name = None, *args,**kwargs):
        if val_name is None:
            val_name = cls.val_name
        if isinstance(pattern,str):
            pattern = re.compile(pattern, re.I if cls.ignore_case else 0)

        def _op(text):
            out = {}
            for line in cls._tolist(text):
                m = pattern.match(line)
                if m:
                    dct = m.groupdict()
                    key = dct.get(key_name)
                    if key:
                        if key_update is None:
                            key_norm = index_normalize(key)
                        elif isinstance(key_update, collections.Callable):
                            key_norm = key_update(key)
                        else:
                            key_norm = key
                        out.update({ key_norm : dct if val_name is None else dct[val_name]})
            return out

        if isinstance(text,(list,types.GeneratorType)):
            return [ _op(item) for item in text ]
        return _op(text)

class parsekvi(parsekv):
    r"""Find all occurrences of one pattern (case insensitive), returns a dict of groupdicts

    It works a little like :class:`textops.parsekv` except that the pattern is case insensitive.

    Args:
        pattern (str): a regular expression string (case insensitive).
        key_name (str): The key name to optain the value that will be the key of the groupdict
            ('key' by default)
        key_update (callable): function to convert/normalize the calculated key.
            If ``None``, the keys is normalized.
            If not ``None`` but not callable ,the key is unchanged.
        val_name (str): instead of storing the groupdict, on can choose to select
            the value at the key ``val_name`. (by default, None : means the whole groupdict)

    Returns:
        dict: A dict of MatchObject groupdicts

    Examples:
        >>> s = '''name: Lapouyade
        ... first name: Eric
        ... country: France'''
        >>> s | parsekvi(r'(?P<key>NAME):\s*(?P<val>.*)')
        {'name': {'key': 'name', 'val': 'Lapouyade'}}
    """
    ignore_case = True

class keyval(parsekv):
    r"""Return a dictionnay where keys and values are taken from the pattern specify

    It is a shortcut for :class:`textops.parsekv` with val_name='val'
    The input can be a string or a list of strings.

    Args:
        pattern (str): a regular expression string.
        key_name (str): The key name to optain the value that will be the key of the groupdict
            ('key' by default)
        key_update (callable): function to convert/normalize the calculated key.
            If ``None``, the keys is normalized.
            If not ``None`` but not callable ,the key is unchanged.
        val_name (str): instead of storing the groupdict, on can choose to select
            the value at the key ``val_name`. (by default, None means 'val')

    Returns:
        dict: A dict of key:val from the matched pattern groupdict or a list of dicts if the input is a list of strings

    Examples:
        >>> s = '''name: Lapouyade
        ... first name: Eric
        ... country: France'''
        >>> s | keyval(r'(?P<key>.*):\s*(?P<val>.*)')         #doctest: +NORMALIZE_WHITESPACE
        {'name': 'Lapouyade', 'first_name': 'Eric', 'country': 'France'}

        >>> s = [ '''name: Lapouyade
        ... first name: Eric ''',
        ... '''name: Python
        ... first name: Guido''' ]
        >>> s | keyval(r'(?P<key>.*):\s*(?P<val>.*)')         #doctest: +NORMALIZE_WHITESPACE
        [{'name': 'Lapouyade', 'first_name': 'Eric '}, {'name': 'Python', 'first_name': 'Guido'}]

    """
    val_name = 'val'

class keyvali(keyval):
    r"""Return a dictionnay where keys and values are taken from the pattern specify

    It works a little like :class:`textops.keyval` except that the pattern is case insensitive.

    Args:
        pattern (str): a regular expression string (case insensitive).
        key_name (str): The key name to optain the value that will be the key of the groupdict
            ('key' by default)
        key_update (callable): function to convert/normalize the calculated key.
            If ``None``, the keys is normalized.
            If not ``None`` but not callable ,the key is unchanged.
        val_name (str): instead of storing the groupdict, on can choose to select
            the value at the key ``val_name`. (by default, None means 'val')

    Returns:
        dict: A dict of key:val from the matched pattern groupdict

    Examples:
        >>> s = '''name IS Lapouyade
        ... first name IS Eric
        ... country IS France'''
        >>> s | keyvali(r'(?P<key>.*) is (?P<val>.*)')         #doctest: +NORMALIZE_WHITESPACE
        {'name': 'Lapouyade', 'first_name': 'Eric', 'country': 'France'}
    """
    ignore_case = True

class find_pattern(TextOp):
    r"""Fast pattern search

    This operation can be use to find a pattern very fast : it uses :func:`re.search` on the whole input
    text at once. The input text is not read line by line, this means it must fit into memory.
    It returns the first captured group (named or not named group).

    Args:
        pattern (str): a regular expression string (case sensitive).

    Returns:
        str: the first captured group or NoAttr if not found

    Examples:
        >>> s = '''This is data text
        ... Version: 1.2.3
        ... Format: json'''
        >>> s | find_pattern(r'^Version:\s*(.*)')
        '1.2.3'
        >>> s | find_pattern(r'^Format:\s*(?P<format>.*)')
        'json'
        >>> s | find_pattern(r'^version:\s*(.*)') # 'version' : no match because case sensitive
        NoAttr
    """
    ignore_case = False

    @classmethod
    def op(cls,text, pattern, *args,**kwargs):
        if isinstance(pattern,str):
            pattern = re.compile(pattern, re.M | (re.I if cls.ignore_case else 0))
        text = cls._tostr(text)
        m = pattern.search(text)
        if m :
            grps = m.groups()
            return grps[0] if grps else NoAttr
        return NoAttr

class find_patterni(find_pattern):
    r"""Fast pattern search (case insensitive)

    It works like :class:`textops.find_pattern` except that the pattern is case insensitive.

    Args:
        pattern (str): a regular expression string (case insensitive).

    Returns:
        str: the first captured group or NoAttr if not found

    Examples:
        >>> s = '''This is data text
        ... Version: 1.2.3
        ... Format: json'''
        >>> s | find_patterni(r'^version:\s*(.*)')
        '1.2.3'
    """
    ignore_case=True

class find_patterns(TextOp):
    r"""Fast multiple pattern search

    It works like :class:`textops.find_pattern` except that one can specify a list or a dictionary
    of patterns. Patterns must contains capture groups.
    It returns a list or a dictionary of results depending on the patterns argument type.
    Each result will be the re.MatchObject groupdict if there
    are more than one capture named group in the pattern otherwise directly the value corresponding
    to the unique captured group.
    It is recommended to use *named* capture group, if not, the groups will be automatically named
    'groupN' with N the capture group order in the pattern.

    Args:
        patterns (list or dict): a list or a dictionary of patterns.

    Returns:
        dict: patterns search result

    Examples:
        >>> s = '''This is data text
        ... Version: 1.2.3
        ... Format: json'''
        >>> r = s | find_patterns({
        ... 'version':r'^Version:\s*(?P<major>\d+)\.(?P<minor>\d+)\.(?P<build>\d+)',
        ... 'format':r'^Format:\s*(?P<format>.*)',
        ... })
        >>> r
        {'version': {'major': '1', 'minor': '2', 'build': '3'}, 'format': 'json'}
        >>> r.version.major
        '1'
        >>> s | find_patterns({
        ... 'version':r'^Version:\s*(\d+)\.(\d+)\.(\d+)',
        ... 'format':r'^Format:\s*(.*)',
        ... })
        {'version': {'group0': '1', 'group1': '2', 'group2': '3'}, 'format': 'json'}
        >>> s | find_patterns({'version':r'^version:\s*(.*)'}) # lowercase 'version' : no match
        {}
        >>> s = '''creation: 2015-10-14
        ... update: 2015-11-16
        ... access: 2015-11-17'''
        >>> s | find_patterns([r'^update:\s*(.*)', r'^access:\s*(.*)', r'^creation:\s*(.*)'])
        ['2015-11-16', '2015-11-17', '2015-10-14']
        >>> s | find_patterns([r'^update:\s*(?P<year>.*)-(?P<month>.*)-(?P<day>.*)',
        ... r'^access:\s*(.*)', r'^creation:\s*(.*)'])
        [{'year': '2015', 'month': '11', 'day': '16'}, '2015-11-17', '2015-10-14']
    """
    stop_when_found = False
    ignore_case = False

    @classmethod
    def op(cls,text, patterns,*args,**kwargs):
        out = []
        text = cls._tostr(text)
        if isinstance(patterns, dict):
            patterns_list = list(patterns.items())
        else:
            patterns_list = enumerate(patterns)
        for attr,pattern in patterns_list:
            if isinstance(pattern,str):
                pattern = re.compile(pattern, re.M | (re.I if cls.ignore_case else 0))
            if pattern:
                m = pattern.search(text)
                if m :
                    tmp_groupdict = m.groupdict() or dict([('group%s' % k,v) for k,v in enumerate(m.groups())])
                    groupdict = {}
                    for grp, val in list(tmp_groupdict.items()):
                        if grp[:3] == 'INT':
                            try:
                                groupdict[grp[3:]] = int(val)
                            except ValueError:
                                groupdict[grp[3:]] = 0
                        else:
                            groupdict[grp] = val
                    groupdict = cls.pre_store(groupdict)
                    if len(groupdict) == 1:
                        out.append((attr, groupdict.popitem()[1]))
                    else:
                        out.append((attr, groupdict))
                    if cls.stop_when_found:
                        break
        if isinstance(patterns, dict):
            out = dict(out)
        else:
            out = [ i[1] for i in out ]
        return out

    @classmethod
    def pre_store(self,groupdict):
        return groupdict

class find_patternsi(find_patterns):
    r"""Fast multiple pattern search (case insensitive)

    It works like :class:`textops.find_patterns` except that patterns are case insensitive.

    Args:
        patterns (dict): a dictionary of patterns.

    Returns:
        dict: patterns search result

    Examples:
        >>> s = '''This is data text
        ... Version: 1.2.3
        ... Format: json'''
        >>> s | find_patternsi({'version':r'^version:\s*(.*)'})     # case insensitive
        {'version': '1.2.3'}
    """
    ignore_case=True


class find_first_pattern(find_patterns):
    r"""Fast multiple pattern search, returns on first match

    It works like :class:`textops.find_patterns` except that it stops searching on first match.

    Args:
        patterns (list): a list of patterns.

    Returns:
        str or dict: matched value if only one capture group otherwise the full groupdict

    Examples:
        >>> s = '''creation: 2015-10-14
        ... update: 2015-11-16
        ... access: 2015-11-17'''
        >>> s | find_first_pattern([r'^update:\s*(.*)', r'^access:\s*(.*)', r'^creation:\s*(.*)'])
        '2015-11-16'
        >>> s | find_first_pattern([r'^UPDATE:\s*(.*)'])
        NoAttr
        >>> s | find_first_pattern([r'^update:\s*(?P<year>.*)-(?P<month>.*)-(?P<day>.*)'])
        {'year': '2015', 'month': '11', 'day': '16'}
    """
    stop_when_found = True

    @classmethod
    def op(cls,text, patterns,*args,**kwargs):
        data = super(find_first_pattern,cls).op(text, patterns)
        if not data:
            return NoAttr
        return data[0]

class find_first_patterni(find_first_pattern):
    r"""Fast multiple pattern search, returns on first match

    It works like :class:`textops.find_first_pattern` except that patterns are case insensitives.

    Args:
        patterns (list): a list of patterns.

    Returns:
        str or dict: matched value if only one capture group otherwise the full groupdict

    Examples:
        >>> s = '''creation: 2015-10-14
        ... update: 2015-11-16
        ... access: 2015-11-17'''
        >>> s | find_first_patterni([r'^UPDATE:\s*(.*)'])
        '2015-11-16'
    """
    ignore_case=True

class parse_indented(TextOp):
    r"""Parse key:value indented text

    It looks for key:value patterns, store found values in a dictionary. Each time a new indent is
    found, a sub-dictionary is created. The keys are normalized (only keep ``A-Za-z0-9_``), the values
    are stripped.

    Args:
        sep (str): key:value separator (Default : ':')

    Returns:
        dict: structured keys:values

    Examples:
        >>> s = '''
        ... a:val1
        ... b:
        ...     c:val3
        ...     d:
        ...         e ... : val5
        ...         f ... :val6
        ...     g:val7
        ... f: val8'''
        >>> s | parse_indented()
        {'a': 'val1', 'b': {'c': 'val3', 'd': {'e': 'val5', 'f': 'val6'}, 'g': 'val7'}, 'f': 'val8'}
        >>> s = '''
        ... a --> val1
        ... b --> val2'''
        >>> s | parse_indented(r'-->')
        {'a': 'val1', 'b': 'val2'}
    """
    @classmethod
    def op(cls, text, sep=r':', *args,**kwargs):
        indent_level = 0
        out = {}
        indent_node = {indent_level:out}
        dct = out
        prev_k = None
        # parse the text
        for line in cls._tolist(text):
            m = re.match(r'^(\s*)(\S.*)', line)
            if m:
                k,v = (re.split(sep,m.group(2)) + [''])[:2]
                indent = len(m.group(1))
                if indent < indent_level:
                    dct = indent_node.get(indent)
                    while dct is None:
                        indent -= 1
                        dct = indent_node.get(indent)
                    indent_level = indent
                    for ik in list(indent_node.keys()):
                        if ik > indent:
                            del indent_node[ik]
                elif indent > indent_level:
                    if prev_k is not None:
                        dct[prev_k] = {}
                        dct = dct[prev_k]
                    indent_node[indent] = dct
                    indent_level = indent
                k = index_normalize(k)
                v = v.strip()
                if k in dct:
                    prev_v = dct[k]
                    if isinstance(prev_v,dict):
                        dct[k]=[prev_v,{}]
                        dct = dct[k][-1]
                    elif isinstance(prev_v,str):
                        dct[k]=[prev_v,v]
                    else:
                        if isinstance(prev_v[0],str):
                            dct[k].append(v)
                        else:
                            dct[k].append({})
                            dct = dct[k][-1]
                    prev_k = None
                else:
                    dct[k]=v
                    prev_k = k
        return out

class parse_smart(TextOp):
    r"""Try to automatically parse a text

    It looks for key/value patterns, store found values in a dictionary.
    It tries to respect indents by creating sub-dictionaries.
    The keys are normalized (only keep ``A-Za-z0-9_``), the values are stripped.

    Returns:
        dict: structured keys:values

    Examples:
        >>> s = '''
        ... Date/Time:       Wed Dec  2 09:51:17 NFT 2015
        ... Sequence Number: 156637
        ... Machine Id:      00F7B0114C00
        ...    Node Id:         xvio6
        ... Class:           H
        ... Type:            PERM
        ...    WPAR:            Global
        ...    Resource Name:   hdisk21
        ...       Resource Class:  disk
        ... Resource Type:   mpioapdisk
        ... Location:        U78AA.001.WZSHM0M-P1-C6-T1-W201400A0B8292A18-L13000000000000
        ...
        ... VPD:
        ...         Manufacturer................IBM
        ...         Machine Type and Model......1815      FAStT
        ...         ROS Level and ID............30393134
        ...         Serial Number...............
        ...         Device Specific.(Z0)........0000053245004032
        ...         Device Specific.(Z1)........
        ...
        ... Description
        ... DISK OPERATION ERROR
        ...
        ... Probable Causes
        ... DASD DEVICE
        ... '''
        >>> parsed = s >> parse_smart()
        >>> print(parsed.pretty())
        {   'class': 'H',
            'date_time': 'Wed Dec  2 09:51:17 NFT 2015',
            'description': ['DISK OPERATION ERROR'],
            'location': 'U78AA.001.WZSHM0M-P1-C6-T1-W201400A0B8292A18-L13000000000000',
            'machine_id': {'machine_id': '00F7B0114C00', 'node_id': 'xvio6'},
            'probable_causes': ['DASD DEVICE'],
            'resource_type': 'mpioapdisk',
            'sequence_number': '156637',
            'type': {   'resource_name': {   'resource_class': 'disk',
                                             'resource_name': 'hdisk21'},
                        'type': 'PERM',
                        'wpar': 'Global'},
            'vpd': {   'device_specific_z0': '0000053245004032',
                       'device_specific_z1': '',
                       'machine_type_and_model': '1815      FAStT',
                       'manufacturer': 'IBM',
                       'ros_level_and_id': '30393134',
                       'serial_number': ''}}
        >>> print(parsed.vpd.device_specific_z0)
        0000053245004032
    """
    @classmethod
    def op(cls, text, *args,**kwargs):
        sep = r'[^a-zA-Z0-9_()\.-]{2,}|[:=]|\.{2,}|[_-]{3,}'
        indent_level = 0
        out = {}
        indent_node = {indent_level:out}
        dct = out
        prev_k = None
        block_step = 1
        # parse the text
        for line in cls._tolist(text):
            if not line.strip():
                block_step = 1
            else:
                m = re.match(r'^(\s*)(\S.*)', line)
                if m:
                    k,v = (re.split(sep,m.group(2),1) + [''])[:2]
                    v = v.strip()
                    indent = len(m.group(1))
                    #print indent,indent_level,block_step,line,'****',prev_k,k
                    if block_step==1:
                        if not v and re.search(r'\w+',k):
                            block_step = 2
                        else:
                            block_step = 0
                    elif block_step == 2:
                        if indent == indent_level:
                            block_k = prev_k
                            prev_k = index_normalize(k)
                            dct[block_k] = [m.group(2)]
                            block_step = 3
                            continue
                        else:
                            block_step = 0
                    elif block_step == 3:
                        if indent == indent_level:
                            dct[block_k].append(m.group(2))
                            prev_k = index_normalize(k)
                            continue
                        else:
                            block_step = 0

                    #print '-> ',indent,indent_level,block_step

                    if indent < indent_level:
                        dct = indent_node.get(indent)
                        while dct is None:
                            indent -= 1
                            dct = indent_node.get(indent)
                        indent_level = indent
                        for ik in list(indent_node.keys()):
                            if ik > indent:
                                del indent_node[ik]
                        if not v:
                            block_step = 2
                    elif indent > indent_level:
                        if prev_k is not None:
                            if prev_v:
                                dct[prev_k] = {prev_k:prev_v}
                            else:
                                dct[prev_k] = {}
                            dct = dct[prev_k]
                        indent_node[indent] = dct
                        indent_level = indent

                    k = index_normalize(k)
                    if k in dct:
                        prev_v = dct[k]
                        if isinstance(prev_v,dict):
                            dct[k]=[prev_v,{}]
                            dct = dct[k][-1]
                        elif isinstance(prev_v,str):
                            dct[k]=[prev_v,v]
                        else:
                            if isinstance(prev_v[0],str):
                                dct[k].append(v)
                            else:
                                dct[k].append({})
                                dct = dct[k][-1]
                        prev_k = None
                    else:
                        dct[k]=v
                        prev_k = k
                        prev_v = v
        return out


class state_pattern(TextOp):
    r""" States and patterns parser

    This is a *state machine* parser :
    The main advantage is that it reads line-by-line the whole input text only once to collect all
    data you want into a multi-level dictionary. It uses patterns to select rules to be applied.
    It uses states to ensure only a set of rules are used against specific document sections.

    Args:
        states_patterns_desc (tupple) : descrption of states and patterns :
            see below for explaination
        reflags : re flags, ie re.I or re.M or re.I | re.M (Default : no flag)
        autostrip : before being stored, groupdict keys and values are stripped (Default : True)

    Returns:
        dict : parsed data from text

    |
    | **The states_patterns_desc :**

    It looks like this::

        ((<if state1>,<goto state1>,<pattern1>,<out data path1>,<out filter1>),
        ...
        (<if stateN>,<goto stateN>,<patternN>,<out data pathN>,<out filterN>))

    ``<if state>``
        is a string telling on what state(s) the pattern must be searched,
        one can specify several states with comma separated string or a tupple. if ``<if state>``
        is empty, the pattern will be searched for all lines.
        Note : at the beginning, the state is 'top'

    ``<goto state>``
        is a string corresponding to the new state if the pattern matches.
        use an empty string to not change the current state. One can use any string, usually,
        it corresponds to a specific section name of the document to parse where specific
        rules has to be used.
        if the pattern matches, no more rules are used for the current line except when you specify
        ``__continue__`` for the goto state. This is useful when you want to apply several rules on the same line.

    ``<pattern>``
        is a string or a re.regex to match a line of text.
        one should use named groups for selecting data, ex: ``(?P<key1>pattern)``

    ``<out data path>``
        is a string with a dot separator or a tuple telling where to place the groupdict
        from pattern maching process,
        The syntax is::

            '{contextkey1}.{contextkey2}. ... .{contextkeyN}'
            or
            ('{contextkey1}','{contextkey2}', ... ,'{contextkeyN}')
            or
            'key1.key2.keyN'
            or
            'key1.key2.keyN[]'
            or
            '{contextkey1}.{contextkey2}. ... .keyN[]'
            or
            '>context_dict_key'
            or
            '>>context_dict_key'
            or
            '>context_dict_key.{contextkey1}. ... .keyN'
            or
            '>>context_dict_key.{contextkey1}. ... .keyN'
            or
            None

        The contextdict (see after the definition) is used to format strings with ``{contextkeyN}`` syntax.
        instead of ``{contextkeyN}``, one can use a simple string to put data in a static path.

        Once the path fully formatted, let's say to ``key1.key2.keyN``, the parser will store the
        value into the result dictionnary at :
        ``{'key1':{'key2':{'keyN' : thevalue }}}``

        Example, Let's take the following data path ::

            data path : 'disks.{name}.{var}'

            if contextdict = {'name':'disk1','var':'size'}

            then the formatted data path is : 'disks.disk1.size',
            This means that the parsed data will be stored at :
            ``{'disks':{'disk1':{'size' : theparsedvalue depending on <out filter> }}}``


        One can use the string ``[]`` at the end of the path : the groupdict will be appended in a list
        ie : ``{'key1':{'key2':{'keyN' : [thevalue,...] }}}``

        if ``'>context_dict_key'`` is used, data is not store in parsed data but will be stored
        in context dict at ``context_dict_key`` key. by this way, you can differ the parsed date storage.
        To finally store to the parsed data use ``'<context_dict_key'`` for ``<out filter>``
        in some other rule.
        ``'>>context_dict_key'`` works like ``'>context_dict_key'`` but it updates data instead of
        replacing them (in others words : use ``>`` to start with an empty set of data, then
        use ``>>`` to update the data set).
        One can add dotted notation to complete data path: ``>>context_dict_key.{contextkey1}. ... .keyN``

        if None is used : nothing is stored

    ``<out filter>``
        is used to build the value to store,

        it could be :

            * None : no filter is applied, the re.MatchObject.groupdict() is stored
            * a dict : mainly to initalize the differed data set when using
              ``'>context_dict_key'`` in ``<out data path>``
            * ``'<context_dict_key'`` to store data from context dict at key ``context_dict_key``
            * a string : used as a format string with context dict, the formatted string is stored
            * a callable : to calculate the value to be stored and modify context dict if needed.
              the re.MatchObject and the context dict are given as arguments,
              it must return a tuple : the value to store AND the new context dict or None if unchanged

    **How the parser works :**

    You have a document where the syntax may change from one section to an another : You have just
    to give a name to these kind of sections : it will be your state names.
    The parser reads line by line the input text : For each line, it will look for the *first*
    matching rule from ``states_patterns_desc`` table, then will apply the rule.
    One rule has got 2 parts : the matching parameters, and the action parameters.

    Matching parameters:
        To match, a rule requires the parser to be at the specified state ``<if state>`` AND
        the line to be parsed must match the pattern ``<pattern>``. When the parser is at the first
        line, it has the default state ``top``. The pattern follow the
        standard python ``re`` module syntax. It is important to note that you must capture text
        you want to collect with the named group capture syntax, that is ``(?P<mydata>mypattern)``.
        By this way, the parser will store text corresponding to ``mypattern`` to a contextdict at
        the key ``mydata``.

    Action parameters:
        Once the rule matches, the action is to store ``<out filter>`` into the final dictionary at
        a specified ``<out data path>``.

    **Context dict :**

    The context dict is used within ``<out filter>`` and ``<out data path>``, it is a dictionary that
    is *PERSISTENT* during the whole parsing process :
    It is empty at the parsing beginning and will accumulate all captured pattern. For exemple, if
    a first rule pattern contains ``(?P<key1>.*),(?P<key2>.*)`` and matches the document line
    ``val1,val2``, the context dict will be ``{ 'key1' : 'val1', 'key2' : 'val2' }``. Then if a
    second rule pattern contains ``(?P<key2>.*):(?P<key3>.*)`` and matches the document line
    ``val4:val5`` then the context dict will be *UPDATED* to
    ``{ 'key1' : 'val1', 'key2' : 'val4', 'key3' : 'val5' }``.
    As you can see, the choice of the key names are *VERY IMPORTANT* in order to avoid collision
    across all the rules.

    Examples:

        >>> s = '''
        ... first name: Eric
        ... last name: Lapouyade'''
        >>> s | state_pattern( (('',None,'(?P<key>.*):(?P<val>.*)','{key}','{val}'),) )
        {'first_name': 'Eric', 'last_name': 'Lapouyade'}
        >>> s | state_pattern( (('',None,'(?P<key>.*):(?P<val>.*)','{key}',None),) ) #doctest: +NORMALIZE_WHITESPACE
        {'first_name': {'key': 'first name', 'val': 'Eric'},
        'last_name': {'key': 'last name', 'val': 'Lapouyade'}}
        >>> s | state_pattern((('',None,'(?P<key>.*):(?P<val>.*)','my.path.{key}','{val}'),))
        {'my': {'path': {'first_name': 'Eric', 'last_name': 'Lapouyade'}}}

        >>> s = '''Eric
        ... Guido'''
        >>> s | state_pattern( (('',None,'(?P<val>.*)','my.path.info[]','{val}'),) )
        {'my': {'path': {'info': ['Eric', 'Guido']}}}

        >>> s = '''
        ... Section 1
        ... ---------
        ...   email = ericdupo@gmail.com
        ...
        ... Section 2
        ... ---------
        ...   first name: Eric
        ...   last name: Dupont'''
        >>> s | state_pattern( (                                    #doctest: +NORMALIZE_WHITESPACE
        ... ('','section1','^Section 1',None,None),
        ... ('','section2','^Section 2',None,None),
        ... ('section1', '', '(?P<key>.*)=(?P<val>.*)', 'section1.{key}', '{val}'),
        ... ('section2', '', '(?P<key>.*):(?P<val>.*)', 'section2.{key}', '{val}')) )
        {'section1': {'email': 'ericdupo@gmail.com'},
        'section2': {'first_name': 'Eric', 'last_name': 'Dupont'}}

        >>> s = '''
        ... Disk states
        ... -----------
        ... name: c1t0d0s0
        ... state: good
        ... fs: /
        ... name: c1t0d0s4
        ... state: failed
        ... fs: /home
        ...
        ... '''
        >>> s | state_pattern( (                                    #doctest: +NORMALIZE_WHITESPACE
        ... ('top','disk',r'^Disk states',None,None),
        ... ('disk','top', r'^\s*$',None,None),
        ... ('disk', '', r'^name:(?P<diskname>.*)',None, None),
        ... ('disk', '', r'(?P<key>.*):(?P<val>.*)', 'disks.{diskname}.{key}', '{val}')) )
        {'disks': {'c1t0d0s0': {'state': 'good', 'fs': '/'},
        'c1t0d0s4': {'state': 'failed', 'fs': '/home'}}}

        >>> s = '''
        ... {
        ... name: c1t0d0s0
        ... state: good
        ... fs: /
        ... },
        ... {
        ... fs: /home
        ... name: c1t0d0s4
        ... }
        ... '''
        >>> s | state_pattern( (                                     #doctest: +NORMALIZE_WHITESPACE
        ... ('top','disk',r'{','>disk_info',{}),
        ... ('disk', '', r'(?P<key>.*):(?P<val>.*)', '>>disk_info.{key}', '{val}'),
        ... ('disk', 'top', r'}', 'disks.{disk_info[name]}', '<disk_info'),
        ... ) )
        {'disks': {'c1t0d0s0': {'name': 'c1t0d0s0', 'state': 'good', 'fs': '/'},
        'c1t0d0s4': {'fs': '/home', 'name': 'c1t0d0s4'}}}

        >>> s='firstname:Eric lastname=Lapouyade'
        >>> s | state_pattern((
        ... ('top','',r'firstname:(?P<val>\S+)','firstname','{val}'),
        ... ('top','',r'.*lastname=(?P<val>\S+)','lastname','{val}'),
        ... ))
        {'firstname': 'Eric'}

        >>> s='firstname:Eric lastname=Lapouyade'
        >>> s | state_pattern((
        ... ('top','__continue__',r'firstname:(?P<val>\S+)','firstname','{val}'),
        ... ('top','',r'.*lastname=(?P<val>\S+)','lastname','{val}'),
        ... ))
        {'firstname': 'Eric', 'lastname': 'Lapouyade'}

    """

    @classmethod
    def op(cls,text, states_patterns_desc, reflags=0, autostrip=True,**kwargs):
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
                if isinstance(ifstate, str):
                    ifstate = ifstate.split(',')
            if isinstance(pattern, str):
                pattern = re.compile(pattern,reflags)
            if isinstance(datapath, str):
                if not datapath:
                    datapath = []
                else:
                    datapath = datapath.split('.')
            states_patterns.append((ifstate, gotostate, pattern, datapath, outfilter))

        # parse the text
        for line in cls._tolist(text):
            logger.debug('state:%10s, line = %s',state, line)
            for ifstate, gotostate, pattern, datapath, outfilter in states_patterns:
                logger.debug('  ? %10s "%10s" r\'%s\' "%s" "%s"',ifstate, gotostate, pattern.pattern, datapath, outfilter)
                if not ifstate or state in ifstate:
                    m=pattern.match(line)
                    if m:
                        g = m.groupdict()
                        if autostrip:
                            g = dict([ (k,v.strip() if isinstance(v,str) else v) for k,v in list(m.groupdict().items()) ])
                        groups_context.update(g,_ifstate=ifstate,_gotostate=gotostate,_state=state)
                        logger.debug('  -> OK')
                        logger.debug('    context = %s',groups_context)
                        if datapath is not None:
                            if datapath[0].startswith('>'):
                                k = datapath[0][1:].strip()
                                if k.startswith('>'):
                                    k = k[1:]
                                    data = groups_context.setdefault(k,textops.DefaultDict(lambda k:'_%s_not_found' % k,{}))
                                else:
                                    groups_context[k] = textops.DefaultDict(lambda k:'_%s_not_found' % k,{})
                                    data = groups_context[k]
                                datapath = datapath[1:]
                            else:
                                data = root_data

                            for p in datapath:
                                p = dformat(p,groups_context,context_key_not_found)
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

                            if isinstance(outfilter, collections.Callable):
                                g,new_groups_context=outfilter(m,groups_context)
                                if new_groups_context is not None:
                                    groups_context = new_groups_context
                            elif isinstance(outfilter, str):
                                if outfilter.startswith('<'):
                                    g = groups_context.get(outfilter[1:].strip(),{})
                                else:
                                    g=dformat(outfilter,groups_context,context_key_not_found)
                            elif isinstance(outfilter, dict):
                                g = outfilter

                            if isinstance(data,list):
                                data.append(g)
                            else:
                                if isinstance(g,dict):
                                    data.update(g)
                                else:
                                    prev_data[p] = g
                        if gotostate == '__continue__':
                            continue
                        if gotostate:
                            state = gotostate
                        break
        return root_data
