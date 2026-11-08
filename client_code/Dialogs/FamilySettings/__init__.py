from anvil import *

from ._anvil_designer import FamilySettingsTemplate
from ... import ftp, state


class FamilySettings(FamilySettingsTemplate):
    """The owner's family settings: board name and the weekly brownie goal (10 to 5000, steps of 10).
    Closes with True when saved."""

    def __init__(self, **properties):
        super().__init__(**properties)
        fam = ftp.st()["family"]
        self.name_box.text = fam["name"]
        state.set_control_attr(self.name_box, "maxlength", 40)
        self._goal = fam["weekly_goal"] or 100
        self._draw()

    def _draw(self):
        self.dom_nodes["goal"].textContent = str(self._goal)

    @handle("less_button", "click")
    def less_button_click(self, **event_args):
        self._goal = max(10, self._goal - 10)
        self._draw()

    @handle("more_button", "click")
    def more_button_click(self, **event_args):
        self._goal = min(5000, self._goal + 10)
        self._draw()

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        if ftp.run("update_family", {"name": self.name_box.text or "", "weekly_goal": self._goal}):
            self.raise_event("x-close-alert", value=True)

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
