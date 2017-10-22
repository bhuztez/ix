==
ix
==

command line client for online judges

run locally

.. code-block:: console

    $ python3 -mix run solutions/POJ/1000.c

check against sample input/output

.. code-block:: console

    $ python3 -mix test solutions/POJ/1000.c

submit solution

.. code-block:: console

    $ python3 -mix submit -w solutions/POJ/1000.c


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

