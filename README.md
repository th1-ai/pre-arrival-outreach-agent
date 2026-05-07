# Pre-Arrival Outreach Agent

A Claude Code skill for hotel operators. It scans your PMS for premium upcoming bookings, drafts a personalised welcome message in the operator's voice, and hands off to concierge once the guest replies — building the relationship before arrival and driving concierge revenue (transfers, tours, restaurants).

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

---

## What it does

- **Scans the PMS for qualifying upcoming guests** — by default, premium room types checking in 7-21 days from today (configurable)
- **Skips guests who've already been contacted** by searching the sent folder for a matching subject line
- **Drafts a personalised welcome** using one of the templates (suite, premium room, longer-stay addition) — first name, exact dates, room name, dietary question, transfer offer, restaurant recommendation
- **Routes correctly** — direct bookings to the guest's personal email, OTA bookings to the relay address, all from the right hotel inbox
- **Sends only after explicit approval** — every draft is shown to the operator first
- **Hands off high-value guests to concierge** — adds them to a VIP tracker so the next reply is picked up by the concierge skill

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- One or more email accounts you can read/draft programmatically (Gmail via the Google Workspace CLI is the reference setup)
- A PMS with API access — the skill calls a `lookup_guest`-style tool and a pre-arrival scanner that returns upcoming reservations within a date window. The reference setup is Cloudbeds, but any PMS with these endpoints works.
- A concierge tracker (Google Sheet or equivalent) for VIP hand-off (optional)

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/pre-arrival-outreach-agent.git
   cd pre-arrival-outreach-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/skills/pre-arrival-outreach/SKILL.md`](.claude/skills/pre-arrival-outreach/SKILL.md)** — replace the placeholders described in [Customising](#customising), and adapt the message templates to your property's voice, location, and amenities.

4. **Open in Claude Code** and trigger the skill:

   > "Pre-arrival — who needs a welcome message?"

---

## File structure

```
pre-arrival-outreach-agent/
├── README.md                                            # This file
├── .env.example                                         # Inboxes, PMS auth, sign-off identity
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
| `{{INBOX_PRIMARY}}` | B2B / supplier inbox | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Hotel-room guest inbox (used for outbound) | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property inbox | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Email-provider CLI wrapper | `gws` |
| `{{PMS_LOOKUP_TOOL}}` | Reservation lookup tool | `tools/lookup_guest.py` |
| `{{PRE_ARRIVAL_TOOL}}` | Pre-arrival scanner | `tools/pre_arrival_scan.py` |
| `{{DRAFT_NEW_TOOL}}` | New-email helper | `tools/create_draft_email.py` |
| `{{OPERATOR_NAME}}` | Name to sign off with | `Jane Doe` |
| `{{HOTEL_NAME}}` | Hotel name | `Your Hotel` |
| `{{NEAREST_AIRPORT}}` | Closest airport for international guests | `Edinburgh` |
| `{{LOCAL_RESTAURANT}}` | Your top local restaurant recommendation | `The Witchery` |
| `{{CONCIERGE_FORM_URL}}` | Optional whole-property concierge form | `https://yourhotel.com/concierge` |

The reference setup uses scripts named `tools/lookup_guest.py`, `tools/pre_arrival_scan.py`, and `tools/create_draft_email.py`. Yours can live anywhere and use any names — the placeholders are the only thing the skill cares about.

```bash
sed -i '' \
  -e 's|{{PRE_ARRIVAL_TOOL}}|tools/pre_arrival_scan.py|g' \
  -e 's|{{NEAREST_AIRPORT}}|Edinburgh|g' \
  -e 's|{{LOCAL_RESTAURANT}}|The Witchery|g' \
  .claude/skills/pre-arrival-outreach/SKILL.md
```

You will also want to **edit the message templates** directly in `SKILL.md` to fit your property — the templates are the brand voice, and they're meant to be tweaked.

---

## How memory works

This skill leans on Claude Code's per-project memory. Useful patterns to record include:

- **Repeat guest preferences** — "guest X is gluten-free, always sits at the corner table"
- **Local intel** — "the restaurant has a 6-week wait in summer, suggest the bistro alternative"
- **Sending mistakes** — e.g. "always send to the OTA relay address for Booking.com guests, never the personal email scraped from the booking"
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

---

## License

MIT — see [LICENSE](LICENSE).
