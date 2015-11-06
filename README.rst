===============
Getting started
===============

| python-textops provides many text operations at string level, list level or whole text level.
| These operations can be chained with a 'dotted' or 'piped' notation.
| Chained operations are stored into a single lazy object, they will be executed only when an input text will be provided.

Install
-------

To install::

    pip install python-textops

Overview
--------

The usual way to use textops is something like below. IMPORTANT : Note that textops library redefines
the python **bitwise OR** operator '|' in order to use it as a 'pipe' like in a Unix shell::

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

Examples
--------

Piped then dotted notation (recommended)::

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

Documentation
-------------

Please, `read documentation here : <http://python-textops.readthedocs.org>`_