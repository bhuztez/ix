==
ix
==

ix is command line client for online judges. Fetch sample test cases,
test your solutions against them, submit your solutions.


Quick Start
===========

.. code-block:: console

    $ git clone git://github.com/bhuztez/ix.git
    $ cd ix
    $ python3 -mix submit -w solutions/HR/solve-me-first.c
    [SUBMIT] solutions/HR/solve-me-first.c
    HR (hackerrank.com)
    Username: your_username
    Password:
    [SUBMIT] solutions/HR/solve-me-first.c: Accepted
    $


Supported Online Judges
=======================

============== ====== =======================
Online Judge   Submit Fetch sample test cases
============== ====== =======================
GeeksForGeeks  Y      N
HackerRank     Y      Y
POJ            Y      Y
SPOJ           Y      Y
UVa
============== ====== =======================


Using ix
========

.. toctree::
   :maxdepth: 2

   usage
   configuration
   environment


Extending ix
============

.. toctree::
   :maxdepth: 2

   client
   reader
   storage
