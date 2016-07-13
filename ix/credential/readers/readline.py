import readline
from getpass import getpass

class ReadlineCredentialReader:

    def __init__(self):
        pass

    def get(self, title, fields, credential):
        def read():
            print(title)
            for key, desc, is_password in fields:
                default = credential.get(key, '')
                if is_password:
                    if default:
                        result = getpass(desc + " (use old if left blank): ") or default
                    else:
                        result = getpass(desc + ": ")
                else:
                    readline.set_startup_hook(lambda: readline.insert_text(default))
                    try:
                        result = input(desc + ": ")
                    finally:
                        readline.set_startup_hook()
                credential[key] = result
        return read
