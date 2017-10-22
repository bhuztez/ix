==================
Credential storage
==================

.. code-block:: python3

    from ix.credential import BaseCredentialStorage

    class MyCredentialStorage(BaseCredentialStorage):
        def __init__(self):
            self.data = {}

        def load(self, name):
            return dict(self.data.get(name, {}))

        def save(self, name, credential):
            self.data[name] = dict(credential)
