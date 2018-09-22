==
ix
==

ix is command line client of online judges. Fetch sample test cases,
test your solutions against them, submit your solutions.


Quick Start
===========

.. code-block:: console

    $ git clone git://github.com/bhuztez/ix.git
    $ cd ix
    $ python3 -mix submit -w solutions/POJ/1000.c
    [SUBMIT] solutions/POJ/1000.c
    POJ (poj.org)
    Username: your_username
    Password:
    [SUBMIT] solutions/POJ/1000.c: Accepted (Memory: 328K, Time: 0MS)
    $


Supported Online Judges
=======================

============== ====== =======================
Online Judge   Submit Fetch sample test cases
============== ====== =======================
`AOJ`__        Y      Y
`POJ`__        Y      Y
============== ====== =======================

.. __: http://judge.u-aizu.ac.jp/onlinejudge/index.jsp
.. __: http://poj.org/


Using ix
========

.. toctree::
   :maxdepth: 2

   usage
   configuration


Extending ix
============

.. toctree::
   :maxdepth: 2

   Adding client of online judge <client>
