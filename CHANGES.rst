0.3.0 (2017-03-23)
------------------
* add fileops and runops

0.2.14 (2017-02-28)
-------------------
* sed() and sedi() now accept list of patterns to search and list of replacement strings

0.2.12 (2017-02-27)
-------------------
* add tofile() and teefile()

0.2.11 (2017-01-31)
-------------------
* Remove version limitation over sphinx package in setup.py

0.2.10 (2017-01-26)
-------------------
* added textops.extend_type

0.2.9 (2016-12-06)
------------------

* Fix autostrip in state_pattern() when no groupdict
* add __continue__ for goto _state in state_pattern()
* parsek* and keyval now can parse list of strings

0.2.8 (2016-11-02)
------------------

* fix MySQLdb does not support UnicodeExt
* callable attribute starting with '_' will not be extended anymore

0.2.6 (2016-04-12)
------------------

* Improve out data path in state_pattern() op

0.2.5 (2016-04-12)
------------------

* Add sgrep*() ops

0.2.4 (2016-03-23)
------------------

* Add dostrip() op
* Improve sed() op

0.2.3 (2016-03-17)
------------------

* Add wcount*() ops

0.2.2 (2016-02-16)
------------------

* cut and cutre now accept maxsplit parameter

0.2.1 (2016-02-16)
------------------

* add aggregate() list operation

0.2.0 (2015-12-16)
------------------

* Better repr display in ipython

0.1.9 (2015-12-15)
------------------

* Add eformat
* Add context dict parameter for format and render operations

0.1.8 (2015-12-10)
------------------

* Add less(), skess() list operations
* Add parse_smart() parser

0.1.7 (2015-11-26)
------------------

* Add some operations
* perf tunning

0.1.3 (2015-11-20)
------------------

* Tune many things
* All is now documented

0.1.2 (2015-11-04)
------------------

* More docs and doctests

0.1.1 (2015-11-04)
------------------
First working package