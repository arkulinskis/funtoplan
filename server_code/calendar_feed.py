"""The family week in the phone's own calendar: a private iCalendar feed (RFC 5545) per seat.

    https://funtoplan.com/cal/<token>.ics          events from 7 days ago on + every open task with a due date
    https://funtoplan.com/cal/<token>.ics?mine=1   the same events, but only the tasks on that person's name

Apple Calendar subscribes to the webcal:// form of the address, Google Calendar through
calendar.google.com/calendar/r?cid=<address> (Dialogs/CalLink builds both). Calendar apps fetch it about once an hour.

Who can read what: the token (uuid4, 128 random bits) is the only key. It belongs to one seat (cal_links row, made by
api.a_cal_link) and only ever opens that seat's own family board; a reset gives a new token, and a seat that left or was
removed gets 404 (its rows are deleted by api._release as well). The feed shows titles, times, places, names and
points - never notes, comments, chat or anyone's email.

Served at the domain root with @anvil.server.route (same guard as seo_routes.py); /_/api/cal/<token>.ics
(http_endpoint) always works too, for runtimes without routes (the local App Server).
"""
import re
from datetime import datetime, timedelta, timezone

import anvil
import anvil.server
import anvil.tables.query as q
from anvil.tables import app_tables

SITE = "https://funtoplan.com"
TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
OPEN = ("todo", "doing", "review")
PAST_DAYS = 7          # events this far back stay in the calendar
FETCH_NOTE_MIN = 10    # write last_fetch at most this often
NOT_READY = ("The phone calendar link is almost ready: the app needs a small update by its owner first. "
             "Everything else works as usual.")
ROUTE = getattr(anvil.server, "route", None)
PATH = "/cal/" if ROUTE else "/_/api/cal/"


def feed_path(token):
    """The address of a token's feed, relative to the site (the browser adds its own origin)."""
    return PATH + token + ".ics"


# ---------------------------------------------------------------- iCalendar text (RFC 5545)
def esc(value):
    """TEXT values: backslash, semicolon and comma escaped, newlines as \\n."""
    s = str(value or "")
    s = s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return s.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")


def fold(line):
    """Lines longer than 75 octets continue on the next line after CRLF + one space (never inside a character)."""
    if len(line.encode("utf-8")) <= 75:
        return line
    parts, cur, size, limit = [], "", 0, 75
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            parts.append(cur)
            cur, size, limit = "", 0, 74  # a continuation line starts with the space
        cur += ch
        size += n
    parts.append(cur)
    return "\r\n ".join(parts)


