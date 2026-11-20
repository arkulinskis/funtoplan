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
import anvil.secrets  # noqa: E402
anvil.secrets.SECRETS["admin_emails"] = "admin@example.com"  # the App Secret, faked
from anvil.tables import app_tables as T  # noqa: E402

for name in ("api", "legal_server", "SchemaCheck", "calendar_feed"):
    importlib.import_module("app." + name)
cf = importlib.import_module("app.calendar_feed")
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


# ---------------------------------------------------------------- kid seats (no account, no phone)
def member_named(state, name):
    return [m for m in state["members"] if m["name"] == name][0]


def item_in(state, item_id):
    return [it for it in state["items"] if it["id"] == item_id][0]


as_user(mom)
st = ok(api("bootstrap"))["state"]
mom_id, kid_user_id = member_named(st, "Mom")["id"], member_named(st, "Kid")["id"]
d = ok(api("add_kid", display_name="Leo", avatar="🦖", color="#2fa36b"))
leo_id = d["kid"]
leo_row = T.members.get_by_id(leo_id)
assert leo_row["user"] is None and leo_row["role"] == "kid" and leo_row["active"], "a kid seat has no account"
assert member_named(d["state"], "Leo")["kid"] is True and member_named(d["state"], "Mom")["kid"] is False
assert any("kid seat for 🦖 Leo" in m["text"] for m in d["state"]["messages"])
bad(api("add_kid", display_name="   "))  # a name or nickname is needed
ok(api("update_kid", member_id=leo_id, display_name="Leo", avatar="🦕", color="#3a7be0"))
assert T.members.get_by_id(leo_id)["avatar"] == "🦕"
bad(api("update_kid", member_id=kid_user_id, display_name="Renamed"))  # grown-ups edit their own profile

# "Leo did it": Leo gets the points through the ledger, Mom is recorded as the one who checked it
t1 = ok(api("save_item", kind="task", title="Feed the cat", points=10, assignee=leo_id))["saved"]
d = ok(api("complete", id=t1, for_member=leo_id))
assert d["fx"] == {"kind": "done", "points": 10, "who": "Leo"}, d["fx"]
assert member_named(d["state"], "Leo")["points"] == 10
logs = list(T.points_log.search(member=leo_row))
assert len(logs) == 1 and logs[0]["delta"] == 10, "points_log row for the kid"
it = item_in(d["state"], t1)
assert it["completed_by"] == leo_id and it["approved_by"] == mom_id and it["status"] == "done"
assert any("marked by Mom" in m["text"] and m["author"] == leo_id for m in d["state"]["messages"]), "chat shows it"
# a grown-up can't be ticked off by someone else
t2 = ok(api("save_item", kind="task", title="Bins out", points=5))["saved"]
bad(api("complete", id=t2, for_member=kid_user_id))
bad(api("complete", id=t2, for_member="not-a-member"))
# an approval task ticked off for a kid needs no Review step: the grown-up has just checked it
t3 = ok(api("save_item", kind="task", title="Tidy room", points=5, requires_approval=True))["saved"]
d = ok(api("complete", id=t3, for_member=leo_id))
assert item_in(d["state"], t3)["status"] == "done" and member_named(d["state"], "Leo")["points"] == 15
# giving an open bounty to a kid
ok(api("claim", id=t2, for_member=leo_id))
assert T.items.get_by_id(t2)["assignee"] == leo_row
# wants are for grown-ups' accounts
w = ok(api("save_item", kind="want", title="Ice cream"))["saved"]
bad(api("complete", id=w, for_member=leo_id))
# reopening takes the kid's points back
ok(api("reopen", id=t3))
assert T.members.get_by_id(leo_id)["points"] == 10

# the 4-seat cap counts kid seats
mia_id = ok(api("add_kid", display_name="Mia", avatar="🦄"))["kid"]
bad(api("add_kid", display_name="Zed"), "full")
dad = T.users.add_row(email="dad@example.com", enabled=True, signed_up=now)
as_user(dad)
bad(api("join_family", code=code), "full")
assert ok(api("preview_join", code=code))["full"] is True

# Take turns rotates through kid seats too (join order: Mom, Kid, Leo, Mia)
as_user(kid)
rt = ok(api("save_item", kind="task", title="Water plants", recurrence="weekly", rotate=True, assignee=kid_user_id,
            due_date=TODAY))["saved"]
