"""Page addresses: #name/arg -> a page Form (open_form), with sign-in and family-board rules.

    PAGES[name] = (who may open it, browser-tab title)
        who: None = anyone, "guest" = signed out only, "user" = signed in (no board needed), "family" = on a board
    NAV = the main menu (desktop rail + phone tab bar): (page, label, icon)
Invite links keep the JavaScript version's address: #join=ABC123 (the QR code holds it). The code is remembered
(ftp.S["pending_join"]) and the visitor lands on the landing page, the start page or their board.
"""
import re

import anvil
import anvil.js
from anvil.js import window

from . import ftp, state

PAGES = {
    "landing": (None, "A family chore board with brownie points"),
    "auth": ("guest", "Log in"),
    "start": ("user", "Start or join a family board"),
    "home": ("family", "Today"),
    "board": ("family", "Board"),
    "chat": ("family", "Family chat"),
    "family": ("family", "Family"),
}
NAV = [("home", "Home", "home"), ("board", "Board", "board"), ("chat", "Chat", "chat"), ("family", "Family", "family")]
APP_NAME = "Fun To Plan"
_r: dict = {"after": "", "listening": False, "page": ""}


def _form(name):
    """The page's Form class (imported when first needed, so start-up stays quick)."""
    if name == "landing":
        from .Pages.Landing import Landing
        return Landing
    if name == "auth":
        from .Pages.Auth import Auth
        return Auth
    if name == "start":
        from .Pages.Start import Start
        return Start
    if name == "board":
        from .Pages.Board import Board
        return Board
    if name == "chat":
        from .Pages.Chat import Chat
        return Chat
    if name == "family":
        from .Pages.Family import Family
        return Family
    from .Pages.Home import Home
    return Home


def parse(hash_text):
    h = (hash_text or "").lstrip("#").lstrip("!").lstrip("/").split("?")[0]
    parts = [window.decodeURIComponent(p) for p in h.split("/") if p]
    return (parts[0] if parts else ""), parts[1:]


def href(name, *args):
    return "#" + "/".join([name] + [window.encodeURIComponent(str(a)) for a in args if a not in (None, "")])


def home_page():
    if ftp.st():
        return "home"
    return "start" if state.me() else "landing"


def current():
    return _r["page"]


def show():
    """Open the page for the current address."""
    name, args = parse(window.location.hash)
    m = re.match(r"^join=([A-Za-z0-9]{6})$", name)
    if m:  # an invite link or QR code
        ftp.S["pending_join"] = m.group(1).upper()
        name, args = home_page(), []
        if name == "home":
            if ftp.st()["family"]["code"] != ftp.S["pending_join"]:
                state.toast("You are already on a family board. Leave it first to join another one.")
            ftp.S["pending_join"] = None
        window.history.replaceState(None, "", href(name))
    if name not in PAGES:
        name, args = home_page(), []
    who = PAGES[name][0]
    moved = False
    if who == "guest" and state.me():
        name, args, moved = home_page(), [], True
    elif who in ("user", "family") and not state.me():
        _r["after"] = window.location.hash  # the address stays: back there after logging in
        name, args = "auth", []
    elif who == "family" and not ftp.st():
        name, args, moved = "start", [], True
    elif name == "start" and ftp.st():
        name, args, moved = "home", [], True
    if moved:
        window.history.replaceState(None, "", href(name))
    window.document.title = PAGES[name][1] + " · " + APP_NAME
    window.UI_READY = False
    _r["page"] = name
    page = _form(name)(args=args)
    anvil.open_form(page)
    shell = getattr(page, "layout", None)
    if shell is not None and hasattr(shell, "refresh"):
        shell.refresh(name)  # Anvil reuses the layout between pages: tell it who is signed in and which page is open
    if not getattr(page, "keeps_scroll", False):
        window.scrollTo(0, 0)
    window.UI_READY = True  # tests and screenshots wait for this


def go(name, *args):
    """Go to a page. Same address again = reload the page."""
    target = href(name, *args)
    if window.location.hash == target:
        show()
    else:
        window.location.hash = target


def replace(name, *args):
    """Change the address without opening anything (a page that switches its own view)."""
    window.history.replaceState(None, "", href(name, *args))


def after_sign_in():
    """Once signed in: the page they were heading for, or their board (or the start page without one)."""
    target = _r["after"]
    _r["after"] = ""
    if target and target != window.location.hash:
        window.location.hash = target
    else:
        go(home_page())


def _on_hash(event):
    show()


def start():
    if not _r["listening"]:
        window.addEventListener("hashchange", anvil.js.report_exceptions(_on_hash))
        _r["listening"] = True
    show()
