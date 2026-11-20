"""Fun To Plan's client data layer and shared helpers (was the top half of theme/assets/ftp.js).

    ftp.api(action, payload)      the ONE way to the server: ftp_api(action, payload_json) in server_code/api.py
                                  (QUERIES / MUTATIONS); raises ApiError(message, code) on {"ok": false}
    ftp.run(action, payload)      api() + apply the reply + friendly error handling (toast, sign-in, onboarding);
                                  returns the reply's data, or None when it failed
    ftp.S                         the family board the server sent (S["st"]): family, members, items, messages
    ftp.listen(fn) / unlisten(fn) pages, the Shell and the card dialog redraw when the board changes
    sync                          every 8 s (and when the tab comes back) `sync` asks for the board only if its
                                  version changed, so every device stays up to date without reloading
Plus the board rules the pages share (eff, needs_you, level_of ...), dates, and opening the dialogs.
"""
import json
import re
import anvil
import anvil.js
import anvil.server
from anvil.js import window

from . import state

POLL_MS = 8000
MAX_MEMBERS = 4
AVATARS = ["🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐸", "🐵", "🦉", "🐧", "🐳", "🦄", "🐝", "🐢", "🐙", "🦖", "🐶", "🐱",
           "🚀", "⭐", "🌈", "🍀", "🍩", "🎸", "👩", "👨", "👧", "👦", "👵", "👴"]
COLORS = ["#e5484d", "#f07c2a", "#f2b51d", "#2fa36b", "#3a7be0", "#8a5cd6", "#e0559a", "#2b2a33"]
COLOR_NAMES = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink", "Ink"]
LEVELS = [(0, "Rookie"), (30, "Helper"), (80, "Sidekick"), (150, "Teammate"), (250, "Ace"), (400, "Hero"),
          (600, "Champion"), (850, "Captain"), (1150, "Legend"), (1500, "Mythic")]
KIND = {"task": ("check", "Task"), "event": ("calendar", "Event"), "want": ("starf", "Want")}
COLS = [("todo", "To do"), ("doing", "In progress"), ("review", "Review"), ("done", "Done")]
RECUR = {"none": "Never", "daily": "Daily", "weekdays": "Weekdays", "weekly": "Weekly", "biweekly": "Every 2 weeks",
         "monthly": "Monthly"}
DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
PRI = {"high": 0, "normal": 1, "low": 2}

S: dict = {"st": None, "mm": {}, "seq": {}, "pending_join": None, "filter": "all", "col": "todo", "lb": "week",
           "timer": None, "syncing": False, "listeners": [], "dialog": False}


class ApiError(Exception):
    def __init__(self, message, code="error"):
        super().__init__(message)
        self.code = code


def loose(x):
    """Hands a JS object or a form's dom_nodes on untyped (Anvil's validator can't type dynamic keys)."""
    return x


# ------------------------------------------------------------------ dates (the browser's own clock and time zone)
def jsdate(*args):
    return window.Date(*args)


def now_ms():
    return window.Date.now()


def pad(n):
    return ("0" if n < 10 else "") + str(int(n))


def ymd(d):
    return "%d-%s-%s" % (d.getFullYear(), pad(d.getMonth() + 1), pad(d.getDate()))


def today_str():
    return ymd(jsdate())


def parse_ymd(s):
    if not s:
        return None
    p = s[:10].split("-")
    return jsdate(int(p[0]), int(p[1]) - 1, int(p[2]))


def add_days(d, n):
    x = jsdate(d.getTime())
    x.setDate(x.getDate() + n)
    return x


def day_diff(d):
    a = jsdate(d.getFullYear(), d.getMonth(), d.getDate())
    t = jsdate()
    t = jsdate(t.getFullYear(), t.getMonth(), t.getDate())
    return int(round((a.getTime() - t.getTime()) / 864e5))


def fmt_day(d):
    diff = day_diff(d)
    if diff == 0:
        return "Today"
    if diff == 1:
        return "Tomorrow"
    if diff == -1:
        return "Yesterday"
    if 1 < diff < 7:
        return DOW[d.getDay()]
    return "%s %d %s" % (DOW[d.getDay()], d.getDate(), MON[d.getMonth()])


