# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This modules provides casting features, that is to force the output type """

from textops import TextOp, pp, stru
from zipfile import ZipFile
import os
import re

class cat(TextOp):
    r""" Return the content of the file with the path given in the input text

    If a context dict is specified, the path is formatted with that context (str.format)

    Args:
        context (dict): The context to format the file path (Optionnal)

    Yields:
        str: the file content lines

    Examples:
        >>> open('/tmp/testfile.txt','w').write('here is the file content')
        >>> '/tmp/testfile.txt' | cat()                 #doctest: +ELLIPSIS
        <generator object extend_type_gen at ...>
        >>> '/tmp/testfile.txt' | cat().tostr()
        'here is the file content'
        >>> '/tmp/testfile.txt' >> cat()
        ['here is the file content']
        >>> '/tmp/testfile.txt' | cat().upper().tostr()
        'HERE IS THE FILE CONTENT'
        >>> context = {'path':'/tmp/'}
        >>> '{path}testfile.txt' | cat(context)                 #doctest: +ELLIPSIS
        <generator object extend_type_gen at ...>
        >>> '{path}testfile.txt' | cat(context).tostr()
        'here is the file content'
        >>> cat('/tmp/testfile.txt').s
        'here is the file content'
        >>> cat('/tmp/testfile.txt').upper().s
        'HERE IS THE FILE CONTENT'
        >>> cat('/tmp/testfile.txt').l
        ['here is the file content']
        >>> cat('/tmp/testfile.txt').g                 #doctest: +ELLIPSIS
        <generator object extend_type_gen at ...>
        >>> for line in cat('/tmp/testfile.txt'):
        ...     print line
        ...
        here is the file content
        >>> for bits in cat('/tmp/testfile.txt').grep('content').cut():
        ...     print bits
        ...
        ['here', 'is', 'the', 'file', 'content']
        >>> open('/tmp/testfile.txt','w').write('here is the file content\nanother line')
        >>> '/tmp/testfile.txt' | cat().tostr()
        'here is the file content\nanother line'
        >>> '/tmp/testfile.txt' | cat().tolist()
        ['here is the file content', 'another line']
        >>> cat('/tmp/testfile.txt').s
        'here is the file content\nanother line'
        >>> cat('/tmp/testfile.txt').l
        ['here is the file content', 'another line']
        >>> context = {'path': '/tmp/'}
        >>> cat('/{path}/testfile.txt',context).l
        ['here is the file content', 'another line']
        >>> for bits in cat('/tmp/testfile.txt').grep('content').cut():
        ...     print bits
        ...
        ['here', 'is', 'the', 'file', 'content']
    """
    @classmethod
    def op(cls,text, context = {},*args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with open(path) as fh:
                    for line in fh:
                        yield line.rstrip('\r\n')


class zipcat(TextOp):
    r""" Return the content of the zip file with the path given in the input text

    If a context dict is specified, the path is formatted with that context (str.format)

    Args:
        member (str): the file inside the zip to read
        context (dict): The context to format the file path (Optionnal)
        password (str): The password to open zip if it is encrypted (Optionnal)

    Yields:
        str: the file content lines

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, member, context = {}, password=None, *args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with ZipFile(path) as zipfile:
                    for line in zipfile.read(member,password).splitlines():
                        yield line.rstrip('\r\n')


class zipcatre(TextOp):
    r""" Return the content of the zip file with the path given in the input text

    If a context dict is specified, the path is formatted with that context (str.format)
    Works like :class:`textops.zipcat` except that the member name is a regular expression :
    it will cat all member matching the regex

    Args:
        member_regex (str or regex): the regex to find the files inside the zip to read
        context (dict): The context to format the file path (Optionnal)
        password (str): The password to open zip if it is encrypted (Optionnal)

    Yields:
        str: the file content lines

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, member_regex, context = {}, password=None, *args,**kwargs):
        if isinstance(member_regex,basestring):
            member_regex = re.compile(member_regex)
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with ZipFile(path) as zipfile:
                    for zipinfo in zipfile.infolist():
                        if member_regex.search(zipinfo.filename):
                            for line in zipfile.read(zipinfo,password).splitlines():
                                yield line.rstrip('\r\n')


