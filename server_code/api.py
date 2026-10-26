"""Fun To Plan - server API.

Every client request goes through a single callable, `ftp_api(action, payload_json)`.
All rules (membership, approvals, points, recurring tasks) live here so the
client can never award itself points or read another family's board.

Data model (see anvil.yaml for the full schema):
  families   - one shared board ("the FAMILY epic"), joined with a 6-letter code
  members    - a user's seat in a family (2-4 people), with avatar + points
  items      - cards on the board: kind = task | event | want
  messages   - family chat, system activity and per-card comments
  points_log - ledger of every point awarded or revoked
"""

import calendar
import json
import random
import re
import uuid
from datetime import date, datetime, timedelta, timezone
from itertools import islice

import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

MAX_MEMBERS = 4
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
KINDS = ("task", "event", "want")
OPEN_STATUSES = ("todo", "doing", "review")
PRIORITIES = ("low", "normal", "high")
RECURRENCES = ("none", "daily", "weekdays", "weekly", "biweekly", "monthly")
DONE_VISIBLE_DAYS = 30
CHAT_HISTORY = 150
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class ApiError(Exception):
  def __init__(self, message, code="error"):
    super().__init__(message)
    self.code = code


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------

def _now():
  return datetime.now(timezone.utc)


def _iso(value):
  return value.isoformat() if value is not None else None


def _mid(row):
  return row.get_id() if row is not None else None


def _txt(value, max_len, required=False, label="Text"):
  value = value.strip() if isinstance(value, str) else ""
  if required and not value:
    raise ApiError(f"{label} is required.")
  return value[:max_len]


def _int(value, lo, hi, default=0):
  try:
    value = int(value)
  except (TypeError, ValueError):
    return default
  return max(lo, min(hi, value))


def _client_today(p):
  """The client's local date, so recurring tasks follow the family's calendar."""
  utc_today = _now().date()
  try:
    d = date.fromisoformat(str(p.get("_today")))
    if abs((d - utc_today).days) <= 1:
      return d
  except (TypeError, ValueError):
    pass
  return utc_today


def _parse_date(value):
  if not value:
    return None
  try:
    return date.fromisoformat(str(value)[:10])
  except ValueError:
    raise ApiError("That date doesn't look right.")


def _parse_datetime(value):
  if not value:
    return None
  try:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
  except ValueError:
    raise ApiError("That date and time don't look right.")
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
  return dt


def _n(value):
  """Numbers from Data Tables may come back as floats; the UI wants whole numbers."""
  try:
    return int(value or 0)
  except (TypeError, ValueError):
    return 0


def _key(row):
  return f"FAM-{_n(row['seq'])}"


def _bump(family):
  family["version"] = _n(family["version"]) + 1


def _active_members(family):
  rows = [m for m in app_tables.members.search(family=family, active=True)]
  rows.sort(key=lambda m: m["joined"] or _now())
  return rows


def _new_code():
  for _ in range(50):
    code = "".join(random.choice(CODE_ALPHABET) for _ in range(6))
    if app_tables.families.get(join_code=code) is None:
      return code
  raise ApiError("Couldn't create a join code, please try again.")


def _norm_code(value):
  value = (value or "").upper()
  # Accept a full invite link as well as a bare code.
  m = re.search(r"JOIN=([A-Z0-9]{6})", value)
  if m:
    return m.group(1)
  return "".join(ch for ch in value if ch in CODE_ALPHABET)[:6]


def _ctx(need_family=True):
  user = anvil.users.get_user()
  if user is None:
    raise ApiError("Please log in to continue.", "auth")
  member = app_tables.members.get(user=user, active=True)
  family = member["family"] if member else None
  if need_family and member is None:
    raise ApiError("You're not part of a family board yet.", "nofamily")
  return user, member, family


def _item(p, family):
  row = None
  item_id = p.get("id")
  if item_id:
    try:
      row = app_tables.items.get_by_id(item_id)
    except Exception:
      row = None
  if row is None or _mid(row["family"]) != _mid(family):
    raise ApiError("That card no longer exists.", "gone")
  return row


