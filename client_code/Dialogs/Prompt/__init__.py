from anvil import *

from ._anvil_designer import PromptTemplate
from ... import state


class Prompt(PromptTemplate):
    """A short question with a text box (sending a task back: "What still needs doing?").
    Closes with the text ("" allowed) or None when cancelled."""

    def __init__(self, title="", placeholder="", ok="OK", **properties):
        super().__init__(**properties)
        self.dom_nodes["title"].textContent = title
        self.text_box.placeholder = placeholder
        self.ok_button.text = ok
        state.set_control_attr(self.text_box, "maxlength", 500)
        state.set_control_attr(self.text_box, "aria-label", placeholder or title)

    @handle("", "show")
    def form_show(self, **event_args):
        self.text_box.focus()

    @handle("ok_button", "click")
    def ok_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=(self.text_box.text or "").strip())

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
