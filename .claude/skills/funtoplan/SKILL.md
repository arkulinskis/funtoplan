---
name: funtoplan
description: Context, workflow and recipes for Fun To Plan (funtoplan.com), the user's Anvil family board for 2–4 people (tasks, events and wants on one board, QR-code join, chat, recurring tasks, bounties and brownie points), with a neumorphic sunrise-gradient look. Load this before any feature request, bug fix, restyle or deploy for Fun To Plan.
---

# Fun To Plan: working on the app

**What it is:** a small Jira with one epic, **FAMILY**. One person creates the family board; up to 3 others join by scanning its **QR code** (or typing the 6-letter code). Cards (`FAM-12`) are **tasks** (assignee or open, due date, priority, brownie-point bounty, optional approval, recurrence with "take turns"), **events** (date, time, place, "I'm in") and **wants** (+1). Columns To do → In progress → Review → Done. Everyone acknowledges cards, comments, and chats (with an activity feed; `FAM-12` in a message links the card). Brownie points, levels (Rookie → Mythic), weekly family goal, podium, confetti. A landing page explains it all before log in.

**Where it lives:**
- App repo **github.com/arkulinskis/funtoplan**, branch `master`; Anvil pulls master. Live: **https://funtoplan.com**.
- This folder **is** the Anvil repo ("git" layout). README.md lists the features.

**What the user wants:** mobile first (bottom tab bar, bottom sheets) and good on desktop (side rail, 4 columns). Neumorphism with a tasteful sunrise gradient that says family and responsibility (baby blue, soft greys, inky blacks; charcoal night mode; Nunito + JetBrains Mono). The loading spinner and app icon match that design. Claude deploys.

## Workflow

1. `python -I C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\apps_status.py funtoplan -v`; pull Anvil's commits; never touch someone else's uncommitted work.
2. Edit the files here.
3. `python C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\gitapp_check.py funtoplan` → `ALL CHECKS PASSED` (includes `node --check` of ftp.js).
   Server logic: `python ...\APP_MAKER\tools\gitapp_test.py funtoplan <script>`, calling `anvil.server.call("ftp_api", "<action>", json.dumps(payload))` and `json.loads` on the reply.
   The UI is plain JavaScript: after changing ftp.js/ftp.css, re-read the change carefully (there is no local harness yet; one could mount `FunToPlan.mount(node, bridge)` with a fake bridge if a big UI change needs screenshots).
4. Bump `?v=` on the `_/theme/ftp.css` / `ftp.js` / icon tags in `anvil.yaml → native_deps.head_html` whenever those files change, so browsers fetch the new ones.
5. Commit only your files as arkulinskis with the Co-Authored-By line; `git push origin master`.
6. Schema changes: `anvil.yaml → db_schema`; the user accepts the Schema Mismatch alert.

## Architecture

```
client_code/Form1/       the startup form: mounts window.FunToPlan into its DOM node and is the bridge:
                         bridge(action, payload_json) -> JSON string. login / signup / reset_password / logout use Anvil Users
                         (+ legal.refresh_soon / signed_out); everything else -> server ftp_api(action, payload_json)
server_code/api.py       ALL rules. One callable ftp_api(action, payload_json): QUERIES (bootstrap, sync, preview_join, item_detail)
                         and MUTATIONS (create_family, join_family, save_item, complete, approve, reject, reopen, move, claim, ack,
                         delete_item, comment, send_message, update_profile, update_family, regen_code, remove_member, leave_family),
                         each mutation inside a transaction (_mutate). Replies {"ok": true, "data": …} or
                         {"ok": false, "error", "code"} (ApiError). Families have a `version`: clients poll `sync` every 8 s and only get
                         new state when it changed.
theme/assets/ftp.js      the whole interface (no framework): screens, board, sheets, QR rendering (qrcode-generator), polling, landing page
theme/assets/ftp.css     the neumorphic design system (light + night)
theme/assets/theme.css   Anvil's startup spinner (gradient logo tile + chasing sunrise arc), applied before the app loads
theme/assets/            favicon.svg, logo.png (metadata.logo_img), apple-touch-icon.png
```

**Tables** (all server-only): `families` (join_code, version, next_seq, weekly_goal), `members` (family, user, display_name, avatar, color, role, points, active), `items` (the cards: kind, status, assignee, dates, priority, points, recurrence/rotate/series, requires_approval, acks, completed/approved by…), `messages` (chat + activity), `points_log` (the ledger; reopening a card takes points back), `users` (+ legal_*).

## Recipes

- **New action:** write `a_<name>(p)` (query) or `m_<name>(p, user, me, family)` (mutation) in api.py, register it in QUERIES / MUTATIONS, call it from ftp.js with `api('<name>', payload)`. Raise `ApiError("friendly text")` for user errors. Mutations must keep the family `version` bump (done by _mutate).
- **Points:** always through the points_log ledger, never by editing member points directly.

## Gotchas

- The 4-person cap and membership checks live on the server; keep every rule there (the browser only sees its own family).
- Password minimum here is 6 characters (Form1.bridge).
- Theme.css is inlined by Anvil before the app loads; the spinner styles must stay there (see APP_MAKER/ANVIL_NOTES.md).

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit`. Don't edit `theme/assets/legal-kit.js`, `client_code/legal.py` or `server_code/legal_server.py` here: change `apps/funtoplan.json` there, run `python -I build.py funtoplan && python -I install.py funtoplan`, then commit and push here.
- The sign-up form in ftp.js keeps the consent tick box (`LegalKit.consentField()` / `consentChecked`).
