==
ix
==

.. image:: https://travis-ci.org/bhuztez/ix.svg?branch=master
    :target: https://travis-ci.org/bhuztez/ix

command line client for online judges

run locally

.. code-block:: console

    $ python3 -mix run solutions/POJ/1000.c

check against sample test cases

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
