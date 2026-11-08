from anvil import *
from anvil.js import window

from ._anvil_designer import InviteTemplate
from ... import ftp


class Invite(InviteTemplate):
    """The big invite QR code and the join code, with Copy link / Share."""

    def __init__(self, **properties):
        super().__init__(**properties)
        fam = ftp.st()["family"]
        d = ftp.loose(self.dom_nodes)
        d["title"].textContent = "Join " + fam["name"]
        drawn = bool(window.FTP.qr(d["qr"], ftp.invite_link()))
        d["qr"].style.display = "" if drawn else "none"
        self.no_qr.visible = not drawn
        for i, ch in enumerate(fam["code"][:6]):
            d["t%d" % i].textContent = ch
        d["tiles"].setAttribute("aria-label", "Join code " + " ".join(fam["code"]))
        self.share_button.visible = ftp.can_share()

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        ftp.copy_link()

    @handle("share_button", "click")
    def share_button_click(self, **event_args):
        ftp.share_link()

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
