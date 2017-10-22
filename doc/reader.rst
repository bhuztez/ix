=================
Credential reader
=================

.. code-block:: python3

    class MyCredentialReader

        def get(self, title, fields, credential):
            def read():
                for key, desc, is_password in fields:
                    credential[key] = 'N/A'
            return read
