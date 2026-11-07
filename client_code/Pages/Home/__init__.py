import math

from anvil import *

from ._anvil_designer import HomeTemplate
from ... import ftp


class Home(HomeTemplate):
    """Today (#home): your level ring and points, the family's weekly goal, what needs you (approve / I'm in / Done),
    open bounties to claim, events in the next two weeks and what got done lately. Redraws when the board syncs."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.refresh()

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self.refresh)

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self.refresh)

    def refresh(self):
        s = ftp.st()
        m = ftp.me()
        if not s or not m:
            return
        fam, lv, d = s["family"], ftp.level_of(m["points"]), self.dom_nodes
        ftp.text(d["fam_name"], fam["name"])
        c = 2 * math.pi * 38
        d["ring_fill"].setAttribute("stroke-dashoffset", "%.1f" % (c * (1 - max(0.02, min(1, lv["pct"])))))
        ftp.text(d["level_num"], lv["n"])
        ftp.text(d["hello"], ftp.greeting() + ",")
        ftp.text(d["me_name"], m["name"] + " " + m["avatar"])
        ftp.text(d["level_title"], lv["title"])
        ftp.text(d["me_points"], m["points"])
        ftp.text(d["week"], "+%d this week" % max(0, m["week_points"]))
        ftp.text(d["next"], ("%d brownie points to level %d" % (lv["to_next"], lv["n"] + 1)) if lv["next"] else "Max level reached. Legendary!")
        wt, goal = ftp.week_total(), fam["weekly_goal"] or 100
        pct = int(round(min(1, wt / goal) * 100))
        ftp.text(d["week_total"], wt)
        d["goal_bar"].style.width = "%d%%" % pct
        d["goal_bar_box"].setAttribute("aria-valuenow", str(pct))
        self.family_stack.items = [{"m": x, "size": "xs"} for x in ftp.active_members()]
        ftp.text(d["goal_text"], "Goal smashed! Treat yourselves 🎉" if wt >= goal else "%d brownie points to go together" % (goal - wt))

        needs = ftp.needs_you()
        ftp.text(d["needs_count"], len(needs) or "")
        self.needs_panel.items = [{"it": it, "status": it["status"] == "review",
                                   "cta": "approve" if it["status"] == "review" else ("ack" if it["kind"] == "event" else "complete")}
                                  for it in needs[:8]]
        self.needs_empty.visible = not needs
        bounties = ftp.sort_open([it for it in s["items"] if it["kind"] == "task" and it["status"] == "todo"
                                  and not it.get("assignee") and it["points"] > 0])
        ftp.text(d["bounty_count"], len(bounties) or "")
        self.bounty_panel.items = [{"it": it, "cta": "claim"} for it in bounties[:5]]
        self.bounty_empty.visible = not bounties
        events = sorted([it for it in s["items"] if it["kind"] == "event" and ftp.eff(it) == "todo"
                         and ftp.day_diff(ftp.jsdate(it["event_at"])) <= 14], key=lambda it: it["event_at"])
        ftp.text(d["event_count"], len(events) or "")
        self.event_panel.items = [{"it": it} for it in events[:5]]
        self.event_empty.visible = not events
        recent = ftp.sort_done([it for it in s["items"] if it["kind"] != "event" and it["status"] == "done"])[:4]
        self.recent_part.visible = bool(recent)
        self.recent_panel.items = recent

    @handle("theme_button", "click")
    def theme_button_click(self, **event_args):
        ftp.toggle_theme()