def _member_in(family, member_id, allow_none=True):
  if not member_id:
    if allow_none:
      return None
    raise ApiError("Pick a family member.")
  try:
    row = app_tables.members.get_by_id(member_id)
  except Exception:
    row = None
  if row is None or _mid(row["family"]) != _mid(family) or not row["active"]:
    raise ApiError("That person isn't in this family.")
  return row


def _sys(family, actor, text, item=None):
  app_tables.messages.add_row(
    family=family, author=actor, kind="system", text=text, item=item, created=_now()
  )


def _profile(p, user):
  email = user["email"] or ""
  name = _txt(p.get("display_name"), 24) or email.split("@")[0][:24] or "Me"
  avatar = _txt(p.get("avatar"), 8) or "🦊"
  color = p.get("color") if COLOR_RE.match(str(p.get("color") or "")) else "#8ecdf2"
  return name, avatar, color


def _next_seq(family):
  seq = _n(family["next_seq"]) or 1
  family["next_seq"] = seq + 1
  return seq


def _advance(d, rec):
  if rec == "daily":
    return d + timedelta(days=1)
  if rec == "weekdays":
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
      d = d + timedelta(days=1)
    return d
  if rec == "weekly":
    return d + timedelta(days=7)
  if rec == "biweekly":
    return d + timedelta(days=14)
  if rec == "monthly":
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
  return d + timedelta(days=1)


# ----------------------------------------------------------------------------
# Serialisation
# ----------------------------------------------------------------------------

def _member_dict(m, week_points, done_counts):
  mid = _mid(m)
  return {
    "id": mid,
    "name": m["display_name"],
    "avatar": m["avatar"],
    "color": m["color"],
    "role": m["role"],
    "points": _n(m["points"]),
    "week_points": week_points.get(mid, 0),
    "done_30": done_counts.get(mid, 0),
    "active": bool(m["active"]),
    "joined": _iso(m["joined"]),
  }


def _item_dict(r):
  return {
    "id": _mid(r),
    "seq": _n(r["seq"]),
    "key": _key(r),
    "kind": r["kind"],
    "title": r["title"],
    "notes": r["notes"] or "",
    "status": r["status"],
    "assignee": _mid(r["assignee"]),
    "created_by": _mid(r["created_by"]),
    "created": _iso(r["created"]),
    "updated": _iso(r["updated"]),
    "due_date": _iso(r["due_date"]),
    "event_at": _iso(r["event_at"]),
    "location": r["location"] or "",
    "link": r["link"] or "",
    "priority": r["priority"] or "normal",
    "points": _n(r["points"]),
    "recurrence": r["recurrence"] or "none",
    "rotate": bool(r["rotate"]),
    "occurrence": _n(r["occurrence"]) or 1,
    "requires_approval": bool(r["requires_approval"]),
    "completed_by": _mid(r["completed_by"]),
    "completed_at": _iso(r["completed_at"]),
    "approved_by": _mid(r["approved_by"]),
    "points_awarded": _n(r["points_awarded"]),
    "acks": list(r["acks"] or []),
    "comment_count": _n(r["comment_count"]),
  }


def _msg_dict(m):
  item = m["item"]
  return {
    "id": _mid(m),
    "kind": m["kind"],
    "author": _mid(m["author"]),
    "text": m["text"],
    "created": _iso(m["created"]),
    "item": _mid(item),
  }


