from anvil import *
import anvil.js

from ._anvil_designer import NavLinkTemplate
from ... import router


class NavLink(NavLinkTemplate):
    """A main-menu link in the rail (desktop) or the tab bar (phone).
    item = {page, label, icon, on, badge, style: "rail" | "tab"}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        node = anvil.js.get_dom_node(self)
        node.className = ("rail-item" if it["style"] == "rail" else "tab") + (" on" if it.get("on") else "")
        node.setAttribute("href", router.href(it["page"]))
        if it.get("on"):
            node.setAttribute("aria-current", "page")
        self.icon.classes.add("ic-" + it["icon"])
        self.dom_nodes["label"].textContent = it["label"]
        n = it.get("badge") or 0
        self.badge.visible = bool(n)
        anvil.js.get_dom_node(self.badge).textContent = "9+" if n > 9 else str(n)
