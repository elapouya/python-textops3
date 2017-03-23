..
   Generated: Thu Mar 23 15:03:55 2017

   @author : Eric Lapouyade

=======
fileops
=======

.. automodule:: textops.ops.fileops
.. currentmodule:: textops

bzcat
-----
   .. autoclass:: bzcat(context={})

cat
---
   .. autoclass:: cat(context={})

find
----
   .. autoclass:: find(pattern='*', context={}, only_files=False, only_dirs=False)

findre
------
   .. autoclass:: findre(pattern='', context={}, only_files=False, only_dirs=False)

gzcat
-----
   .. autoclass:: gzcat(context={})

ls
--
   .. autoclass:: ls(pattern='*', context={}, only_files=False, only_dirs=False)

replacefile
-----------
   .. autoclass:: replacefile(filename, mode='w', newline='\n')

stats
-----
   .. autoclass:: stats()

teefile
-------
   .. autoclass:: teefile(filename, mode='w', newline='\n')

tobz2file
---------
   .. autoclass:: tobz2file(filename, mode='w', newline='\n')

tofile
------
   .. autoclass:: tofile(filename, mode='w', newline='\n')

togzfile
--------
   .. autoclass:: togzfile(filename, mode='wb', newline='\n')

tozipfile
---------
   .. autoclass:: tozipfile(filename, member, mode='w', newline='\n')

unzip
-----
   .. autoclass:: unzip(member, topath=None, password=None, context={}, ignore=False)

unzipre
-------
   .. autoclass:: unzipre(member_regex, topath=None, password=None, context={}, ignore=False)

zipcat
------
   .. autoclass:: zipcat(member, context={}, password=None)

zipcatre
--------
   .. autoclass:: zipcatre(member_regex, context={}, password=None)

ziplist
-------
   .. autoclass:: ziplist(context={})
