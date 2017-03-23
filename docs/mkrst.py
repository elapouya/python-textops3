# -*- coding: utf-8 -*-
#
# Created : 2017-03-23
#
# @author: Eric Lapouyade
#
import inspect
from textops import TextOp
from datetime import datetime
import os

modules = [ f[:-3] for f in os.listdir('../textops/ops') if not f.endswith('.pyc') and not f.startswith('_') ]

for mod_name in modules:
    print mod_name,'...'

    m = __import__('textops.ops.%s' % mod_name, fromlist=[''])

    out = """..
   Generated: %s

   @author : Eric Lapouyade

""" % datetime.now().strftime('%c')

    out += '=' * len(mod_name)
    out += '\n' + mod_name
    out += '\n' + '=' * len(mod_name)
    out += '\n'
    out += '\n' + '.. automodule:: textops.ops.%s' % mod_name
    out += '\n' + '.. currentmodule:: textops'
    out += '\n'

    for cls_name,cls in sorted(vars(m).items(),key=lambda x:x[0]):
        if isinstance(cls,type):
            if issubclass(cls,TextOp) and cls is not TextOp:
                meth = None
                addvarargs = False
                if hasattr(cls,'fn'):
                    meth = cls.fn
                elif hasattr(cls, 'testline'):
                    meth = cls.testline
                    addvarargs=True
                else:
                    meth = cls.op

                try:
                    if callable(meth):
                        margs = inspect.getargspec(meth)
                        args = margs.args
                        defaults = margs.defaults
                        if defaults:
                            for i,d in enumerate(reversed(margs.defaults),start=1):
                                if d == 9223372036854775807:
                                    args[-i] = '%s=sys.maxint' % args[-i]
                                else:
                                    args[-i] = '%s=%r' % (args[-i],d)

                        out += '\n' + cls_name
                        out += '\n' + '-' * len(cls_name)
                        out += '\n' + '   .. autoclass:: %s(%s%s)' % (cls_name,', '.join(args[2:]),', *args, **kwargs' if addvarargs else '')
                        out += '\n'
                except TypeError:
                    pass
    with open('%s.rst' % mod_name,'w') as fh:
        fh.write(out)