def _state(member, family):
  now = _now()
  members = list(app_tables.members.search(family=family))

  week_points = {}
  for log in app_tables.points_log.search(family=family, created=q.greater_than(now - timedelta(days=7))):
    mid = _mid(log["member"])
    week_points[mid] = week_points.get(mid, 0) + _n(log["delta"])

  open_items = list(app_tables.items.search(family=family, status=q.any_of(*OPEN_STATUSES)))
  done_items = list(app_tables.items.search(
    family=family, status="done", completed_at=q.greater_than(now - timedelta(days=DONE_VISIBLE_DAYS))
  ))
  stale_event = now - timedelta(days=DONE_VISIBLE_DAYS)
  items = [
    r for r in open_items
    if not (r["kind"] == "event" and r["event_at"] is not None and r["event_at"] < stale_event)
  ] + done_items

  done_counts = {}
  for r in done_items:
    mid = _mid(r["completed_by"])
    if mid:
      done_counts[mid] = done_counts.get(mid, 0) + 1

  msgs = list(islice(app_tables.messages.search(
    tables.order_by("created", ascending=False),
    family=family, kind=q.any_of("chat", "system"),
  ), CHAT_HISTORY))
  msgs.reverse()

  return {
    "version": _n(family["version"]),
    "server_time": _iso(now),
    "me": _mid(member),
    "family": {
      "id": _mid(family),
      "name": family["name"],
      "code": family["join_code"],
      "weekly_goal": _n(family["weekly_goal"]) or 100,
      "created": _iso(family["created"]),
      "max_members": MAX_MEMBERS,
    },
    "members": [_member_dict(m, week_points, done_counts) for m in members],
    "items": sorted((_item_dict(r) for r in items), key=lambda d: -d["seq"]),
    "messages": [_msg_dict(m) for m in msgs],
  }


def _detail(family, row):
  comments = app_tables.messages.search(
    tables.order_by("created", ascending=True), family=family, item=row, kind="comment"
  )
  series_done = 0
  if row["series"]:
    series_done = len(app_tables.items.search(family=family, series=row["series"], status="done"))
  return {
    "item": _item_dict(row),
    "comments": [_msg_dict(c) for c in comments],
    "series_done": series_done,
  }


# ----------------------------------------------------------------------------
# Queries (read only)
# ----------------------------------------------------------------------------

def a_bootstrap(p):
  user, member, family = _ctx(need_family=False)
  return {"email": user["email"], "state": _state(member, family) if member else None}


def a_sync(p):
  user, member, family = _ctx(need_family=False)
  if member is None:
    return {"email": user["email"], "state": None}
  if p.get("version") == _n(family["version"]):
    return {"unchanged": True}
  return {"email": user["email"], "state": _state(member, family)}


def a_preview_join(p):
  _ctx(need_family=False)
  code = _norm_code(p.get("code"))
  family = app_tables.families.get(join_code=code) if len(code) == 6 else None
  if family is None:
    raise ApiError("That code doesn't match any family.", "badcode")
  members = _active_members(family)
  return {
    "code": code,
    "name": family["name"],
    "members": [{"name": m["display_name"], "avatar": m["avatar"], "color": m["color"]} for m in members],
    "full": len(members) >= MAX_MEMBERS,
  }


def a_item_detail(p):
  _, _, family = _ctx()
  return _detail(family, _item(p, family))


# ----------------------------------------------------------------------------
# Mutations (each runs inside a transaction)
# ----------------------------------------------------------------------------

def _seed(family, me, p):
  """A few starter cards so a brand new board shows what it can do."""
  today = _client_today(p)
  tz_offset = _int(p.get("_tz"), -900, 900, 0)  # JS getTimezoneOffset(): minutes UTC - local
  days_to_sunday = (6 - today.weekday()) % 7 or 7
  meeting_local = datetime.combine(today + timedelta(days=days_to_sunday), datetime.min.time()).replace(hour=18)
  meeting_utc = (meeting_local + timedelta(minutes=tz_offset)).replace(tzinfo=timezone.utc)
  now = _now()
  seeds = [
    dict(kind="task", title="Water the plants 🌿", notes="Bounty! Anyone can claim it. Repeats every week and takes turns.",
         due_date=today, points=10, recurrence="weekly", rotate=True, priority="normal"),
    dict(kind="task", title="Tidy up the living room", notes="Needs approval: someone else checks it before brownie points are paid out.",
         due_date=today + timedelta(days=1), points=20, requires_approval=True, priority="high"),
    dict(kind="event", title="Family meeting", notes="Plan the week together. Tap “I'm in” to acknowledge.",
         event_at=meeting_utc, location="Kitchen table", priority="normal"),
    dict(kind="want", title="Board game night 🎲", notes="Wants are wishes for the family. +1 them to show support.",
         priority="low", link=""),
  ]
  for s in seeds:
    rec = s.get("recurrence", "none")
    app_tables.items.add_row(
      family=family, seq=_next_seq(family), kind=s["kind"], title=s["title"], notes=s.get("notes", ""),
      status="todo", assignee=None, created_by=me, created=now, updated=now,
      due_date=s.get("due_date"), event_at=s.get("event_at"), location=s.get("location", ""), link=s.get("link", ""),
      priority=s.get("priority", "normal"), points=s.get("points", 0), recurrence=rec, rotate=s.get("rotate", False),
      requires_approval=s.get("requires_approval", False), series=uuid.uuid4().hex if rec != "none" else None,
      occurrence=1, acks=[], comment_count=0, points_awarded=0, points_to=None, spawned_next=False,
      completed_by=None, completed_at=None, approved_by=None,
    )


