from configparser import ConfigParser, Error
from .. import BaseCredentialStorage, lazy_property


class IniCredentialStorage(BaseCredentialStorage):

    def __init__(self, filename):
        self.filename = filename

    @lazy_property
    def parser(self):
        parser = ConfigParser(allow_no_value=True)
        try:
            f = open(self.filename, "r")
        except IOError:
            return parser

        with f:
            try:
                parser.readfp(f)
            except Error:
                pass

            return parser

    def load(self, name):
        if not self.parser.has_section(name):
            self.parser.add_section(name)
        return dict(self.parser[name].items())

    def save(self, name, credential):
        self.parser[name] = credential
        with open(self.filename, 'w') as f:
            self.parser.write(f)
