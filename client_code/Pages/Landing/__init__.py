from anvil import *

from ._anvil_designer import LandingTemplate
from ... import ftp, state

# The app's video on the Addanapp YouTube channel (APP_MAKER/youtube/manifest.json), shown in the Watch section.
YT_VIDEO = "qWP3bxxPTWE"


class Landing(LandingTemplate):
    """What visitors see first (#landing): what the app is and how it works, before they log in or sign up.
    Opened from an invite link (#join=ABC123), it says so and the buttons read "Join your family"."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        invited = bool(ftp.S["pending_join"])
        self.invited_note.visible = invited
        signed_in = bool(state.me())
        self.nav_login.visible = not signed_in
        self.nav_open.visible = signed_in
        if invited:
            for node in (self.dom_nodes["cta_main"], self.dom_nodes["cta_final"]):
                node.firstChild.textContent = "Join your family "
            self.dom_nodes["final_h"].textContent = "Your family is waiting."
            self.dom_nodes["final_p"].textContent = "Create an account or log in, pick an avatar, and you're on the board."
        self.dom_nodes["yt_cover"].addEventListener("click", self._play)

    def _play(self, event):
        self.dom_nodes["yt_frame"].innerHTML = (
            '<iframe src="https://www.youtube-nocookie.com/embed/' + YT_VIDEO + '?autoplay=1&rel=0&playsinline=1" '
            'title="Fun To Plan video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" '
            'allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>')

    @handle("theme_button", "click")
    def theme_button_click(self, **event_args):
        ftp.toggle_theme()
