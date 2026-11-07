from anvil import *
import anvil.js

from ._anvil_designer import AvatarTemplate
from ... import ftp


class Avatar(AvatarTemplate):
    """A round magnet with the person's emoji, in a row of avatars (RepeatingPanel role "stack").
    item = {"m": member dict or None (an open seat), "size": "xs" | "sm" | "lg" | ""}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        ftp.avatar(anvil.js.get_dom_node(self), self.item.get("m"), self.item.get("size") or "")