class ziplist(TextOp):
    r""" Return the name of the files included within the zip file

    The zip file name is taken from text input

    Args:
        context (dict): The context to format the file path (Optionnal)

    Yields:
        str: the file names

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, context = {}, *args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with ZipFile(path) as zipfile:
                    for zipinfo in zipfile.infolist():
                        yield zipinfo.filename

class zipextract(TextOp):
    r""" Extract a file from a zip archive

    The zip file name is taken from text input.

    Args:
        member (str): the file name to extract from the zip archive
        topath (str): the directory path to extract to (Default : current directory)
        password (str): The password to open zip if it is encrypted (Optionnal)
        context (dict): The context to format the file path and topath argument (Optionnal)
        ignore (bool): If True do not raise exception when member does not exist (Default : False)

    Yields:
        str: the zip archive name

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, member, topath=None, password=None, context = {}, ignore=False, *args,**kwargs):
        if topath and context:
            topath = topath.format(**context)
            topath = os.path.expanduser(topath)
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with ZipFile(path) as zipfile:
                    try:
                        zipfile.extract(member,topath,password)
                    except KeyError:
                        if not ignore:
                            raise
                yield path

class zipextractre(TextOp):
    r""" Extract files having a specified name pattern from a zip archive

    The zip file name is taken from text input.

    Args:
        member_regex (str or regex): the regex to find the first file inside the zip to read
        topath (str): the directory path to extract to (Default : current directory)
        password (str): The password to open zip if it is encrypted (Optionnal)
        context (dict): The context to format the file path and topath argument (Optionnal)

    Yields:
        str: the zip archive name

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, member_regex, topath=None, password=None, context = {}, ignore=False, *args,**kwargs):
        if isinstance(member_regex,basestring):
            member_regex = re.compile(member_regex)
        if topath and context:
            topath = topath.format(**context)
            topath = os.path.expanduser(topath)
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with ZipFile(path) as zipfile:
                    for zipinfo in zipfile.infolist():
                        if member_regex.search(zipinfo.filename):
                            zipfile.extract(zipinfo,topath,password)
                yield path

class tofile(TextOp):
    r"""send input to file

    tofile() must the last text operation, if you want to write to file AND continue some text operations,
    use :class:`textops.teefile` instead.

    Args:
        filename (str): The file to send output to
        mode (str): File open mode (Default : 'w')
        newline (str): The newline string to add for each line (default: '\n')

    Examples:
        >>> '/var/log/dmesg' | cat() | grep('error') | tofile('/tmp/errors.log')

    """
    @classmethod
    def op(cls,text,filename,mode='w', newline='\n',*args,**kwargs):
        with open(filename,mode) as fh:
            for i,line in enumerate(cls._tolist(text)):
                if i>0:
                    fh.write(newline)
                fh.write(stru(line))

class teefile(TextOp):
    r"""send input to file AND yield the same input text

    Args:
        filename (str): The file to send output to
        mode (str): File open mode (Default : 'w')
        newline (str): The newline string to add for each line (default: '\n')

    Yields:
        str, list or dict: the same input text

    Examples:
        >>> '/var/log/dmesg' | cat() | teefile('/tmp/dmesg_before') | grep('error') | tofile('/tmp/dmesg_after')

    """
    @classmethod
    def op(cls,text,filename,mode='w', newline='\n',*args,**kwargs):
        with open(filename,mode) as fh:
            for i,line in enumerate(cls._tolist(text)):
                if i>0:
                    fh.write(newline)
                fh.write(stru(line))
                yield line

class tozipfile(TextOp):
    r"""send input to zip file

    tozipfile() must the last text operation

    Args:
        filename (str): The zip file to send COMPRESSED output to
        member (str): The name of the file INSIDE the zip file to send UNCOMPRESSED output to
        newline (str): The newline string to add for each line (default: '\n')

    Examples:
        >>> '/var/log/dmesg' | cat() | grep('error') | tozipfile('/tmp/errors.log.zip','/tmp/errors.log')

    Note:
        Password encrypted zip creation is not supported.

    """
    @classmethod
    def op(cls,text,filename,member, mode='w', newline='\n',*args,**kwargs):
            with ZipFile(filename,mode) as zipfile:
                zipfile.writestr(member,TextOp.make_string(text,newline))