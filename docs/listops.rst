..
   Generated: Thu Mar 23 15:03:55 2017

   @author : Eric Lapouyade

=======
listops
=======

.. automodule:: textops.ops.listops
.. currentmodule:: textops

after
-----
   .. autoclass:: after(pattern, get_begin=False)

afteri
------
   .. autoclass:: afteri(pattern, get_begin=False)

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
   .. autoclass:: between(begin, end, get_begin=None, get_end=None, key=None)

betweenb
--------
   .. autoclass:: betweenb(begin, end, get_begin=None, get_end=None, key=None)

betweenbi
---------
   .. autoclass:: betweenbi(begin, end, get_begin=None, get_end=None, key=None)

betweeni
--------
   .. autoclass:: betweeni(begin, end, get_begin=None, get_end=None, key=None)

doformat
--------
   .. autoclass:: doformat(format_str='{0}\n', join_str='', context={}, defvalue='-')

doreduce
--------
   .. autoclass:: doreduce(reduce_fn, initializer=None)

dorender
--------
   .. autoclass:: dorender(format_str='{0}\n', context={}, defvalue='-')

doslice
-------
   .. autoclass:: doslice(begin=0, end=sys.maxint, step=1)

dostrip
-------
   .. autoclass:: dostrip()

findhighlight
-------------
   .. autoclass:: findhighlight(pattern, line_prefix='   ', line_suffix='', hline_prefix='-> ', hline_suffix='', found_prefix='>>>', found_suffix='<<<', nlines=0, blines=0, elines=0, ellipsis='...', findall=True, ignorecase=False, line_nbr=False)

first
-----
   .. autoclass:: first()

formatdicts
-----------
   .. autoclass:: formatdicts(format_str='{key} : {val}\n', join_str='', context={}, defvalue='-')

formatitems
-----------
   .. autoclass:: formatitems(format_str='{0} : {1}\n', join_str='', context={}, defvalue='-')

formatlists
-----------
   .. autoclass:: formatlists(format_str, join_str='', context={}, defvalue='-')

greaterequal
------------
   .. autoclass:: greaterequal(value, *args, **kwargs)

greaterthan
-----------
   .. autoclass:: greaterthan(value, *args, **kwargs)

grep
----
   .. autoclass:: grep(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepc
-----
   .. autoclass:: grepc(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepci
------
   .. autoclass:: grepci(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepcv
------
   .. autoclass:: grepcv(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepcvi
-------
   .. autoclass:: grepcvi(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepi
-----
   .. autoclass:: grepi(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepv
-----
   .. autoclass:: grepv(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

grepvi
------
   .. autoclass:: grepvi(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

haspattern
----------
   .. autoclass:: haspattern(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

haspatterni
-----------
   .. autoclass:: haspatterni(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

head
----
   .. autoclass:: head(lines)

iffn
----
   .. autoclass:: iffn(filter_fn=None)

inrange
-------
   .. autoclass:: inrange(begin, end, get_begin=True, get_end=False, *args, **kwargs)

last
----
   .. autoclass:: last()

lcount
------
   .. autoclass:: lcount()

less
----
   .. autoclass:: less(lines)

lessequal
---------
   .. autoclass:: lessequal(value, *args, **kwargs)

lessthan
--------
   .. autoclass:: lessthan(value, *args, **kwargs)

linetester
----------
   .. autoclass:: linetester(, *args, **kwargs)

mapfn
-----
   .. autoclass:: mapfn(map_fn)

mapif
-----
   .. autoclass:: mapif(map_fn, filter_fn=None)

merge_dicts
-----------
   .. autoclass:: merge_dicts()

norepeat
--------
   .. autoclass:: norepeat()

outrange
--------
   .. autoclass:: outrange(begin, end, get_begin=False, get_end=False, *args, **kwargs)

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
   .. autoclass:: rmblank(pattern=None, key=None, has_key=None, attr=None, has_attr=None)

sed
---
   .. autoclass:: sed(pats, repls)

sedi
----
   .. autoclass:: sedi(pats, repls)

skess
-----
   .. autoclass:: skess(begin, end)

skip
----
   .. autoclass:: skip(lines)

sortdicts
---------
   .. autoclass:: sortdicts(key, reverse=False)

sortlists
---------
   .. autoclass:: sortlists(col, reverse=False)

span
----
   .. autoclass:: span(nbcols, fill_str='')

splitblock
----------
   .. autoclass:: splitblock(pattern, include_separator=0, skip_first=False)

subitem
-------
   .. autoclass:: subitem(n)

subitems
--------
   .. autoclass:: subitems(ntab)

subslice
--------
   .. autoclass:: subslice(begin=0, end=sys.maxint, step=1)

tail
----
   .. autoclass:: tail(lines)

uniq
----
   .. autoclass:: uniq()

wcount
------
   .. autoclass:: wcount(pattern=None, key=None)

wcounti
-------
   .. autoclass:: wcounti(pattern=None, key=None)

wcountv
-------
   .. autoclass:: wcountv(pattern=None, key=None)

wcountvi
--------
   .. autoclass:: wcountvi(pattern=None, key=None)
