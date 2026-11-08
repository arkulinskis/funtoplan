from anvil import *

from ._anvil_designer import CardTemplate
from ... import ftp

# the action button some lists put on a card: (label, roles)
CTAS = {
    "approve": ("Approve", ["btn", "btn-sm", "btn-dark", "ic-shield"]),
    "ack": ("I'm in", ["btn", "btn-sm", "ic-thumb"]),
    "complete": ("Done", ["btn", "btn-sm", "ic-check"]),
    "claim": ("Claim", ["btn", "btn-sm", "btn-blue", "ic-hand"]),
}


class Card(CardTemplate):
    """One card on the fridge: a sticky note (yellow task, blue event, pink want, mint when done) held by a magnet.
    Tapping it opens the card's sheet. item = {"it": card dict, "cta": None | "approve" | "ack" | "complete" | "claim",
    "status": show the status pill}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item["it"]
        done = ftp.eff(it) == "done"
        self.card.classes.add("k-" + it["kind"])
        self.card.classes["is-done"] = done
        icon, label = ftp.KIND[it["kind"]]
        self.type_chip.classes.add("t-" + it["kind"])
        self.type_ic.classes.add("ic-" + icon)
        ftp.text(self.dom_nodes["key"], it["key"])
        ftp.text(self.dom_nodes["title"], it["title"])
        anvil_open = self.open
        from ... import state
        state.set_attr(anvil_open, "aria-label", "Open %s: %s (%s)" % (it["key"], it["title"], label))
        self.prio.visible = it["priority"] in ("high", "low")
        self.prio.classes.add(it["priority"])
        self.prio_ic.classes.add("ic-up" if it["priority"] == "high" else "ic-down")
        self.status.visible = bool(self.item.get("status"))
        self.status.classes.add("s-" + ftp.eff(it))
        ftp.text(self.dom_nodes["status_text"], ftp.status_label(it))
        self.pts.visible = bool(it["points"])
        ftp.text(self.dom_nodes["pts_text"], it["points"])
        self._meta(it, done)
        who = ftp.member(it.get("assignee"))
        cta = self.item.get("cta")
        self.cta_box.visible = bool(cta)
        if cta:
            self.cta.text, self.cta.role = CTAS[cta]
        whonode = self.dom_nodes["who"]
        whonode.style.display = "" if (who and not cta) else "none"
        if who and not cta:
            ftp.avatar(whonode, who, "xs")
        self.open_slot.visible = not cta and not who and it["kind"] == "task" and not done

    def _meta(self, it, done):
        self.m_due.visible = False
        if it["kind"] == "task" and it.get("due_date"):
            d = ftp.parse_ymd(it["due_date"])
            diff = ftp.day_diff(d)
            self.m_due.visible = True
            self.due_ic.classes.add("ic-clock")
            self.m_due.classes["warn"] = not done and diff < 0
            self.m_due.classes["soon"] = not done and diff == 0
            ftp.text(self.dom_nodes["due_text"], ftp.fmt_day(d))
        elif it["kind"] == "event" and it.get("event_at"):
            self.m_due.visible = True
            self.due_ic.classes.add("ic-calendar")
            self.m_due.classes["soon"] = not done and ftp.day_diff(ftp.jsdate(it["event_at"])) == 0
            ftp.text(self.dom_nodes["due_text"], ftp.fmt_when(it["event_at"]))
        self.m_place.visible = it["kind"] == "event" and bool(it.get("location"))
        ftp.text(self.dom_nodes["place_text"], it.get("location"))
        rec = it.get("recurrence") or "none"
        self.m_repeat.visible = rec != "none"
        if rec != "none":
            from ... import state
            state.set_attr(self.m_repeat, "title", "Repeats " + ftp.RECUR[rec].lower())
        ftp.text(self.dom_nodes["repeat_text"], "turns" if it.get("rotate") else "")
        self.m_approval.visible = bool(it.get("requires_approval"))
        self.m_link.visible = it["kind"] == "want" and bool(it.get("link"))
        self.m_comments.visible = bool(it.get("comment_count"))
        ftp.text(self.dom_nodes["comments_text"], it.get("comment_count"))
        self.m_acks.visible = bool(it["acks"])
        self.acks_ic.classes.add("ic-thumb" if it["kind"] == "want" else "ic-eye")
        ftp.text(self.dom_nodes["acks_text"], len(it["acks"]))

    def open_click(self, event):
        ftp.open_detail(self.item["it"]["id"])

    @handle("cta", "click")
    def cta_click(self, **event_args):
        it, cta = self.item["it"], self.item["cta"]
        ftp.item_act(cta, it["id"], self.cta)
