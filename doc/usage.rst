==================
Command line usage
==================

ix could be called like this

.. code-block:: console

    $ python3 -mix [options] subcommand [args]

:program:`python3 -mix` has several options

.. program:: python3 -mix

.. option:: -h, --help

    show help message and quit

.. option:: -k, --keep-going

    keep going when some task failed

.. option:: -v, --verbose

    show verbose outputs

.. option:: --no-ask

    do not ask for password

.. option:: -c CFG, --config CFG

    use config file at CFG

    Be default, ix uses :file:`ixcfg.py` at current working directory as :any:`configuration`. 

run
===

:program:`python3 -mix run` compiles and runs your solution. It is called like this.

.. code-block:: console

    $ python3 -mix run [options] filename

where *filename* is the path to your solution.

:program:`python3 -mix run` has several options

.. program:: python3 -mix run

.. option:: -h, --help

    show help message and quit

.. option:: -r, --recompile

    recompile if already compiled before run


test
====

:program:`python3 -mix test` checks your solution against sample test cases. It is called like this.

.. code-block:: console

    $ python3 -mix run [options] filename

where *filename* is the path to your solution.

:program:`python3 -mix test` has several options

.. program:: python3 -mix test

.. option:: -h, --help

    show help message and quit

.. option:: -r, --recompile

    recompile if already compiled before test


generate
========

:program:`python3 -mix generate` prints the code to be submitted. You may whatever preprocessing you what in :py:func:`prepare_submission`. This command allows you to check what is to be submitted. It is called like this.

.. code-block:: console

    $ python3 -mix generate [options] filename

where *filename* is the path to your solution.

:program:`python3 -mix generate` has several options

.. program:: python3 -mix generate

.. option:: -h, --help

    show help message and quit


submit
======

:program:`python3 -mix submit` submits your solution to online judge. It is called like this.

.. code-block:: console

    $ python3 -mix submit [options] filename

where *filename* is the path to your solution.

:program:`python3 -mix submit` has several options

.. program:: python3 -mix submit

.. option:: -h, --help

    show help message and quit

.. option:: -w, --wait

    wait until verdict


clean
=====

:program:`python3 -mix clean` removes generated files. It is called like this.

.. code-block:: console

    $ python3 -mix clean [options] filename

where *filename* is the path to your solution.

:program:`python3 -mix clean` has several options

.. program:: python3 -mix clean

.. option:: -h, --help

    show help message and quit


help
====

:program:`python3 -mix help` prints help message. It is called like this.

.. code-block:: console

    $ python3 -mix help [options]

:program:`python3 -mix help` has several options

.. program:: python3 -mix help

.. option:: -h, --help

    show help message and quit

