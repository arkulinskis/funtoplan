"""Server tests for api.ftp_api (the one action-style API the Forms call) against the strict Anvil mock.

    python tools/testing/test_server.py          -> prints ALL OK, or the first failure
"""
import datetime as dt
import importlib
import json
import os
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
_tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(PROJECT / "server_code", _tmp / "app", ignore=shutil.ignore_patterns("__pycache__"))
(_tmp / "app" / "__init__.py").write_text("")
os.environ["ANVIL_APP_YAML"] = str(PROJECT / "anvil.yaml")
sys.path[:0] = [str(HERE / "mock"), str(_tmp)]
import anvil.server  # noqa: E402
import anvil.users  # noqa: E402
from anvil.tables import app_tables as T  # noqa: E402

for name in ("api", "legal_server", "SchemaCheck"):
    importlib.import_module("app." + name)
now = dt.datetime.now(dt.timezone.utc)
TODAY = dt.date.today().isoformat()


def as_user(row):
    anvil.users.CURRENT[0] = row
    anvil.server.session.use(row.get_id() if row is not None else None)


def api(action, **payload):
    payload.setdefault("_today", TODAY)
    payload.setdefault("_tz", 0)
    raw = anvil.server.call("ftp_api", action, json.dumps(payload))
    return json.loads(raw)


def ok(r):
    assert r.get("ok"), r
    return r["data"]


def bad(r, code=None):
    assert r.get("ok") is False and r.get("error"), r
    if code:
        assert r.get("code") == code, r
    return r


mom = T.users.add_row(email="mom@example.com", enabled=True, signed_up=now)
kid = T.users.add_row(email="kid@example.com", enabled=True, signed_up=now)

as_user(None)
bad(api("bootstrap"), "auth")
as_user(mom)
assert ok(api("bootstrap"))["state"] is None
bad(api("save_item", kind="task", title="x"), "nofamily")
st = ok(api("create_family", family_name="The Tests", display_name="Mom", avatar="🦊", color="#e5484d", seed=True))["state"]
assert st["family"]["name"] == "The Tests" and len(st["items"]) == 4 and st["members"][0]["role"] == "owner"
code = st["family"]["code"]

as_user(kid)
pv = ok(api("preview_join", code=code))
assert pv["name"] == "The Tests" and not pv["full"]
bad(api("preview_join", code="ZZZZZZ"), "badcode")
st = ok(api("join_family", code=code, display_name="Kid", avatar="🐼", color="#3a7be0"))["state"]
assert len([m for m in st["members"] if m["active"]]) == 2

saved = ok(api("save_item", kind="task", title="Wash the car", points=20, requires_approval=True, priority="high"))
iid = saved["saved"]
d = ok(api("complete", id=iid))
assert d["fx"]["kind"] == "review", "approval needed with 2 people"
as_user(mom)
d = ok(api("approve", id=iid))
kid_m = [m for m in d["state"]["members"] if m["name"] == "Kid"][0]
assert kid_m["points"] == 20, "points paid on approval"
ver = d["state"]["version"]
assert ok(api("sync", version=ver)).get("unchanged") is True
ok(api("send_message", text="Hi FAM-1"))
assert ok(api("sync", version=ver))["state"]["version"] != ver
ok(api("comment", id=iid, text="Nice work"))
det = ok(api("item_detail", id=iid))
assert len(det["comments"]) == 1
ok(api("reopen", id=iid))
d = ok(api("bootstrap"))
assert [m for m in d["state"]["members"] if m["name"] == "Kid"][0]["points"] == 0, "reopen takes the points back"
ok(api("delete_item", id=iid))
bad(api("item_detail", id=iid), "gone")
print("ALL OK")
