class lazy_property(object):

    def __init__(self, fun):
        self.fun = fun

    def __get__(self, instance, owner):
        o = self.fun(instance)
        instance.__dict__[self.fun.__name__] = o
        return o


class Credential:

    def __init__(self, name, storage):
        self.name = name
        self.storage = storage
        self.dirty = False

    @lazy_property
    def data(self):
        return self.storage.load(self.name)

    def save(self):
        if self.dirty:
            self.storage.save(self.name, self.data)
            self.dirty = False

    def get(self, name, default):
        return self.data.get(name, default)

    def __getitem__(self, name):
        return self.data[name]

    def __setitem__(self, name, value):
        if name in self.data and self.data[name] == value:
            return
        assert isinstance(value, str)
        self.dirty = True
        self.data[name] = value

    def __delitem__(self, name):
        del self.data[name]
        self.dirty = True

    def __contains__(self, name):
        return name in self.data


class BaseCredentialStorage:

    def __getitem__(self, name):
        return Credential(name, self)

    def load(self, name):
        raise NotImplementedError

    def save(self, name, credential):
        raise NotImplementedError
