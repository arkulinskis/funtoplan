import random
import re

from anvil import *

from ._anvil_designer import StartTemplate
from ... import auth, ftp, router, state


class Start(StartTemplate):
    """Onboarding (#start), for people signed in but not on a board yet: pick a name, avatar and colour, then join a
    family with its 6-letter code (typed, from an invite link, or scanned with the camera) or start a new board
    (with or without starter cards)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        email = (state.me() or {}).get("email") or ""
        guess = re.sub(r"[._-]+", " ", email.split("@")[0]).title()[:24]
        self.picker.set_profile(guess, ftp.AVATARS[random.randint(0, 7)], ftp.COLORS[0])
        ftp.text(self.dom_nodes["signed_as"], "Signed in as " + email)
        state.set_control_attr(self.code_box, "maxlength", 6)
        state.set_control_attr(self.code_box, "autocomplete", "off")
        state.set_control_attr(self.code_box, "autocapitalize", "characters")
        state.set_control_attr(self.code_box, "spellcheck", "false")
        state.set_control_attr(self.code_box, "aria-label", "Family code")
        state.set_control_attr(self.family_box, "maxlength", 40)
        self.scan_button.visible = bool(window_can_scan())
        self.preview.visible = False
        state.control(self.code_box).addEventListener("input", self._code_input)
        code = ftp.S["pending_join"]
        self.invited_note.visible = bool(code)
        self.grid.classes["invited"] = bool(code)
        if code:
            self.code_box.text = code
            self._preview(code)

    # ---- join
    def _code_input(self, event):
        box = state.control(self.code_box)
        val = re.sub(r"[^A-Z0-9]", "", (box.value or "").upper())[:6]
        if box.value != val:
            box.value = val
        self.code_box.text = val
        if len(val) == 6:
            self._preview(val)
        else:
            self.preview.visible = False

    def _preview(self, code):
        try:
            pv = ftp.api("preview_join", {"code": code})
        except ftp.ApiError as e:
            self.preview.visible = False
            self._err(self.join_error, str(e))
            return
        self._err(self.join_error, None)
        self.preview_panel.items = [{"m": m, "size": "sm"} for m in pv["members"]]
        ftp.text(self.dom_nodes["preview_name"], pv["name"])
        ftp.text(self.dom_nodes["preview_seats"], "%d of 4 seats taken%s" % (len(pv["members"]), " · this board is full" if pv["full"] else ""))
        self.preview.visible = True

    def _err(self, label, text):
        label.visible = bool(text)
        label.text = text or ""

    @handle("scan_button", "click")
    def scan_button_click(self, **event_args):
        code = ftp.scan_code()
        if code:
            self.code_box.text = code
            ftp.S["pending_join"] = code
            state.toast("Code found: " + code)
            self._preview(code)

    @handle("code_box", "pressed_enter")
    def code_box_pressed_enter(self, **event_args):
        self.join_button_click()

    @handle("join_button", "click")
    def join_button_click(self, **event_args):
        code = (self.code_box.text or "").strip().upper()
        if len(code) != 6:
            self._err(self.join_error, "Codes have 6 letters and numbers.")
            return
        p = self.picker.value()
        p["code"] = code
        d = ftp.run("join_family", p)
        if d and d.get("state"):
            ftp.S["pending_join"] = None
            state.toast("Welcome to %s! 👋" % d["state"]["family"]["name"])
            router.go("home")

    # ---- create
    def seed_click(self, event):
        el = event.currentTarget
        on = not el.classList.contains("on")
        el.classList.toggle("on", on)
        el.setAttribute("aria-checked", "true" if on else "false")

    @handle("family_box", "pressed_enter")
    def family_box_pressed_enter(self, **event_args):
        self.create_button_click()

    @handle("create_button", "click")
    def create_button_click(self, **event_args):
        name = (self.family_box.text or "").strip()
        if not name:
            self._err(self.create_error, "Give your family board a name.")
            self.family_box.focus()
            return
        self._err(self.create_error, None)
        p = self.picker.value()
        p["family_name"] = name
        import anvil.js
        p["seed"] = bool(anvil.js.get_dom_node(self.seed_toggle).classList.contains("on"))
        d = ftp.run("create_family", p)
        if d and d.get("state"):
            state.toast("Your family board is ready! Invite the others from the Family tab.")
            router.go("home")

    @handle("logout_button", "click")
    def logout_button_click(self, **event_args):
        auth.sign_out()
        router.go("landing")


def window_can_scan():
    from anvil.js import window
    return window.FTP.canScan()
