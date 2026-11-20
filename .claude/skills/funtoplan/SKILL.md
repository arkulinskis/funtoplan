---
name: funtoplan
description: Context, workflow and recipes for Fun To Plan (funtoplan.com), the user's Anvil family board for up to 4 seats (tasks, events and wants on one board, QR-code join, kid seats without phones, a 7-day Week planner with a private phone-calendar feed, chat, recurring tasks that take turns, bounties, brownie points and a "who's carrying the load" panel), with a "fridge door" look (sticky notes, magnets, washi tape, handwritten headings). Native Anvil Forms. Load this before any feature request, bug fix, restyle or deploy for Fun To Plan.
---

# Fun To Plan: working on the app

**What it is:** a small Jira with one epic, **FAMILY**. One person creates the family board; others join by scanning its
**QR code** (or typing the 6-letter code). Up to **4 seats**, and a seat is either a grown-up's account or a **kid seat**
(no account, no phone: a first name or nickname, an emoji, points). Cards (`FAM-12`) are **tasks** (assignee or open, due
date, priority, brownie-point bounty, optional approval, recurrence with "take turns"), **events** (date, time, place,
"I'm in") and **wants** (+1). Columns To do → In progress → Review → Done. Chat with an activity feed (`FAM-12` links the
card), card comments, levels (Rookie → Mythic), weekly family goal, podium, confetti. **This week** (`#week`) shows the
family week and gives each person a private **calendar feed** for their phone. **Who's carrying the load?** on Family shows
Planned / Did / Checked per person. A landing page explains it all before log in.

**Where it lives:**
- Repo **github.com/arkulinskis/funtoplan**, branch `master`; Anvil pulls master. Live: **https://funtoplan.com**.
- This folder (`funtoplan-forms`) **is** the Anvil repo ("git" layout), **native Anvil Forms** since 2026-11-07 (the
  old JavaScript version with `Form1`, `ftp.js`, `ftp.css` and `tools/preview` is gone).
- **Read `APP_MAP.md` first** (generated code map: pages, server actions with line numbers, tables, who calls what), and
  ask the code graph (`graphify query "..."` from this folder) before reading many files. README.md lists the features.

**What the user wants:** mobile first (bottom tab bar 2 + the red + magnet + 2, bottom sheets) and good on desktop (side
rail, 4 board columns). The **fridge door** look (chosen 2026-10-31; no neumorphic soft shadows): warm enamel background,
cards as sticky notes held by round magnets (tasks yellow, events blue, wants pink, done mint, slight tilt), big panels as
paper with washi tape, `FAM-12` keys as black label-maker tape (red tape on dark paper at night), handwritten headings in
Caveat over Figtree, JetBrains Mono for keys/codes, glossy magnet buttons, the join code as fridge alphabet magnets.
Night = dark slate fridge; notes keep pastel paper + dark ink. English only. Claude deploys (push to master).

## Workflow

1. `python -I C:\Users\arkvi\Documents\CLAUDE\APP_MAKER\tools\apps_status.py funtoplan -v`; `git pull --ff-only` for
   Anvil's "Edited ..." commits; never touch someone else's uncommitted work.
2. Edit the files here (APP_MAP.md says where). Follow APP_MAKER/design/README.md for anything people see.
3. `python tools/check.py` → `ALL CHECKS PASSED` (Anvil's validator on every template and Python file, `node --check`,
   asset hashes, server tests in `tools/testing/test_server.py` on the strict Anvil mock).
