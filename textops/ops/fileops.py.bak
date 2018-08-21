# -*- coding: utf-8 -*-
#
# Created : 2015-04-03
#
# @author: Eric Lapouyade
#
""" This modules provides casting features, that is to force the output type """

from textops import TextOp, pp, stru
from zipfile import ZipFile
import gzip
import os
import re
from glob import iglob
import fnmatch
import bz2

class cat(TextOp):
    r""" Return the content of the file with the path given in the input text

    If a context dict is specified, the path is formatted with that context (str.format)
    The file must have a textual content.

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

class ls(TextOp):
    r""" Return a list of files/dirs

    it uses the python :func:`glob.glob` so it will do a Unix style pathname pattern expansion

    Args:
        pattern (str): the file pattern to search
        context (dict): The context to format the file path (Optionnal)
        only_files (bool): get only files (Default : False)
        only_dirs (bool): get only dirs (Default : False)

    Yields:
        str: file name matching the pattern

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, pattern='*', context = {}, only_files=False, only_dirs=False, *args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            for f in iglob(path):
                if only_dirs and not os.path.isdir(f):
                    continue
                if only_files and not os.path.isfile(f):
                    continue
                yield f

class stats(TextOp):
    r""" Return a dict or a list of dicts containing the filename and its statistics

    it uses the python :func:`os.stat` to get file statistics, the filename is stored in 'filename' key

    Yields:
        dict: file name and file statistics in the same dict

    Examples:
        To come ...
    """
    @classmethod
    def op(cls, text, *args,**kwargs):
        for path in cls._tolist(text):
            stat = os.stat(path)
            d = { k:getattr(stat,k) for k in dir(stat) if not k.startswith('_') }
            d.update(filename=path)
            yield d

class find(TextOp):
    r""" Return a list of files/dirs matching a pattern

    find recursively files/dirs matching a pattern. The pattern is a unix-like pattern,
    it searches only against the last part of the path (basename)

    Args:
        pattern (str): the file pattern to search
        context (dict): The context to format the file path (Optionnal)
        only_files (bool): get only files (Default : False)
        only_dirs (bool): get only dirs (Default : False)

    Yields:
        str: file name matching the pattern

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, pattern='*', context = {}, only_files=False, only_dirs=False, *args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            for root, dirs, files in os.walk(path):
                if not only_files:
                    for name in dirs:
                        if fnmatch.fnmatch(name, pattern):
                            yield os.path.join(root, name)
                if not only_dirs:
                    for name in files:
                        if fnmatch.fnmatch(name, pattern):
                            yield os.path.join(root, name)

class findre(TextOp):
    r""" Return a list of files/dirs matching a pattern

    find recursively files/dirs matching a pattern. The pattern is a python regex,
    it searches against the whole file path

    Args:
        pattern (str or regex): the file pattern to search
        context (dict): The context to format the file path (Optionnal)
        only_files (bool): get only files (Default : False)
        only_dirs (bool): get only dirs (Default : False)

    Yields:
        str: file name matching the pattern

    Examples:
        To come ...
    """
    @classmethod
    def op(cls,text, pattern='', context = {}, only_files=False, only_dirs=False, *args,**kwargs):
        if isinstance(pattern,basestring):
            pattern = re.compile(pattern)
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            for root, dirs, files in os.walk(path):
                if not only_files:
                    for name in dirs:
                        f=os.path.join(root, name)
                        if pattern.search(f):
                            yield f
                if not only_dirs:
                    for name in files:
                        f=os.path.join(root, name)
                        if pattern.search(f):
                            yield f


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

class unzip(TextOp):
    r""" Extract ONE file from a zip archive

    The zip file name is taken from text input.

    Args:
        member (str): the file name to extract from the zip archive
        topath (str): the directory path to extract to (Default : current directory)
        password (str): The password to open zip if it is encrypted (Optionnal)
        context (dict): The context to format the file path and topath argument (Optionnal)
        ignore (bool): If True do not raise exception when member does not exist (Default : False)

    Yields:
        str: the member file path

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
                yield os.path.join(topath or '',member)