series = T.items.get_by_id(rt)["series"]
ok(api("complete", id=rt))
nxt = [r for r in T.items.search(series=series, status="todo")][0]
assert nxt["assignee"] == leo_row, "the next turn is Leo's"
as_user(mom)
ok(api("complete", id=nxt.get_id(), for_member=leo_id))
nxt2 = [r for r in T.items.search(series=series, status="todo")][0]
assert nxt2["assignee"] == T.members.get_by_id(mia_id), "then Mia's"

# two grown-ups: your own approval task still needs the other one
as_user(kid)
ap = ok(api("save_item", kind="task", title="Vacuum", points=5, requires_approval=True))["saved"]
assert ok(api("complete", id=ap))["fx"]["kind"] == "review"
bad(api("approve", id=ap))
as_user(mom)
assert ok(api("approve", id=ap))["fx"]["kind"] == "approved"

# one grown-up + kid seats: the grown-up's own approval tasks don't get stuck in Review
solo = T.users.add_row(email="solo@example.com", enabled=True, signed_up=now)
as_user(solo)
st = ok(api("create_family", family_name="Solo Family", display_name="Sam", seed=False))["state"]
solo_code = st["family"]["code"]
ava_id = ok(api("add_kid", display_name="Ava", avatar="🐼"))["kid"]
sp = ok(api("save_item", kind="task", title="Groceries", points=5, requires_approval=True))["saved"]
assert ok(api("complete", id=sp))["fx"]["kind"] == "done", "a single grown-up finishes their own approval task"
# owner hand-over skips kid seats; with no grown-up left, the kid seats close too
partner = T.users.add_row(email="partner@example.com", enabled=True, signed_up=now)
as_user(partner)
ok(api("join_family", code=solo_code, display_name="Pat"))
as_user(solo)
ok(api("leave_family"))
assert T.members.get_by_id(ava_id)["role"] == "kid" and T.members.get_by_id(ava_id)["active"]
pat = [m for m in T.members.search(user=partner)][0]
assert pat["role"] == "owner", "ownership goes to the grown-up, not the kid who joined earlier"
as_user(partner)
ok(api("leave_family"))
assert not T.members.get_by_id(ava_id)["active"], "kid seats close when no grown-up is left"


# ---------------------------------------------------------------- phone calendar link + feed
def feed(token, mine=None):
    r = cf.serve(token, mine)
    body = r.body.get_bytes().decode("utf-8") if hasattr(r.body, "get_bytes") else str(r.body)
    return r.status, body


def valid_ics(text):
    """The parts of RFC 5545 a calendar app trips over: CRLF lines, 75-octet folding, nesting, required properties."""
    assert text.endswith("\r\n") and "\n" not in text.replace("\r\n", ""), "CRLF line endings only"
    raw = text.split("\r\n")[:-1]
    for line in raw:
        assert len(line.encode("utf-8")) <= 75, "folded at 75 octets: %r" % line
    lines = []
    for line in raw:
        if line.startswith(" "):
            lines[-1] += line[1:]
        else:
            lines.append(line)
    stack = []
    for line in lines:
        name = line.split(":", 1)[0].split(";", 1)[0]
        assert ":" in line and name and name.replace("-", "").isalnum() and name.isupper(), "content line: %r" % line
        if name == "BEGIN":
            stack.append((line.split(":", 1)[1], set()))
        elif name == "END":
            comp, have = stack.pop()
            assert comp == line.split(":", 1)[1], "BEGIN/END pairs"
            if comp == "VEVENT":
                assert {"UID", "DTSTAMP", "DTSTART"} <= have, "VEVENT needs UID, DTSTAMP, DTSTART"
            if comp == "VCALENDAR":
                assert {"VERSION", "PRODID"} <= have
            if comp == "VALARM":
                assert {"ACTION", "TRIGGER", "DESCRIPTION"} <= have
        else:
            stack[-1][1].add(name)
    assert not stack and lines[0] == "BEGIN:VCALENDAR" and lines[-1] == "END:VCALENDAR"
    return lines


