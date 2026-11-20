from anvil import *

from ._anvil_designer import KidSeatTemplate
from ... import ftp, state


class KidSeat(KidSeatTemplate):
    """Add a kid seat (add_kid) or edit one (update_kid): a first name or nickname, an emoji and a magnet colour.
    Kid seats have no account and no phone (the Terms bar under-16 accounts); grown-ups tick off their jobs.
    Closes with a toast text when saved, else None."""

    def __init__(self, kid_id=None, **properties):
        super().__init__(**properties)
        kid = ftp.member(kid_id) if kid_id else None
        self._id = kid["id"] if kid else None
        self.picker.set_labels("Name or nickname", "Leo, Mia, Bug…")
        if kid:
            self.picker.set_profile(kid["name"], kid["avatar"], kid["color"])
            self.dom_nodes["title"].textContent = "Edit " + kid["name"]
            self.save_button.text = "Save"
            self.dom_nodes["seats"].textContent = ""
        else:
            avatar, color = ftp.fresh_look()
            self.picker.set_profile("", avatar, color)
            left = ftp.MAX_MEMBERS - len(ftp.active_members())
            self.dom_nodes["seats"].textContent = "A kid seat counts as one of the board's %d seats (%s)." % (
                ftp.MAX_MEMBERS, ftp.plural(left, "seat") + " left")
        self.picker.name_box.add_event_handler("change", self._name_changed)
        self._name_changed()

    def _name_changed(self, **event_args):
        name = (self.picker.value()["display_name"] or "Leo").strip()
        self.dom_nodes["did_it"].textContent = "“%s did it”" % name

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        v = self.picker.value()
        if not v["display_name"]:
            state.toast("Give your kid a name or nickname.", "error")
            state.focus(self.picker.name_box)
            return
        if self._id:
            v["member_id"] = self._id
            if ftp.run("update_kid", v):
                self.raise_event("x-close-alert", value="Saved")
        elif ftp.run("add_kid", v):
            self.raise_event("x-close-alert", value="%s %s has a seat on the board" % (v["avatar"], v["display_name"]))

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
