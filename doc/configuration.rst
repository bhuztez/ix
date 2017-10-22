=============
Configuration
=============

Required
========

.. py:data:: SOLUTION_PATTERN

    Regular expression to extract :code:`oj` and :code:`problem` from path to solution. The path is relative to :py:data:`SOLUTIONS_DIR`.

    For example:

    .. code-block:: python3

        SOLUTION_PATTERN = r'^(?P<oj>\w+)/(?P<problem>[^/]+)\.c$'

.. py:function:: get_compile_argv(filename)

    To run your solution and check against sample test cases, your solution might have to be compiled first.

    Return :code:`(Arguments, Target)`, where :code:`Arguments` is the arguments of the command to compile your code, and :code:`Target` is the path to generated file.

    Return :code:`None`, if no compilation needed, e.g. script.

    For example,

    .. code-block:: python3

        from ix.utils import replace_ext

        def get_compile_argv(filename):
            target = replace_ext(filename, "elf")
            return ['gcc', '-o', target, filename], target


.. py:function:: prepare_submission(envs, filename)

    Online judges provide different :any:`environment`\ s to support different languages and compilers.

    You have to choose one of them before submit. You might also do preprocessing accordingly.

    return :code:`(Env, Code)`, where :code:`Env` is the chosen environment, :code:`Code` is code to be submitted.

    return :code:`None`, if no suitable environment found

    For example,

    .. code-block:: python3

        def prepare_submission(envs, filename):
            envs = [c for c in envs
                    if c.lang == 'C' and c.name in ('MinGW', 'GCC')]
            if not envs:
                return None
            with open(filename,'r') as f:
                code = f.read()
            return envs[0], code

Optional
========

.. py:data:: ROOTDIR

    Root directory of all files. By default, it is set to current working directory, you may override this in your configuration, and default :py:data:`SOLUTIONS_DIR` and :py:data:`TESTCASES_DIR` will change accordingly.

.. py:data:: SOLUTIONS_DIR

    Root directory of all solutions. By default, it is set to :code:`${ROOTDIR}/solutions`

.. py:data:: TESTCASES_DIR

    Root directory of all fetched sample test cases. By default, it is set to :code:`${ROOTDIR}/testcases`


.. py:data:: VERBOSE

    Whether or not to print verbose output

    By default, this is set to :code:`True` if environment variable :code:`VERBOSE` is set to :code:`true`, :code:`on` or :code:`1`.

    This could be override by command line options


.. py:data:: NO_ASK

    Do not ask for password, if this is set to :code:`True`

    By default, this is set to :code:`True` if environment variable :code:`NO_ASK` is set to :code:`true`, :code:`on` or :code:`1`.

    This could be override by command line options


.. py:data:: LOGIN_MAX_RETRY

    Max times of retry, when login failed.

    By default, it is set to :code:`2`


.. py:function:: has_to_recompile(source, target)

    Check if compilation needed.

    By default, it is set to

    .. code-block:: python3

        import os, os.path

        def has_to_recompile(source, target):
            if not os.path.exists(target):
                return True
            elif os.stat(source).st_mtime >= os.stat(target).st_mtime:
                return True
            return False


.. py:function:: get_run_argv(filename)

    Arguments to run executable

    By default, it is set to

    .. code-block:: python3

        def get_run_argv(filename):
            return [filename]


.. py:function:: default_testcase_prefix(oj, problem)

    Return prefix of filename of test case. Filename of inputs would be :code:`${prefix}.in(.${n})`, filename of outputs would be :code:`${prefix}.out(.${n})`.

    By default, it is set to

    .. code-block:: python3

        import os.path

        def default_testcase_prefix(oj, problem):
            return os.path.join(oj, problem)

.. py:data:: testcase_prefixes

    You may want a different prefix of test case for some online judges.

    By default this is set to :code:`{}`

    For example,

    .. code-block:: python3

        import os.path

        testcase_prefixes = {
            "HR": lambda problem: os.path.join("HR", problem)}


.. py:data:: CREDENTIAL_READER

    how to read password when not logged in

    By default, it is set to :code:`ix.credential.readers.readline.ReadlineCredentialReader()`


.. py:data:: CREDENTIAL_STORAGE

    where to store credentials

    By default, it is set to :code:`ix.credential.storages.sqlite.SqliteCredentialStorage(os.path.join(ROOTDIR, "credentials.sqlite"))`



Helper functions
================

.. py:function:: ix.utils.index_of(l,x)

    .. code-block:: pycon

        >>> from ix.utils import index_of
        >>> index_of([2,1,2],1)
        1
        >>> index_of([2,1,2],3)
        3

.. py:function:: ix.utils.replace_ext(filename, ext)

    .. code-block:: pycon

        >>> from ix.utils import replace_ext
        >>> replace_ext("a.c","elf")
        'a.elf'