def fmt_time(d):
    return pad(d.getHours()) + ":" + pad(d.getMinutes())


def fmt_when(iso):
    d = jsdate(iso)
    return fmt_day(d) + " · " + fmt_time(d)


def ago(iso):
    if not iso:
        return ""
    s = (now_ms() - jsdate(iso).getTime()) / 1000
    if s < 60:
        return "just now"
    if s < 3600:
        return "%dm ago" % (s // 60)
    if s < 86400:
        return "%dh ago" % (s // 3600)
    if s < 7 * 86400:
        return "%dd ago" % (s // 86400)
    d = jsdate(iso)
    return "%d %s" % (d.getDate(), MON[d.getMonth()])


def plural(n, one, many=None):
    return "%s %s" % (n, one if n == 1 else (many or one + "s"))


def level_of(points):
    p, i = max(0, points or 0), 0
    while i + 1 < len(LEVELS) and p >= LEVELS[i + 1][0]:
        i += 1
    cur = LEVELS[i]
    nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return {"n": i + 1, "title": cur[1], "next": nxt[0] if nxt else None, "to_next": (nxt[0] - p) if nxt else 0,
            "pct": ((p - cur[0]) / (nxt[0] - cur[0])) if nxt else 1}


def greeting():
    h = jsdate().getHours()
    if h < 5:
        return "Hey night owl"
    if h < 12:
        return "Good morning"
    if h < 18:
        return "Good afternoon"
    return "Good evening"


# ------------------------------------------------------------------ the board
def st():
    return S["st"]


def me():
    s = S["st"]
    return S["mm"].get(s["me"]) if s else None


def is_owner():
    m = me()
    return bool(m and m["role"] == "owner")


def member(mid):
    return S["mm"].get(mid) if mid else None


def active_members():
    """Everyone with a seat, kid seats included, in join order (the order Take turns rotates in)."""
    s = S["st"]
    ms = [m for m in (s["members"] if s else []) if m["active"]]
    return sorted(ms, key=lambda m: m.get("joined") or "")


def is_kid(m):
    return bool(m and m.get("kid"))


def grownups():
    """Seats with an account. Only they approve, so "someone else" for an approval means another grown-up."""
    return [m for m in active_members() if not is_kid(m)]


def kids():
    return [m for m in active_members() if is_kid(m)]


KID_AVATARS = ["🦖", "🦄", "🐼", "🐸", "🐙", "🐯", "🚀", "⭐", "🐳", "🦉"]


def fresh_look():
    """An emoji and a magnet colour nobody on the board has yet, for a new kid seat."""
    used_a = [m["avatar"] for m in active_members()]
    used_c = [m["color"] for m in active_members()]
    avatar = next((a for a in KID_AVATARS if a not in used_a), KID_AVATARS[0])
    color = next((c for c in COLORS if c not in used_c), COLORS[2])
    return avatar, color


def item_by_id(iid):
    s = S["st"]
    for it in (s["items"] if s else []):
        if it["id"] == iid:
            return it
    return None


def eff(it):
    """The column a card shows in: events move to Done 3 hours after they start."""
    if it["kind"] == "event":
        return "done" if it.get("event_at") and jsdate(it["event_at"]).getTime() < now_ms() - 3 * 3600e3 else "todo"
    return it["status"]


def status_label(it):
    s = eff(it)
    if it["kind"] == "event":
        return "Happened" if s == "done" else "Upcoming"
    if it["kind"] == "want":
        return {"todo": "Wanted", "doing": "On it", "review": "Review", "done": "Got it"}[s]
    return {"todo": "To do", "doing": "In progress", "review": "Review", "done": "Done"}[s]


def _when(it):
    return (it.get("event_at") if it["kind"] == "event" else it.get("due_date")) or ""


def sort_open(items):
    """High priority first, then the soonest date (cards without one after), then the newest."""
    return sorted(items, key=lambda it: (PRI.get(it["priority"], 1), 0 if _when(it) else 1, _when(it), -it["seq"]))


def sort_done(items):
    return sorted(items, key=lambda it: it.get("completed_at") or it.get("event_at") or "", reverse=True)


def week_total():
    return sum(max(0, m["week_points"]) for m in active_members())


def needs_you():
    """Approvals, my open tasks, events this week I haven't answered, and kids' jobs due today or earlier (kids have
    no phone, so a grown-up ticks them off: "Leo did it")."""
    s = S["st"]
    if not s:
        return []
    mine, many = s["me"], len(grownups()) > 1
    today = today_str()
    out = []
    for it in s["items"]:
        k, st_ = it["kind"], it["status"]
        if k == "task" and st_ == "review":
            hit = (not many) or it.get("completed_by") != mine
        elif k == "task" and st_ in ("todo", "doing") and is_kid(member(it.get("assignee"))):
            hit = bool(it.get("due_date")) and it["due_date"][:10] <= today
        elif k == "task" and st_ in ("todo", "doing"):
            hit = it.get("assignee") == mine
        elif k == "event" and eff(it) == "todo":
            d = day_diff(jsdate(it["event_at"]))
            hit = 0 <= d <= 7 and mine not in it["acks"]
        else:
            hit = False
        if hit:
            out.append(it)
    ordered = sort_open(out)
    return sorted(ordered, key=lambda it: 0 if it["status"] == "review" else 1)


def _seen_key():
    return "ftp.seen." + S["st"]["family"]["id"]


def unread_count():
    s = S["st"]
    if not s:
        return 0
    try:
        seen = window.localStorage.getItem(_seen_key()) or ""
    except Exception:
        seen = ""
    return len([m for m in s["messages"] if m["kind"] == "chat" and m["author"] != s["me"] and m["created"] > seen])


def mark_chat_seen():
    s = S["st"]
    if s and s["messages"]:
        try:
            window.localStorage.setItem(_seen_key(), s["messages"][-1]["created"])
        except Exception:
            pass


def invite_link():
    loc = window.location
    return loc.origin + loc.pathname + "#join=" + S["st"]["family"]["code"]


# ------------------------------------------------------------------ server
def api(action, payload=None, quiet=False):
    p = dict(payload or {})
    p["_today"] = today_str()
    p["_tz"] = jsdate().getTimezoneOffset()
    caller = anvil.server.call_s if quiet else anvil.server.call
    res = json.loads(caller("ftp_api", action, json.dumps(p)))
    if not res or not res.get("ok"):
        raise ApiError((res or {}).get("error") or "Something went wrong.", (res or {}).get("code") or "error")
    return res["data"]


def _index():
    s = S["st"]
    S["mm"] = {m["id"]: m for m in s["members"]}
    S["seq"] = {it["seq"]: it for it in s["items"]}


def set_board(board):
    """A new board from the server (or None: not on a family board)."""
    S["st"] = board
    if board:
        _index()
        start_polling()
    else:
        S["mm"], S["seq"] = {}, {}
        stop_polling()


def apply(data):
    if not data:
        return
    if data.get("email"):
        state.set_me({"email": data["email"]})
    if "state" in data:
        had = S["st"] is not None
        set_board(data["state"])
        if data["state"]:
            notify()
        elif had:
            from . import router
            router.go("start")


def notify():
    for fn in list(S["listeners"]):
        try:
            fn()
        except Exception as e:  # one broken listener mustn't stop the others
            print("listener failed:", e)


def listen(fn):
    if fn not in S["listeners"]:
        S["listeners"].append(fn)


def unlisten(fn):
    if fn in S["listeners"]:
        S["listeners"].remove(fn)


def handle_error(e):
    """Expected problems: signed out elsewhere, session expired, not on a board any more, card deleted."""
    code = getattr(e, "code", None)
    name = type(e).__name__
    from . import router
    if name == "SessionExpiredError" or code == "session":
        state.toast("Your session expired. Reloading…", "error")
        window.setTimeout(lambda: window.location.reload(), 1400)
        return
    if code == "auth":
        signed_out()
        router.go("landing")
        return
    if code == "nofamily":
        set_board(None)
        router.go("start")
        return
    state.toast(str(e) or "Something went wrong.", "error")


def run(action, payload=None):
    try:
        data = api(action, payload)
    except ApiError as e:
        handle_error(e)
        return None
    except Exception as e:
        if type(e).__name__ == "SessionExpiredError":
            handle_error(e)
            return None
        raise
    apply(data)
    return data


def bootstrap():
    """Who is signed in, and their family board. Returns True when signed in."""
    try:
        data = api("bootstrap")
    except ApiError:
        state.set_me(None)
        set_board(None)
        return False
    state.set_me({"email": data.get("email")})
    set_board(data.get("state"))
    return True


def signed_out():
    state.set_me(None)
    set_board(None)


# ------------------------------------------------------------------ keeping every device up to date
def _tick(*args):
    s = S["st"]
    if not s or S["syncing"] or window.document.hidden:
        return
    S["syncing"] = True
    try:
        d = api("sync", {"version": s["version"]}, quiet=True)
        if not d.get("unchanged"):
            if not d.get("state"):
                state.toast("You are no longer part of that family board.")
            apply(d)
    except ApiError as e:
        if e.code in ("auth", "session"):
            handle_error(e)
    except Exception:
        pass  # offline for a moment: try again on the next tick
    finally:
        S["syncing"] = False


def start_polling():
    if S["timer"] is None:
        S["timer"] = window.setInterval(_tick, POLL_MS)


def stop_polling():
    if S["timer"] is not None:
        window.clearInterval(S["timer"])
        S["timer"] = None


def _visible(event):
    if not window.document.hidden:
        _tick()


window.document.addEventListener("visibilitychange", _visible)


# ------------------------------------------------------------------ small DOM helpers for the templates
def text(node, value):
    node.textContent = "" if value is None else str(value)


def avatar(node, m, size=""):
    """Fill a <span class="avatar"> for member m (or an empty seat)."""
    node.className = "avatar " + size + ("" if m else " empty")
    node.textContent = (m.get("avatar") or "?") if m else "?"
    if m:
        node.style.setProperty("--c", m.get("color") or "#3a7be0")
        node.setAttribute("title", m.get("name") or "")
        node.setAttribute("role", "img")
        node.setAttribute("aria-label", m.get("name") or "Someone")
    else:
        node.removeAttribute("title")
        node.setAttribute("aria-hidden", "true")


def rich(node, txt, on_key=None):
    """Chat and note text: plain text with web links and FAM-12 card links (opens the card)."""
    node.textContent = ""
    doc = window.document
    pos = 0
    for m in re.finditer(r"(https?://[^\s<]+)|\bFAM-(\d+)\b", txt or ""):
        if m.start() > pos:
            node.appendChild(doc.createTextNode(txt[pos:m.start()]))
        if m.group(1):
            a = doc.createElement("a")
            a.setAttribute("href", m.group(1))
            a.setAttribute("target", "_blank")
            a.setAttribute("rel", "noopener")
            a.textContent = m.group(1)
        else:
            it = S["seq"].get(int(m.group(2)))
            if it:
                a = doc.createElement("button")
                a.setAttribute("type", "button")
                a.className = "keylink"
                a.textContent = m.group(0)
                a.setAttribute("aria-label", "Open card %s: %s" % (m.group(0), it["title"]))
                iid = it["id"]
                a.addEventListener("click", lambda e, iid=iid: (on_key or open_detail)(iid))
            else:
                a = doc.createElement("span")
                a.className = "keylink"
                a.textContent = m.group(0)
        node.appendChild(a)
        pos = m.end()
    if pos < len(txt or ""):
        node.appendChild(doc.createTextNode(txt[pos:]))


def is_dark():
    root = loose(window.document.documentElement)
    return bool(root.classList.contains("ui-dark"))


def toggle_theme():
    state.set_theme("light" if is_dark() else "dark")


def where(el):
    """The screen point at the middle of an element (a node or an Anvil component), or the middle of the window."""
    try:
        node = el if hasattr(el, "getBoundingClientRect") else anvil.js.get_dom_node(el)
        r = node.getBoundingClientRect()
        if r.width:
            return (r.left + r.width / 2, r.top + r.height / 2)
    except Exception:
        pass
    return (window.innerWidth / 2, window.innerHeight / 2)


def burst_at(xy, label, points=False):
    """Confetti at a screen point (from where(), taken before the list redraws)."""
    window.FTP.burst(xy[0], xy[1], label, bool(points))


# ------------------------------------------------------------------ card actions (from cards, Home and the dialog)
def item_act(action, iid, el=None, extra=None, detail=False):
    p = {"id": iid, "_detail": detail}
    p.update(extra or {})
    el = where(el)
    d = run(action, p)
    if not d:
        return None
    fx = d.get("fx") or {}
    if fx.get("kind") == "done" and fx.get("who"):  # a kid seat's job, ticked off by a grown-up
        pts = fx.get("points")
        burst_at(el, ("+%d for %s" % (pts, fx["who"])) if pts else ("%s did it! ✓" % fx["who"]), pts)
    elif fx.get("kind") in ("done", "approved"):
        pts = fx.get("points")
        burst_at(el, ("+%d brownie points" % pts) if pts else ("Approved ✓" if fx["kind"] == "approved" else "Done! ✓"), pts)
    elif fx.get("kind") == "review":
        state.toast("Sent for approval ✋")
    elif fx.get("kind") == "want":
        burst_at(el, "Got it! 🎁")
    if action == "claim":
        state.toast("It's yours! Go get those brownie points.")
    return d


def reject(iid):
    from .Dialogs.Prompt import Prompt
    reason = _sheet(Prompt(title="Send back for another try", placeholder="What still needs doing? (optional)",
                           ok="Send back"))
    if reason is None:
        return False
    d = run("reject", {"id": iid, "reason": reason})
    if d:
        state.toast("Sent back ↩")
    return bool(d)


# ------------------------------------------------------------------ dialogs (bottom sheets on phones)
def _sheet(form):
    S["dialog"] = True
    try:
        return anvil.alert(form, buttons=[], dismissible=True, large=True, role="sheet")
    finally:
        S["dialog"] = False


def open_detail(iid):
    """A card's sheet. It can hand over to the editor, another card (FAM-12 link) or the send-back question."""
    from .Dialogs.Detail import Detail
    nxt = ("open", iid)
    while nxt:
        kind, target = nxt
        nxt = None
        if kind == "open":
            if not item_by_id(target):
                return
            r = _sheet(Detail(item_id=target))
        elif kind == "edit":
            open_editor(target)
            return
        else:  # "reject": ask why, then back to the card
            reject(target)
            r = ("open", target) if item_by_id(target) else None
        if isinstance(r, (list, tuple)) and len(r) == 2:
            nxt = (r[0], r[1])


def open_editor(iid=None, kind=None, preset=None):
    """The card editor. preset (new cards only) fills it in: {"due": "YYYY-MM-DD" (task due date and event day),
    "assignee": member id, "recurrence": "weekly", "notes": ..., "hint": a line shown above the form}."""
    from .Dialogs.Editor import Editor
    r = _sheet(Editor(item_id=iid, kind=kind, preset=preset))
    if r and r.get("saved"):
        it = item_by_id(r["saved"])
        state.toast("Saved" if iid else ((it["key"] + " added to the board") if it else "Card added"))


def open_kid_seat(kid_id=None):
    """Add a kid seat (no phone, no account), or edit one."""
    from .Dialogs.KidSeat import KidSeat
    r = _sheet(KidSeat(kid_id=kid_id))
    if r:
        state.toast(r)


def open_cal_link():
    """The "Add to my phone calendar" sheet (Apple / Google / copy, Only my jobs, Reset)."""
    from .Dialogs.CalLink import CalLink
    _sheet(CalLink())


# ------------------------------------------------------------------ the week (Pages/Week)
def week_start(d):
    """Monday of d's week (a JS Date at local midnight)."""
    return jsdate(d.getFullYear(), d.getMonth(), d.getDate() - (d.getDay() + 6) % 7)


def advance(d, rec):
    """The next date of a repeating task: the same rule as the server's api._advance (JS Dates, local time)."""
    if rec == "weekdays":
        x = add_days(d, 1)
        while x.getDay() in (0, 6):
            x = add_days(x, 1)
        return x
    if rec in ("weekly", "biweekly"):
        return add_days(d, 7 if rec == "weekly" else 14)
    if rec == "monthly":
        ny = d.getFullYear() + (1 if d.getMonth() == 11 else 0)
        nm = (d.getMonth() + 1) % 12
        last = jsdate(ny, nm + 1, 0).getDate()
        return jsdate(ny, nm, min(d.getDate(), last))
    return add_days(d, 1)


def _next_turn(order, who):
    if who in order:
        return order[(order.index(who) + 1) % len(order)]
    return order[0] if order else None


def ghost_turns(until):
    """The coming copies of every open repeating task up to the date `until` ("YYYY-MM-DD"), as the server will make
    them: each one after the current card, rotated through active_members() in join order when it takes turns.
    -> [{"it": the open card, "date": "YYYY-MM-DD", "who": member id or None}]"""
    s = S["st"]
    if not s:
        return []
    order = [m["id"] for m in active_members()]
    today = today_str()
    out = []
    for it in s["items"]:
        rec = it.get("recurrence") or "none"
        if it["kind"] != "task" or it["status"] == "done" or rec == "none" or not it.get("due_date"):
            continue
        who = it.get("assignee")
        nxt = advance(parse_ymd(it["due_date"]), rec)
        while ymd(nxt) < today:  # finished late, the next copy jumps to today or later (api._spawn_next)
            nxt = advance(nxt, rec)
        n = 0
        while ymd(nxt) <= until and n < 40:
            n += 1
            if it.get("rotate"):
                who = _next_turn(order, who)
            out.append({"it": it, "date": ymd(nxt), "who": who})
            nxt = advance(nxt, rec)
    return out


# ------------------------------------------------------------------ fair share (Pages/Family)
def load_share(days=30):
    """Who carries the load over the last `days`: per active seat, cards they Planned (added; repeat copies don't
    count), tasks they Did (done or waiting in Review) and cards they Checked (approved, or ticked off for a kid).
    -> {"rows": [{"m", "planned", "did", "checked"}], "split": [(grown-up, planned)], "total": grown-ups' planned}"""
    s = S["st"]
    if not s:
        return {"rows": [], "split": [], "total": 0}
    rows = {m["id"]: {"m": m, "planned": 0, "did": 0, "checked": 0} for m in active_members()}
    since = jsdate(now_ms() - days * 864e5).toISOString()[:19]
    for it in s["items"]:
        made = (it.get("created") or "")[:19]
        if made >= since and (it.get("occurrence") or 1) == 1 and it.get("created_by") in rows:
            rows[it["created_by"]]["planned"] += 1
        when = (it.get("completed_at") or "")[:19]
        if when < since:
            continue
        if it["kind"] == "task" and it["status"] in ("done", "review") and it.get("completed_by") in rows:
            rows[it["completed_by"]]["did"] += 1
        if it.get("approved_by") in rows:
            rows[it["approved_by"]]["checked"] += 1
    ordered = [rows[m["id"]] for m in active_members()]
    split = [(row["m"], row["planned"]) for row in ordered if not is_kid(row["m"])]
    return {"rows": ordered, "split": split, "total": sum(pair[1] for pair in split)}


def new_card(kind=None):
    if kind is None and window.location.hash.startswith("#board") and S["filter"] in KIND:
        kind = S["filter"]
    open_editor(None, kind)


def open_invite():
    from .Dialogs.Invite import Invite
    _sheet(Invite())


def open_profile():
    from .Dialogs.Profile import Profile
    if _sheet(Profile()):
        state.toast("Profile updated")


def open_family_settings():
    from .Dialogs.FamilySettings import FamilySettings
    if _sheet(FamilySettings()):
        state.toast("Family settings saved")


def scan_code():
    """The camera QR reader; returns the code it found, or None."""
    from .Dialogs.Scan import Scan
    return _sheet(Scan())


def ask(title, text, ok, danger=False):
    return anvil.confirm(text, title=title, buttons=[("Cancel", False), (ok, True)], dismissible=True)


def copy_link():
    window.FTP.copy(invite_link())
    state.toast("Invite link copied")


def can_share():
    return bool(window.navigator.share)


def share_link():
    fam = S["st"]["family"]
    try:
        window.navigator.share({"title": "Join " + fam["name"] + " on Fun To Plan",
                                "text": "Join our family board! Code: " + fam["code"], "url": invite_link()})
    except Exception:
        pass