4. `python -I tools/ui_test.py` → `ALL UI TESTS PASSED`: the real app in the Anvil App Server (Docker container
   `funtoplan-dev`, port from `ui_test.py`), driven by `tools/ui/smoke.js` (signs up, starts a board, walks every page
   incl. #week, opens a card, adds one). Server edits need `--restart`; `--stop` when done; `--shots DIR` for screenshots.
5. After theme/asset changes: `python tools/assets.py` refreshes the `?v=` hashes, but it rewrites anvil.yaml in block
   style: keep Anvil's compact style and change only the hashes (see APP_MAKER/ANVIL_NOTES.md).
6. Commit only your files as arkulinskis (noreply address) with the Co-Authored-By line; `git push origin master`.
7. New tables/columns: `anvil.yaml → db_schema`; the user accepts the Schema Mismatch alert ("The schema of the source
   code is correct"). Then refresh the code map (`APP_MAKER/standard/app_map.py funtoplan`) and the graph.

## Architecture

```
server_code/api.py         ALL rules. One callable ftp_api(action, payload_json) -> JSON string:
                           QUERIES (bootstrap, sync, preview_join, item_detail, cal_link) and MUTATIONS (create_family,
                           join_family, save_item, complete, approve, reject, reopen, move, claim, ack, delete_item, comment,
                           send_message, update_profile, update_family, regen_code, remove_member, leave_family, add_kid,
                           update_kid), each mutation inside a transaction (_mutate) that bumps the family `version`.
                           Replies {"ok": true, "data"} or {"ok": false, "error", "code"} (ApiError).
server_code/calendar_feed.py  the phone-calendar feed (RFC 5545) at /cal/<token>.ics (route) + /_/api/cal/<token>.ics
server_code/AppStatus.py, AdminAccess.py, KeepAlive.py, SchemaCheck.py   APP_MAKER standard (status report, admins, session ping)
server_code/seo_routes.py, legal_server.py   kit files (APP_MAKER/seo, APP_MAKER/legal-kit): don't edit here
client_code/startup.py     bootstrap -> router.start()
client_code/router.py      #name/arg -> page Form (PAGES, _form, NAV); #join=ABC123 invite links; sign-in/board rules
client_code/ftp.py         the client data layer: api()/run(), the board in S["st"], 8-s sync + listen()/notify(), board rules
                           (eff, needs_you, grownups/kids), dates, week maths (week_start, advance, ghost_turns), load_share,
                           and opening the sheets (open_detail, open_editor(preset=...), open_kid_seat, open_cal_link ...)
client_code/Layouts/Shell  rail + tab bar + footer; redrawn by refresh(page) and on every sync
client_code/Pages/         Landing, Auth, Start, Home, Board, Week, Chat, Family
client_code/Items/         Card, DoneRow, ChatRow, Comment, MemberRow, ShareRow, WeekDay, WeekEntry, Avatar, Choice, NavLink
client_code/Dialogs/       Detail (card sheet), Editor, KidSeat, CalLink, FamilySettings, Invite, Profile, Prompt, Scan
client_code/Components/ProfilePicker   name + emoji + magnet colour (start page, profile, kid seats)
theme/assets/app.css       the fridge-door design system (tokens on :root, night = html.ui-dark)
theme/assets/ftp-fx.js     the only JS engine: confetti (FTP.burst), invite QR, camera scanner, copy
theme/assets/app-kit.js    UI helpers + the icon table (UI.ICONS -> tools/build_icons.py -> icons.css)
theme/assets/theme.css     Anvil's startup spinner (a sticky note swinging from a magnet)
```

**Tables** (all server-only): `families` (join_code, version, next_seq, weekly_goal), `members` (family, user (None for a
kid seat), display_name, avatar, color, role owner/member/kid, points, active, joined), `items` (the cards), `messages`
(chat, activity, comments), `points_log` (the ledger), `cal_links` (family, member, token, created, last_fetch),
`error_log`, `users` (+ legal_*, is_admin).

## Product rules (keep them)

- **Kid seats** are `members` rows with `user=None, role="kid"`: only a first name/nickname, emoji, colour and points (the
  Terms bar under-16 accounts; a kid seat is "through the guardian's account"). They count toward the 4 seats, show in
  the podium, assignee picker, Take turns and Week. A grown-up finishes a kid's task with `complete` / `claim` +
  `for_member=<kid id>` (must be an active kid seat in this family, else ApiError): the kid gets the points through the
  ledger, the grown-up is recorded as `approved_by` (shown as "Checked"), the activity line ends "· marked by Mom", and
  there is no Review step. Wants can't be done for kids.
- **Approvals** count grown-ups only (`_grownups`): with one grown-up their own approval tasks finish straight away and
  `approve` doesn't block self-approval; with 2+ someone else approves. Mirror any change in `ftp.needs_you` and
  `Dialogs/Detail._actions`.
- **Leaving:** ownership goes to the first grown-up by join order, never a kid; if no grown-up is left, the kid seats are
  closed too. `_release` also deletes the seat's calendar links.
- **Calendar feed:** one `cal_links` row per seat (`cal_link` query, own transaction, no version bump); token = uuid4 hex;
  `reset` makes a new one (old URL -> 404); the feed reads only that seat's family, never notes/chat/emails; a seat that
  left or was removed gets 404; `?mine=1` = family events + only that person's tasks. Before the schema is accepted,
  `cal_link` answers code `nocal` with a friendly message and nothing else breaks. The client builds the URL from
  `window.location.origin + path`, so it follows the domain people use.
- **Week page:** built only from `ftp.st()` (open cards + 30 days of done ones). Weeks start on Monday. Events always show;
  the person filter applies to tasks and coming turns. `ftp.ghost_turns` must stay in step with `api._advance` /
  `_spawn_next` / `_rotate_assignee` (rotation through `active_members()` in join order, kids included).
- **Fair share** (`ftp.load_share`): Planned = cards created in the last 30 days with `occurrence == 1`; Did = tasks done or
  in review; Checked = `approved_by`. The nudge shows at >= 65% of >= 6 grown-up-planned cards; kids show Did only.
- **Points:** always through the points_log ledger, never by editing member points directly.

## Recipes

- **New action:** `a_<name>(p)` (query) or `m_<name>(p, user, me, family)` (mutation) in api.py, register it in QUERIES /
  MUTATIONS, call it with `ftp.run("<name>", payload)` (or `ftp.api` when the form handles errors itself). Raise
  `ApiError("friendly text")` for user errors. Add a server test.
- **New page:** `client_code/Pages/<Name>/` (form_template.html with `<anvil-form layout="Fun_To_Plan.Layouts.Shell">` +
  `__init__.py` with `refresh()`, `ftp.listen` in show / `unlisten` in hide), register in router.py `PAGES` + `_form()`
  (+ `NAV` only if it belongs in the 4-item menu).
- **New sheet:** `client_code/Dialogs/<Name>/` with the `.ftp-dlg` markup (sheet-grip, sheet-head, sheet-body, sheet-foot),
  closed with `raise_event("x-close-alert", value=...)`, opened through `ftp._sheet(Form())`.
- **New icon:** add it to `UI.ICONS` in app-kit.js, run `python -I tools/build_icons.py`, use `ic-<name>`.
- **A new pastel "note" surface:** add its selector to the night ink list at the top of app.css
  (`:root, .ui-dark :is(.card, ...)`), or its text turns light-on-pastel at night.

## Gotchas

- Anvil Buttons render an empty icon `<i>`; app.css hides it. Labels add padding; templates mostly use `anvil:dom-node`
  + `ftp.text()` for changing text.
- Skulpt: comprehension variables leak (never name one `t`, `_` or after an import); no `nonlocal`; no `typing`. For
  dynamic `dom_nodes[...]` keys or attributes that start as None, pass them through `ftp.loose()` for the validator.
- `anvil:name` on a template's root element isn't seen by the validator: item roots get a class instead.
- **Continue with Google**: `login_with_google()` returns None for someone without an account; auth.py then calls
  `signup_with_google()` (the sign-up view needs the Privacy & Terms tick first).
- Theme.css is inlined by Anvil before the app loads; the spinner styles must stay there.
- Card colour comes from the `k-<kind>` class; tilt and magnet colour from the card's position in the list.
- The App Server keeps accounts made by tests in the Docker volume `funtoplan-data`.

## Privacy & Terms (legal kit)

From `C:/Users/arkvi/Documents/CLAUDE/APP_MAKER/legal-kit`. Don't edit `theme/assets/legal-kit.js`, `client_code/legal.py`
or `server_code/legal_server.py` here: change `apps/funtoplan.json` there, run `python -I build.py funtoplan && python -I
install.py funtoplan`, then commit and push here. Kid seats and the calendar link are described there (2026-11-20).
The sign-up form keeps the consent tick box (`legal.consent_field()` / `legal.consent_ok()`).