def _utc(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _uid(row):
    return re.sub(r"[^0-9A-Za-z]+", "-", str(row.get_id())).strip("-") + "@funtoplan.com"


def _n(v):
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def _who(m):
    return ("%s %s" % (m["avatar"] or "", m["display_name"] or "")).strip() if m is not None else ""


def _event(row, stamp, members):
    start = row["event_at"]
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    names = [members[a]["display_name"] for a in (row["acks"] or []) if a in members]
    desc = ["FAM-%d" % _n(row["seq"])]
    if row["assignee"] is not None:
        desc.append("Host: " + _who(row["assignee"]))
    desc.append(("Coming: " + ", ".join(names)) if names else "Nobody has said “I'm in” yet")
    desc.append("Open the family board: %s/#board" % SITE)
    lines = [
        "BEGIN:VEVENT",
        "UID:" + _uid(row),
        "DTSTAMP:" + stamp,
        "DTSTART:" + _utc(start),
        "DTEND:" + _utc(start + timedelta(hours=1)),
        "SUMMARY:" + esc(row["title"]),
    ]
    if row["location"]:
        lines.append("LOCATION:" + esc(row["location"]))
    lines += [
        "DESCRIPTION:" + esc("\n".join(desc)),
        "STATUS:CONFIRMED",
        "LAST-MODIFIED:" + _utc(row["updated"] or row["created"] or start),
        "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + esc(row["title"]), "TRIGGER:-PT1H", "END:VALARM",
        "END:VEVENT",
    ]
    return lines


def _task(row, stamp):
    d = row["due_date"]
    who = _who(row["assignee"]) or "✋ anyone"
    summary = ["FAM-%d" % _n(row["seq"]), row["title"] or "", who]
    if _n(row["points"]):
        summary.append("%d 🍫" % _n(row["points"]))
    if row["status"] == "review":
        summary.append("waiting for approval")
    desc = []
    if row["priority"] == "high":
        desc.append("High priority")
    if (row["recurrence"] or "none") != "none":
        desc.append("Repeats " + row["recurrence"] + (", taking turns" if row["rotate"] else ""))
    if row["requires_approval"]:
        desc.append("Someone checks it before the brownie points are paid")
    desc.append("Tick it off on the family board: %s/#board" % SITE)
    return [
        "BEGIN:VEVENT",
        "UID:" + _uid(row),
        "DTSTAMP:" + stamp,
        "DTSTART;VALUE=DATE:" + d.strftime("%Y%m%d"),
        "DTEND;VALUE=DATE:" + (d + timedelta(days=1)).strftime("%Y%m%d"),
        "SUMMARY:" + esc(" · ".join(summary)),
        "DESCRIPTION:" + esc("\n".join(desc)),
        "TRANSP:TRANSPARENT",
        "LAST-MODIFIED:" + _utc(row["updated"] or row["created"] or datetime.now(timezone.utc)),
        "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:" + esc(row["title"]), "TRIGGER:PT9H", "END:VALARM",
        "END:VEVENT",
    ]


def build_ics(family, member, mine=False, now=None):
    """The whole feed for one seat's family (only that family's rows are ever read)."""
    now = now or datetime.now(timezone.utc)
    stamp = _utc(now)
    members = {m.get_id(): m for m in app_tables.members.search(family=family)}
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Arkvital//Fun To Plan//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:" + esc("%s · Fun To Plan" % (family["name"] or "Family")),
        "X-WR-CALDESC:" + esc("The family week from %s: events and jobs with a due date." % SITE),
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]
    events = app_tables.items.search(family=family, kind="event", event_at=q.greater_than_or_equal_to(now - timedelta(days=PAST_DAYS)))
    for row in sorted(events, key=lambda r: r["event_at"]):
        lines += _event(row, stamp, members)
    tasks = [r for r in app_tables.items.search(family=family, kind="task", status=q.any_of(*OPEN)) if r["due_date"] is not None]
    if mine:
        tasks = [r for r in tasks if r["assignee"] is not None and r["assignee"].get_id() == member.get_id()]
    for row in sorted(tasks, key=lambda r: (r["due_date"], _n(r["seq"]))):
        lines += _task(row, stamp)
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"


# ---------------------------------------------------------------- the address
def _table():
    try:
        return getattr(app_tables, "cal_links")
    except Exception:
        return None


def _not_found():
    return anvil.server.HttpResponse(404, "No calendar here. Ask for a new link on the Week page of Fun To Plan.",
                                     headers={"Content-Type": "text/plain; charset=utf-8", "X-Robots-Tag": "noindex"})


def find_link(token):
    """The cal_links row for a token, or None (bad format, unknown, reset, or the seat left that family)."""
    token = str(token or "")
    if token.endswith(".ics"):
        token = token[:-4]
    table = _table()
    if not TOKEN_RE.match(token) or table is None:
        return None
    try:
        rows = list(table.search(token=token))
    except Exception:
        return None
    if len(rows) != 1:
        return None
    link = rows[0]
    member, family = link["member"], link["family"]
    if member is None or family is None or not member["active"] or member["family"] is None:
        return None
    if member["family"].get_id() != family.get_id():
        return None
    return link


def serve(token, mine_flag=None):
    link = find_link(token)
    if link is None:
        return _not_found()
    if mine_flag is None:
        try:
            mine_flag = (anvil.server.request.query_params or {}).get("mine")
        except Exception:
            mine_flag = None
    mine = str(mine_flag or "").lower() in ("1", "true", "yes", "on")
    now = datetime.now(timezone.utc)
    body = build_ics(link["family"], link["member"], mine, now)
    try:
        last = link["last_fetch"]
        if last is None or (now - (last if last.tzinfo else last.replace(tzinfo=timezone.utc))) > timedelta(minutes=FETCH_NOTE_MIN):
            link["last_fetch"] = now
    except Exception:
        pass
    return anvil.server.HttpResponse(
        200, anvil.BlobMedia("text/calendar; charset=utf-8", body.encode("utf-8"), name="funtoplan.ics"),
        headers={"Cache-Control": "private, max-age=900", "X-Robots-Tag": "noindex, nofollow",
                 "Content-Disposition": 'inline; filename="funtoplan.ics"'})


@anvil.server.http_endpoint("/cal/:token")
def cal_feed_endpoint(token=None, mine=None, **params):
    return serve(token, mine)


if ROUTE:  # the domain-root address (funtoplan.com/cal/...): the Python 3.10+ server runtimes have routes
    @ROUTE("/cal/:token")
    def cal_feed_route(token=None, mine=None, **params):
        return serve(token, mine)
