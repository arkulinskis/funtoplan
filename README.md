# Fun To Plan

A shared family board for 2–4 people, built on [Anvil](https://anvil.works). Think of it as a small Jira with one epic, **FAMILY**: tasks, events and wants all go on one board. Everyone can add cards, acknowledge them, comment and chat. Doing tasks earns **brownie points**.

Works on phones (bottom tab bar, bottom sheets) and on desktop (side rail, 4-column board). The look is neumorphic: baby blue, soft grays and inky blacks, with an optional charcoal night mode.

## Features

- **One family board.** One person creates the board and the others join by scanning its **QR code** (or typing the 6-letter code). Up to 4 people.
- **Three card types.** Each card gets a key like `FAM-12`.
  - **Task**: assignee (or open to anyone), due date, priority, brownie point bounty.
  - **Event**: date, time, place, optional host. Family members tap "I'm in".
  - **Want**: a wish for the family or one person, with an optional link. Others can "+1" it.
- **Board.** Columns are To do → In progress → Review → Done. You can filter by type, by your own cards, or by bounties.
- **Bounties.** Add brownie points to a task. Anyone can claim an open bounty, and the points are paid when it's done.
- **Optional approval.** If a task needs approval, finishing it moves it to *Review*. Someone else in the family then approves it (and the points are paid) or sends it back with a note.
- **Recurring tasks.** Tasks can repeat daily, on weekdays, weekly, every 2 weeks or monthly. The next one is created when the current one is done. Turn on **Take turns** to rotate the next one through the family.
- **Acknowledge.** Every card shows who has seen it, who's coming, or who +1'd it.
- **Chat.** Family chat plus an activity feed ("Mom completed FAM-7 · +10 brownie points"). Typing `FAM-12` in a message links to that card. Each card also has its own comment thread.
- **Game elements.** Levels from Rookie to Mythic with a progress ring, a weekly family brownie goal, and a 7-day and all-time podium. A little confetti burst plays when points are earned.
- **Reopen safety.** Reopening a finished card takes back the points it paid.

## Getting it running in Anvil

1. In the Anvil editor choose **Clone from GitHub** and paste this repository URL. If you already linked this repo to an app, just pull the latest `master`.
2. Anvil creates the Data Tables from `anvil.yaml`: `families`, `members`, `items`, `messages`, `points_log`, plus `users`. If it asks, accept the schema changes.
3. Make sure the **Users** service allows email + password sign-up. It's already configured in `anvil.yaml`.
4. Press **Run**. To invite family on other phones, **publish** the app (Publish → share via public URL). QR codes point at whatever URL the app is opened from.

## How it's built

| Path | What it does |
| --- | --- |
| `server_code/api.py` | All business rules: membership, the 4-person cap, approvals, points ledger, recurring tasks, chat. A single callable, `ftp_api(action, payload_json)`, runs every change inside a transaction. |
| `client_code/Form1/` | Startup form. It mounts the UI and acts as the bridge: login, sign-up and logout use Anvil Users, and everything else calls `ftp_api`. |
| `theme/assets/ftp.js` | The interface, written in plain JavaScript with no framework: screens, board, sheets, QR rendering, polling every 8 seconds for family updates. |
| `theme/assets/ftp.css` | The neumorphic design system (light and night). |
| `anvil.yaml` | Services, table schema and the head HTML that loads fonts, the QR library and the assets above. |

All tables are server-only (`client: none`), so a browser can only see and change its own family's board through the server rules.
