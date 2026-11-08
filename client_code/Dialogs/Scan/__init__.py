from anvil import *
from anvil.js import window

from ._anvil_designer import ScanTemplate
from ... import state


class Scan(ScanTemplate):
    """The camera QR reader (FTP.scan in theme/assets/ftp-fx.js, BarcodeDetector). Closes with the 6-letter code it
    read, or None. The camera stops when the sheet closes."""

    @handle("", "show")
    def form_show(self, **event_args):
        window.FTP.scan(self.dom_nodes["video"], self._found, self._fail)

    @handle("", "hide")
    def form_hide(self, **event_args):
        window.FTP.stopScan()

    def _found(self, code):
        self.raise_event("x-close-alert", value=code)

    def _fail(self, message):
        state.toast(message, "error")
        self.raise_event("x-close-alert", value=None)

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
