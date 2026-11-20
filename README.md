# Fun To Plan

A shared family board for 2–4 people, built on [Anvil](https://anvil.works). Think of it as a small Jira with one epic, **FAMILY**: tasks, events and wants all go on one board. Everyone can add cards, acknowledge them, comment and chat. Doing tasks earns **brownie points**.

Works on phones (bottom tab bar, bottom sheets) and on desktop (side rail, 4-column board). The look is the family fridge door: cards are sticky notes held up by magnets (tasks yellow, events blue, wants pink, done mint), bigger panels are paper sheets stuck on with washi tape, card numbers look like label-maker tape and headings are handwritten (Caveat over Figtree). Night mode is a dark slate fridge with the same notes.

## Features

- **Landing page.** Visitors who aren't logged in first see what the app does, how it works, the card types, brownie points and a short FAQ. Log in and sign up are one tap away. People who are already logged in go straight to their board.

- **One family board.** One person creates the board and the others join by scanning its **QR code** (or typing the 6-letter code). Up to 4 seats.
- **Kid seats (no phone needed).** On Family, "Add a kid" gives a child a seat with just a first name or nickname, an emoji and a colour: no account, no phone (children under 16 never get their own account). Kids count as one of the 4 seats and appear on the podium, in the assignee picker, in Take turns and on the Week page. On a kid's task the card's main button reads "🦖 Leo did it": a grown-up taps it, Leo gets the brownie points (through the points ledger), and the chat says "· marked by Mom". Open tasks show "Or a kid did it" chips. Kids' jobs due today land in the grown-ups' "Needs you".
- **Three card types.** Each card gets a key like `FAM-12`.
  - **Task**: assignee (or open to anyone), due date, priority, brownie point bounty.
  - **Event**: date, time, place, optional host. Family members tap "I'm in".
  - **Want**: a wish for the family or one person, with an optional link. Others can "+1" it.
- **Board.** Columns are To do → In progress → Review → Done. You can filter by type, by your own cards, or by bounties.
- **Bounties.** Add brownie points to a task. Anyone can claim an open bounty, and the points are paid when it's done.
- **Optional approval.** If a task needs approval, finishing it moves it to *Review*. Another grown-up then approves it (and the points are paid) or sends it back with a note. A board with one grown-up (plus kid seats) finishes its own approval tasks straight away, and a grown-up ticking off a kid's job counts as the check.
- **Recurring tasks.** Tasks can repeat daily, on weekdays, weekly, every 2 weeks or monthly. The next one is created when the current one is done. Turn on **Take turns** to rotate the next one through the family.
- **Acknowledge.** Every card shows who has seen it, who's coming, or who +1'd it.
- **Chat.** Family chat plus an activity feed ("Mom completed FAM-7 · +10 brownie points"). Typing `FAM-12` in a message links to that card. Each card also has its own comment thread.
- **Game elements.** Levels from Rookie to Mythic with a progress ring, a weekly family brownie goal, and a 7-day and all-time podium. A little confetti burst plays when points are earned.
- **Reopen safety.** Reopening a finished card takes back the points it paid.
- **This week (`#week`).** A 7-day planner opened from the Board ("Week") and Home ("Week view"): previous / next week, a person filter (Everyone or one person, kids too), what's still open from before, each day's events by time and tasks due that day, faded "↻ Leo's turn" notes for the coming turns of repeating tasks, a + per day that opens the editor with that date, and an Anytime list of undated jobs. Phones stack the days with today open; wide screens show 7 columns.
- **Phone calendar link.** "Add to my phone calendar" gives each person a private iCalendar feed (`/cal/<token>.ics`) that Apple Calendar (webcal), Google Calendar or Outlook subscribe to, with an "Only my jobs" switch, Copy and Reset (the old link stops working). Events from a week ago on and every open dated task, with alarms. Free, unlike the paid sync of other family apps.
- **Who's carrying the load?** A panel on Family: Planned (cards added, repeats not counted) / Did (tasks finished) / Checked (approvals, kids' jobs ticked off) per person over 30 days, the grown-ups' planning split ("Mom 72% · Dad 28%"), and when one grown-up planned 65% or more of at least 6 cards, a nudge with an **Own a job** (or **Hand over a job**) button that opens a weekly task owned end to end. Balanced months get "Nicely shared 🤝".

## Getting it running in Anvil

1. In the Anvil editor choose **Clone from GitHub** and paste this repository URL. If you already linked this repo to an app, just pull the latest `master`.
2. Anvil creates the Data Tables from `anvil.yaml`: `families`, `members`, `items`, `messages`, `points_log`, `cal_links`, `error_log`, plus `users`. If it asks, accept the schema changes ("The schema of the source code is correct").
3. Make sure the **Users** service allows email + password sign-up. It's already configured in `anvil.yaml`.
4. Press **Run**. To invite family on other phones, **publish** the app (Publish → share via public URL). QR codes point at whatever URL the app is opened from.

## How it's built

| Path | What it does |
| --- | --- |
| `server_code/api.py` | All business rules: membership, the 4-seat cap (kid seats included), approvals, points ledger, recurring tasks, chat, calendar links. A single callable, `ftp_api(action, payload_json)`, runs every change inside a transaction. |
| `server_code/calendar_feed.py` | The private phone-calendar feed: RFC 5545 text at `/cal/<token>.ics` (and `/_/api/cal/<token>.ics`). |
| `client_code/` | Native Anvil Forms: `startup.py` + `router.py` (addresses `#home`, `#board`, `#week`, `#chat`, `#family` ...), `ftp.py` (the client data layer: one server API, 8-second sync, board rules, week + fair-share maths), `Layouts/Shell`, `Pages/`, `Items/`, `Dialogs/` (bottom sheets on phones), `Components/ProfilePicker`. |
| `theme/assets/app.css` | The "fridge door" design system (light and night). `ftp-fx.js` is the only JavaScript engine: confetti, invite QR, camera scanner, copy. |
| `tools/` | `check.py` (Anvil's validator, JS parse, asset hashes, server tests), `ui_test.py` (the real app in the open-source Anvil App Server in Docker, driven by headless Chrome). |
| `anvil.yaml` | Services, table schema and the head HTML that loads fonts, the QR library and the assets above. |

All tables are server-only (`client: none`), so a browser can only see and change its own family's board through the server rules.

<!-- libraries:start -->
## Libraries and outside services

What this project uses besides its own code. Generated by `APP_MAKER/tools/libraries.py`; to change it, edit `APP_MAKER/libraries/catalog.py` and re-run the script.

| Name | How it gets in | Used here for |
|---|---|---|
| [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) 1.4.4 | Loaded from a CDN | Makes QR codes from a piece of text or a link. |
| [YouTube embeds](https://developers.google.com/youtube/player_parameters) | Outside web service | Plays a YouTube video inside the page (the privacy-friendlier youtube-nocookie address). |
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | Caveat, Figtree, JetBrains Mono |

**Built into the browser:** Camera, microphone and screen, BarcodeDetector, Web Share, localStorage, Clipboard.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil Email, Anvil JS bridge (anvil.js), Anvil Secrets, Anvil Users, Anvil Google service, Anvil HTTP, Anvil timezones (anvil.tz).

**Build and test tools (not shipped):** axe-core, Node.js, Headless Chrome (DevTools Protocol), PyYAML.

<!-- libraries:end -->
