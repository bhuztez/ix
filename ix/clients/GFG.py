import json
from . import login_required, request, with_cookie, Env

USER = "user"
PASS = "pass"

CREDENTIAL_INPUT_TITLE = "GFG (www.geeksforgeeks.org)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "Username", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC", ver="4.5", os="Linux", arch="x86_64", lang="C", lang_ver="C11") : "c",
    Env(name="GCC", ver="4.5", os="Linux", arch="x86_64", lang="C++", lang_ver="C++11") : "cpp",
}

request_with_credential = with_cookie("cookie")(request)


def login(client):
    status,headers,body = client.post_form(
        "http://auth.geeksforgeeks.org/auth.php",
        { USER: client.credential[USER],
          PASS: client.credential[PASS],
          "reqType": "Login",
          "rem": "on"},
        request = request_with_credential)
    if status != 200:
        return None

    data = json.loads(body.decode("utf-8"))
    return "redirect" in data


def fetch(client,problem):
    pass


@login_required
def submit(client, problem, env, code):
    status,headers,body = client.post_form(
        "http://practice.geeksforgeeks.org/ajax/solutionChecking.php",
        {"lang": env,
         "pid": problem,
         "code": code},
        request = request_with_credential)
    if status != 200:
        return False

    if len(body) == 0:
        return None

    if body.startswith(b"Correct Answer."):
        return (True, "Correct", True)

    if body.startswith(b'<br>'):
        parts = body[4:].split(b":<br>")
        if len(parts) > 1:
            return (True, parts[0].decode("utf-8"), False)

    return (True, "Wrong", False)


def check(client, problem, token):
    return token
