import doctest
from textops import *
import os
import json

modules = [ 'textops.base',
            'textops.ops.cast',
            'textops.ops.fileops',
            'textops.ops.listops',
            'textops.ops.parse',
            'textops.ops.recode',
            'textops.ops.runops',
            'textops.ops.strops',
            'textops.ops.wrapops',
            ]
files = [ 'docs/intro.rst' ]

failed = 0
tested = 0

print '=' * 60

for m in modules:
    print 'Testing %s ...' % m
    mod = __import__(m,fromlist=[''])
    fcount, tcount = doctest.testmod(mod,globs=globals(),optionflags=doctest.REPORT_NDIFF)
    failed += fcount
    tested += tcount

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in files:
    print 'Testing %s ...' % f
    path = os.path.join(base_dir,f)
    fcount, tcount = doctest.testfile(path,False,globs=globals(),optionflags=doctest.REPORT_NDIFF)
    failed += fcount
    tested += tcount

print '=' * 60
print 'Number of tests : %s' % tested
print 'Failed : %s' % failed