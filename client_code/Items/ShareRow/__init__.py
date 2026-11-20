from anvil import *

from ._anvil_designer import ShareRowTemplate
from ... import ftp


class ShareRow(ShareRowTemplate):
    """One seat in "Who's carrying the load?" on the Family page: Planned / Did / Checked over the last 30 days,
    as mini bars scaled to the family's biggest number. Kid seats show Did only.
    item = {"row": {"m", "planned", "did", "checked"} from ftp.load_share, "max": the biggest number}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        row, top = self.item["row"], max(1, self.item["max"])
        m = row["m"]
        d = ftp.loose(self.dom_nodes)
        kid = ftp.is_kid(m)
        ftp.avatar(d["who"], m, "sm")
        ftp.text(d["name"], m["name"])
        ftp.text(d["tag"], "kid seat" if kid else "")
        for key, part in (("planned", "plan"), ("did", "did"), ("checked", "chk")):
            n = row[key]
            d["b_" + part].style.display = "none" if (kid and key != "did") else ""
            ftp.text(d["n_" + part], n)
            d["f_" + part].style.width = "%d%%" % int(round(n * 100.0 / top))
