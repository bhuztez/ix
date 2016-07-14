import lxml.html
import json
from . import login_required, request, with_cookie, Compiler

USER = "login_user"
PASS = "password"

CREDENTIAL_INPUT_TITLE = "SPOJ (www.spoj.com)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "Username", False),
    (PASS, "Password", True),
)

COMPILERS = {
    Compiler(name="GCC",   ver="5.1",   os="Linux", arch="x86", lang="C++", lang_ver="C++03") : "1",
    Compiler(name="GCC",   ver="5.1",   os="Linux", arch="x86", lang="C",   lang_ver="C")     : "11",
    Compiler(name="GCC",   ver="5.1",   os="Linux", arch="x86", lang="C",   lang_ver="C99")   : "34",
    Compiler(name="GCC",   ver="4.3.2", os="Linux", arch="x86", lang="C++", lang_ver="C++03") : "41",
    Compiler(name="GCC",   ver="4.3.2", os="Linux", arch="x86", lang="C++", lang_ver="C++14") : "44",
    Compiler(name="clang", ver="3.7",   os="Linux", arch="x86", lang="C",   lang_ver="C11")   : "81",
    Compiler(name="clang", ver="3.7",   os="Linux", arch="x86", lang="C++", lang_ver="C++03") : "82",
}


request_with_credential = with_cookie("cookie")(request)

def login(client):
    status,headers,body = client.post_form(
        "http://www.spoj.com/login",
        { USER: client.credential[USER],
          PASS: client.credential[PASS],
          'autologin': '1',
          'next_raw': '/'},
        request = request_with_credential)
    return status == 302


def fetch(client, problem):
    status, _, body = client.get("http://www.spoj.com/problems/" + problem + "/")
    if status != 200:
        return False
    doc = lxml.html.fromstring(body.decode("utf-8"))
    input, output = doc.xpath('//div[@id="problem-body"]/pre[1]/b')
    return [{"in":input.tail,"out":output.tail}]


@login_required
def submit(client, problem, compiler, code):
    status,headers,body = client.post_multipart_form(
        "http://www.spoj.com/submit/complete/",
        { "file": code,
          "lang": compiler,
          "problemcode": problem,
          "submit": "Submit!"},
        request = request_with_credential)
    if status != 200:
        return False

    doc = lxml.html.fromstring(body.decode("utf-8"))
    submission_id = doc.xpath('//input[@name="newSubmissionId"]/@value')
    if not submission_id:
        return None
    submission_id = submission_id[0]
    return submission_id


def fragment_to_text(frag):
    frag = lxml.html.fragments_fromstring(frag.strip())[0]
    if not isinstance(frag, str):
        frag = frag.text

    return frag.replace('\n','').replace('\t','')


def check(client, problem, token):
    status,headers,body = client.post_form(
        "http://www.spoj.com/status/ajax=1,ajaxdiff=1",
        {"ids": token})
    if status != 200:
        return False

    data = json.loads(body.decode('utf-8'))[0]
    description = fragment_to_text(data["status_description"])

    if data.get("final", "0") != "1":
        return (False, description, False)

    if data["status"] != 15:
        return (True, description, False)

    time = fragment_to_text(data["time"])
    mem = data["mem"].strip()
    return (True, description, True, "TIME: %s, MEM: %s"%(time,mem))
