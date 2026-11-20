import re

from anvil import *

from ._anvil_designer import WeekTemplate
from ... import ftp, router

DOW_LONG = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
OPEN = ("todo", "doing", "review")


class Week(WeekTemplate):
    """This week (#week, #week/YYYY-MM-DD = the week holding that day; weeks start on Monday): previous / next week,
    whose jobs (Everyone or one person, kid seats too), what's still open from before, seven days (stacked on phones
    with today open, two columns on tablets, seven on wide screens) with events by time, tasks due that day and the
    coming turns of repeating tasks ("↻ Leo's turn", from ftp.ghost_turns), a + per day (the editor with that date),
    and Anytime (open jobs without a date). Built from the board in the browser (ftp.st()); redraws when it syncs.
    "Add to my phone calendar" opens Dialogs/CalLink."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._start = self._week_of(args[0] if args else None)
        self.open_days: dict = {}  # "YYYY-MM-DD" -> open on phones (Items/WeekDay remembers taps here)
        self.people_panel.add_event_handler("x-pick", self._pick_person)
        self.refresh()

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self.refresh)

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self.refresh)

    def _week_of(self, text):
        day = ftp.parse_ymd(text) if text and re.match(r"^\d{4}-\d{2}-\d{2}$", text) else None
        return ftp.week_start(day or ftp.jsdate())

    def _range_text(self, a, b):
        if a.getMonth() == b.getMonth():
            return "%d – %d %s %d" % (a.getDate(), b.getDate(), ftp.MON[b.getMonth()], b.getFullYear())
        return "%d %s – %d %s %d" % (a.getDate(), ftp.MON[a.getMonth()], b.getDate(), ftp.MON[b.getMonth()], b.getFullYear())

    def refresh(self):
        s = ftp.st()
        if not s:
            return
        d = ftp.loose(self.dom_nodes)
        days = [ftp.add_days(self._start, i) for i in range(7)]
        keys = [ftp.ymd(x) for x in days]
        first, end, today = keys[0], keys[6], ftp.today_str()
        this_week = first <= today <= end
        ftp.text(d["range"], ("This week · " if this_week else "") + self._range_text(days[0], days[6]))
        self.today_button.visible = not this_week
        who = ftp.S.get("wk_who") or "all"
        if who != "all" and not (ftp.member(who) and ftp.member(who)["active"]):
            who = "all"
        ftp.S["wk_who"] = who
        self.people_panel.items = [{"key": "all", "kind": "chip", "on": who == "all", "label": "Everyone"}] + [
            {"key": m["id"], "kind": "chip", "on": who == m["id"], "m": m, "label": m["name"]} for m in ftp.active_members()]

        per = {k: [] for k in keys}
        overdue, anytime = [], []
        for it in s["items"]:
            if it["kind"] == "event" and it.get("event_at"):
                when = ftp.jsdate(it["event_at"])
                key = ftp.ymd(when)
                if key in per:  # events are the family's: every filter shows them
                    per[key].append({"it": it, "time": ftp.fmt_time(when), "order": "0" + ftp.fmt_time(when)})
                continue
            if it["kind"] != "task" or not (who == "all" or it.get("assignee") == who):
                continue
            due = (it.get("due_date") or "")[:10]
            if not due:
                if it["status"] in OPEN:
                    anytime.append(it)
            elif due in per:
                late = it["status"] in OPEN and due < today
                rank = "1" if it["status"] in OPEN else "2"
                per[due].append({"it": it, "late": late, "order": rank + str(ftp.PRI.get(it["priority"], 1))})
            elif this_week and due < first and it["status"] in OPEN:
                overdue.append(it)
        for g in ftp.ghost_turns(end):
            if g["date"] in per and (who == "all" or g["who"] == who):
                per[g["date"]].append({"it": g["it"], "ghost": True, "who": g["who"], "order": "3"})

        if not self.open_days:  # phones: today open (other weeks: the days that have something on)
            for key in keys:
                self.open_days[key] = (key == today) if this_week else bool(per[key])
        self.days_panel.items = [{"date": key, "dow": DOW_LONG[days[i].getDay()], "num": days[i].getDate(),
                                  "mon": ftp.MON[days[i].getMonth()], "today": key == today, "past": key < today,
                                  "open": bool(self.open_days.get(key)), "page": self,
                                  "entries": sorted(per[key], key=lambda e: e["order"])}
                                 for i, key in enumerate(keys)]
        self.overdue_part.visible = bool(overdue)
        ftp.text(d["overdue_count"], len(overdue) or "")
        self.overdue_panel.items = [{"it": it, "late": True, "show_day": True} for it in ftp.sort_open(overdue)]
        self.anytime_panel.items = [{"it": it} for it in ftp.sort_open(anytime)]
        self.anytime_empty.visible = not anytime
        ftp.text(d["anytime_count"], len(anytime) or "")
        name = ftp.member(who)["name"] if who != "all" else ""
        ftp.text(d["foot"], ("Showing %s's jobs and the family's events." % name) if name else
                 "Faded notes with ↻ are coming turns of repeating jobs.")

    def _go(self, start):
        self._start = start
        self.open_days = {}
        key = ftp.ymd(start)
        if key == ftp.ymd(ftp.week_start(ftp.jsdate())):
            router.replace("week")
        else:
            router.replace("week", key)
        self.refresh()

    def _pick_person(self, key, **event_args):
        ftp.S["wk_who"] = key
        self.refresh()

    @handle("prev_button", "click")
    def prev_button_click(self, **event_args):
        self._go(ftp.add_days(self._start, -7))

    @handle("next_button", "click")
    def next_button_click(self, **event_args):
        self._go(ftp.add_days(self._start, 7))

    @handle("today_button", "click")
    def today_button_click(self, **event_args):
        self._go(ftp.week_start(ftp.jsdate()))

    @handle("cal_button", "click")
    def cal_button_click(self, **event_args):
        ftp.open_cal_link()
