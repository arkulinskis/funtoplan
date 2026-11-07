from anvil import *

from ._anvil_designer import ProfilePickerTemplate
from ... import ftp, state


class ProfilePicker(ProfilePickerTemplate):
    """How the family sees you: name, emoji avatar, magnet colour. Used by the start page and the profile sheet.
    set_profile(name, avatar, color) fills it; value() -> {"display_name", "avatar", "color"} for the server."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self._avatar, self._color = ftp.AVATARS[0], ftp.COLORS[0]
        state.set_control_attr(self.name_box, "maxlength", 24)
        state.set_control_attr(self.name_box, "autocomplete", "nickname")
        self.emoji_panel.add_event_handler("x-pick", self._pick_avatar)
        self.color_panel.add_event_handler("x-pick", self._pick_color)
        self._draw()

    def set_profile(self, name, avatar, color):
        self.name_box.text = name or ""
        self._avatar = avatar or ftp.AVATARS[0]
        self._color = color or ftp.COLORS[0]
        self._draw()

    def value(self):
        return {"display_name": (self.name_box.text or "").strip(), "avatar": self._avatar, "color": self._color}

    def _draw(self):
        self.emoji_panel.items = [{"key": a, "kind": "emoji", "on": a == self._avatar} for a in ftp.AVATARS]
        self.color_panel.items = [{"key": c, "kind": "swatch", "on": c == self._color, "label": n}
                                  for c, n in zip(ftp.COLORS, ftp.COLOR_NAMES)]

    def _pick_avatar(self, key, **event_args):
        self._avatar = key
        self._draw()
        state.refocus(self.emoji_panel, key)

    def _pick_color(self, key, **event_args):
        self._color = key
        self._draw()
        state.refocus(self.color_panel, key)