def m_create_family(p, user, me, family):
  if me is not None:
    raise ApiError("You already belong to a family board. Leave it first.")
  name = _txt(p.get("family_name"), 40, True, "Family name")
  display_name, avatar, color = _profile(p, user)
  now = _now()
  family = app_tables.families.add_row(
    name=name, join_code=_new_code(), created=now, version=1, next_seq=1, weekly_goal=100
  )
  me = app_tables.members.add_row(
    family=family, user=user, display_name=display_name, avatar=avatar, color=color,
    role="owner", points=0, active=True, joined=now,
  )
  _sys(family, me, "started the family board 🎉")
  if p.get("seed", True):
    _seed(family, me, p)
  return {}


def m_join_family(p, user, me, family):
  if me is not None:
    raise ApiError("You already belong to a family board. Leave it first.")
  code = _norm_code(p.get("code"))
  family = app_tables.families.get(join_code=code) if len(code) == 6 else None
  if family is None:
    raise ApiError("That code doesn't match any family. Check it and try again.", "badcode")
  if len(_active_members(family)) >= MAX_MEMBERS:
    raise ApiError("This family board is full (4 people max).", "full")
  display_name, avatar, color = _profile(p, user)
  previous = [m for m in app_tables.members.search(family=family, user=user)]
  if previous:
    # Welcome back: keep the old seat and its points.
    me = previous[0]
    me.update(display_name=display_name, avatar=avatar, color=color, active=True, role="member", joined=_now())
  else:
    me = app_tables.members.add_row(
      family=family, user=user, display_name=display_name, avatar=avatar, color=color,
      role="member", points=0, active=True, joined=_now(),
    )
  _sys(family, me, "joined the family 👋")
  return {}


def m_save_item(p, user, me, family):
  kind = p.get("kind")
  if kind not in KINDS:
    raise ApiError("Pick a card type.")
  title = _txt(p.get("title"), 140, True, "Title")
  notes = _txt(p.get("notes"), 2000)
  priority = p.get("priority") if p.get("priority") in PRIORITIES else "normal"
  assignee = _member_in(family, p.get("assignee"))

  fields = dict(
    kind=kind, title=title, notes=notes, priority=priority, assignee=assignee,
    due_date=None, event_at=None, location="", link="", points=0,
    recurrence="none", rotate=False, requires_approval=False,
  )
  if kind == "task":
    fields["due_date"] = _parse_date(p.get("due_date"))
    fields["points"] = _int(p.get("points"), 0, 500)
    fields["recurrence"] = p.get("recurrence") if p.get("recurrence") in RECURRENCES else "none"
    fields["rotate"] = bool(p.get("rotate")) and fields["recurrence"] != "none"
    fields["requires_approval"] = bool(p.get("requires_approval"))
  elif kind == "event":
    fields["event_at"] = _parse_datetime(p.get("event_at"))
    if fields["event_at"] is None:
      raise ApiError("Events need a date and time.")
    fields["location"] = _txt(p.get("location"), 120)
  else:
    link = _txt(p.get("link"), 400)
    if link and not re.match(r"^https?://", link, re.I):
      link = "https://" + link
    fields["link"] = link

  now = _now()
  if p.get("id"):
    row = _item(p, family)
    if row["status"] == "done" and kind != row["kind"]:
      raise ApiError("Reopen a finished card before changing its type.")
    if kind == "event" or (kind == "want" and row["status"] == "review"):
      fields["status"] = "todo" if row["status"] != "done" else "done"
    if fields["recurrence"] != "none" and not row["series"]:
      fields["series"] = uuid.uuid4().hex
    row.update(updated=now, **fields)
    return {"saved": _mid(row)}

  row = app_tables.items.add_row(
    family=family, seq=_next_seq(family), status="todo", created_by=me, created=now, updated=now,
    series=uuid.uuid4().hex if fields["recurrence"] != "none" else None, occurrence=1,
    acks=[], comment_count=0, points_awarded=0, points_to=None, spawned_next=False,
    completed_by=None, completed_at=None, approved_by=None, **fields
  )
  label = {"task": "a task", "event": "an event", "want": "a want"}[kind]
  extra = f" · {_n(row['points'])} brownie point bounty" if row["points"] else ""
  _sys(family, me, f"added {label} {_key(row)} · {title}{extra}", row)
  return {"saved": _mid(row)}


