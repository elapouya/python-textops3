import doctest
from textops import *
import os

modules = [ 'textops.ops.strops', 'textops.ops.cast']
files = [ 'docs/intro.rst' ]

for m in modules:
    print 'Testing %s ...' % m
    mod = __import__(m,fromlist=[''])
    doctest.testmod(mod,globs=globals())

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in files:
    print 'Testing %s ...' % f
    path = os.path.join(base_dir,f)
    doctest.testfile(path,False,globs=globals())