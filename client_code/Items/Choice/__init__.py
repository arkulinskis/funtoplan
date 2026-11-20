from anvil import *
import anvil.js

from ._anvil_designer import ChoiceTemplate
from ... import ftp


class Choice(ChoiceTemplate):
    """One choice in a picker: an emoji avatar, a colour swatch, or a person (avatar + name).
    item = {"key", "kind": "emoji" | "swatch" | "person" | "chip", "on", "label", "m" (person/chip: member-like dict)}.
    "chip" = a small horizontal chip (avatar + label): the Week page's person filter, the card sheet's kid buttons.
    A click raises "x-pick" (key=...) on the RepeatingPanel; the picker redraws and keeps the focus (data-key)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        node = anvil.js.get_dom_node(self)
        node.setAttribute("data-key", str(it["key"]))
        node.setAttribute("aria-pressed", "true" if it.get("on") else "false")
        face, dot, label = self.dom_nodes["face"], self.dom_nodes["dot"], self.dom_nodes["label"]
        kind = it["kind"]
        if kind == "emoji":
            node.className = "emoji-btn" + (" on" if it.get("on") else "")
            node.textContent = it["key"]
            node.setAttribute("aria-label", "Avatar " + it["key"])
        elif kind == "swatch":
            node.className = "swatch" + (" on" if it.get("on") else "")
            face.remove()
            label.remove()
            dot.style.background = it["key"]
            node.setAttribute("aria-label", it.get("label") or it["key"])
        elif kind == "chip":
            node.className = "chip person-chip" + (" on" if it.get("on") else "")
            dot.remove()
            if it.get("m"):
                ftp.avatar(face, it["m"], "xs")
                face.setAttribute("aria-hidden", "true")
            else:
                face.remove()
            ftp.text(label, it.get("label") or (it["m"]["name"] if it.get("m") else ""))
        else:
            node.className = "pick-item" + (" on" if it.get("on") else "")
            dot.remove()
            ftp.avatar(face, it["m"], "sm")
            face.setAttribute("aria-hidden", "true")
            ftp.text(label, it["m"]["name"])
        node.addEventListener("click", self._click)

    def _click(self, event):
        if self.parent is not None:
            self.parent.raise_event("x-pick", key=self.item["key"])
