"""The app starts here (anvil.yaml: startup module). One server call (`bootstrap`: who is signed in and their family
board; Anvil's loading spinner shows meanwhile), the Privacy & Terms kit, then the page for the address."""
from . import ftp, legal, router

LEGAL_THEME = {"accent": "#cf3b42"}  # colours for the Privacy & Terms page (the red magnet)

legal.setup(LEGAL_THEME)
if ftp.bootstrap():
    legal.refresh_soon()  # Privacy & Terms: reminder bar for signed-in people who haven't accepted the current version
router.start()
