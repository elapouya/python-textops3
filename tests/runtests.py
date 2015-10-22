import doctest
from textops import *

modules = [ 'textops.ops.strops' ]

for m in modules:
    print 'Testing %s ...' % m
    mod = __import__(m,fromlist=[''])
    doctest.testmod(mod,globs=globals())
