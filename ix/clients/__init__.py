import sys
import json
from functools import wraps
from importlib import import_module
from urllib.parse import urlparse, urlencode
from http.client import HTTPConnection, HTTPSConnection
from collections import namedtuple
from email.message import Message

__version__ = ".".join(sys.version.split(".",2)[:2])


class Form(Message):

    def __init__(self):
        Message.__init__(self)
        self.add_header('Content-Type', 'multipart/form-data')
        self._payload = []

    def _write_headers(self, _generator):
        # skip headers
        pass


class Field(Message):

    def __init__(self,name,text):
        Message.__init__(self)
        self.add_header('Content-Disposition','form-data',name=name,charset="utf-8")
        self.set_payload(text,None)


def login_required(func):
    @wraps(func)
    def wrapper(client, *args, **kwargs):
        if client.credential:
            result = func(client, *args, **kwargs)
            if result is not None:
                return result
        else:
            client.read_credential()

        if not client.login():
            return
        return func(client, *args, **kwargs)
    return wrapper


Connections = {
    "http": HTTPConnection,
    "https": HTTPSConnection,
}


def request(client, method, url, body=None, headers=None):
    headers = headers or {}
    headers['Connection'] = 'close'
    headers.setdefault('User-Agent', 'Python-urllib/' + __version__)

    o = urlparse(url)
    host, _, port = o.netloc.partition(":")
    conn = Connections[o.scheme](host, port or None)
    if client.config.VERBOSE:
        conn.set_debuglevel(1)
    path = o.path
    if o.query:
        path += '?' + o.query
    conn.request(method, path, body, headers)

    response = conn.getresponse()

    status = response.status
    headers = response.headers
    body = response.read()
    conn.close()
    return (status, headers, body)


def with_cookie(field):
    from urllib.request import Request
    from urllib.response import addinfourl
    from http.cookiejar import LWPCookieJar
    from io import StringIO

    def decorator(request):
        def wrapper(client, method, url, body=None, headers=None):
            cookiejar = LWPCookieJar()
            cookiejar._really_load(
                StringIO("#LWP-Cookies-2.0\n" + client.credential.get(field,'')),
                "cookies.txt",True,True)
            req = Request(url, body, headers or {}, method=method)
            cookiejar.add_cookie_header(req)
            status, headers, body = request(client,req.method,req.full_url,req.data,dict(req.header_items()))
            response = addinfourl(None, headers, req.full_url, status)
            cookiejar.extract_cookies(response,req)
            client.credential[field] = cookiejar.as_lwp_str()
            return (status, headers, body)
        return wrapper

    return decorator


class Client:

    def __init__(self, name, mod, credential, read_credential, config):
        self.name = name
        self.mod = mod
        self.credential = credential
        self.read_credential = read_credential
        self.config = config

    def login(self):
        result = True

        for i in range(self.config.LOGIN_MAX_RETRY+1):
            result = self.mod.login(self)
            if result:
                self.credential.save()
                return True
            if self.config.NO_ASK:
                return result

            self.read_credential()

        return False

    def get(self, url, params=None, headers=None, request=request):
        if params:
            url += '?' + urlencode(params)
        return request(self, 'GET', url, headers=headers)

    def post(self, url, body, headers=None, request=request):
        return request(self, 'POST', url, body, headers)

    def post_json(self, url, data, headers=None, request=request):
        headers = headers or None
        headers['Content-Type'] = 'application/json; charset=utf-8'
        return request(self, 'POST', url, json.dumps(data), headers)

    def post_form(self, url, data, headers=None, request=request):
        headers = headers or {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        return self.post(url, urlencode(data).encode("utf-8"), headers, request)

    def post_multipart_form(self, url, data, headers=None, request=request):
        headers = headers or {}
        form = Form()
        for name,value in data.items():
            if isinstance(value,bytes):
                form.attach(Field(name,value))
            else:
                form.attach(Field(name,str(value).encode('utf-8')))
        data = form.as_string()
        headers['Content-Type'] = form['Content-Type']
        return self.post(url, data.encode('utf-8'), headers, request)

    def fetch(self, problem):
        return self.mod.fetch(self, problem)

    def submit(self, problem, env, code):
        return self.mod.submit(self, problem, env, code)

    def check(self, problem, token):
        return self.mod.check(self, problem, token)

    def get_envs(self):
        return self.mod.ENVS


class ClientLoader:

    def __init__(self, config):
        self.credential_storage = config.CREDENTIAL_STORAGE
        self.credential_reader = config.CREDENTIAL_READER
        self.config = config
        self.clients = {}

    def load(self, name):
        client = self.clients.get(name, None)
        if client is None:
            mod = import_module("." + name, __package__)
            credential = self.credential_storage[name]
            read_credential = self.credential_reader.get(mod.CREDENTIAL_INPUT_TITLE, mod.CREDENTIAL_INPUT_FIELDS, credential)
            client = Client(name, mod, credential, read_credential, self.config)
            self.clients[name] = client
        return client

Env = namedtuple('Env', ['name','ver','os','arch','lang','lang_ver'])
