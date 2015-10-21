==============
python-textops
==============

Introduction
------------

python-textops provides many text operations at string level, line level or whole text level.
These operations can be chained with the 'dotted' notation or 'piped' notation. 
You can also build a lazy filter object to apply operations after their definition.


Quickstart
----------

To install::

    pip install python-textops

Usage::

    from textops import *

    # here a filter to find the first line with an error and put it in uppercase :
    myfilter = grepi('error').first().upper()
    # Note : str standard methods (like 'upper') can be used directly in chained dotted notation
    
    # you can use unix shell 'pipe' symbol into python code to chain operations :
    myfilter = grepi('error') | first() | strop.upper()
    # Note : str methods must be prefixed with 'strop.'

    # To execute the filter :
    print myfilter('this is an error')
    # Note : python generators are used as far as possible to be able to manage huge data set like big files.

    # To execute operations at once, specify the input text:
    print grepi('error').first().upper()('this is an error')

    # or use the pipe symbol (the bitwise operator has been redefined):
    print 'this is an error' | grepi('error').first().upper()

    # or use the pipe everywhere : 
    print 'this is an error\nthis is a warning' | grepi('error') | first() | strop.upper()
    
    # or use chained textop in a 'for' loop:
    for line in cat('errors.log'):
        print line

    # To execute ops directly from strings or lists with the dotted notation, 
    # you just have to use textops Extended types : StrExt and ListExt :
    s = StrExt('this is an error\nthis is a warning')
    print s.grepi('error').first().upper()
    # Note : As soon as you are using textops Extended type, generators cannot be used anymore : all data must fit into memory

    # your text can have multiple lines :
    print 'this is an error\nthis is a warning'|grepi('error').first().upper()

    # or can be a list :
    print ['this is an error','this is a warning']|grepi('error').first().upper()

    # textops works also on list of list (you can optionally grep on a specific column) :
    print ListExt([['this is an','error'],['this is a','warning']]).grepi('error',1).first().upper()

    # ... or a list of dict (you can optionally grep on a specific key) :
    print ListExt([{ 'msg':'this is an', 'level':'error'},{'msg':'this is a','level':'warning'}]).grepi('error','level').first()

    # textops provides DictExt class that has got the attribute access functionnality :
    d = DictExt({ 'a' : { 'b' : 1}})
    print d.a.b

    # If attributes are reserved or contains space, one can use normal form :
    d = DictExt({ 'this' : { 'is' : { 'a' : {'very deep' : { 'dict' : 'yes it is'}}}}})
    print d.this['is'].a['very deep'].dict

    # You can use dotted notation for setting information in dict BUT only on one level at a time :
    d = DictExt()
    d.a = DictExt()
    d.a.b = 2


Example ::

    # Using textops Extended type "StrExt" (Not optimized for big files) :
    logs = StrExt(open('my_log_file.log').read())
    errors = logs.range('2014','2016').grepi(r'error|critical').cut(':')
    for date,level,msg in errors:
        print 'date = %s, level = %s : %s' % (date,level,msg)

    OR

    # optimized for huge file:
    for date,level,msg in cat('my_log_file.log').range('2014','2016').grepi(r'error|critical').cut(':'):
        print 'date = %s, level = %s : %s' % (date,level,msg)

    # Example of my_log_file.log:

    2013-03-01:Info:textops rocks
    2014-11-01:Info:you can also use pipe symbole to inject data in the ops
    2015-05-22:Error:textops can manage huge file
    2015-07-23:Critical:it uses generators along the chained ops when possible
    2016-09-12:Info:textops provides extended basic types : StrExt, DictExt, ListExt, UnicodeExt

    # Result:

    date = 2015-05-22, level = Error : textops can manage huge file
    date = 2015-07-23, level = Critical : it uses generators along the chained ops when possible



Available operations :
----------------------

String operations :
...................

* cut
* cutca
* cutdct
* cutkv
* cutre
* echo
* length
* matches
* splitln

Line/list operations:
.....................

* after
* afteri
* before
* beforei
* between
* betweenb
* betweenbi
* betweeni
* cat
* doreduce
* first
* formatdicts
* formatitems
* grep
* grepc
* grepci
* grepcv
* grepcvi
* grepi
* grepv
* grepvi
* haspattern
* haspatterni
* head
* iffn
* last
* mapfn
* mapif
* merge_dicts
* range
* rmblank
* run
* sed
* sedi
* slice
* span
* subitem
* subitems
* tail
* uniq

Whole text operations:
......................

* find_first_pattern
* find_first_patterni
* find_pattern
* find_patterni
* find_patterns
* find_patternsi
* mgrep
* mgrepi
* mgrepv
* mgrepvi
* parse_indented
* parseg
* parsegi
* parsek
* parseki
* parsekv
* parsekvi
* state_pattern

Wrapped from python operations:
...............................

* alltrue
* anytrue
* dosort
* getmax
* getmin
* linenbr

Cast operations:
................

* todatetime
* tofloat
* toint
* tolist
* toliste
* toslug
* tostr
* tostre
* tostrenl
* tostrnl

Extended Types:
...............

* DictExt
* ListExt
* StrExt
* UnicodeExt