from anvil import *
from anvil.js import window

from ._anvil_designer import FamilyTemplate
from ... import auth, ftp, router, state


class Family(FamilyTemplate):
    """The family (#family): invite (QR code, the code as fridge magnets, seats, copy / share / big QR, Add a kid),
    the brownie leaderboard (7 days / all time podium), who's carrying the load (Planned / Did / Checked, the
    planning split, "Own a job"), members (kid seats can be edited; the owner can remove people) and settings
    (profile, family settings, night mode, new join code, Privacy & Terms, leave, log out)."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        self.share_button.visible = ftp.can_share()
        self._code = None
        self._own = ftp.loose(None)  # the Editor preset behind "Own a job" / "Hand over a job"
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
        n_kids = len(ftp.kids())
        who = ftp.plural(len(members) - n_kids, "grown-up") + ((" + " + ftp.plural(n_kids, "kid")) if n_kids else "")
        if spots > 0:
            ftp.text(d["spots"], "%s. Scan with a phone camera to join, or add a kid who has no phone. %s left." % (who, ftp.plural(spots, "seat")))
        else:
            ftp.text(d["spots"], "%s. Your board is full (%d seats)." % (who, fam["max_members"]))
        self.kid_button.visible = spots > 0
        for i in range(4):
            x = members[i] if i < len(members) else None
            ftp.avatar(d["s%d" % i], x, "sm")
            if x and ftp.is_kid(x):
                d["s%d" % i].classList.add("kid")
                d["s%d" % i].setAttribute("title", x["name"] + " · kid seat")
                d["s%d" % i].setAttribute("aria-label", x["name"] + ", kid seat")
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
        self._share(m, spots)
        ftp.text(d["foot"], "Fun To Plan · made for families of 2–4 · board " + fam["code"])

    def _share(self, m, spots):
        """Who's carrying the load (last 30 days): Planned / Did / Checked per seat, the grown-ups' planning split,
        and a nudge to own a whole job when one grown-up plans 65% or more of at least 6 cards."""
        d = ftp.loose(self.dom_nodes)
        sh = ftp.load_share(30)
        rows, split, total = sh["rows"], sh["split"], sh["total"]
        top = max([max(row["planned"], row["did"], row["checked"]) for row in rows] + [1])
        self.share_panel.items = [{"row": row, "max": top} for row in rows]
        many = len(split) >= 2
        self.split_box.visible = many and total > 0
        self.note_box.visible = False
        self._own = ftp.loose(None)
        verdict = ""
        if many and total > 0:
            bar = d["split_bar"]
            bar.textContent = ""
            parts = []
            for pair in split:
                gm, n = pair[0], pair[1]
                parts.append("%s %d%%" % (gm["name"], int(round(n * 100.0 / total))))
                if n:
                    seg = window.document.createElement("i")
                    seg.style.width = "%.1f%%" % (n * 100.0 / total)
                    seg.style.setProperty("--c", gm["color"] or "#3a7be0")
                    bar.appendChild(seg)
            ftp.text(d["split_text"], " · ".join(parts))
            bar.setAttribute("aria-label", "Planning split: " + ", ".join(parts))
            heavy = max(split, key=lambda pair: pair[1])
            if total >= 6 and heavy[1] >= 0.65 * total:
                self.note_box.visible = True
                today = ftp.today_str()
                if heavy[0]["id"] == m["id"]:
                    other = min([pair for pair in split if pair[0]["id"] != m["id"]], key=lambda pair: pair[1])[0]
                    ftp.text(d["note_text"], "You planned %d of %d cards. Planning is work too. Hand a whole job to %s?"
                             % (heavy[1], total, other["name"]))
                    self.own_button.text = "Hand over a job"
                    self._own = {"assignee": other["id"], "recurrence": "weekly", "due": today,
                                 "notes": "%s owns it end to end: notice, plan, do." % other["name"],
                                 "hint": "A whole job for %s: they notice it, plan it and do it, every week." % other["name"]}
                else:
                    ftp.text(d["note_text"], "%s planned %d of %d cards. Planning is work too. Want to own a whole job?"
                             % (heavy[0]["name"], heavy[1], total))
                    self.own_button.text = "Own a job"
                    self._own = {"assignee": m["id"], "recurrence": "weekly", "due": today,
                                 "notes": "You own it end to end: notice, plan, do.",
                                 "hint": "Your job from start to finish: you notice it, plan it and do it, every week."}
            elif total >= 6:
                verdict = "Nicely shared 🤝"
            else:
                verdict = "Too early to tell: %s planned so far." % ftp.plural(total, "card")
        elif not many:
            verdict = ("Only one grown-up plans here. Invite your partner to share the planning." if spots > 0
                       else "One grown-up plans everything here.")
        ftp.text(d["verdict"], verdict)
        d["verdict"].style.display = "" if verdict else "none"

    @handle("own_button", "click")
    def own_button_click(self, **event_args):
        if self._own:
            ftp.open_editor(None, "task", self._own)

    @handle("kid_button", "click")
    def kid_button_click(self, **event_args):
        ftp.open_kid_seat()

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
