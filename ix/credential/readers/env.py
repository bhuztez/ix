import os

class EnvironmentCredentialReader:

    def __init__(self):
        pass

    def get(self, title, fields, credential):
        def read():
            print(title)
            for key, desc, is_password in fields:
                credential[key] = os.environ[title.split(' ')[0] + '_' + key]
        return read
