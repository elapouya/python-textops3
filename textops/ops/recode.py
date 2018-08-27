# -*- coding: utf-8 -*-
#
# Created : 2016-03-09
#
# @author: Eric Lapouyade
#
""" This module gathers operations for text recoding """

from textops import TextOp
import copy
import re


MULTIPLELINESTRING_TAG = '{0:-^78}'.format('< Multiline string as list >')

class list_to_multilinestring(TextOp):
    r"""In a data structure, change all tagged list of strings into multiline strings

    This is useful to undo data recoded by :class:`multilinestring_to_list`.

    Returns:
        Same data structure with tagged lists replaced by multiple line strings.

    Examples:

        >>> data=[
        ...    [
        ...        "-------------------------< Multiline string as list >-------------------------",
        ...        "line1",
        ...        "line2",
        ...        "line3"
        ...    ],
        ...    {
        ...        "key2": [
        ...            "-------------------------< Multiline string as list >-------------------------",
        ...            "lineA",
        ...            "lineB",
        ...            "lineC",
        ...            "lineD"
        ...        ],
        ...        "key1": "one line"
        ...    }
        ... ]
        >>> data | list_to_multilinestring()
        ['line1\nline2\nline3', {'key2': 'lineA\nlineB\nlineC\nlineD', 'key1': 'one line'}]
    """

    @classmethod
    def _l2m_recode(cls,val,tag=MULTIPLELINESTRING_TAG, *args,**kwargs):
        return '\n'.join(val[1:])

    @classmethod
    def _l2m_walk(cls,obj,tag=MULTIPLELINESTRING_TAG, *args,**kwargs):
        if isinstance(obj,list):
            for key,val in enumerate(obj):
                if val and isinstance(val,list) and val[0]==tag:
                    obj[key] = cls._l2m_recode(val,*args,**kwargs)
                else:
                    cls._l2m_walk(val)
        elif isinstance(obj,dict):
            for key,val in list(obj.items()):
                if val and isinstance(val,list) and val[0]==tag:
                    obj[key] = cls._l2m_recode(val,*args,**kwargs)
                else:
                    cls._l2m_walk(val)
        elif isinstance(obj,str):
            return cls._l2m_recode(obj,*args,**kwargs)

    @classmethod
    def op(cls,text,in_place=False,tag=MULTIPLELINESTRING_TAG, *args,**kwargs):
        if text and isinstance(text,list) and text[0]==tag:
            return cls._l2m_recode(text,*args,**kwargs)
        if not in_place:
            text = copy.deepcopy(text)
        cls._l2m_walk(text,*args,**kwargs)
        return text

class multilinestring_to_list(TextOp):
    r"""In a data structure, change all multiline strings into a list of strings

    This is useful for json.dump() or dumps() in order to have a readable json data when the
    structure has some strings with many lines.
    This works on imbricated dict and list. Dictionary keys are not changed, only their values.
    Each generated list of strings is tagged with a first item (``MULTIPLELINESTRING_TAG``).
    By this way the process is reversible : see :class:`list_to_multilinestring`

    Returns:
        Same data structure with multiple line strings replaced by lists.

    Examples:

        >>> data=['line1\nline2\nline3',{'key1':'one line','key2':'lineA\nlineB\nlineC\nlineD'}]
        >>> print(json.dumps(data,indent=4))  #doctest: +NORMALIZE_WHITESPACE
        [
            "line1\nline2\nline3",
            {
                "key1": "one line",
                "key2": "lineA\nlineB\nlineC\nlineD"
            }
        ]
        >>> print(json.dumps(data | multilinestring_to_list(),indent=4) )  #doctest: +NORMALIZE_WHITESPACE
        [
            [
                "-------------------------< Multiline string as list >-------------------------",
                "line1",
                "line2",
                "line3"
            ],
            {
                "key1": "one line",
                "key2": [
                    "-------------------------< Multiline string as list >-------------------------",
                    "lineA",
                    "lineB",
                    "lineC",
                    "lineD"
                ]
            }
        ]
    """
    @classmethod
    def _m2l_recode(cls,val,tag=MULTIPLELINESTRING_TAG, *args,**kwargs):
        return [tag] + val.split('\n') if '\n' in val else val

    @classmethod
    def _m2l_walk(cls,obj,*args,**kwargs):
        if isinstance(obj,list):
            for key,val in enumerate(obj):
                if isinstance(val,str):
                    obj[key] = cls._m2l_recode(val,*args,**kwargs)
                else:
                    cls._m2l_walk(val)
        elif isinstance(obj,dict):
            for key,val in list(obj.items()):
                if isinstance(val,str):
                    obj[key] = cls._m2l_recode(val,*args,**kwargs)
                else:
                    cls._m2l_walk(val)

    @classmethod
    def op(cls,text,in_place=False,*args,**kwargs):
        if isinstance(text,str):
            return cls._m2l_recode(text,*args,**kwargs)
        if not in_place:
            text = copy.deepcopy(text)
        cls._m2l_walk(text,*args,**kwargs)
        return text