from anvil import *

from ._anvil_designer import CommentTemplate
from ... import ftp


class Comment(CommentTemplate):
    """A comment on a card (the card's sheet). item = message dict. FAM-12 in the text opens that card."""

    def __init__(self, **properties):
        super().__init__(**properties)
        c = self.item
        a = ftp.member(c.get("author"))
        ftp.avatar(self.dom_nodes["who"], a, "sm")
        ftp.text(self.dom_nodes["name"], (a["name"] if a else "Someone") + " · " + ftp.ago(c.get("created")))
        ftp.rich(self.dom_nodes["text"], c["text"], self._open)

    def _open(self, iid):
        self.parent.raise_event("x-open", item_id=iid)
