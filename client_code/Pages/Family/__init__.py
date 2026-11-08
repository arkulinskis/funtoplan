from anvil import *
from anvil.js import window

from ._anvil_designer import FamilyTemplate
from ... import auth, ftp, router, state


class Family(FamilyTemplate):
    """The family (#family): invite (QR code, the code as fridge magnets, seats, copy / share / big QR), the
    brownie leaderboard (7 days / all time podium), members (the owner can remove people) and settings (profile,
    family settings, night mode, new join code, Privacy & Terms, leave, log out)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        self.share_button.visible = ftp.can_share()
        self._code = None
        self.dom_nodes["qr"].addEventListener("click", self.invite_click)
        self.refresh()

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self.refresh)

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self.refresh)

    def refresh(self):
        s = ftp.st()
        m = ftp.me()
        if not s or not m:
            return
        d = ftp.loose(self.dom_nodes)
        fam, members, owner = s["family"], ftp.active_members(), ftp.is_owner()
        self.title.text = fam["name"]
        self.settings_button.visible = owner
        self.family_row.visible = owner
        self.code_row.visible = owner
        if self._code != fam["code"]:
            self._code = fam["code"]
            if not window.FTP.qr(d["qr"], ftp.invite_link()):
                d["qr"].style.display = "none"
            for i, ch in enumerate(fam["code"][:6]):
                d["t%d" % i].textContent = ch
            d["tiles"].setAttribute("aria-label", "Join code " + " ".join(fam["code"]))
        spots = fam["max_members"] - len(members)
        ftp.text(d["spots"], ("Scan with a phone camera to join. %s left." % ftp.plural(spots, "seat")) if spots > 0 else "Your board is full (4 people).")
        for i in range(4):
            ftp.avatar(d["s%d" % i], members[i] if i < len(members) else None, "sm")
            if i >= len(members):
                d["s%d" % i].className = "seat"
                d["s%d" % i].textContent = "·"
        key = "week_points" if ftp.S["lb"] == "week" else "points"
        ranked = sorted(members, key=lambda x: -x[key])
        for i in range(3):
            x = ranked[i] if i < len(ranked) else None
            getattr(self, "pod%d" % i).classes["empty-pod"] = x is None
            ftp.avatar(d["pa%d" % i], x, "lg")
            ftp.text(d["pn%d" % i], x["name"] if x else "Open seat")
            ftp.text(d["pp%d" % i], max(0, x[key]) if x else "")
        for name, on in (("week", ftp.S["lb"] == "week"), ("all", ftp.S["lb"] == "all")):
            btn = getattr(self, "lb_" + name)
            btn.classes["on"] = on
            state.set_attr(btn, "aria-pressed", "true" if on else "false")
        ftp.text(d["member_count"], "%d / %d" % (len(members), fam["max_members"]))
        self.member_panel.items = members
        lv = ftp.level_of(m["points"])
        ftp.text(d["profile_sub"], "%s %s · Level %d %s" % (m["avatar"], m["name"], lv["n"], lv["title"]))
        ftp.text(d["email"], (state.me() or {}).get("email"))
        self._night()
        ftp.text(d["foot"], "Fun To Plan · made for families of 2–4 · board " + fam["code"])

    def _night(self):
        dark = ftp.is_dark()
        self.night_toggle.classes["on"] = dark
        state.set_attr(self.night_toggle, "aria-checked", "true" if dark else "false")

    def lb_click(self, event):
        ftp.S["lb"] = event.currentTarget.getAttribute("data-lb")
        self.refresh()

    def invite_click(self, event):
        ftp.open_invite()

    @handle("big_qr_button", "click")
    def big_qr_button_click(self, **event_args):
        ftp.open_invite()

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        ftp.copy_link()

    @handle("share_button", "click")
    def share_button_click(self, **event_args):
        ftp.share_link()

    def profile_click(self, event):
        ftp.open_profile()

    @handle("settings_button", "click")
    def settings_button_click(self, **event_args):
        ftp.open_family_settings()

    def settings_click(self, event):
        ftp.open_family_settings()

    def night_click(self, event):
        ftp.toggle_theme()
        self._night()

    def code_click(self, event):
        if ftp.ask("Make a new join code?", "The current QR code and invite links will stop working. People already in the family stay.", "New code"):
            if ftp.run("regen_code"):
                state.toast("New code: " + ftp.st()["family"]["code"])

    def leave_click(self, event):
        if ftp.ask("Leave %s?" % ftp.st()["family"]["name"], "You can rejoin later with the code and keep your brownie points.", "Leave", True):
            if ftp.run("leave_family"):
                state.toast("You left the family board")
                router.go("start")

    def logout_click(self, event):
        auth.sign_out()
        router.go("landing")