as_user(mom)
mom_row = T.members.get_by_id(mom_id)
c1 = ok(api("cal_link"))
tok = c1["token"]
assert len(tok) == 32 and c1["path"].endswith("/cal/%s.ics" % tok), c1
assert ok(api("cal_link"))["token"] == tok and len(list(T.cal_links.search(member=mom_row))) == 1, "one row per seat"
ev = ok(api("save_item", kind="event", title="Lunch, pizza; then\nnap", location="Gran's, kitchen",
            event_at=(now + dt.timedelta(days=2)).isoformat()))["saved"]
ok(api("ack", id=ev))
ok(api("save_item", kind="task", title="A very long job title " * 4, assignee=mom_id, points=10,
       due_date=(dt.date.today() + dt.timedelta(days=1)).isoformat()))
ok(api("save_item", kind="task", title="Feed the fish", assignee=leo_id, points=5, due_date=TODAY))
status, text = feed(tok)
assert status == 200
lines = valid_ics(text)
if os.environ.get("FTP_SHOW_ICS"):
    sys.stdout.buffer.write(text.encode("utf-8"))
fam_row = mom_row["family"]
n_events = len([r for r in T.items.search(family=fam_row, kind="event") if r["event_at"] and r["event_at"] >= now - dt.timedelta(days=7)])
n_tasks = len([r for r in T.items.search(family=fam_row, kind="task") if r["status"] in ("todo", "doing", "review") and r["due_date"]])
assert lines.count("BEGIN:VEVENT") == n_events + n_tasks and n_events >= 2 and n_tasks >= 3, (n_events, n_tasks)
assert "SUMMARY:Lunch\\, pizza\\; then\\nnap" in lines and "LOCATION:Gran's\\, kitchen" in lines, "commas, semicolons, newlines escaped"
assert any(l.startswith("X-WR-CALNAME:The Tests · Fun To Plan") for l in lines)
assert any(l.startswith("DESCRIPTION:") and "Coming: Mom" in l for l in lines)
assert any(l.startswith("SUMMARY:FAM-") and "🦕 Leo" in l and "5 🍫" in l for l in lines), "a kid's job shows the kid"
assert ("UID:%s@funtoplan.com" % "-".join(x for x in __import__("re").split(r"[^0-9A-Za-z]+", ev) if x)) in lines
assert "Solo Family" not in text and "Groceries" not in text, "only this family's board"
assert "dad@example.com" not in text and "mom@example.com" not in text, "no emails"
_, mine_text = feed(tok, "1")
mine_lines = valid_ics(mine_text)
mine_tasks = [l for l in mine_lines if l.startswith("DTSTART;VALUE=DATE")]
assert len(mine_tasks) == len([r for r in T.items.search(family=fam_row, kind="task", assignee=mom_row)
                               if r["status"] in ("todo", "doing", "review") and r["due_date"]]) >= 1
assert "Leo" not in "".join(l for l in mine_lines if l.startswith("SUMMARY:FAM-")), "only my jobs"
c3 = ok(api("cal_link", reset=True))
assert c3["token"] != tok and feed(tok)[0] == 404 and feed(c3["token"])[0] == 200, "reset kills the old address"
for junk in ("", "abc", "../../etc", "0" * 32, c3["token"].upper(), c3["token"] + "x"):
    assert feed(junk)[0] == 404, junk
assert feed(c3["token"] + ".ics")[0] == 200
# a removed member's link stops working
as_user(kid)
kid_tok = ok(api("cal_link"))["token"]
assert feed(kid_tok)[0] == 200
as_user(mom)
ok(api("remove_member", member_id=kid_user_id))
assert feed(kid_tok)[0] == 404 and not list(T.cal_links.search(token=kid_tok)), "removed seat: 404, row gone"
# before the schema is accepted: a friendly message, nothing else breaks
saved_table = T.cal_links
delattr(T, "cal_links")
try:
    bad(api("cal_link"), "nocal")
    assert feed(c3["token"])[0] == 404
    assert ok(api("bootstrap"))["state"] is not None
finally:
    setattr(T, "cal_links", saved_table)
# folding keeps multi-byte characters whole
long_line = "SUMMARY:" + "🍫é" * 40
folded = cf.fold(long_line)
assert all(len(part.encode("utf-8")) <= 75 for part in folded.split("\r\n")) and folded.replace("\r\n ", "") == long_line
print("ALL OK")