def _rotate_assignee(row, family):
  members = _active_members(family)
  if not members:
    return None
  current = _mid(row["assignee"])
  ids = [_mid(m) for m in members]
  if current in ids:
    return members[(ids.index(current) + 1) % len(members)]
  return members[0]


def _spawn_next(row, family, today):
  rec = row["recurrence"]
  nxt = _advance(row["due_date"] or today, rec)
  while nxt < today:
    nxt = _advance(nxt, rec)
  assignee = row["assignee"]
  if row["rotate"]:
    assignee = _rotate_assignee(row, family)
  elif assignee is not None and not assignee["active"]:
    assignee = None
  now = _now()
  app_tables.items.add_row(
    family=family, seq=_next_seq(family), kind="task", title=row["title"], notes=row["notes"],
    status="todo", assignee=assignee, created_by=row["created_by"], created=now, updated=now,
    due_date=nxt, event_at=None, location="", link="", priority=row["priority"], points=row["points"],
    recurrence=rec, rotate=row["rotate"], requires_approval=row["requires_approval"],
    series=row["series"] or uuid.uuid4().hex, occurrence=(_n(row["occurrence"]) or 1) + 1,
    acks=[], comment_count=0, points_awarded=0, points_to=None, spawned_next=False,
    completed_by=None, completed_at=None, approved_by=None,
  )
  row["spawned_next"] = True


def _finish(row, family, completer, approver, today):
  now = _now()
  row.update(status="done", completed_by=completer, completed_at=now, approved_by=approver, updated=now)
  pts = _n(row["points"])
  if pts > 0 and completer is not None:
    completer["points"] = _n(completer["points"]) + pts
    row.update(points_awarded=pts, points_to=completer)
    app_tables.points_log.add_row(
      family=family, member=completer, delta=pts, reason=f"{_key(row)} {row['title']}", item=row, created=now
    )
  if approver is not None:
    tail = f" · +{pts} brownie points to {completer['display_name']}" if pts and completer else ""
    _sys(family, approver, f"approved {_key(row)} · {row['title']}{tail}", row)
  else:
    tail = f" · +{pts} brownie points" if pts else ""
    _sys(family, completer, f"completed {_key(row)} · {row['title']}{tail}", row)
  if row["recurrence"] not in (None, "none") and not row["spawned_next"]:
    _spawn_next(row, family, today)
  return pts


def m_complete(p, user, me, family):
  row = _item(p, family)
  if row["kind"] == "event":
    raise ApiError("Events can't be completed. Acknowledge them instead.")
  if row["status"] in ("done", "review"):
    raise ApiError("This card is already finished.")
  now = _now()
  if row["kind"] == "want":
    row.update(status="done", completed_by=me, completed_at=now, updated=now)
    _sys(family, me, f"got it! {_key(row)} · {row['title']} 🎁", row)
    return {"fx": {"kind": "want"}}
  if row["requires_approval"] and len(_active_members(family)) > 1:
    row.update(status="review", completed_by=me, completed_at=now, updated=now)
    _sys(family, me, f"finished {_key(row)} · {row['title']} and asks for approval ✋", row)
    return {"fx": {"kind": "review"}}
  pts = _finish(row, family, me, None, _client_today(p))
  return {"fx": {"kind": "done", "points": pts}}


