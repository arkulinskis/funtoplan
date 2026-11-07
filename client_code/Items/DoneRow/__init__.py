from anvil import *

from ._anvil_designer import DoneRowTemplate
from ... import ftp, state


class DoneRow(DoneRowTemplate):
    """"Recently done" on Home: who finished it, when, and the brownie points it paid. item = card dict."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        who = ftp.member(it.get("completed_by"))
        ftp.avatar(self.dom_nodes["who"], who, "sm")
        ftp.text(self.dom_nodes["title"], it["title"])
        ftp.text(self.dom_nodes["sub"], (who["name"] if who else "Someone") + " · " + ftp.ago(it.get("completed_at")))
        self.pts.visible = bool(it.get("points_awarded"))
        ftp.text(self.dom_nodes["pts_text"], "+%s" % it.get("points_awarded"))
        self.status.visible = not it.get("points_awarded")
        ftp.text(self.dom_nodes["status_text"], ftp.status_label(it))
        state.set_attr(self.open, "aria-label", "Open %s: %s" % (it["key"], it["title"]))

    def open_click(self, event):
        ftp.open_detail(self.item["id"])
