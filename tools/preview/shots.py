"""Screenshots of every Fun To Plan screen from the local preview (tools/preview/serve.py must be running).

    python -I tools/preview/shots.py <port> <outdir> [desktop|phone] [light|night] [app|landing|spinner]

Defaults: all sizes, both themes, all parts. Uses APP_MAKER/template/tools/live/drive.mjs (headless Chrome).
"""
import json
import os
import pathlib
import subprocess
import sys

DRIVE = pathlib.Path(r"C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\template\tools\live\drive.mjs")


def steps_for(part, phone, tag):
  # D() = the app's document (inside the phone iframe on phone runs)
  D = "(document.querySelector('iframe') ? document.querySelector('iframe').contentDocument : document)"
  click = lambda sel: {"eval": f"(function(){{var e={D}.querySelector({json.dumps(sel)}); if(!e) return 'MISSING {sel}'; e.click(); return 'ok';}})()"}
  scroll = lambda sel, y: {"eval": f"(function(){{var e={D}.querySelector({json.dumps(sel)}); if(e) e.scrollTop={y}; return 'ok';}})()"}
  shot = lambda name: {"shot": f"{tag}-{name}"}
  wait = {"wait": 700}
  if part == "spinner":
    return [{"wait": 600}, shot("spinner")]
  if part == "landing":
    s = [{"waitFor": f"{D}.querySelector('.land-h1')", "timeout": 20000}, {"wait": 900}, shot("landing-1")]
    for i, y in enumerate((800, 1700, 2600, 3500, 9000), 2):
      s += [scroll(".land", y), {"wait": 400}, shot(f"landing-{i}")]
    s += [scroll(".land", 0), click(".land-nav .btn, .land-cta .btn"), wait, shot("auth")]
    return s
  nav = (".tab[data-view={}]" if phone else ".rail-item[data-view={}]").format
  s = [{"waitFor": f"{D}.querySelector('.hero')", "timeout": 20000}, {"wait": 1200}, shot("home")]
  s += [scroll(".main", 700), {"wait": 300}, shot("home-2"), scroll(".main", 0)]
  s += [click(nav("board")), wait, shot("board")]
  if phone:
    s += [scroll(".main", 520), {"wait": 300}, shot("board-2"), scroll(".main", 0)]
  s += [click(".board .card"), {"wait": 1200}, shot("detail"), click(".layer .backdrop"), {"wait": 500}]
  s += [click(nav("chat")), {"wait": 900}, shot("chat")]
  s += [click(nav("family")), wait, shot("family")]
  s += [scroll(".main", 900), {"wait": 300}, shot("family-2"), scroll(".main", 0)]
  s += [click(".tab-add" if phone else ".rail-add"), {"wait": 900}, shot("new-card")]
  s += [{"eval": f"(function(){{var b={D}.querySelectorAll('.layer .seg button'); if(b[1]) b[1].click(); return b.length;}})()"}, {"wait": 500}, shot("new-event")]
  return s


def main():
  port, out = sys.argv[1], pathlib.Path(sys.argv[2])
  sizes = [a for a in sys.argv[3:] if a in ("desktop", "phone")] or ["desktop", "phone"]
  themes = [a for a in sys.argv[3:] if a in ("light", "night")] or ["light", "night"]
  parts = [a for a in sys.argv[3:] if a in ("app", "landing", "spinner")] or ["app", "landing", "spinner"]
  out.mkdir(parents=True, exist_ok=True)
  for size in sizes:
    for theme in themes:
      for part in parts:
        if part == "spinner" and size == "phone":
          continue
        tag = f"{size}-{theme}"
        who = "guest" if part == "landing" else "mom"
        q = f"as={who}&theme={theme}"
        base = f"http://127.0.0.1:{port}"
        url = f"{base}/spinner?theme={theme}" if part == "spinner" else (f"{base}/phone?{q}" if size == "phone" else f"{base}/?{q}")
        steps = out / f"steps-{tag}-{part}.json"
        steps.write_text(json.dumps(steps_for(part, size == "phone", tag)), encoding="utf-8")
        env = dict(os.environ, WINDOW="520,1000" if size == "phone" else "1280,900")
        r = subprocess.run(["node", str(DRIVE), url, str(steps), str(out / f"run-{tag}-{part}")], env=env,
                           capture_output=True, encoding="utf-8", errors="replace")
        for line in r.stdout.splitlines():
          if any(k in line for k in ("EXCEPTION", "MISSING", "TIMEOUT", "error", "ERROR")):
            print(tag, part, line)
        for png in (out / f"run-{tag}-{part}").glob("*.png"):
          png.replace(out / png.name)
  print("shots in", out)


if __name__ == "__main__":
  main()
