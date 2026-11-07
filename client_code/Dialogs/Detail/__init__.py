from anvil import *

from ._anvil_designer import DetailTemplate
from ... import ftp, state

ACTIONS = ["claim", "start", "unstart", "reject", "reopen", "complete", "approve"]


class Detail(DetailTemplate):
    """A card's sheet: title, notes (links + FAM-12), badges, who / when, "seen by / coming / wanted by" with the
    acknowledge button, the actions its state allows, and comments (item_detail). Stays live while the board syncs.
    Closes with None, ("edit", id), ("open", other id) for a FAM-12 link, or ("reject", id) for Send back."""

    def __init__(self, item_id=None, **properties):
        super().__init__(**properties)
        self._id = item_id
        self._data = None
        state.set_control_attr(self.comment_box, "maxlength", 1000)
        state.set_control_attr(self.comment_box, "aria-label", "Add a comment")
        state.set_control_attr(self.comment_box, "autocomplete", "off")
        self.comment_panel.add_event_handler("x-open", self._open_other)
        self._draw()

    @handle("", "show")
    def form_show(self, **event_args):
        ftp.listen(self._board_changed)
        self._load()

    @handle("", "hide")
    def form_hide(self, **event_args):
        ftp.unlisten(self._board_changed)

    def _close(self, value=None):
        self.raise_event("x-close-alert", value=value)

    def _load(self):
        try:
            self._data = ftp.api("item_detail", {"id": self._id})
        except ftp.ApiError as e:
            if e.code == "gone":
                state.toast(str(e), "error")
                self._close()
            return
        self._draw()

    def _board_changed(self):
        it = ftp.item_by_id(self._id)
        if not it:
            state.toast("That card was removed.")
            self._close()
            return
        if self._data and len(self._data["comments"]) != it["comment_count"]:
            self._load()
        else:
            self._draw()

    def _person(self, avatar, label, mid, fallback=""):
        m = ftp.member(mid)
        avatar.style.display = "" if m else "none"
        if m:
            ftp.avatar(avatar, m, "xs")
            label.textContent = m["name"] + ("" if m["active"] else " (left)")
            label.className = ""
        else:
            label.textContent = fallback
            label.className = "muted"

    def _draw(self):
        it = ftp.item_by_id(self._id) or (self._data or {}).get("item")
        if not it:
            return
        d, data, mine = self.dom_nodes, self._data, ftp.st()["me"]
        kind, s = it["kind"], it["status"]
        icon, label = ftp.KIND[kind]
        self.type_chip.classes.add("t-" + kind)
        self.type_ic.classes.add("ic-" + icon)
        ftp.text(d["key"], it["key"])
        for c in ("todo", "doing", "review", "done"):
            self.status.classes["s-" + c] = ftp.eff(it) == c
        ftp.text(d["status_text"], ftp.status_label(it))
        ftp.text(d["title"], it["title"])
        d["notes"].style.display = "" if it["notes"] else "none"
        ftp.rich(d["notes"], it["notes"], self._open_key)
        self.b_points.visible = bool(it["points"])
        ftp.text(d["points"], "%d brownie points" % it["points"])
        self.b_prio.visible = it["priority"] != "normal"
        self.b_prio.classes["pill-black"] = it["priority"] == "high"
        self.prio_ic.classes["ic-up"] = it["priority"] == "high"
        self.prio_ic.classes["ic-down"] = it["priority"] != "high"
        ftp.text(d["prio"], it["priority"] + " priority")
        self.b_recur.visible = it["recurrence"] != "none"
        ftp.text(d["recur"], "%s%s · #%d" % (ftp.RECUR.get(it["recurrence"], ""), " · takes turns" if it["rotate"] else "", it["occurrence"]))
        done_n = (data or {}).get("series_done") or 0
        self.b_series.visible = bool(done_n)
        ftp.text(d["series"], "done " + ftp.plural(done_n, "time"))
        self.b_approval.visible = bool(it["requires_approval"])
        self._meta(it, d)
        acked = mine in it["acks"]
        ack_label = {"event": ("You're in", "I'm in"), "want": ("You +1'd", "Me too")}.get(kind, ("Acknowledged", "Got it"))
        ftp.text(d["ack_word"], {"event": "Coming", "want": "Wanted by"}.get(kind, "Seen by"))
        ackers = [ftp.member(x) for x in it["acks"] if ftp.member(x)]
        self.ack_panel.items = [{"m": m, "size": "xs"} for m in ackers]
        self.ack_none.visible = not ackers
        self.ack_button.text = ack_label[0] if acked else ack_label[1]
        self.ack_button.role = ["btn", "btn-sm", "pressed", "ic-check"] if acked else ["btn", "btn-sm", "btn-blue", "ic-thumb"]
        self._actions(it, mine)
        comments = data["comments"] if data else None
        self.comments_wait.visible = comments is None
        self.comments_none.visible = comments == []
        self.comment_panel.items = comments or []
        ftp.text(d["comment_count"], it["comment_count"] or "")
        self.edit_button.visible = True

    def _meta(self, it, d):
        kind = it["kind"]
        self.r_link.visible = False
        rows = []
        if kind == "task":
            rows.append(("Assignee", it.get("assignee"), "open to anyone", None))
            rows.append(("Due", None, None, ftp.fmt_day(ftp.parse_ymd(it["due_date"])) if it.get("due_date") else "No due date"))
        elif kind == "event":
            rows.append(("When", None, None, ftp.fmt_when(it["event_at"]) if it.get("event_at") else ""))
            if it.get("location"):
                rows.append(("Where", None, None, it["location"]))
            if it.get("assignee"):
                rows.append(("Host", it["assignee"], "", None))
        else:
            rows.append(("For", it.get("assignee"), "The whole family", None))
            if it.get("link"):
                self.r_link.visible = True
                d["link"].href = it["link"]
                d["link"].textContent = it["link"].replace("https://", "").replace("http://", "")[:60]
        for i in range(3):
            r = rows[i] if i < len(rows) else None
            n = str(i + 1)
            getattr(self, "r" + n).visible = r is not None
            if r:
                ftp.text(d["k" + n], r[0])
                if r[3] is not None:
                    d["a" + n].style.display = "none"
                    d["v" + n].textContent = r[3]
                    d["v" + n].className = ""
                else:
                    self._person(d["a" + n], d["v" + n], r[1], r[2])
        self._person(d["a_created"], d["v_created"], it.get("created_by"), "Someone")
        ftp.text(d["created_ago"], ftp.ago(it.get("created")))
        show_done = bool(it.get("completed_by")) and it["status"] in ("done", "review")
        self.r_done.visible = show_done
        if show_done:
            ftp.text(d["k_done"], "Got by" if kind == "want" else "Done by")
            self._person(d["a_done"], d["v_done"], it["completed_by"])
            ftp.text(d["done_ago"], ftp.ago(it.get("completed_at")))
        self.r_appr.visible = bool(it.get("approved_by"))
        if it.get("approved_by"):
            self._person(d["a_appr"], d["v_appr"], it["approved_by"])

    def _actions(self, it, mine):
        show = set()
        kind, s = it["kind"], it["status"]
        texts = {"start": "Start", "unstart": "Back to to-do", "complete": "Mark done", "reopen": "Reopen", "approve": "Approve"}
        waiting = False
        if kind == "task":
            if s == "todo":
                show |= {"start", "complete"} | (set() if it.get("assignee") else {"claim"})
            elif s == "doing":
                show |= {"unstart", "complete"}
            elif s == "review":
                if it.get("completed_by") != mine or len(ftp.active_members()) < 2:
                    show |= {"reject", "approve"}
                    if it["points"]:
                        texts["approve"] = "Approve · pay %d" % it["points"]
                else:
                    waiting = True
                    show.add("reopen")
                    texts["reopen"] = "Withdraw"
            elif s == "done":
                show.add("reopen")
        elif kind == "want":
            texts.update(start="On it", unstart="Not yet", complete="Got it!", reopen="Want it again")
            if s == "todo":
                show |= {"start", "complete"}
            if s == "doing":
                show |= {"unstart", "complete"}
            if s == "done":
                show.add("reopen")
        for a in ACTIONS:
            btn = getattr(self, "a_" + a)
            btn.visible = a in show
            if a in texts:
                btn.text = texts[a]
        self.a_complete.role = ["btn", "btn-dark", "ic-starf" if kind == "want" else "ic-check"]
        self.waiting.visible = waiting

    # ---- actions
    def _act(self, action, btn, extra=None):
        ftp.item_act(action, self._id, btn, extra, detail=True)

    @handle("ack_button", "click")
    def ack_button_click(self, **event_args):
        self._act("ack", self.ack_button)

    @handle("a_claim", "click")
    def a_claim_click(self, **event_args):
        self._act("claim", self.a_claim)

    @handle("a_start", "click")
    def a_start_click(self, **event_args):
        self._act("move", self.a_start, {"to": "doing"})

    @handle("a_unstart", "click")
    def a_unstart_click(self, **event_args):
        self._act("move", self.a_unstart, {"to": "todo"})

    @handle("a_complete", "click")
    def a_complete_click(self, **event_args):
        self._act("complete", self.a_complete)

    @handle("a_approve", "click")
    def a_approve_click(self, **event_args):
        self._act("approve", self.a_approve)

    @handle("a_reopen", "click")
    def a_reopen_click(self, **event_args):
        self._act("reopen", self.a_reopen)

    @handle("a_reject", "click")
    def a_reject_click(self, **event_args):
        self._close(("reject", self._id))

    @handle("edit_button", "click")
    def edit_button_click(self, **event_args):
        self._close(("edit", self._id))

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self._close()

    def _open_key(self, iid):
        if iid != self._id:
            self._close(("open", iid))

    def _open_other(self, item_id, **event_args):
        self._open_key(item_id)

    # ---- comments
    @handle("comment_box", "pressed_enter")
    def comment_box_pressed_enter(self, **event_args):
        self.send_button_click()

    @handle("send_button", "click")
    def send_button_click(self, **event_args):
        text = (self.comment_box.text or "").strip()
        if not text:
            return
        self.comment_box.text = ""
        d = ftp.run("comment", {"id": self._id, "text": text, "_detail": True})
        if not d:
            self.comment_box.text = text
            return
        if d.get("detail"):
            self._data = d["detail"]
            self._draw()