def m_approve(p, user, me, family):
  row = _item(p, family)
  if row["status"] != "review":
    raise ApiError("This card isn't waiting for approval.")
  completer = row["completed_by"]
  if completer is not None and _mid(completer) == _mid(me) and len(_active_members(family)) > 1:
    raise ApiError("Someone else in the family has to approve your own work.")
  pts = _finish(row, family, completer or me, me, _client_today(p))
  return {"fx": {"kind": "approved", "points": pts}}


def m_reject(p, user, me, family):
  row = _item(p, family)
  if row["status"] != "review":
    raise ApiError("This card isn't waiting for approval.")
  reason = _txt(p.get("reason"), 500)
  now = _now()
  row.update(status="doing", completed_at=None, updated=now)
  _sys(family, me, f"sent {_key(row)} · {row['title']} back for another try ↩", row)
  if reason:
    app_tables.messages.add_row(family=family, author=me, kind="comment", text=reason, item=row, created=now)
    row["comment_count"] = _n(row["comment_count"]) + 1
  return {}


def m_reopen(p, user, me, family):
  row = _item(p, family)
  if row["status"] not in ("done", "review"):
    raise ApiError("This card is still open.")
  now = _now()
  if row["points_awarded"] and row["points_to"] is not None:
    target = row["points_to"]
    target["points"] = _n(target["points"]) - _n(row["points_awarded"])
    app_tables.points_log.add_row(
      family=family, member=target, delta=-_n(row["points_awarded"]),
      reason=f"{_key(row)} reopened", item=row, created=now,
    )
  row.update(status="todo", completed_by=None, completed_at=None, approved_by=None,
             points_awarded=0, points_to=None, updated=now)
  _sys(family, me, f"reopened {_key(row)} · {row['title']}", row)
  return {}


def m_move(p, user, me, family):
  row = _item(p, family)
  to = p.get("to")
  if row["kind"] == "event" or to not in ("todo", "doing"):
    raise ApiError("That move isn't possible.")
  if row["status"] not in ("todo", "doing"):
    raise ApiError("Reopen the card first.")
  row.update(status=to, updated=_now())
  if to == "doing" and row["kind"] == "task" and row["assignee"] is None:
    row["assignee"] = me
  return {}


def m_claim(p, user, me, family):
  row = _item(p, family)
  if row["kind"] != "task" or row["status"] == "done":
    raise ApiError("Only open tasks can be claimed.")
  current = row["assignee"]
  if current is not None and current["active"] and _mid(current) != _mid(me):
    raise ApiError(f"{current['display_name']} already has this one.")
  row.update(assignee=me, updated=_now())
  if row["points"]:
    _sys(family, me, f"claimed the bounty {_key(row)} · {row['title']} ({_n(row['points'])} brownie points)", row)
  return {}


def m_ack(p, user, me, family):
  row = _item(p, family)
  acks = list(row["acks"] or [])
  mid = _mid(me)
  if mid in acks:
    acks.remove(mid)
    acked = False
  else:
    acks.append(mid)
    acked = True
  row["acks"] = acks
  return {"acked": acked}


def m_delete_item(p, user, me, family):
  row = _item(p, family)
  if _mid(row["created_by"]) != _mid(me) and me["role"] != "owner":
    raise ApiError("Only the person who created this card (or the family owner) can delete it.")
  for msg in app_tables.messages.search(item=row):
    if msg["kind"] == "comment":
      msg.delete()
    else:
      msg["item"] = None
  for log in app_tables.points_log.search(item=row):
    log["item"] = None
  key, title = _key(row), row["title"]
  row.delete()
  _sys(family, me, f"deleted {key} · {title}")
  return {"deleted": True}


def m_comment(p, user, me, family):
  row = _item(p, family)
  text = _txt(p.get("text"), 1000, True, "Comment")
  app_tables.messages.add_row(family=family, author=me, kind="comment", text=text, item=row, created=_now())
  row["comment_count"] = _n(row["comment_count"]) + 1
  return {}


