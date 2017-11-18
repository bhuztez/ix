import json
import websocket
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

    ws = websocket.WebSocket()
    ws.connect("ws://ionazn.org/status")

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

    return {"socket": ws, "lang": env}


STATUS = {
    -1: "Judge Not Available",
    0: "Compile Error",
    1: "Wrong Answer",
    2: "Time Limit Exceeded",
    3: "Memory Limit Exceeded",
    4: "Accepted",
    5: "Waiting Judge",
    6: "Output Limit Exceeded",
    7: "Runtime Error",
    8: "Presentation Error",
    9: "Running",
}


def check(client, problem, token):
    ws = token["socket"]
    lang = token["lang"]
    user = client.credential[USER]

    while True:
        data = json.loads(ws.recv())
        if data['userID'] != user:
            continue
        if data['lang'] != lang:
            continue
        if problem != "{}_{}".format(data['lessonID'], data['problemID']):
            continue

        runID = token.get("runID", None)

        if runID is None:
            runID = data['runID']
            token["runID"] = runID

        if data['runID'] != runID:
            continue

        status = data["status"]
        message = STATUS.get(status, None)

        if status in (5, 9):
            return (False, message, False)
        elif status == 4:
            return (True, message, True, 'Memory: {memory}, Time: {cputime}, Length: {code}'.format(**data))
        elif status >= 0:
            return (True, message, False)

        return False
