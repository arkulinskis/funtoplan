"""Local preview of Fun To Plan: the real ftp.js UI on top of the real server_code/api.py (strict Anvil mock).

    python C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/tools/gitapp_test.py funtoplan tools/preview/serve.py [port]
    (no -I: the mock reads anvil.yaml with PyYAML)

Then open http://127.0.0.1:<port>/?as=mom   (as = mom | dad | mia | leo | guest; &theme=night for night mode)

A demo family ("The Ozolins", 4 people, ~14 cards, chat, points) is seeded on start. Every browser shares one
signed-in user (the last ?as=), which is fine for screenshots. The page uses anvil.yaml's head_html (minus the legal
kit, which needs Anvil) and inlines theme/assets/theme.css like Anvil does. /spinner shows Anvil's startup spinner.
"""
import http.server
import json
import pathlib
import socketserver
import sys
from datetime import date, datetime, timedelta, timezone

import yaml
import anvil.users
from anvil.tables import app_tables as T
from app import api

REPO = pathlib.Path(__file__).resolve().parents[2]
ASSETS = REPO / "theme" / "assets"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
TYPES = {".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".html": "text/html"}

PEOPLE = {
  "mom": ("Mom", "🦊", "#e8505b"),
  "dad": ("Dad", "🐻", "#2f80ed"),
  "mia": ("Mia", "🦄", "#9b51e0"),
  "leo": ("Leo", "🦖", "#27ae60"),
}
USERS = {}


def call(who, action, **payload):
  anvil.users.CURRENT[0] = USERS[who]
  payload.setdefault("_today", date.today().isoformat())
  out = json.loads(api.ftp_api(action, json.dumps(payload)))
  if not out["ok"]:
    raise RuntimeError(f"{action}: {out['error']}")
  return out["data"]


def item_id(title):
  for r in T.items.search():
    if r["title"] == title:
      return r.get_id()
  raise KeyError(title)


def seed():
  for who, (name, _, _) in PEOPLE.items():
    email = f"{who}@ozolins.example"
    USERS[who] = T.users.add_row(email=email, enabled=True)
    anvil.users.PASSWORDS[email] = "secret1"
  name, av, col = PEOPLE["mom"]
  call("mom", "create_family", family_name="The Ozolins", display_name=name, avatar=av, color=col, seed=True)
  code = list(T.families.search())[0]["join_code"]
  for who in ("dad", "mia", "leo"):
    name, av, col = PEOPLE[who]
    call(who, "join_family", code=code, display_name=name, avatar=av, color=col)
  mid = {w: T.members.get(user=USERS[w]).get_id() for w in PEOPLE}
  today = date.today()
  sat = today + timedelta(days=(5 - today.weekday()) % 7 or 7)
  cards = [
    ("mom", dict(kind="task", title="Empty the dishwasher", assignee=mid["leo"], due_date=today.isoformat(), points=15, priority="high")),
    ("dad", dict(kind="task", title="Walk Biscuit 🐕", assignee=mid["mia"], due_date=today.isoformat(), points=10, recurrence="daily", rotate=True)),
    ("mom", dict(kind="task", title="Mow the lawn", due_date=(today + timedelta(days=3)).isoformat(), points=40, notes="Bounty! First to claim it gets it.")),
    ("dad", dict(kind="task", title="Sort the recycling", assignee=mid["dad"], due_date=(today - timedelta(days=1)).isoformat(), points=5)),
    ("mia", dict(kind="task", title="Science project poster", assignee=mid["mia"], due_date=(today + timedelta(days=5)).isoformat(), points=25)),
    ("leo", dict(kind="task", title="Clean my room", assignee=mid["leo"], points=20, requires_approval=True)),
    ("mom", dict(kind="event", title="Mia's football match ⚽", event_at=datetime.combine(sat, datetime.min.time()).replace(hour=10, tzinfo=timezone.utc).isoformat(), location="Riverside Park")),
    ("dad", dict(kind="event", title="Grandma's birthday dinner", event_at=datetime.combine(today + timedelta(days=9), datetime.min.time()).replace(hour=18, tzinfo=timezone.utc).isoformat(), location="Grandma's")),
    ("leo", dict(kind="want", title="Trampoline park trip", priority="high")),
    ("mia", dict(kind="want", title="Pizza Friday 🍕")),
    ("dad", dict(kind="task", title="Fix the bike tyre", assignee=mid["dad"], points=15)),
    ("mom", dict(kind="task", title="Bake cookies for school", assignee=mid["mom"], points=10)),
  ]
  for who, c in cards:
    call(who, "save_item", **c)
  call("mia", "move", id=item_id("Science project poster"), to="doing")
  call("dad", "move", id=item_id("Fix the bike tyre"), to="doing")
  call("leo", "complete", id=item_id("Clean my room"))
  call("mom", "complete", id=item_id("Bake cookies for school"))
  call("leo", "complete", id=item_id("Empty the dishwasher"))
  call("mia", "complete", id=item_id("Walk Biscuit 🐕"))
  call("mia", "claim", id=item_id("Water the plants 🌿"))
  call("mia", "complete", id=item_id("Water the plants 🌿"))
  for who in ("mom", "dad", "leo"):
    call(who, "ack", id=item_id("Mia's football match ⚽"))
  call("mia", "ack", id=item_id("Pizza Friday 🍕"))
  call("leo", "ack", id=item_id("Pizza Friday 🍕"))
  call("dad", "comment", id=item_id("Mow the lawn"), text="I'll lend you the good gloves 🧤")
  call("mom", "send_message", text="Who's picking up milk on the way home?")
  call("dad", "send_message", text="Me! Also FAM-7 is looking lonely 👀")
  call("leo", "send_message", text="I cleaned my room, someone check FAM-10 pls")
  call("mia", "send_message", text="Can we do pizza on Friday? 🍕")


def page(who, theme):
  head = yaml.safe_load((REPO / "anvil.yaml").read_text(encoding="utf-8"))["native_deps"]["head_html"]
  head = "\n".join(l for l in head.splitlines() if "legal-kit" not in l)
  theme_css = (ASSETS / "theme.css").read_text(encoding="utf-8")
  return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<base href="/"><script>try {{ localStorage.setItem('ftp.theme', {json.dumps(theme)}); }} catch (e) {{}}</script>
<style>{theme_css}</style>{head}</head><body><div id="host"></div><script>
fetch('/as?who={who}').then(function () {{
  FunToPlan.mount(document.getElementById('host'), function (action, payload) {{
    return fetch('/api', {{ method: 'POST', body: JSON.stringify({{ action: action, payload: payload }}) }}).then(function (r) {{ return r.text(); }});
  }});
}});
</script></body></html>"""


def spinner_page(theme):
  theme_css = (ASSETS / "theme.css").read_text(encoding="utf-8")
  attr = ' data-ftp-theme="night"' if theme == "night" else ""
  return f"""<!doctype html><html{attr}><head><meta charset="utf-8"><style>
html, body {{ margin: 0; height: 100%; }} .anvil-spinner {{ position: fixed; background-color: var(--anvil-spinner-bg); }}
{theme_css}</style></head><body><div class="anvil-spinner"><svg class="anvil-spinner-svg"></svg></div></body></html>"""


def bridge(action, payload_json):
  p = json.loads(payload_json or "{}")
  try:
    if action == "login":
      anvil.users.login_with_email(p.get("email", ""), p.get("password", ""))
      action, payload_json = "bootstrap", "{}"
    elif action == "signup":
      anvil.users.signup_with_email(p.get("email", ""), p.get("password", ""))
      action, payload_json = "bootstrap", "{}"
    elif action == "logout":
      anvil.users.logout()
      return json.dumps({"ok": True, "data": {}})
    elif action == "reset_password":
      return json.dumps({"ok": True, "data": {}})
  except Exception as e:
    return json.dumps({"ok": False, "error": str(e) or type(e).__name__, "code": "auth_failed"})
  return api.ftp_api(action, payload_json)


class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self, *a):
    pass

  def reply(self, body, ctype="text/html", code=200):
    data = body if isinstance(body, bytes) else body.encode("utf-8")
    self.send_response(code)
    self.send_header("Content-Type", ctype + ("; charset=utf-8" if not ctype.startswith("image/png") else ""))
    self.send_header("Cache-Control", "no-store")
    self.end_headers()
    self.wfile.write(data)

  def do_GET(self):
    path, _, query = self.path.partition("?")
    qs = dict(x.split("=", 1) for x in query.split("&") if "=" in x)
    if path == "/":
      return self.reply(page(qs.get("as", "mom"), qs.get("theme", "light")))
    if path == "/phone":  # a 390 x 844 phone frame around the app (headless Chrome windows can't be that narrow)
      return self.reply('<!doctype html><body style="margin:0;background:#888"><iframe src="/?%s" '
                        'style="width:390px;height:844px;border:0;display:block"></iframe></body>' % query)
    if path == "/spinner":
      return self.reply(spinner_page(qs.get("theme", "light")))
    if path == "/as":
      who = qs.get("who", "mom")
      anvil.users.CURRENT[0] = USERS.get(who)
      return self.reply("ok", "text/plain")
    if path.startswith("/_/theme/"):
      f = ASSETS / path[len("/_/theme/"):]
      if f.is_file():
        return self.reply(f.read_bytes(), TYPES.get(f.suffix, "application/octet-stream"))
    self.reply("not found", "text/plain", 404)

  def do_POST(self):
    body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
    self.reply(bridge(body.get("action"), body.get("payload")), "application/json")


if __name__ == "__main__":
  seed()
  socketserver.TCPServer.allow_reuse_address = False
  with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as srv:
    print(f"Fun To Plan preview on http://127.0.0.1:{PORT}/?as=mom", flush=True)
    srv.serve_forever()
