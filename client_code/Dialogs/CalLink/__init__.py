from anvil import *
from anvil.js import window

from ._anvil_designer import CalLinkTemplate
from ... import ftp, state


class CalLink(CalLinkTemplate):
    """"Add to my phone calendar" (from the Week page): my seat's private feed (cal_link in server_code/api.py, served
    by server_code/calendar_feed.py) as an Apple Calendar link (webcal://), a Google Calendar link
    (calendar.google.com/calendar/r?cid=...) and Copy; "Only my jobs" adds ?mine=1; Reset makes a new link and the
    old one stops working. States: making the link, ready, error (incl. before the new table is accepted)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self._link = ftp.loose(None)
        self._mine = False
        self._show("wait")

    @handle("", "show")
    def form_show(self, **event_args):
        if self._link is None:
            self._load(False)

    def _show(self, which):
        self.wait_box.visible = which == "wait"
        self.err_box.visible = which == "error"
        self.ready_box.visible = which == "ready"

    def _load(self, reset):
        self._show("wait")
        try:
            self._link = ftp.api("cal_link", {"reset": bool(reset)})
        except ftp.ApiError as e:
            if e.code in ("auth", "session", "nofamily"):
                self.raise_event("x-close-alert", value=None)
                ftp.handle_error(e)
                return
            self._error(str(e))
            return
        except Exception as e:
            if type(e).__name__ == "SessionExpiredError":
                self.raise_event("x-close-alert", value=None)
                ftp.handle_error(e)
                return
            self._error("We couldn't reach Fun To Plan just now. Check your connection and try again.")
            return
        self._draw()
        self._show("ready")
        if reset:
            state.toast("New link made. The old one has stopped working: subscribe again with this one.")

    def _error(self, text):
        self.dom_nodes["err_text"].textContent = text
        self._show("error")

    def _url(self):
        return window.location.origin + self._link["path"] + ("?mine=1" if self._mine else "")

    def _draw(self):
        d = ftp.loose(self.dom_nodes)
        url = self._url()
        webcal = "webcal://" + url.split("://", 1)[1]
        d["apple_link"].setAttribute("href", webcal)
        d["google_link"].setAttribute("href", "https://calendar.google.com/calendar/r?cid=" + window.encodeURIComponent(webcal))
        d["url"].textContent = url
        self.mine_toggle.classes["on"] = self._mine
        state.set_attr(self.mine_toggle, "aria-checked", "true" if self._mine else "false")
        last = self._link.get("last_fetch")
        d["fetched"].textContent = ("A calendar last checked it " + ftp.ago(last) + ".") if last else \
            "No calendar has used this link yet."

    def mine_click(self, event):
        self._mine = not self._mine
        self._draw()

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        window.FTP.copy(self._url())
        state.toast("Link copied. Paste it into your calendar app's “subscribe” box.")

    @handle("reset_button", "click")
    def reset_button_click(self, **event_args):
        if ftp.ask("Make a new link?", "The old link stops working right away, so calendars that use it stop updating. "
                   "Subscribe again with the new one.", "Reset link", True):
            self._load(True)

    @handle("retry_button", "click")
    def retry_button_click(self, **event_args):
        self._load(False)

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
