from setuptools import setup,find_packages
import os
import re

def read(*names):
    values = []
    for filename in names:
        if os.path.isfile(filename):
            try:
                with open(filename) as fd:
                    values.append(fd.read())
            except:
                values.append('')
        else:
            values.append('')
    return values


long_description = """{0}

News
====

{1}
""".format(*read('README.rst', 'CHANGES.rst'))

def get_version(pkg):
    path = os.path.join(os.path.dirname(__file__),pkg,'__init__.py')
    with open(path) as fh:
        m = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]',fh.read(),re.M)
    if m:
        return m.group(1)
    raise RuntimeError("Unable to find __version__ string in %s." % path)

setup(name='python-textops3',
      version=get_version('textops'),
      description='Python text operations module',
      long_description=long_description,
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
      ],
      keywords='textops',
      url='https://github.com/elapouya/python-textops3',
      author='Eric Lapouyade',
      author_email='elapouya@gmail.com',
      license='LGPL 2.1',
      packages=find_packages(),
      install_requires=['addicted3',
                        'python-dateutil',
                        'python-slugify',
                        'chardet'],
      extras_require={'docs': ['Sphinx', 'sphinxcontrib-napoleon']},
      eager_resources=['docs'],
      zip_safe=False)
