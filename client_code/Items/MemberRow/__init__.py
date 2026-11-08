from anvil import *

from ._anvil_designer import MemberRowTemplate
from ... import ftp, state


class MemberRow(MemberRowTemplate):
    """A member on the Family page: avatar, name (you / owner), level, cards done this month, brownie points;
    the board's owner can remove the others. item = member dict."""

    def __init__(self, **properties):
        super().__init__(**properties)
        x = self.item
        me = ftp.me()
        lv = ftp.level_of(x["points"])
        ftp.avatar(self.dom_nodes["who"], x)
        ftp.text(self.dom_nodes["name"], x["name"])
        self.you.visible = bool(me and x["id"] == me["id"])
        self.owner.visible = x["role"] == "owner"
        ftp.text(self.dom_nodes["level"], "Lv %d %s · %s done this month" % (lv["n"], lv["title"], ftp.plural(x["done_30"], "card")))
        ftp.text(self.dom_nodes["points"], x["points"])
        self.remove_button.visible = ftp.is_owner() and not self.you.visible
        self.remove_button.text = "Remove " + x["name"]

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        m = self.item
        if ftp.ask("Remove %s?" % m["name"], "%s will lose access to the board. Their open tasks become open to anyone." % m["name"], "Remove", True):
            if ftp.run("remove_member", {"member_id": m["id"]}):
                state.toast(m["name"] + " was removed")
