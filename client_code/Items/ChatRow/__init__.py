from anvil import *
import anvil.js

from ._anvil_designer import ChatRowTemplate
from ... import ftp


class ChatRow(ChatRowTemplate):
    """One line of the family chat: a day label (first message of a day), then either an activity line
    ("Mom completed FAM-12 ...") or a message bubble (yours on the right, in yellow).
    item = {"m": message dict, "day": "Today" or None}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        m, day = self.item["m"], self.item.get("day")
        self.day.visible = bool(day)
        anvil.js.get_dom_node(self.day).textContent = day or ""
        a = ftp.member(m.get("author"))
        system = m["kind"] == "system"
        self.sys.visible = system
        self.msg.visible = not system
        name = a["name"] if a else "Someone"
        if system:
            node = self.dom_nodes["sys_who"]
            node.style.display = "" if a else "none"
            if a:
                ftp.avatar(node, a, "xs")
            ftp.text(self.dom_nodes["sys_name"], name)
            ftp.rich(self.dom_nodes["sys_text"], m["text"])
            return
        mine = m.get("author") == ftp.st()["me"]
        self.msg.classes["mine"] = mine
        who = self.dom_nodes["who"]
        who.style.display = "none" if mine else ""
        if not mine:
            ftp.avatar(who, a, "sm")
        nm = self.dom_nodes["name"]
        nm.style.display = "none" if mine else ""
        ftp.text(nm, name)
        ftp.rich(self.dom_nodes["text"], m["text"])
        ftp.text(self.dom_nodes["when"], ftp.fmt_time(ftp.jsdate(m["created"])))
