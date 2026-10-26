from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.js
import json

# Fun To Plan
# -----------
# The whole interface is a neumorphic single-page UI (theme/assets/ftp.js + ftp.css)
# mounted inside this form. This form is the bridge between that UI and Anvil:
#   - login / signup / logout use the Anvil Users service
#   - everything else goes to the server module `api.ftp_api`
# Requests and responses travel as JSON strings, so nothing gets lost in
# translation between JavaScript and Python.

AUTH_ERRORS = {
  'AuthenticationFailed': 'Wrong email or password.',
  'UserExists': 'An account with that email already exists. Try logging in.',
  'EmailNotConfirmed': 'Please confirm your email address first (check your inbox).',
  'AccountIsNotEnabled': 'This account is not enabled yet.',
  'TooManyPasswordFailures': 'Too many attempts. Please wait a moment and try again.',
  'PasswordNotAcceptable': 'Please choose a stronger password.',
  'SessionExpiredError': 'Your session expired. Reloading…',
}


class Form1(Form1Template):
  def __init__(self, **properties):
    super().__init__(**properties)
    self._mounted = False
    self.add_event_handler('show', self._on_show)

  def _on_show(self, **event_args):
    if self._mounted:
      return
    self._mounted = True
    app = anvil.js.window.FunToPlan
    app.mount(anvil.js.get_dom_node(self), self.bridge)

  # Called from JavaScript. Blocking calls return a Promise on the JS side.
  def bridge(self, action, payload_json):
    try:
      payload = json.loads(payload_json) if payload_json else {}
      with anvil.server.no_loading_indicator:
        if action == 'login':
          anvil.users.login_with_email(payload.get('email', '').strip(), payload.get('password', ''), remember=True)
          return self._api('bootstrap', '{}')
        if action == 'signup':
          email = payload.get('email', '').strip()
          password = payload.get('password', '')
          if len(password) < 6:
            return self._error('Use at least 6 characters for your password.', 'auth_failed')
          anvil.users.signup_with_email(email, password)
          if anvil.users.get_user() is None:
            anvil.users.login_with_email(email, password, remember=True)
          return self._api('bootstrap', '{}')
        if action == 'reset_password':
          anvil.users.send_password_reset_email(payload.get('email', '').strip())
          return json.dumps({'ok': True, 'data': {}})
        if action == 'logout':
          anvil.users.logout()
          return json.dumps({'ok': True, 'data': {}})
        return self._api(action, payload_json)
    except Exception as e:
      name = type(e).__name__
      if name == 'SessionExpiredError':
        return self._error(AUTH_ERRORS[name], 'session')
      if name in AUTH_ERRORS:
        message = str(e) if name not in ('AuthenticationFailed',) else AUTH_ERRORS[name]
        return self._error(message or AUTH_ERRORS[name], 'auth_failed')
      return self._error(str(e) or 'Something went wrong. Please try again.', 'error')

  def _api(self, action, payload_json):
    return anvil.server.call('ftp_api', action, payload_json)

  def _error(self, message, code):
    return json.dumps({'ok': False, 'error': message, 'code': code})
