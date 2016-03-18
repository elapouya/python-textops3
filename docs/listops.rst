..
   Created : 2015-11-04

   @author: Eric Lapouyade

=======
listops
=======
.. automodule:: textops.ops.listops
.. currentmodule:: textops

after
-----
   .. autoclass:: after(pattern, get_begin=False, key=None)

afteri
------
   .. autoclass:: afteri(pattern, get_begin=False, key=None)

aggregate
---------
   .. autoclass:: aggregate(having, same_key=False, join_str='|')

before
------
   .. autoclass:: before(pattern, get_end=False, key=None)

beforei
-------
   .. autoclass:: beforei(pattern, get_end=False, key=None)

between
-------
   .. autoclass:: between(begin, end, get_begin=False, get_end=False, key=None)

betweeni
--------
   .. autoclass:: betweeni(begin, end, get_begin=False, get_end=False, key=None)

betweenb
--------
   .. autoclass:: betweenb(begin, end, get_begin=False, get_end=False, key=None)

betweenbi
---------
   .. autoclass:: betweenbi(begin, end, get_begin=False, get_end=False, key=None)

cat
---
   .. autoclass:: cat(context={})

doformat
--------
   .. autoclass:: doformat(format_str='{0}\\n',join_str = '', context={}, defvalue='-')

doreduce
--------
   .. autoclass:: doreduce(reduce_fn, initializer=None)

dorender
--------
   .. autoclass:: dorender(format_str='{0}\\n', context={}, defvalue='-')

doslice
-------
   .. autoclass:: doslice(begin=0, end=sys.maxsize, step=1)

dostrip
-------
   .. autoclass:: dostrip()

findhighlight
-------------
   .. autoclass:: findhighlight(pattern,line_prefix='   ',line_suffix='', hline_prefix='-> ',hline_suffix='', found_prefix='>>>',found_suffix='<<<',nlines=0, blines=0, elines=0, ellipsis='...', findall=True, ignorecase=False, line_nbr=False)

first
-----
   .. autoclass:: first( )

formatdicts
-----------
   .. autoclass:: formatdicts(format_str='{key} : {val}\\n',join_str = '', context={}, defvalue='-')

formatitems
-----------
   .. autoclass:: formatitems(format_str='{0} : {1}\\n',join_str = '', context={}, defvalue='-')

formatlists
-----------
   .. autoclass:: formatlists(format_str,join_str = '', context={}, defvalue='-')

greaterequal
------------
   .. autoclass:: greaterequal(value, key=None)

greaterthan
-----------
   .. autoclass:: greaterthan(value, key=None)

grep
----
   .. autoclass:: grep(pattern, key=None)

grepi
-----
   .. autoclass:: grepi(pattern, key=None)

grepv
-----
   .. autoclass:: grepv(pattern, key=None)

grepvi
------
   .. autoclass:: grepvi(pattern, key=None)

grepc
-----
   .. autoclass:: grepc(pattern, key=None)

grepci
------
   .. autoclass:: grepci(pattern, key=None)

grepcv
------
   .. autoclass:: grepcv(pattern, key=None)

grepcvi
-------
   .. autoclass:: grepcvi(pattern, key=None)

haspattern
----------
   .. autoclass:: haspattern(pattern, key=None)

haspatterni
-----------
   .. autoclass:: haspatterni(pattern, key=None)

head
----
   .. autoclass:: head(lines)

iffn
----
   .. autoclass:: iffn(filter_fn=None)

inrange
-------
   .. autoclass:: inrange(begin, end, get_begin=True, get_end=False, key=None)

last
----
   .. autoclass:: last( )

lcount
------
   .. autoclass:: lcount()

less
----
   .. autoclass:: less(lines)

lessequal
---------
   .. autoclass:: lessequal(value, key=None)

lessthan
--------
   .. autoclass:: lessthan(value, key=None)

merge_dicts
-----------
   .. autoclass:: merge_dicts()

mapfn
-----
   .. autoclass:: mapfn(map_fn)

mapif
-----
   .. autoclass:: mapif(map_fn, filter_fn=None)

mrun
----
   .. autoclass:: mrun(context={})

outrange
--------
   .. autoclass:: outrange(begin, end, get_begin=False, get_end=False, key=None)

renderdicts
-----------
   .. autoclass:: renderdicts(format_str='{key} : {val}', context={}, defvalue='-')

renderitems
-----------
   .. autoclass:: renderitems(format_str='{0} : {1}', context={}, defvalue='-')

renderlists
-----------
   .. autoclass:: renderlists(format_str, context={}, defvalue='-')

resplitblock
------------
   .. autoclass:: resplitblock(pattern, include_separator=0, skip_first=False)

rmblank
-------
   .. autoclass:: rmblank()

run
---
   .. autoclass:: run(context={})

sed
---
   .. autoclass:: sed(pat,repl)

sedi
----
   .. autoclass:: sedi(pat,repl)

skess
-----
   .. autoclass:: skess(begin,end)

skip
----
   .. autoclass:: skip(lines)

span
----
   .. autoclass:: span(nbcols, fill_str='')

splitblock
----------
   .. autoclass:: splitblock(pattern, include_separator=0, skip_first=False)

subslice
--------
   .. autoclass:: subslice(begin=0, end=sys.maxsize, step=1)

subitem
-------
   .. autoclass:: subitem(n)

subitems
--------
   .. autoclass:: subitems(ntab)

tail
----
   .. autoclass:: tail(lines)

uniq
----
   .. autoclass:: uniq()

wcount
------
   .. autoclass:: wcount(pattern, key=None)

wcounti
-------
   .. autoclass:: wcounti(pattern, key=None)

wcountv
-------
   .. autoclass:: wcountv(pattern, key=None)

wcountvi
--------
   .. autoclass:: wcountvi(pattern, key=None)


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

