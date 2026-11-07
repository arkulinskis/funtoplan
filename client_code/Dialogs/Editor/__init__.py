from anvil import *

from ._anvil_designer import EditorTemplate
from ... import ftp, state

PLACEHOLDER = {"task": "Take out the recycling", "event": "Grandma's birthday dinner", "want": "New football for the park"}
SEGS = {"kind": ("k_", ["task", "event", "want"]), "priority": ("p_", ["low", "normal", "high"]),
        "recurrence": ("r_", list(ftp.RECUR)), "points": ("pt_", ["0", "5", "10", "20", "50"])}


class Editor(EditorTemplate):
    """New card / Edit FAM-12 (save_item): kind, title, notes, then per kind -
    task: who's on it (or anyone), due date (+ Today / Tomorrow / Weekend), priority, bounty points, repeat, take
    turns, needs approval; event: date, time, place, host; want: who wants it, link, how much.
    The creator or the board's owner can delete. Closes with {"saved": id} or {"deleted": True}."""

    def __init__(self, item_id=None, kind=None, **properties):
        super().__init__(**properties)
        it = ftp.item_by_id(item_id) if item_id else None
        now = ftp.jsdate()
        next_hour = ftp.jsdate(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1)
        ev = ftp.jsdate(it["event_at"]) if it and it.get("event_at") else next_hour
        self._id = it["id"] if it else None
        self.e: dict = {"kind": it["kind"] if it else (kind if kind in ftp.KIND else "task"),
                  "assignee": it.get("assignee") if it else None,
                  "priority": it["priority"] if it else "normal", "points": it["points"] if it else 0,
                  "recurrence": it["recurrence"] if it else "none", "rotate": bool(it and it["rotate"]),
                  "requires_approval": bool(it and it["requires_approval"])}
        self.title_box.text = it["title"] if it else ""
        self.notes_box.text = it["notes"] if it else ""
        self.due_box.text = (it.get("due_date") or "")[:10] if it else ""
        self.date_box.text = ftp.ymd(ev)
        self.time_box.text = ftp.fmt_time(ev)
        self.place_box.text = it.get("location", "") if it else ""
        self.link_box.text = it.get("link", "") if it else ""
        for box, typ in ((self.due_box, "date"), (self.date_box, "date"), (self.time_box, "time")):
            state.control(box).setAttribute("type", typ)  # the App Server's TextBox has no date/time types
        for box, n in ((self.title_box, 140), (self.notes_box, 2000), (self.place_box, 120), (self.link_box, 400)):
            state.set_control_attr(box, "maxlength", n)
        state.set_control_attr(self.link_box, "inputmode", "url")
        state.set_control_attr(self.due_box, "aria-label", "Due date")
        self.dom_nodes["title"].textContent = ("Edit " + it["key"]) if it else "New card"
        self.save_button.text = "Save changes" if it else "Add to board"
        self.delete_button.visible = bool(it and (it.get("created_by") == ftp.st()["me"] or ftp.is_owner()))
        self.who_panel.add_event_handler("x-pick", self._pick)
        self._draw()

    def _draw(self):
        e = self.e
        k = e["kind"]
        self.title_box.placeholder = PLACEHOLDER[k]
        self.task_part.visible = k == "task"
        self.event_part.visible = k == "event"
        self.want_part.visible = k == "want"
        self.dom_nodes["who_label"].textContent = {"task": "Who's on it", "event": "Host", "want": "Who wants it"}[k]
        none = {"id": "", "name": "Anyone" if k == "task" else "Family", "avatar": "✋" if k == "task" else "👪", "color": "#9aa8b6"}
        self.who_panel.items = [{"key": m["id"] or "-", "kind": "person", "on": (e["assignee"] or "") == m["id"], "m": m}
                                for m in [none] + ftp.active_members()]
        for key, (prefix, values) in SEGS.items():
            for v in values:
                on = str(e[key]) == v
                btn = getattr(self, prefix + v)
                btn.classes["on"] = on
                state.set_attr(btn, "aria-pressed", "true" if on else "false")
        for v in ("low", "normal", "high"):
            getattr(self, "w_" + v).classes["on"] = e["priority"] == v
            state.set_attr(getattr(self, "w_" + v), "aria-pressed", "true" if e["priority"] == v else "false")
        due = self.due_box.text or ""
        for name, val in self._quick_dates().items():
            getattr(self, "d_" + name).classes["on"] = due == val
        self.dom_nodes["points"].textContent = str(e["points"])
        self.rotate_row.visible = e["recurrence"] != "none"
        for key, tog in (("rotate", self.rotate_toggle), ("requires_approval", self.approval_toggle)):
            tog.classes["on"] = bool(e[key])
            state.set_attr(tog, "aria-checked", "true" if e[key] else "false")

    def _quick_dates(self):
        today = ftp.jsdate()
        sat = ftp.add_days(today, ((6 - today.getDay() + 7) % 7) or 7)
        return {"today": ftp.ymd(today), "tomorrow": ftp.ymd(ftp.add_days(today, 1)), "weekend": ftp.ymd(sat), "none": ""}

    def set_click(self, event):
        el = event.currentTarget
        k, v = el.getAttribute("data-k"), el.getAttribute("data-v")
        if k == "due":
            self.due_box.text = self._quick_dates()[v]
        elif k == "points":
            self.e["points"] = int(v)
        else:
            self.e[k] = v
        self._draw()

    def flip_click(self, event):
        k = event.currentTarget.getAttribute("data-k")
        self.e[k] = not self.e[k]
        self._draw()

    def _pick(self, key, **event_args):
        self.e["assignee"] = None if key == "-" else key
        self._draw()
        state.refocus(self.who_panel, key)

    @handle("less_button", "click")
    def less_button_click(self, **event_args):
        self.e["points"] = max(0, self.e["points"] - 5)
        self._draw()

    @handle("more_button", "click")
    def more_button_click(self, **event_args):
        self.e["points"] = min(500, self.e["points"] + 5)
        self._draw()

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        e = self.e
        title = (self.title_box.text or "").strip()
        if not title:
            state.toast("Give the card a title.", "error")
            self.title_box.focus()
            return
        p = {"id": self._id, "kind": e["kind"], "title": title, "notes": self.notes_box.text or "",
             "assignee": e["assignee"] or None, "priority": e["priority"]}
        if e["kind"] == "task":
            p.update(due_date=state.control(self.due_box).value or None, points=e["points"], recurrence=e["recurrence"],
                     rotate=e["rotate"], requires_approval=e["requires_approval"])
        elif e["kind"] == "event":
            date = state.control(self.date_box).value or ""
            if not date:
                state.toast("Pick a date for the event.", "error")
                return
            y, mo, d = [int(x) for x in date.split("-")]
            hh, mm = [int(x) for x in ((state.control(self.time_box).value or "12:00").split(":") + ["0"])[:2]]
            p["event_at"] = ftp.jsdate(y, mo - 1, d, hh, mm).toISOString()
            p["location"] = self.place_box.text or ""
        else:
            p["link"] = self.link_box.text or ""
        r = ftp.run("save_item", p)
        if r:
            self.raise_event("x-close-alert", value={"saved": r.get("saved")})

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        it = ftp.item_by_id(self._id)
        if ftp.ask("Delete %s?" % (it["key"] if it else "card"),
                   "This removes the card and its comments for everyone. Brownie points already earned are kept.", "Delete", True):
            if ftp.run("delete_item", {"id": self._id}):
                state.toast("Card deleted")
                self.raise_event("x-close-alert", value={"deleted": True})

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
