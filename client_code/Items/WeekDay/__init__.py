from anvil import *
import anvil.js

from ._anvil_designer import WeekDayTemplate
from ... import ftp


class WeekDay(WeekDayTemplate):
    """One day on the Week page: its name and date (a toggle on phones, where only open days show their notes), a +
    that opens the editor with this date, and its notes (Items/WeekEntry). item = {"date", "dow", "num", "mon",
    "today", "past", "open", "entries", "page" (the Week page: remembers which days are open)}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        node = anvil.js.get_dom_node(self)
        node.classList.toggle("today", bool(it["today"]))
        node.classList.toggle("past", bool(it["past"]))
        node.classList.toggle("open", bool(it["open"]))
        d = ftp.loose(self.dom_nodes)
        ftp.text(d["dow"], ("Today · " if it["today"] else "") + it["dow"])
        ftp.text(d["num"], "%d %s" % (it["num"], it["mon"]))
        entries = it["entries"]
        real = len([e for e in entries if not e.get("ghost")])
        ftp.text(d["summary"], ftp.plural(real, "thing") if real else ("next turns" if entries else "free"))
        d["body"].setAttribute("id", "wk-" + it["date"])
        d["toggle"].setAttribute("aria-controls", "wk-" + it["date"])
        d["toggle"].setAttribute("aria-expanded", "true" if it["open"] else "false")
        self.entry_panel.items = entries
        self.free.visible = not entries
        self.add_button.text = "Add on %s %d %s" % (it["dow"], it["num"], it["mon"])
        d["toggle"].addEventListener("click", self._toggle)

    def _toggle(self, event):
        node = anvil.js.get_dom_node(self)
        is_open = not node.classList.contains("open")
        node.classList.toggle("open", is_open)
        self.dom_nodes["toggle"].setAttribute("aria-expanded", "true" if is_open else "false")
        self.item["page"].open_days[self.item["date"]] = is_open

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        ftp.open_editor(None, None, {"due": self.item["date"]})
