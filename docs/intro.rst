===============
Getting started
===============

| python-textops provides many text operations at string level, list level or whole text level.
| These operations can be chained with a 'dotted' or 'piped' notation.
| You can also build lazy filter objects to apply operations after their definition.

Install
-------

To install::

    pip install python-textops

Quickstart
----------

Usage::

   from textops import *

Here is a text filter to find the first line with an error and put it in uppercase::

   myfilter = grepi('error').first().upper()

**Note :**
   str standard methods (like 'upper') can be used directly in chained dotted notation

You can use unix shell 'pipe' symbol into python code to chain operations::

   myfilter = grepi('error') | first() | strop.upper()

**Note :**
   str methods must be prefixed with 'strop.' in piped notations.

To execute the filter::

   >>> myfilter = grepi('error').first().upper()
   >>> print myfilter('this is an error\nthis is a warning')
   THIS IS AN ERROR

**Note :**
   python generators are used as far as possible to be able to manage huge data set like big files.
   Prefer to use the dotted notation, it is more optimized.

To execute operations at once, specify the input text ::

   >>> print grepi('error').first().upper()('this is an error\nthis is a warning')
   THIS IS AN ERROR

... or use one pipe symbol (the bitwise operator has been redefined), 
then use dotted notation for other operations : this is the **recommended way to use textops**::

   >>> print 'this is an error\nthis is a warning' | grepi('error').first().upper()
   THIS IS AN ERROR

... or use the pipe everywhere (internally a little less optimized, but looks like shell)::

   >>> print 'this is an error\nthis is a warning' | grepi('error') | first() | strop.upper()
   THIS IS AN ERROR

To execute ops directly from strings or lists with the dotted notation,
you just have to use textops Extended types : ``StrExt``, ``ListExt`` or ``DictExt`` ::

   >>> s = StrExt('this is an error\nthis is a warning')
   >>> print s.grepi('error').first().upper()
   THIS IS AN ERROR

**Note :**
   As soon as you are using textops Extended type, generators cannot be used anymore :
   all data must fit into memory (it is usually the case).

You can use the operations result in a 'for' loop::

   >>> open('/tmp/errors.log','w').write('error 1\nwarning 1\nwarning 2\nerror 2')
   >>> for line in '/tmp/errors.log' | cat().grepi('warning').head(1).upper():
   ...   print line
   WARNING 1

A shortcut is possible when there is no parameter in the first operation : the input text can be put
as the first parameter of the first operation::

   >>> open('/tmp/errors.log','w').write('error 1\nwarning 1\nwarning 2\nerror 2')
   >>> for line in cat('/tmp/errors.log').grepi('warning').head(1).upper():
   ...   print line
   WARNING 1

...The shortcut works because the 'for' loop triggers operations execution. The print or str() will
also trigger operations execution. for simple assignement, you have to trigger manually
with special attributes::

   >>> open('/tmp/errors.log','w').write('error 1\nwarning 1')
   >>> logs = cat('/tmp/errors.log').s
   >>> print type(logs)
   <class 'textops.base.StrExt'>
   >>> print logs
   error 1
   warning 1

   >>> logs = cat('/tmp/errors.log').l
   >>> print type(logs)
   <class 'textops.base.ListExt'>
   >>> print logs
   ['error 1', 'warning 1']

   >>> logs = cat('/tmp/errors.log').g
   >>> print type(logs)
   <type 'generator'>
   >>> print list(logs)
   ['error 1', 'warning 1']

**Note :**
   | ``.s`` : execute operations and get a string
   | ``.l`` : execute operations and get a list of strings
   | ``.g`` : execute operations and get a generator of strings

your input text can be a list::

   >>> print ['this is an error','this is a warning'] | grepi('error').first().upper()
   THIS IS AN ERROR

textops works also on list of lists (you can optionally grep on a specific column)::

   >>> l = ListExt([['this is an','error'],['this is a','warning']])
   >>> print l.grepi('error',1).first().upper()
   ['THIS IS AN', 'ERROR']

... or a list of dicts (you can optionally grep on a specific key)::

   >>> l = ListExt([{ 'msg':'this is an', 'level':'error'},{'msg':'this is a','level':'warning'}])
   >>> print l.grepi('error','level').first()
   {'msg': 'this is an', 'level': 'error'}

textops provides DictExt class that has got the attribute access functionnality::

   >>> d = DictExt({ 'a' : { 'b' : 'this is an error\nthis is a warning'}})
   >>> print d.a.b.grepi('error').first().upper()
   THIS IS AN ERROR

If attributes are reserved or contains space, one can use normal form::

   >>> d = DictExt({ 'this' : { 'is' : { 'a' : {'very deep' : { 'dict' : 'yes it is'}}}}})
   >>> print d.this['is'].a['very deep'].dict
   yes it is

You can use dotted notation for setting information in dict BUT only on one level at a time::

   >>> d = DictExt()
   >>> d.a = DictExt()
   >>> d.a.b = 'this is my logging data'
   >>> print d
   {'a': {'b': 'this is my logging data'}}

You saw ``cat``, ``grep``, ``first``, ``head`` and ``upper``, but there are many more operations available.

Read The Fabulous Manual !

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

