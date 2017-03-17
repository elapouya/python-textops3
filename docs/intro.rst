..
   Created : 2015-11-04

   @author: Eric Lapouyade


===============
Getting started
===============


Install
-------

To install::

    pip install python-textops

Quickstart
----------

The usual way to use textops is something like below. IMPORTANT : Note that textops library redefines
the python **bitwise OR** operator ``|`` in order to use it as a 'pipe' like in a Unix shell::

   from textops import *

   result = "an input text" | my().chained().operations()

   or

   for result_item in "an input text" | my().chained().operations():
      do_something(result_item)

   or

   myops = my().chained().operations()
   # and later in the code, use them :
   result = myops("an input text")
   or
   result = "an input text" | myops

An "input text" can be :

   * a simple string,
   * a multi-line string (one string having newlines),
   * a list of strings,
   * a strings generator,
   * a list of lists (useful when you cut lines into columns),
   * a list of dicts (useful when you parse a line).

So one can do::

   >>> 'line1line2line3' | grep('2').tolist()
   ['line1line2line3']
   >>> 'line1\nline2\nline3' | grep('2').tolist()
   ['line2']
   >>> ['line1','line2','line3'] | grep('2').tolist()
   ['line2']
   >>> [['line','1'],['line','2'],['line','3']] | grep('2').tolist()
   [['line', '2']]
   >>> [{'line':1},{'line':'2'},{'line':3}] | grep('2').tolist()
   [{'line': '2'}]

.. note::

   As many operations return a generator, they can be used directly in for-loops, but in this
   documentation we added ``.tolist()`` to show the result as a list.

Textops library also redefines ``>>`` operator that works like the ``|`` except that it converts
generators results into lists::

   >>> 'a\nb' | grep('a')                                # doctest: +ELLIPSIS
   <generator object extend_type_gen at ...>
   >>> 'a\nb' | grep('a').tolist()
   ['a']
   >>> 'a\nb' >> grep('a')
   ['a']
   >>> for line in 'a\nb' | grep('a'):
   ...     print line
   a
   >>> 'abc' | length()
   3
   >>> 'abc' >> length()
   3

.. note::

   You should use the pipe ``|`` when you are expecting a huge result or when using for-loops,
   otherwise, the ``>>`` operator is easier to handle as you are not keeping generators.

Here is an example of chained operations to find the first line with an error and put it in uppercase::

   >>> from textops import *
   >>> myops = grepi('error').first().upper()

.. note::

   str standard methods (like 'upper') can be used directly in chained dotted notation.

You can use unix shell 'pipe' symbol into python code to chain operations::

   >>> from textops import *
   >>> myops = grepi('error') | first() | strop.upper()

The main interest for the piped notation is the possibility to avoid importing all operations,
that is to import only textops module::

   >>> import textops as op
   >>> myops = op.grepi('error') | op.first() | op.strop.upper()

.. note::

   str methods must be prefixed with ``strop.`` in piped notations.

Chained operations are not executed (lazy object) until an input text has been provided. You can
use chained operations like a function, or use the pipe symbol to "stream" input text::

   >>> myops = grepi('error').first().upper()
   >>> print myops('this is an error\nthis is a warning')
   THIS IS AN ERROR
   >>> print 'this is an error\nthis is a warning' | myops
   THIS IS AN ERROR

.. note::

   python generators are used as far as possible to be able to manage huge data set like big files.
   Prefer to use the dotted notation, it is more optimized.

To execute operations at once, specify the input text on the same line::

   >>> print grepi('error').first().upper()('this is an error\nthis is a warning')
   THIS IS AN ERROR

A more readable way is to use ONE pipe symbol, then use dotted notation for other operations :
this is the **recommended way to use textops**. Because of the first pipe, there is no need to use
special textops Extended types, you can use standard strings or lists as an input text::

   >>> print 'this is an error\nthis is a warning' | grepi('error').first().upper()
   THIS IS AN ERROR

You could use the pipe everywhere (internally a little less optimized, but looks like shell)::

   >>> print 'this is an error\nthis is a warning' | grepi('error') | first() | strop.upper()
   THIS IS AN ERROR

To execute an operation directly from strings, lists or dicts *with the dotted notation*,
you must use textops Extended types : ``StrExt``, ``ListExt`` or ``DictExt``::

   >>> s = StrExt('this is an error\nthis is a warning')
   >>> print s.grepi('error').first().upper()
   THIS IS AN ERROR

.. note::

   As soon as you are using textops Extended type, textops cannot use gnerators internally anymore :
   all data must fit into memory (it is usually the case, so it is not a real problem).

You can use the operations result in a 'for' loop::

   >>> open('/tmp/errors.log','w').write('error 1\nwarning 1\nwarning 2\nerror 2')
   >>> for line in '/tmp/errors.log' | cat().grepi('warning').head(1).upper():
   ...   print line
   WARNING 1

A shortcut is possible : the input text can be put as the first parameter of the first operation.
nevertheless, in this case, despite the input text is provided, chained operations won't be executed
until used in a for-loop, converted into a string/list or forced by special attributes::

   >>> open('/tmp/errors.log','w').write('error 1\nwarning 1\nwarning 2\nerror 2')

   # Here, operations are excuted because 'print' converts into string :
   # it triggers execution.
   >>> print cat('/tmp/errors.log').grepi('warning').head(1).upper()
   WARNING 1

   # Here, operations are excuted because for-loops or list casting triggers execution.
   >>> for line in cat('/tmp/errors.log').grepi('warning').head(1).upper():
   ...   print line
   WARNING 1

   # Here, operations are NOT executed because there is no for-loops nor string/list cast :
   # operations are considered as a lazy object, that is the reason why
   # only the object representation is returned (chained operations in dotted notation)
   >>> logs = cat('/tmp/errors.log')
   >>> logs
   cat('/tmp/errors.log')
   >>> print type(logs)
   <class 'textops.ops.fileops.cat'>

   # To force execution, use special attribute .s .l or .g :
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

.. note::

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

   >>> l = ListExt([{ 'msg':'this is an', 'level':'error'},
   ... {'msg':'this is a','level':'warning'}])
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

Run tests
---------

Many doctests as been developped, you can run them this way::

   cd tests
   python ./runtests.py

Build documentation
-------------------

An already compiled and up-to-date documentation should be available `here <http://python-textops.readthedocs.org>`_.
Nevertheless, one can build the documentation :

For HTML::

   cd docs
   make html
   cd _build/html
   firefox ./index.html

For PDF, you may have to install some linux packages::

   sudo apt-get install texlive-latex-recommended texlive-latex-extra
   sudo apt-get install texlive-latex-base preview-latex-style lacheck tipa

   cd docs
   make latexpdf
   cd _build/latex
   evince python-textops.pdf   (evince is a PDF reader)

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

