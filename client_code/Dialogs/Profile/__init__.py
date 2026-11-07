from anvil import *

from ._anvil_designer import ProfileTemplate
from ... import ftp


class Profile(ProfileTemplate):
    """My profile: name, avatar and colour (update_profile). Closes with True when saved."""

    def __init__(self, **properties):
        super().__init__(**properties)
        m = ftp.me()
        self.picker.set_profile(m["name"], m["avatar"], m["color"])

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        if ftp.run("update_profile", self.picker.value()):
            self.raise_event("x-close-alert", value=True)

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
