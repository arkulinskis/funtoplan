from anvil import *
import anvil.js

from ._anvil_designer import WeekEntryTemplate
from ... import ftp


class WeekEntry(WeekEntryTemplate):
    """A small note on the Week page: an event (blue, with its time and place), a task due that day (yellow; mint and
    struck through when done; red edge when late) or a coming turn of a repeating task (faded, dashed: "↻ Leo's turn").
    Tap = the card's sheet (a coming turn opens the card it repeats).
    item = {"it": card dict, "time": "18:00" (events), "late", "ghost", "who" (ghost: whose turn), "show_day"}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        x = self.item
        it = x["it"]
        ghost = bool(x.get("ghost"))
        done = ftp.eff(it) == "done" and not ghost
        node = anvil.js.get_dom_node(self)
        node.className = "wk-entry k-" + it["kind"] + (" is-done" if done else "") + (" ghost" if ghost else "") + \
            (" late" if x.get("late") and not done else "")
        d = ftp.loose(self.dom_nodes)
        person = ftp.member(x.get("who")) if ghost else ftp.member(it.get("assignee"))
        if ghost:
            ftp.text(d["time"], "↻")
            note = (person["name"] + "'s turn") if person else "next turn"
        elif it["kind"] == "event":
            ftp.text(d["time"], x.get("time") or "")
            note = it.get("location") or ""
        else:
            ftp.text(d["time"], "")
            note = ""
            if x.get("show_day") and it.get("due_date"):
                note = ftp.fmt_day(ftp.parse_ymd(it["due_date"]))
            elif x.get("late") and not done:
                note = "late"
            elif not person and not done:
                note = "anyone"
        d["time"].style.display = "" if d["time"].textContent else "none"
        ftp.text(d["title"], it["title"])
        ftp.text(d["note"], note)
        d["note"].style.display = "" if note else "none"
        d["who"].style.display = "" if person else "none"
        if person:
            ftp.avatar(d["who"], person, "xs")
            d["who"].setAttribute("aria-hidden", "true")
        pts = it.get("points") or 0
        d["pts"].style.display = "" if (pts and it["kind"] == "task") else "none"
        ftp.text(d["pts_text"], pts)
        label = "%s: %s" % (it["key"], it["title"])
        if ghost:
            label = "Coming turn of %s%s" % (label, (", " + person["name"] + "'s turn") if person else "")
        elif person:
            label += ", " + person["name"]
        if done:
            label += ", done"
        node.setAttribute("aria-label", label)
        node.addEventListener("click", self._click)

    def _click(self, event):
        ftp.open_detail(self.item["it"]["id"])
