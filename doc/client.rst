======
Client
======

Login
=====

.. py:data:: CREDENTIAL_INPUT_TITLE
.. py:data:: CREDENTIAL_INPUT_FIELDS

    :code:`(Key, Description, IsPassword)`

.. py:function:: login(client)

    return :code:`True` when :code:`client.credential` is valid

    return :code:`False` when :code:`client.credential` is invalid

    return :code:`None` when failure caused by other issues.

For example,

.. code-block:: python3

    import json
    from ix.clients import request, with_cookie
    request_with_credential = with_cookie("cookie")(request)

    USER = "username"
    PASS = "password"

    CREDENTIAL_INPUT_TITLE = "EX (example.com)"
    CREDENTIAL_INPUT_FIELDS = (
        (USER, "Username", False),
        (PASS, "Password", True),
    )


    def login(client):
        status,headers,body = client.post_form(
            "https://example.com/login",
            { USER: client.credential[USER],
              PASS: client.credential[PASS]},
            request = request_with_credential)

        if status != 200:
            return None

        data = json.loads(body.decode("utf-8"))
        status = data.get("status",False)
        if not status:
            return False
        return True


Fetch
=====

.. py:function:: fetch(client, problem)

    return :code:`[{"in": "input", "out": "expected output"}]`

    return :code:`False` when failed

    return :code:`None` if not logged in (when decorated with login_required)

    For example,

    .. code-block:: python3

        from ix.clients import login_required

        @login_required
        def fetch(client, problem):
            status,headers,body = client.get(
                "https://example.com/testcase/{}".format(problem),
                request = request_with_credential)
            if status == 403:
                return None
            if status != 200:
                return False

            data = json.loads(body.decode("utf-8"))
            return [{"in": x["input"], "out": x["output"]} for x in data]



Submit
======

.. py:data:: ENVS

    For example,

    .. code-block:: python3

        from ix.clients import Env

        ENVS = {
            Env(name="GCC",
                ver="6.0",
                os="Linux",
                arch="x86",
                lang="C",
                lang_ver="C99"):"c"}


.. py:function:: submit(client, problem, env, code)

    return token on success

    return :code:`False` on failure

    return :code:`None` if not logged in (when decorated with login_required)


    For example,

    .. code-block:: python3

        @login_required
        def submit(client, problem, env, code):
            status,headers,body = client.post_multipart_form(
                "https://example.com/submit",
                { "code": code,
                  "env": env,
                  "pid": problem},
                request = request_with_credential)
            if status == 403:
                return None
            if status != 200:
                return False

            return body.decode("utf-8")




.. py:function:: check(client, problem, token)

    return :code:`(True, message, True)` or :code:`(True, message, True, extra)` on accepted

    return :code:`(True, message, False)` on wrong answer

    return :code:`(False, message, False)` on waiting
 
    return :code:`False` on failure
  
    return :code:`None` if not logged in (when decorated with login_required)


    For example,

    .. code-block:: python3

        @login_required
        def check(client, problem, token):
            status,headers,body = client.get(
                "https://example.com/submission/{}".format(token),
                request = request_with_credential)
            if status == 403:
                return None
            if status != 200:
                return False

            data = json.loads(body.decode("utf-8"))
            if data.get("waiting", False):
                return (False, data["message"], False)
            if not data["accepted"]:
                return (True, data["message"], False)
            if "extra" not in data:
                return (True, data["message"], True)
            return (True, data["message"], True, data["extra"])


Client API
==========

.. py:class:: ix.clients.Client

    .. py:method:: get(self, url, params=None, headers=None, request=request)
    .. py:method:: post(self, url, body, headers=None, request=request)
    .. py:method:: post_json(self, url, data, headers=None, request=request)
    .. py:method:: post_form(self, url, data, headers=None, request=request)
    .. py:method:: post_multipart_form(self, url, data, headers=None, request=request)
