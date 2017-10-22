import lxml.html
from base64 import b64encode
import json
from . import login_required, request, Env

USER = "login"
PASS = "password"

CREDENTIAL_INPUT_TITLE = "HR (hackerrank.com)"
CREDENTIAL_INPUT_FIELDS = (
    (USER, "Username", False),
    (PASS, "Password", True),
)

ENVS = {
    Env(name="GCC", ver="4.9.2", os="Linux", arch="x86_64", lang="C", lang_ver="C99") : "c",
}


def authentication(client):
    return "Basic " + b64encode((client.credential[USER]+":"+client.credential[PASS]).encode("utf-8")).decode("utf-8").strip()


def login(client):
    status,headers,body = client.post_form(
        "https://www.hackerrank.com/auth/login",
        { USER: client.credential[USER],
          PASS: client.credential[PASS],
          "remember_me": "true",
          "fallback": "true"})
    if status != 200:
        return None

    data = json.loads(body.decode("utf-8"))
    status = data.get("status",False)
    if not status:
        return False
    return True


def fetch(client, problem):
    status, _, body = client.get("https://www.hackerrank.com/rest/contests/master/challenges/"+problem)
    if status != 200:
        return False

    html = json.loads(body.decode('utf-8'))["model"]["body_html"]
    doc = lxml.html.fromstring(html)
    indata, = doc.xpath('./div[@class="challenge_sample_input"]/*/*/pre/code/text()')
    outdata, = doc.xpath('./div[@class="challenge_sample_output"]/*/*/pre/code/text()')
    return [{"in": indata, "out": outdata}]


@login_required
def submit(client, problem, env, code):
    status,headers,body = client.post_json(
        "https://www.hackerrank.com/rest/contests/master/challenges/"+problem+"/submissions?",
        {"code": code,
         "language": env,
         "contest_slug": "master"},
        headers={"Authorization": authentication(client)})

    if status != 200:
        return False

    data = json.loads(body.decode("utf-8"))

    if not data.get("status", False):
        return None

    return str(data["model"]["id"])


@login_required
def check(client, problem, token):
    status,headers,body = client.get(
        "https://www.hackerrank.com/rest/contests/master/submissions/" + token,
        headers={"Authorization": authentication(client)})

    if status != 200:
        return False

    data = json.loads(body.decode("utf-8"))
    model = data["model"]
    status = model["status"]

    if model["progress"] < model["progress_states"]:
        return (False, status, False)
    return (True, status, status=="Accepted")
