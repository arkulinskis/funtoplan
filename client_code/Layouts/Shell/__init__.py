from anvil import *
import anvil.js

from ._anvil_designer import ShellTemplate
from ... import ftp, router


class Shell(ShellTemplate):
    """The frame around every page. Members on a board get the desktop rail (brand + family, Home / Board / Chat /
    Family with badges, New card, their level) and the phone tab bar with the red + magnet; the landing, log-in and
    start pages are "bare" (they draw their own headers). The footer with the four links is on every page.

    Anvil keeps ONE Shell while pages come and go, so everything that depends on the board or the page is drawn in
    refresh() (router.show calls it after every page change; ftp.listen calls it when the board syncs)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self._page = ""
        ftp.listen(self._redraw)

    def refresh(self, page):
        self._page = page
        self._redraw()

    def _redraw(self):
        node = anvil.js.get_dom_node(self)
        board = ftp.st()
        bare = not board or self._page in ("landing", "auth", "start")
        node.classList.toggle("bare", bool(bare))
        if bare:
            return
        badges = {"home": len(ftp.needs_you()), "chat": ftp.unread_count() if self._page != "chat" else 0}
        links = [{"page": p, "label": label, "icon": icon, "on": p == self._page, "badge": badges.get(p, 0)}
                 for p, label, icon in router.NAV]
        self.rail_panel.items = [dict(x, style="rail") for x in links]
        self.tab_left.items = [dict(x, style="tab") for x in links[:2]]
        self.tab_right.items = [dict(x, style="tab") for x in links[2:]]
        self.dom_nodes["fam_name"].textContent = board["family"]["name"]
        m = ftp.me()
        self.rail_me.visible = bool(m)
        if m:
            lv = ftp.level_of(m["points"])
            ftp.avatar(self.dom_nodes["me_avatar"], m)
            ftp.text(self.dom_nodes["me_name"], m["name"])
            ftp.text(self.dom_nodes["me_level"], "Lv %d · %s" % (lv["n"], lv["title"]))
            ftp.text(self.dom_nodes["me_points"], m["points"])

    @handle("rail_add", "click")
    def rail_add_click(self, **event_args):
        ftp.new_card()

    @handle("tab_add", "click")
    def tab_add_click(self, **event_args):
        ftp.new_card()
