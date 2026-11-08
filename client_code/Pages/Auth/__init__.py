import re

from anvil import *

from ._anvil_designer import AuthTemplate
from ... import auth, ftp, legal, router, state

EMAIL = re.compile(r"^\S+@\S+\.\S+$")


class Auth(AuthTemplate):
    """Log in (#auth) or sign up (#auth/signup), with Forgot password and Continue with Google.
    Sign-up needs the Privacy & Terms tick box (the legal kit draws it). Passwords: at least 6 characters."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.dom_nodes["consent"].innerHTML = legal.consent_field()
        self._mode = "signup" if args and args[0] == "signup" else "login"
        self.invited_note.visible = bool(ftp.S["pending_join"])
        state.set_control_attr(self.email_box, "autocomplete", "email")
        state.set_control_attr(self.email_box, "inputmode", "email")
        img = state.control(self.google_button).querySelector("img")
        if img:
            img.setAttribute("alt", "")
        self._draw()

    def _draw(self):
        signup = self._mode == "signup"
        self.tab_login.classes["on"] = not signup
        self.tab_signup.classes["on"] = signup
        state.set_attr(self.tab_login, "aria-pressed", "false" if signup else "true")
        state.set_attr(self.tab_signup, "aria-pressed", "true" if signup else "false")
        state.set_control_attr(self.password_box, "autocomplete", "new-password" if signup else "current-password")
        self.password_box.placeholder = "At least 6 characters" if signup else "Your password"
        self.consent_box.visible = signup
        self.forgot_part.visible = not signup
        self.submit_button.text = "Create account" if signup else "Log in"
        self._say(None)

    def _say(self, message):
        self.message.visible = bool(message)
        self.message.text = message or ""

    def mode_click(self, event):
        self._mode = event.currentTarget.getAttribute("data-mode")
        router.replace("auth", "signup" if self._mode == "signup" else "")
        self._draw()

    @handle("email_box", "pressed_enter")
    def email_box_pressed_enter(self, **event_args):
        self.submit_button_click()

    @handle("password_box", "pressed_enter")
    def password_box_pressed_enter(self, **event_args):
        self.submit_button_click()

    @handle("submit_button", "click")
    def submit_button_click(self, **event_args):
        email, password = (self.email_box.text or "").strip(), self.password_box.text or ""
        signup = self._mode == "signup"
        if not email or not password:
            self._say("Enter your email and password.")
            return
        if not EMAIL.match(email):
            self._say("Please enter a valid email address.")
            return
        if signup and len(password) < 6:
            self._say("Use at least 6 characters for your password.")
            return
        if signup and not legal.consent_ok(self.dom_nodes["consent"]):
            return  # the kit shows its own message next to the tick box
        self._say(None)
        self.submit_button.enabled = False
        try:
            r = auth.sign_up(email, password) if signup else auth.sign_in(email, password)
        finally:
            self.submit_button.enabled = True
        if not r["ok"]:
            self._say(r["error"])
            return
        router.after_sign_in()

    @handle("forgot_button", "click")
    def forgot_button_click(self, **event_args):
        email = (self.email_box.text or "").strip()
        if not email:
            self._say("Type your email above first, then tap “Forgot password?”.")
            return
        state.toast(auth.reset(email)["message"])

    @handle("google_button", "click")
    def google_button_click(self, **event_args):
        if self._mode == "signup" and not legal.consent_ok(self.dom_nodes["consent"]):
            return
        r = auth.google()
        if not r["ok"]:
            self._say(r["error"])
            return
        router.after_sign_in()

    @handle("", "show")
    def form_show(self, **event_args):
        if window_wide():
            self.email_box.focus()


def window_wide():
    from anvil.js import window
    return bool(getattr(window.matchMedia("(min-width: 760px)"), "matches"))
