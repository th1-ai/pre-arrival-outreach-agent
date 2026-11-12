# Pre-Arrival Outreach Agent

A Claude Code skill for hotel operators. It scans your PMS for premium upcoming bookings, drafts a personalised welcome message in the operator's voice, and hands off to concierge once the guest replies — building the relationship before arrival and opening the door to concierge services (transfers, tours, restaurants).

It works on request, and it can run on its own on a schedule. How much it does without you is one line in [`AUTONOMY.md`](AUTONOMY.md): report only (the default), prepare drafts, or send the standard welcome within strict limits. See [Run it on its own](#run-it-on-its-own).

Built on the **WAT framework** (Workflows, Agents, Tools): the skill file is the workflow, Claude Code is the agent, and your own scripts are the tools. This repo ships the workflow only. You supply the tools (see [What you need](#what-you-need)).

---

## What it does

- **Scans the PMS for qualifying upcoming guests** — by default, premium room types checking in 7-21 days from today (configurable)
- **Skips guests who should not get a message** — already contacted (matching subject in sent mail or drafts), cancelled bookings, bookings with no usable address
- **Drafts a personalised welcome** from one template with a room-type opening, a longer-stay line and a whole-property line — first name, exact dates, room name, arrival time and dietary questions, transfer offer, restaurant recommendation
- **Routes correctly** — direct bookings to the guest's email, OTA bookings to the relay address, from the right hotel inbox
- **Sends only after explicit approval** — every draft is shown to the operator first, with a list of who was skipped and why. The one exception is Level 3 in `AUTONOMY.md`, which you must switch on yourself
- **Remembers what it did** — one entry per run in `runs/LOG.md`, read by the next run so no guest is handled twice
- **Reports exceptions first** — every report starts with "Needs you"; a quiet run is a few lines
- **Hands off to concierge** — writes each contacted guest to `runs/handoff/pre-arrival-outreach-agent.md`, and adds high-value guests to your VIP tracker if you have one

It does not write to your PMS, and it does not invent room features, prices or availability.

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/overview) installed
- An email account you can search, draft in and send from with a command-line tool (Gmail through a Google Workspace CLI wrapper is the reference setup)
- A PMS with API access, and two small scripts of your own on top of it:
  - a **pre-arrival scanner** that returns upcoming reservations in a date window as JSON (name, email, booking source, room type, check-in date, nights, reservation ID, status)
  - a **reservation lookup** that returns one booking's current status

  The reference setup is Cloudbeds, but any PMS that can supply this data works.
- A **draft helper** script that creates an HTML email draft in a given inbox
- A concierge tracker (Google Sheet or equivalent) for VIP hand-off (optional)

The commands in the skill file show the shape each call takes. If your tools use other flags, edit the commands in `SKILL.md` to match.

---

## Quick start

1. **Clone the repo:**

   ```bash
   git clone https://github.com/th1-ai/pre-arrival-outreach-agent.git
   cd pre-arrival-outreach-agent
   ```

2. **Open Claude Code in the folder** (`claude`) and let it set the skill up with you:

   > "Read the README and set this skill up with me. Ask me for each placeholder value one at a time, then fill them in in `.claude/skills/pre-arrival-outreach/SKILL.md`. Ask which services in the message template we really offer and remove the ones we don't."

   Or do it by hand: replace the placeholders described in [Customising](#customising).

3. **Adapt the message template** in [`.claude/skills/pre-arrival-outreach/SKILL.md`](.claude/skills/pre-arrival-outreach/SKILL.md) to your property's voice, location and amenities.

4. **Optional: copy the env template** if your own tool scripts read their settings from `.env`:

   ```bash
   cp .env.example .env
   ```

   The skill does not read `.env`; it reads the values you set in `SKILL.md`.

5. **Trigger the skill:**

   > "Pre-arrival — who needs a welcome message?"

   or type `/pre-arrival-outreach`.

---

## Verify it works

1. Type `/` in Claude Code. `pre-arrival-outreach` is in the list.
2. Run this check. No placeholder is left when it prints nothing:

   ```bash
   grep -n '{{' .claude/skills/pre-arrival-outreach/SKILL.md
   ```

3. Run your scanner by hand once and confirm it prints JSON.
4. Trigger the skill. You get a list of drafts, a list of skipped guests, and a request for approval. Nothing is sent at this point.
5. For the first live run, approve one message addressed to yourself or a colleague before you approve guest messages.

### Troubleshooting

- **The skill is not in the `/` list.** Start Claude Code from the repo folder, so `.claude/skills/` is inside the project. Check that `SKILL.md` still starts with the `---` frontmatter block on line 1.
- **Claude stops and asks for a value.** A double-brace placeholder is still in `SKILL.md`. Fill it in.
- **A command fails with an unknown flag.** Your tool uses different flags from the reference commands. Edit the command in `SKILL.md`.
- **A guest got skipped as "already contacted".** The check looks for the reservation ID in `runs/LOG.md` and for the subject line "Looking forward to welcoming you on …" in sent mail and drafts. Delete the stale draft, or tell Claude to include that guest.
- **A scheduled run says a command was denied.** The command the agent ran does not match a rule in `.claude/settings.local.json`, or the guard hook blocked it. The report and `runs/LOG.md` give the reason.
- **Every run stops with "PAUSED".** `AUTONOMY.md` must have exactly one line that starts with `Level:`, with the value `0`, `1`, `2`, `3` or `PAUSED`.

---

## File structure

```
pre-arrival-outreach-agent/
├── README.md                                            # This file
├── AUTONOMY.md                                          # The autonomy level, limits and action table (you edit this)
├── .env.example                                         # Optional settings file for your own tool scripts
├── .gitignore
├── LICENSE
├── runs/
│   ├── README.md                                        # Format of the run log and the handoff file
│   └── .gitkeep                                         # LOG.md and handoff/ appear here; git ignores them
└── .claude/
    ├── settings.example.json                            # Example permissions + guard hook for unattended runs (inactive until you copy it)
    ├── hooks/
    │   └── autonomy-guard.py                            # Guard hook: checks drafts and sends against AUTONOMY.md
    └── skills/
        └── pre-arrival-outreach/
            └── SKILL.md                                 # The skill definition
```

---

## Run it on its own

The skill can run without you on a schedule. You decide how far it goes, in [`AUTONOMY.md`](AUTONOMY.md):

| `Level:` | A scheduled run does this |
|---|---|
| `PAUSED` | Nothing, scheduled or on request. It logs why. A missing file or an unknown value counts as `PAUSED` |
| `0` | Nothing on a schedule. The skill works only when you ask |
| `1` (default) | Scans, checks for earlier contact, and reports who is ready, with the proposed text. Writes only `runs/LOG.md` |
| `2` | Also creates the welcome emails as drafts, for you to read and send |
| `3` | Also sends the standard welcome, only for direct room bookings with no notes and no earlier contact, at most 5 per day, inside the send window. The first 5 are shadow-only (drafted, not sent) |

Replies to guests, changed text, OTA and whole-property sends, partner contact, PMS writes and anything about money are never automatic. The full table is in `AUTONOMY.md`.

### 1. Set the permissions

Unattended, nobody can answer a permission prompt, so the run needs an allowlist. [`.claude/settings.example.json`](.claude/settings.example.json) is an example. It is inactive as shipped. To use it:

```bash
cp .claude/settings.example.json .claude/settings.local.json
```

Then replace the placeholders in `.claude/settings.local.json` with the same values as in `SKILL.md` (the `sed` command in [Customising](#customising) works on this file too). Git ignores `settings.local.json`.

What the example does:

- **Allows** only your scanner, your lookup tool, the mailbox search, the draft helper, `date`, and file writes inside `runs/`.
- **Denies** `rm`, `curl`, `wget`, `git push`, reading `.env`, web access, and edits to `AUTONOMY.md`, the hook and the settings files, so the agent cannot raise its own level.
- **Does not allow the send command.** For Level 3, add it yourself: `"Bash({{EMAIL_CLI}} {{INBOX_BOOKINGS}} drafts-send *)"`, with your values.
- **Registers the guard hook** [`.claude/hooks/autonomy-guard.py`](.claude/hooks/autonomy-guard.py) (needs `python3`). Before each shell command it reads `AUTONOMY.md`. A draft below Level 2 or a send below Level 3 needs a human: you get a permission prompt in a session, and a scheduled run denies the call. At Level 3 it blocks sends outside the `Send window` and above the `Daily send cap`. `PAUSED` blocks drafts and sends.

Permission rules match the command text. If you start your tools another way (for example `python3 tools/pre_arrival_scan.py`), write the rules and the commands in `SKILL.md` the same way. The hook recognises drafts and sends by the patterns in the two lists at the top of the script; edit them if your commands differ from the reference ones. Deny rules and the hook stop the usual form of a command, not every possible form, so they are a safety net and not a sandbox.

### 2. Run it once by hand

```bash
cd /path/to/pre-arrival-outreach-agent
claude -p "/pre-arrival-outreach scheduled" --permission-mode dontAsk --max-turns 40 < /dev/null
```

- `-p` runs Claude Code without a session and prints the report.
- `/pre-arrival-outreach scheduled` starts the skill in scheduled mode: it asks nothing and puts open questions under "Needs you".
- `--permission-mode dontAsk` denies every tool call that is not in your allowlist, instead of waiting for an answer.
- `--max-turns 40` stops a run that does not end.

Read the report and `runs/LOG.md`. If a tool was denied, the report says which command; fix the rule or the command so they match.

### 3. Schedule it

Example for cron on macOS or Linux (`crontab -e`), every day at 08:00:

```
0 8 * * * cd /path/to/pre-arrival-outreach-agent && /path/to/claude -p "/pre-arrival-outreach scheduled" --permission-mode dontAsk --max-turns 40 < /dev/null >> runs/cron.log 2>&1
```

This is an example; adjust it to your machine. Cron has a short `PATH`, so use the full path of `claude` (`which claude`) and make sure your own tools are found too. The computer must be on and logged in to Claude Code at that time. Once a day is enough: the window is 7 to 21 days wide. Claude Code Desktop also has local scheduled tasks; see the [Claude Code docs](https://code.claude.com/docs/en/desktop-scheduled-tasks).

A scheduled run on a personal Pro or Max plan uses that plan's limits and is subject to Anthropic's usage policy; for a heavy or business-critical schedule, use an API key or a team plan.

### 4. Move up one level at a time

1. Run at the current level for at least 7 days.
2. Read `runs/LOG.md`. Check that every proposal (Level 1) or draft (Level 2) is one you would have sent unchanged, and that "Needs you" caught the cases you care about.
3. Change the one `Level:` line in `AUTONOMY.md`.
4. At Level 3, add the send rule to your allowlist, and read the 5 shadow entries before the first real send goes out.

To stop everything at once, set `Level: PAUSED`.

### What was tested

The hook script was run against allow and block cases for each level. With placeholder tools, a scheduled run was executed with Claude Code 2.1.323 at Level 1 and at Level 2, and the hook denied a send at Level 1 in a `claude -p` run. Level 3 sending and the cron line were not run against a real mailbox or scheduler: test them with a message to yourself first.

---

## Customising

The skill file uses placeholders so it can be adapted to any email + PMS stack and any property. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{INBOX_BOOKINGS}}` | Hotel-room guest inbox (used for outbound) | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property inbox (use the bookings inbox again if you have only one) | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Email-provider CLI wrapper | `gws` |
| `{{PMS_LOOKUP_TOOL}}` | Reservation lookup tool | `tools/lookup_guest.py` |
| `{{PRE_ARRIVAL_TOOL}}` | Pre-arrival scanner | `tools/pre_arrival_scan.py` |
| `{{DRAFT_NEW_TOOL}}` | New-email draft helper | `tools/create_draft_email.py` |
| `{{OPERATOR_NAME}}` | Name to sign off with | `Jane Doe` |
| `{{HOTEL_NAME}}` | Hotel name | `Your Hotel` |
| `{{NEAREST_AIRPORT}}` | Closest airport for international guests | `Edinburgh` |
| `{{LOCAL_RESTAURANT}}` | Your top local restaurant recommendation | `The Harbour Table` |
| `{{CONCIERGE_FORM_URL}}` | Whole-property concierge form (optional; delete that paragraph in `SKILL.md` if you have none) | `https://yourhotel.com/concierge` |

The reference setup uses scripts named `tools/lookup_guest.py`, `tools/pre_arrival_scan.py`, and `tools/create_draft_email.py`. These scripts are not part of this repo. Yours can live anywhere and use any names — the placeholders are the only thing the skill cares about.

The same placeholders appear in `.claude/settings.example.json`; fill them in your copy, `.claude/settings.local.json`, if you [run the skill on its own](#run-it-on-its-own).

To replace by hand (macOS `sed`; on Linux use `sed -i` without the `''`):

```bash
sed -i '' \
  -e 's|{{PRE_ARRIVAL_TOOL}}|tools/pre_arrival_scan.py|g' \
  -e 's|{{NEAREST_AIRPORT}}|Edinburgh|g' \
  -e 's|{{LOCAL_RESTAURANT}}|The Harbour Table|g' \
  .claude/skills/pre-arrival-outreach/SKILL.md
```

Fields in single braces, such as `{first_name}` and `{check_in_date}`, are filled per guest by the skill. Leave those as they are.

You will also want to **edit the message template** directly in `SKILL.md` to fit your property — the template is the brand voice, and it is meant to be tweaked. Remove any paragraph for a service you do not offer.

---

## How memory works

This skill leans on Claude Code's project memory. Claude Code keeps its own notes per project (auto memory; view and edit them with `/memory`), and you can tell it "remember that …" at any time. Rules that must apply in every session can also go in a `CLAUDE.md` file in the repo root. Useful patterns to record include:

- **Repeat guest preferences** — "guest X is gluten-free, always sits at the corner table"
- **Local intel** — "the restaurant has a 6-week wait in summer, suggest the bistro alternative"
- **Sending mistakes** — e.g. "always send to the OTA relay address for Booking.com guests, never a personal email found elsewhere"
- **Room facts** — the one feature worth mentioning for each premium room
- **Transfer logistics** — pricing, contact details for the local driver, etc.

Keep memory concise — one line per pattern.

---

## Related agents

This skill works well alongside:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts the original reply that turned into the booking
- [`concierge-agent`](https://github.com/th1-ai/concierge-agent) — picks up once the guest replies with requests. Handoff: `runs/handoff/pre-arrival-outreach-agent.md` lists who was contacted and what they were asked
- [`arrival-time-check-agent`](https://github.com/th1-ai/arrival-time-check-agent) — chases missing arrival times closer to check-in. The same handoff file shows who was already asked
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — surfaces who needs outreach today. The last entry of `runs/LOG.md` is the latest run summary, with "Needs you" first
- [`agent-notification-agent`](https://github.com/th1-ai/agent-notification-agent) — can tell you when a run has something under "Needs you"
- [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) — the underlying draft-creation primitive

The full set of 21 agents is at [th1.ai/agent-stack](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
