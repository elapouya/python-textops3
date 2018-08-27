# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This module gathers list/line operations """

from textops import TextOp, dformat, eformat, StrExt, stru
import re
import subprocess
import sys
import os

class run(TextOp):
    r""" Run the command from the input text and return execution output

    | This text operation use subprocess.Popen to call the command.
    | If the command is a string, it will be executed within a shell.
    | If the command is a list (the command and its arguments), the command is executed without a shell.
    | If a context dict is specified, the command is formatted with that context (str.format)

    Args:
        context (dict): The context to format the command to run

    Yields:
        str: the execution output

    Examples:
        >>> cmd = 'mkdir -p /tmp/textops_tests_run;\
        ... cd /tmp/textops_tests_run; touch f1 f2 f3; ls'
        >>> print(cmd | run().tostr())
        f1
        f2
        f3
        >>> print(cmd >> run())
        ['f1', 'f2', 'f3']
        >>> print(['ls', '/tmp/textops_tests_run'] | run().tostr())
        f1
        f2
        f3
        >>> print(['ls', '{path}'] | run({'path':'/tmp/textops_tests_run'}).tostr())
        f1
        f2
        f3
    """
    @classmethod
    def op(cls,text, context = {},*args,**kwargs):
        if isinstance(text, str):
            if context:
                text = text.format(**context)
            p=subprocess.Popen(['sh','-c',text],stdout=subprocess.PIPE)
        else:
            if context:
                text = [ t.format(**context) for t in text ]
            p=subprocess.Popen(text,stdout=subprocess.PIPE)
        while p.returncode is None:
            (stdout, stderr) = p.communicate()
            for line in stdout.splitlines():
                yield line.decode()

class mrun(TextOp):
    r""" Run multiple commands from the input text and return execution output

    | This works like :class:`textops.run` except that each line of the input text will be used as a command.
    | The input text must be a list of strings (list, generator, or newline separated), \
      not a list of lists. Commands will be executed inside a shell.
    | If a context dict is specified, commands are formatted with that context (str.format)

    Args:
        context (dict): The context to format the command to run

    Yields:
        str: the execution output

    Examples:
        >>> cmds = 'mkdir -p /tmp/textops_tests_run\n'
        >>> cmds+= 'cd /tmp/textops_tests_run;touch f1 f2 f3\n'
        >>> cmds+= 'ls /tmp/textops_tests_run'
        >>> print(cmds | mrun().tostr())
        f1
        f2
        f3
        >>> cmds=['mkdir -p /tmp/textops_tests_run',
        ... 'cd /tmp/textops_tests_run; touch f1 f2 f3']
        >>> cmds.append('ls /tmp/textops_tests_run')
        >>> print(cmds | mrun().tostr())
        f1
        f2
        f3
        >>> print(cmds >> mrun())
        ['f1', 'f2', 'f3']
        >>> cmds = ['ls {path}', 'echo "Cool !"']
        >>> print(cmds | mrun({'path':'/tmp/textops_tests_run'}).tostr())
        f1
        f2
        f3
        Cool !
    """
    @classmethod
    def op(cls,text, context = {}, *args,**kwargs):
        for cmd in cls._tolist(text):
            if context:
                cmd = cmd.format(**context)
            p=subprocess.Popen(['sh','-c',cmd],stdout=subprocess.PIPE)
            while p.returncode is None:
                (stdout, stderr) = p.communicate()
                for line in stdout.splitlines():
                    yield line.decode()

class xrun(TextOp):
    r""" Run the command formatted with the context taken from the input text

    Args:
        command (str): The command pattern to run (formatted against the context)
        context(dict): additional context dictionary
        defvalue(str or callable): default string to display when a key or an index is unreachable.

    Yields:
        str: the execution output

    Examples:
        to come...
    """
    @classmethod
    def op(cls,text, cmd, context={}, defvalue='unknwon',*args,**kwargs):
        for incontext in cls._tolist(text):
            if isinstance(incontext,dict):
                custom_cmd = eformat(cmd, (), dict(context, **incontext), defvalue)
            elif isinstance(context,(list,tuple)):
                custom_cmd = eformat(cmd, incontext, context, defvalue)
            else:
                custom_cmd = eformat(cmd, (incontext,), context, defvalue)
            p=subprocess.Popen(['sh','-c',custom_cmd],stdout=subprocess.PIPE)
            while p.returncode is None:
                (stdout, stderr) = p.communicate()
                for line in stdout.splitlines():
                    yield line

