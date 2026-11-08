"""Log in, sign up, reset a password, Continue with Google, log out (Anvil Users service).

Each returns {"ok": True} or {"ok": False, "error": "..."} for the expected problems, so the Auth page can show them
next to the form. On success the family board is loaded (ftp.bootstrap) and the Privacy & Terms kit is told.
"""
import anvil.server
import anvil.users

from . import ftp, legal, state

AUTH_ERRORS = [
    (anvil.users.UserExists, "An account with that email already exists. Try logging in."),
    (anvil.users.EmailNotConfirmed, "Please confirm your email address first (check your inbox)."),
    (anvil.users.AccountIsNotEnabled, "This account is not enabled yet."),
    (anvil.users.TooManyPasswordFailures, "Too many attempts. Please wait a moment and try again."),
    (anvil.users.PasswordNotAcceptable, None),  # Anvil's own message says what's wrong
    (anvil.users.AuthenticationFailed, "Wrong email or password."),
]
EXPECTED = tuple(cls for cls, _ in AUTH_ERRORS)


def _problem(e):
    for cls, msg in AUTH_ERRORS:
        if isinstance(e, cls):
            return {"ok": False, "error": msg or str(e) or "Please choose a stronger password."}
    return {"ok": False, "error": str(e)}


def _signed_in():
    ftp.bootstrap()
    legal.refresh_soon()  # records the sign-up tick box, or reminds people to review new terms
    return {"ok": True}


def sign_in(email, password):
    try:
        anvil.users.login_with_email(email.strip(), password, remember=True)
    except EXPECTED as e:
        return _problem(e)
    return _signed_in()


def sign_up(email, password):
    try:
        anvil.users.signup_with_email(email.strip(), password, remember=True)
        if anvil.users.get_user() is None:
            anvil.users.login_with_email(email.strip(), password, remember=True)
    except EXPECTED as e:
        return _problem(e)
    return _signed_in()


def reset(email):
    try:
        anvil.users.send_password_reset_email(email.strip())
    except anvil.users.AuthenticationFailed:
        pass  # same answer either way, so nobody can find out which emails have accounts
    return {"ok": True, "message": "Password reset email sent. Check your inbox."}


def _google_step_done():
    """After login_with_google() gave None: did the person finish the Google window (they just have no account yet)?"""
    try:
        import anvil.google.auth
        return bool(anvil.google.auth.get_user_email())
    except Exception:
        return True  # can't tell: go on to sign-up, which asks Google again if needed


def google():
    """Sign in with Google, or create the account on the first visit (login_with_google gives None then)."""
    try:
        if anvil.users.login_with_google(remember=True) is None:
            if not _google_step_done() or anvil.users.signup_with_google(remember=True) is None:
                return {"ok": False, "error": "Google sign-in was cancelled."}
    except EXPECTED as e:
        return _problem(e)
    return _signed_in()


def sign_out():
    anvil.users.logout()
    legal.signed_out()
    ftp.signed_out()
