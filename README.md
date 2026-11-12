# Pre-Arrival Outreach Agent

A Claude Code skill for hotel operators. It scans your PMS for premium upcoming bookings, drafts a personalised welcome message in the operator's voice, and hands off to concierge once the guest replies — building the relationship before arrival and opening the door to concierge services (transfers, tours, restaurants).

Built on the **WAT framework** (Workflows, Agents, Tools): the skill file is the workflow, Claude Code is the agent, and your own scripts are the tools. This repo ships the workflow only. You supply the tools (see [What you need](#what-you-need)).

---

## What it does

- **Scans the PMS for qualifying upcoming guests** — by default, premium room types checking in 7-21 days from today (configurable)
- **Skips guests who should not get a message** — already contacted (matching subject in sent mail or drafts), cancelled bookings, bookings with no usable address
- **Drafts a personalised welcome** from one template with a room-type opening, a longer-stay line and a whole-property line — first name, exact dates, room name, arrival time and dietary questions, transfer offer, restaurant recommendation
- **Routes correctly** — direct bookings to the guest's email, OTA bookings to the relay address, from the right hotel inbox
- **Sends only after explicit approval** — every draft is shown to the operator first, with a list of who was skipped and why
- **Hands off high-value guests to concierge** — adds them to your VIP tracker, if you have one, so the next reply is picked up by the concierge agent

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
- **A guest got skipped as "already contacted".** The check looks for the subject line "Looking forward to welcoming you on …" in sent mail and drafts. Delete the stale draft, or tell Claude to include that guest.

---

## File structure

```
pre-arrival-outreach-agent/
├── README.md                                            # This file
├── .env.example                                         # Optional settings file for your own tool scripts
├── .gitignore
├── LICENSE
└── .claude/
    └── skills/
        └── pre-arrival-outreach/
            └── SKILL.md                                 # The skill definition
```

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
- [`concierge-agent`](https://github.com/th1-ai/concierge-agent) — picks up once the guest replies with requests
- [`arrival-time-check-agent`](https://github.com/th1-ai/arrival-time-check-agent) — chases missing arrival times closer to check-in
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — surfaces who needs outreach today
- [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) — the underlying draft-creation primitive

The full set of 21 agents is at [th1.ai/agent-stack](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
