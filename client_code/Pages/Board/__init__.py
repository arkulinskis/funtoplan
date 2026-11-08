from anvil import *

from ._anvil_designer import BoardTemplate
from ... import ftp, router, state

FILTERS = ["all", "task", "event", "want", "mine", "bounty"]
COLS = ["todo", "doing", "review", "done"]


class Board(BoardTemplate):
    """The family epic (#board, #board/<filter>): progress, filters (all / tasks / events / wants / mine / bounties)
    and four columns. Phones show one column at a time (the To do / Doing / Review / Done switch)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        ftp.S["filter"] = args[0] if args and args[0] in FILTERS else "all"  # the address holds the filter
        self.refresh()

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self.refresh)

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self.refresh)

    def _filtered(self, items):
        f, mine = ftp.S["filter"], ftp.st()["me"]
        if f in ("task", "event", "want"):
            return [it for it in items if it["kind"] == f]
        if f == "mine":
            return [it for it in items if it.get("assignee") == mine]
        if f == "bounty":
            return [it for it in items if it["kind"] == "task" and it["points"] > 0]
        return items

    def refresh(self):
        s = ftp.st()
        if not s:
            return
        d = ftp.loose(self.dom_nodes)
        items = s["items"]
        n_open = len([it for it in items if ftp.eff(it) != "done"])
        n_done = len(items) - n_open
        pct = int(round(n_done * 100 / len(items))) if items else 0
        ftp.text(d["fam_name"], s["family"]["name"])
        d["bar"].style.width = "%d%%" % pct
        d["bar_box"].setAttribute("aria-valuenow", str(pct))
        ftp.text(d["n_open"], n_open)
        ftp.text(d["n_done"], n_done)
        ftp.text(d["n_review"], len([it for it in items if it["kind"] == "task" and it["status"] == "review"]))
        self.family_stack.items = [{"m": x, "size": "xs"} for x in ftp.active_members()]
        cols = {c: [] for c in COLS}
        for it in self._filtered(items):
            cols[ftp.eff(it)].append(it)
        for c in COLS:
            lst = ftp.sort_done(cols[c]) if c == "done" else ftp.sort_open(cols[c])
            getattr(self, "p_" + c).items = [{"it": it} for it in lst]
            getattr(self, "e_" + c).visible = not lst
            ftp.text(d["h_" + c], len(lst))
            ftp.text(d["cn_" + c], len(lst))
            getattr(self, "col_" + c).classes["on"] = ftp.S["col"] == c
            btn = getattr(self, "c_" + c)
            btn.classes["on"] = ftp.S["col"] == c
            state.set_attr(btn, "aria-pressed", "true" if ftp.S["col"] == c else "false")
        for f in FILTERS:
            chip = getattr(self, "f_" + f)
            chip.classes["on"] = ftp.S["filter"] == f
            state.set_attr(chip, "aria-pressed", "true" if ftp.S["filter"] == f else "false")

    def filter_click(self, event):
        ftp.S["filter"] = event.currentTarget.getAttribute("data-f")
        router.replace("board", "" if ftp.S["filter"] == "all" else ftp.S["filter"])
        self.refresh()

    def col_click(self, event):
        ftp.S["col"] = event.currentTarget.getAttribute("data-col")
        self.refresh()

    @handle("new_button", "click")
    def new_button_click(self, **event_args):
        ftp.new_card()