class unzipre(TextOp):
    r""" Extract files having a specified name pattern from a zip archive

    The zip file name is taken from text input.

    Args:
        member_regex (str or regex): the regex to find the first file inside the zip to read
        topath (str): the directory path to extract to (Default : current directory)
        password (str): The password to open zip if it is encrypted (Optionnal)
        context (dict): The context to format the file path and topath argument (Optionnal)

    Yields:
        str: the extracted files path

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
                            yield os.path.join(topath or '',zipinfo.filename)

class tofile(TextOp):
    r"""send input to file

    ``tofile()`` must be the last text operation, if you want to write to file AND continue some text operations,
    use :class:`textops.teefile` instead. if you want to write the same file than the one opened,
    please use :class:`textops.replacefile` instead.

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

class replacefile(TextOp):
    r"""send input to file

    Works like :class:`textops.tofile` except it takes care to consume input text generators before writing the file.
    This is mandatory when doing some in-file textops.
    The drawback is that the data to write to file is stored temporarily in memory.

    This does not work::

        cat('myfile').sed('from_patter','to_pattern').tofile('myfile').n

    This works::

        cat('myfile').sed('from_patter','to_pattern').replacefile('myfile').n

    Args:
        filename (str): The file to send output to
        mode (str): File open mode (Default : 'w')
        newline (str): The newline string to add for each line (default: '\n')

    Examples:
        >>> cat('myfile').sed('from_patter','to_pattern').replacefile('myfile').n

    """
    @classmethod
    def op(cls,text,filename,mode='w', newline='\n',*args,**kwargs):
        # get output BEFORE opening the file
        out = TextOp.make_string(text, newline)
        with open(filename, mode) as fh:
            fh.write(out)

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

    ``tozipfile()`` must be the last text operation.

    Args:
        filename (str): The zip file to send COMPRESSED output to
        member (str): The name of the file INSIDE the zip file to send UNCOMPRESSED output to
        mode (str): File open mode (Default : 'w', use 'a' to append an existing zip or create it if not present)
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

class togzfile(TextOp):
    r"""send input to gz file

    ``togzfile()`` must be the last text operation

    Args:
        filename (str): The gz file to send COMPRESSED output to
        mode (str): File open mode (Default : 'wb')
        newline (str): The newline string to add for each line (default: '\n')

    Examples:
        >>> '/var/log/dmesg' | cat() | grep('error') | togzfile('/tmp/errors.log.gz')

    Note:
        Password encrypted zip creation is not supported.

    """
    @classmethod
    def op(cls,text,filename, mode='wb', newline='\n',*args,**kwargs):
            with gzip.open(filename,mode) as fh:
                fh.write(TextOp.make_string(text,newline))

class gzcat(TextOp):
    r"""Uncompress the gzfile(s) with the name(s) given in input text

    If a context dict is specified, the path is formatted with that context (str.format)
    The gzipped file must have a textual content.

    Args:
        context (dict): The context to format the file path (Optionnal)


    Note:
        A list of filename can be given as input text : all specified files will be uncompressed

    Note:
        Password encrypted zip creation is not supported.

    """
    @classmethod
    def op(cls,text, context = {},*args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with gzip.open(path) as fh:
                    for line in fh:
                        yield line.rstrip('\r\n')


class tobz2file(TextOp):
    r"""send input to gz file

    ``tobz2file()`` must be the last text operation

    Args:
        filename (str): The gz file to send COMPRESSED output to
        mode (str): File open mode (Default : 'wb')
        newline (str): The newline string to add for each line (default: '\n')

    Examples:
        >>> '/var/log/dmesg' | cat() | grep('error') | togzfile('/tmp/errors.log.gz')

    Note:
        Password encrypted zip creation is not supported.

    """
    @classmethod
    def op(cls,text,filename, mode='w', newline='\n',*args,**kwargs):
            with bz2.BZ2File(filename,mode) as fh:
                fh.write(TextOp.make_string(text,newline))

class bzcat(TextOp):
    r"""Uncompress the bz2 file(s) with the name(s) given in input text

    If a context dict is specified, the path is formatted with that context (str.format)
    The gzipped file must have a textual content.

    Args:
        context (dict): The context to format the file path (Optionnal)

    Examples:
        >>> '/var/log/dmesg' | cat() | grep('error') | togzfile('/tmp/errors.log.gz')

    Note:
        A list of filename can be given as input text : all specified files will be uncompressed

    """
    @classmethod
    def op(cls,text, context = {},*args,**kwargs):
        for path in cls._tolist(text):
            if context:
                path = path.format(**context)
            path = os.path.expanduser(path)
            if os.path.isfile(path) or os.path.islink(path):
                with bz2.BZ2File(path) as fh:
                    for line in fh:
                        yield line.rstrip('\r\n')
