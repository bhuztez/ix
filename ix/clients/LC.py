import json
from . import login_required, request, with_cookie, with_headers, Env

USER = "login"
PASS = "password"

CREDENTIAL_INPUT_TITLE = "LC (leetcode.com)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "Username", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC",      ver="6.3", os="Linux", arch="x86_64", lang="C",     lang_ver="C11"): "c"}

USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"

request_with_credential = with_headers({"User-Agent": USER_AGENT})(with_cookie("cookie")(request))


def get_csrftoken(client):
    if "cookie" not in client.credential:
        status, headers, body = client.get(
            "https://leetcode.com/",
            request = request_with_credential)
        if status != 200:
            return

    from http.cookiejar import LWPCookieJar
    from io import StringIO

    cookiejar = LWPCookieJar()
    cookiejar._really_load(
        StringIO("#LWP-Cookies-2.0\n" + client.credential["cookie"]),
        "cookies.txt",True,True)
    for cookie in cookiejar:
        if cookie.name == 'csrftoken':
            return cookie.value
    else:
        return

def login(client):
    token = get_csrftoken(client)
    if token is None:
        return

    status, headers, body = client.post_form(
        "https://leetcode.com/accounts/login/",
        { USER: client.credential[USER],
          PASS: client.credential[PASS],
          "csrfmiddlewaretoken": token},
        headers = {
            "Referer": "https://leetcode.com/accounts/login/",
            "X-Requested-With": "XMLHttpRequest"},
        request=request_with_credential)

    if status == 200:
        return True

    if status != 400:
        return False


@login_required
def submit(client, problem, env, code):
    token = get_csrftoken(client)
    if token is None:
        return

    a, b = problem.split('-', 1)

    status,headers,body = client.post_json(
        "https://leetcode.com/problems/{}/submit/".format(b),
        { "typed_code": code,
          "question_id": int(a),
          "lang": env,
          "judge_type": "large"
        },
        headers = {
            "Referer": "https://leetcode.com/problems/{}/description/".format(b),
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": token},
        request=request_with_credential)

    if status == 403:
        return

    if status != 200:
        return False

    data = json.loads(body.decode('utf-8'))
    return data["submission_id"]


def check(client, problem, token):
    status, headers, body = client.get(
        "https://leetcode.com/submissions/detail/{}/check/".format(token),
        request=request_with_credential)

    if status == 403:
        return None

    if status != 200:
        return False

    data = json.loads(body.decode('utf-8'))

    state = data["state"]

    if state != "SUCCESS":
        return (False, state, False)

    msg = data["status_msg"]

    if data["status_code"] != 10:
        return (True, msg, False)

    return (True, msg, True, 'Time: {}'.format(data["status_runtime"]))
