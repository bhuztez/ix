import json
from http.cookiejar import LWPCookieJar
from io import StringIO
from urllib.parse import unquote
from itertools import count
from . import login_required, request, with_cookie, Env

USER = "loginUserID"
PASS = "loginPassword"

CREDENTIAL_INPUT_TITLE = "AOJ (judge.u-aizu.ac.jp)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "User ID", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC",      ver="5.1.1", os="Linux", arch="x86_64", lang="C",     lang_ver="C11"): "C"}


request_with_credential = with_cookie("cookie")(request)



def get_cookies(client,field="cookie"):
    cookiejar = LWPCookieJar()
    cookiejar._really_load(
        StringIO("#LWP-Cookies-2.0\n" + client.credential.get(field,'')),
        "cookies.txt",True,True)
    return list(cookiejar)


def login(client):
    status,headers,body = client.post_form(
        "http://judge.u-aizu.ac.jp/onlinejudge/index.jsp",
        { USER: client.credential[USER],
          PASS: client.credential[PASS]},
        request = request_with_credential)
    if status != 200:
        return None

    for cookie in get_cookies(client):
        if cookie.domain == 'judge.u-aizu.ac.jp' and cookie.name == 'sref':
            return True

    return False


def fetch(client, problem):
    testcases = []

    for case in count(1):
        status,headers,body = client.get(
            "http://analytic.u-aizu.ac.jp:8080/aoj/testcase.jsp",
            {"id": problem, "case": case, "type": "in"})
        if status == 500:
            break
        if status != 200:
            return False

        data = {"in": body.decode("utf-8")}

        if case == 2:
            if data["in"] == testcases[0]["in"]:
                break

        status,headers,body = client.get(
            "http://analytic.u-aizu.ac.jp:8080/aoj/testcase.jsp",
            {"id": problem, "case": case, "type": "out"})
        if status != 200:
            return False

        data["out"] = body.decode("utf-8")
        testcases.append(data)

    return testcases


@login_required
def submit(client, problem, env, code):
    for cookie in get_cookies(client):
        if cookie.domain == 'judge.u-aizu.ac.jp' and cookie.name == 'sref':
            epassword = unquote(cookie.value)
            break
    else:
        return None

    status,headers,body = client.post_form(
        "http://judge.u-aizu.ac.jp/onlinejudge/webservice/submit",
        { "sourceCode": code,
          "language": env,
          "lessonID": problem[:-2],
          "problemNO": problem[-1],
          "userID": client.credential[USER],
          "epassword": epassword,
        },
        request = request_with_credential)
    if status != 200:
        return False

    if body != b'0\n':
        return None

    return True


def check(client, problem, token):
    return False
