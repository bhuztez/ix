import json
from . import login_required, request, with_cookie, Env

USER = "id"
PASS = "password"

CREDENTIAL_INPUT_TITLE = "AOJ (judge.u-aizu.ac.jp)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "User ID", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC",      ver="5.1.1", os="Linux", arch="x86_64", lang="C",     lang_ver="C11"): "C"}


request_with_credential = with_cookie("cookie")(request)


def login(client):
    status,headers,body = client.post_json(
        "https://judgeapi.u-aizu.ac.jp/session",
        { USER: client.credential[USER],
          PASS: client.credential[PASS]},
        request = request_with_credential)

    if status == 200:
        return True

    if status == 400:
        return False

    return None


def fetch(client, problem):
    status,headers,body = client.get(
        "https://judgedat.u-aizu.ac.jp/testcases/{}/header".format(problem))

    if status != 200:
        return False

    testcases = []

    header = json.loads(body.decode("utf-8"))

    for case in header["headers"]:
        status,headers,body = client.get(
            "https://judgedat.u-aizu.ac.jp/testcases/{}/{}".format(problem, case["serial"]))
        if status != 200:
            return False

        data = json.loads(body.decode("utf-8"))
        testcases.append({"in": data["in"], "out": data["out"]})

    return testcases


@login_required
def submit(client, problem, env, code):
    status,headers,body = client.post_json(
        "https://judgeapi.u-aizu.ac.jp/submissions",
        { "sourceCode": code,
          "language": env,
          "problemId": problem,
        },
        request = request_with_credential)


    if status == 400:
        return None

    if status != 200:
        return False

    data = json.loads(body.decode("utf-8"))
    token = data['token']

    status,headers,body = client.get(
        "https://judgeapi.u-aizu.ac.jp/submission_records/recent")

    if status != 200:
        return False

    data = json.loads(body.decode("utf-8"))

    for item in data:
        if item["token"] == token:
            return item["judgeId"]

    return False


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
    status,headers,body = client.get(
        "https://judgeapi.u-aizu.ac.jp/verdicts/{}".format(token))

    if status != 200:
        return False

    data = json.loads(body.decode('utf-8'))["submissionRecord"]
    status = data["status"]
    message = STATUS[status]

    if status in (5, 9):
        return (False, message, False)
    elif status == 4:
        return (True, message, True, 'Memory: {memory}, Time: {cpuTime}, Length: {codeSize}'.format(**data))
    elif status >= 0:
        return (True, message, False)

    return False
