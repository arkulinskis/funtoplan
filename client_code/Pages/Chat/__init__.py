from anvil import *
from anvil.js import window

from ._anvil_designer import ChatTemplate
from ... import ftp, state


class Chat(ChatTemplate):
    """Family chat (#chat): messages and the activity feed, day labels, FAM-12 links to cards. Enter sends on a
    computer (Shift+Enter = new line); the box grows with the text. Opening the chat marks it read."""
    keeps_scroll = True  # the router leaves the scroll alone: the chat starts at the newest message

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        box = state.control(self.text_box)
        box.setAttribute("rows", "1")
        box.setAttribute("maxlength", "1000")
        box.setAttribute("aria-label", "Message the family")
        box.addEventListener("keydown", self._key)
        box.addEventListener("input", self._grow)
        self._count = None

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self.refresh)
        self.refresh()

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self.refresh)

    def refresh(self):
        s = ftp.st()
        if not s:
            return
        doc = ftp.loose(window.document.documentElement)
        near_bottom = self._count is None or doc.scrollHeight - window.scrollY - window.innerHeight < 140
        ftp.text(self.dom_nodes["fam_name"], s["family"]["name"])
        self.family_stack.items = [{"m": x, "size": "sm"} for x in ftp.active_members()]
        rows, last = [], ""
        for m in s["messages"]:
            day = ftp.ymd(ftp.jsdate(m["created"]))
            rows.append({"m": m, "day": ftp.fmt_day(ftp.jsdate(m["created"])) if day != last else None})
            last = day
        key = (len(rows), rows[-1]["m"]["id"] if rows else None)
        if key != self._count:
            self.chat_panel.items = rows
            self._count = key
            if near_bottom:
                window.setTimeout(lambda: window.scrollTo(0, doc.scrollHeight), 30)
        self.chat_empty.visible = not rows
        ftp.mark_chat_seen()

    def _grow(self, event):
        box = state.control(self.text_box)
        box.style.height = "auto"
        box.style.height = "%dpx" % min(140, box.scrollHeight)

    def _key(self, event):
        if getattr(event, "key", None) == "Enter" and not getattr(event, "shiftKey", False) and getattr(window.matchMedia("(hover: hover)"), "matches"):
            event.preventDefault()
            self.send_button_click()

    @handle("send_button", "click")
    def send_button_click(self, **event_args):
        text = (self.text_box.text or "").strip()
        if not text:
            return
        self.text_box.text = ""
        state.control(self.text_box).style.height = ""
        if not ftp.run("send_message", {"text": text}):
            self.text_box.text = text
            return
        root = ftp.loose(window.document.documentElement)
        window.scrollTo(0, root.scrollHeight)