def m_send_message(p, user, me, family):
  text = _txt(p.get("text"), 1000, True, "Message")
  app_tables.messages.add_row(family=family, author=me, kind="chat", text=text, item=None, created=_now())
  return {}


def m_update_profile(p, user, me, family):
  display_name, avatar, color = _profile(p, user)
  me.update(display_name=display_name, avatar=avatar, color=color)
  return {}


def m_update_family(p, user, me, family):
  if me["role"] != "owner":
    raise ApiError("Only the family owner can change these settings.")
  family.update(
    name=_txt(p.get("name"), 40, True, "Family name"),
    weekly_goal=_int(p.get("weekly_goal"), 10, 5000, 100),
  )
  return {}


def m_regen_code(p, user, me, family):
  if me["role"] != "owner":
    raise ApiError("Only the family owner can change the join code.")
  family["join_code"] = _new_code()
  return {}


def _release(member, family):
  member["active"] = False
  for r in app_tables.items.search(family=family, assignee=member, status=q.any_of("todo", "doing")):
    r["assignee"] = None


def m_remove_member(p, user, me, family):
  if me["role"] != "owner":
    raise ApiError("Only the family owner can remove people.")
  target = _member_in(family, p.get("member_id"), allow_none=False)
  if _mid(target) == _mid(me):
    raise ApiError("Use “Leave family” to remove yourself.")
  _release(target, family)
  _sys(family, me, f"removed {target['display_name']} from the family")
  return {}


def m_leave_family(p, user, me, family):
  was_owner = me["role"] == "owner"
  _release(me, family)
  me["role"] = "member"
  if was_owner:
    others = _active_members(family)
    if others:
      others[0]["role"] = "owner"
  _sys(family, me, "left the family")
  return {}


QUERIES = {
  "bootstrap": a_bootstrap,
  "sync": a_sync,
  "preview_join": a_preview_join,
  "item_detail": a_item_detail,
}

MUTATIONS = {
  # action: (handler, needs an existing family)
  "create_family": (m_create_family, False),
  "join_family": (m_join_family, False),
  "save_item": (m_save_item, True),
  "complete": (m_complete, True),
  "approve": (m_approve, True),
  "reject": (m_reject, True),
  "reopen": (m_reopen, True),
  "move": (m_move, True),
  "claim": (m_claim, True),
  "ack": (m_ack, True),
  "delete_item": (m_delete_item, True),
  "comment": (m_comment, True),
  "send_message": (m_send_message, True),
  "update_profile": (m_update_profile, True),
  "update_family": (m_update_family, True),
  "regen_code": (m_regen_code, True),
  "remove_member": (m_remove_member, True),
  "leave_family": (m_leave_family, True),
}


def _mutate(handler, p, need_family):
  def tx():
    user, me, family = _ctx(need_family)
    extra = handler(p, user, me, family) or {}
    # Bump the board version of every family touched so other devices refresh.
    touched = {}
    if family is not None:
      touched[_mid(family)] = family
    now_member = app_tables.members.get(user=user, active=True)
    if now_member is not None:
      touched[_mid(now_member["family"])] = now_member["family"]
    for fam in touched.values():
      _bump(fam)
    return extra

  extra = tables.in_transaction(tx)()
  user, me, family = _ctx(need_family=False)
  out = {"email": user["email"], "state": _state(me, family) if me else None}
  out.update(extra)
  if p.get("_detail") and p.get("id") and family is not None and not extra.get("deleted"):
    try:
      out["detail"] = _detail(family, _item(p, family))
    except ApiError:
      pass
  return out


@anvil.server.callable
def ftp_api(action, payload_json=None):
  """Single entry point for the client. Always returns a JSON string."""
  try:
    p = json.loads(payload_json) if payload_json else {}
    if not isinstance(p, dict):
      p = {}
    if action in QUERIES:
      data = QUERIES[action](p)
    elif action in MUTATIONS:
      handler, need_family = MUTATIONS[action]
      data = _mutate(handler, p, need_family)
    else:
      raise ApiError(f"Unknown action: {action}")
    return json.dumps({"ok": True, "data": data})
  except ApiError as e:
    return json.dumps({"ok": False, "error": str(e), "code": e.code})
