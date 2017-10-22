import lxml.html
from base64 import b64encode
from . import login_required, request, with_cookie, Env

USER = "username"
PASS = "passwd"

CREDENTIAL_INPUT_TITLE = "UVA (uva.onlinejudge.org)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "Username", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC",        ver="5.3.0", os="Linux", arch="x86_64", lang="C",       lang_ver="ANSI C")      : "1",
    Env(name="OpenJDK",    ver="1.8.0", os="Linux", arch="x86_64", lang="Java",    lang_ver="Java 8")      : "2",
    Env(name="GCC",        ver="5.3.0", os="Linux", arch="x86_64", lang="C++",     lang_ver="C++03")       : "3",
    Env(name="FreePascal", ver="3.0.0", os="Linux", arch="x86_64", lang="Pascal",  lang_ver="FreePascal")  : "4",
    Env(name="GCC",        ver="5.3.0", os="Linux", arch="x86_64", lang="C++",     lang_ver="C++11")       : "5",
    Env(name="CPython",    ver="3.5.1", os="Linux", arch="x86_64", lang="Python",  lang_ver="Python 3.5")  : "6",
}

request_with_credential = with_cookie("cookie")(request)

LOGIN_URL = "https://uva.onlinejudge.org/index.php?option=com_comprofiler&task=login"

def login(client):
    status,headers,body = client.get(
        LOGIN_URL,
        request=request_with_credential)
    if status != 200:
        return None
    doc = lxml.html.fromstring(body.decode("utf-8"))
    cbsecuritym3, = doc.xpath('//div[@id="col3"]//input[@name="cbsecuritym3"]/@value')

    status,headers,body = client.post_form(
        LOGIN_URL,
        { USER: client.credential[USER],
          PASS: client.credential[PASS],
          "op2": "login",
          "lang": "english",
          "force_session": "1",
          "return": b"B:"+b64encode(LOGIN_URL.encode('utf-8')),
          "message": "0",
          "loginform": "loginform",
          "remember": "yes",
          "cbsecuritym3": cbsecuritym3,
          "Submit": "Login"},
        request=request_with_credential)
    return status == 301


def fetch(client, problem):
    status, _, body = client.get("https://uva.onlinejudge.org/external/%s/%s.html" % (problem[:-2], problem))
    if status != 200:
        return False
    doc = lxml.html.fromstring(body.decode("utf-8"))

    input, = doc.xpath('//h2[font[a[normalize-space(text())="Sample Input"]]]/following-sibling::pre[1]/text()')
    output, = doc.xpath('//h2[font[a[normalize-space(text())="Sample Output"]]]/following-sibling::pre[1]/text()')
    return [{"in": input, "out": output}]


@login_required
def submit(client, problem, env, code):
    status, headers, body = client.post_multipart_form(
        "https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25&page=save_submission",
        { "problemid": "",
          "category": "",
          "localid": problem,
          "language": env,
          "code": code},
        request=request_with_credential)

    if status != 301:
        return None

    loc = headers.get('location',None)
    if loc is None:
        return False
    return loc.rsplit('+',1)[1]


WAITING = ('Received', 'Sent to judge', 'In judge queue', 'Compiling', 'Running', 'Linking')

@login_required
def check(client, problem, token):
    status, headers, body = client.get(
        "https://uva.onlinejudge.org/index.php",
        {"option": "com_onlinejudge", "Itemid": "9"},
        request=request_with_credential)

    if status != 200:
        return False

    if b"You are not authorised to view this resource." in body:
        return None

    doc = lxml.html.fromstring(body.decode("utf-8"))

    tr = doc.xpath('//div[text()="My Submissions"]/following-sibling::table[1]/tr[td[1]/text()="' + token + '"]')
    if not tr:
        return False
    tr = tr[0]
    verdict, = tr.xpath("td[4]/text()")
    if verdict in WAITING:
        return (False, verdict, False)
    if verdict != 'Accepted':
        return (True, verdict, False)

    time, = tr.xpath("td[6]/text()")
    return (True, verdict, True, "Run Time: %s" % (time,))
