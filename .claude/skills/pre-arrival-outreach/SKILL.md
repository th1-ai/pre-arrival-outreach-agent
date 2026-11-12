---
name: pre-arrival-outreach
description: Finds upcoming premium bookings in the pre-arrival window (default 7-21 days before check-in), skips guests already contacted, and drafts a personalised welcome email for each one for the operator to approve. Use when the operator says "pre-arrival", "welcome messages", "who needs a welcome message", asks to reach out to upcoming guests, or during the morning routine to flag guests entering the outreach window.
---

# Skill: Pre-Arrival Outreach

> **Template note:** Placeholders in double braces are set once per property (see the Customising table in `README.md`). `{single_brace}` fields are filled per guest from the PMS. If any double-brace placeholder is still present in this file when the skill runs, stop and ask the operator for the missing value. Do not guess it.

## Purpose

Identify upcoming premium bookings and prepare personalised pre-arrival welcome messages. This builds the guest relationship before arrival, opens the door to concierge services (transfers, tours, restaurants), and collects arrival time and dietary needs early.

The commands below show the shape of each call. The operator supplies the tools; if their flags differ, follow the tool's own `--help` and tell the operator so this file can be corrected.

## Workflow

### Step 1: Scan for qualifying guests

```bash
{{PRE_ARRIVAL_TOOL}} --format json
```

**Qualifying criteria (default):**
- Room type: premium tiers only (e.g. Suite, Sea-View King)
- Check-in: 7-21 days from today
- Any booking source (direct, OTA, phone)

Use `--all-rooms` to include standard rooms and `--days-min` / `--days-max` to adjust the window.

For each guest you need: name, email, booking source, room type, check-in date, number of nights, reservation ID and status.

- **If the scanner fails or returns something unreadable:** stop and report the error. Do not build a guest list from memory or from the inbox.
- **If it returns no guests:** say so and stop.

### Step 2: Filter the list

Drop a guest, and say why in the report, when:

1. **The booking is not active.** If the scanner output has no status, or the scan is not from today, confirm with `{{PMS_LOOKUP_TOOL}} <reservation_id>`. Never write to a cancelled or no-show booking.
2. **They were already contacted.** Check sent mail and existing drafts:

   ```bash
   {{EMAIL_CLI}} {{INBOX_BOOKINGS}} messages-list --query "in:sent to:<guest_email> subject:welcoming" --max 5
   {{EMAIL_CLI}} {{INBOX_BOOKINGS}} messages-list --query "in:drafts to:<guest_email> subject:welcoming" --max 5
   ```

   For whole-property bookings, run the same check on `{{INBOX_RENTALS}}`. If the guest has already written to the hotel about their stay, do not send the standard template: flag the thread to the operator instead.
3. **There is no usable address.** No email on the booking, or an OTA booking with no relay address. List these for the operator; do not search for the guest's personal email elsewhere.

One guest with several rooms or back-to-back reservations gets **one** message covering the whole stay.

### Step 3: Draft the messages

Pick the opening by room type (see Message Template) and fill the per-guest fields from the PMS data:

- First name, exact check-in date, number of nights, room name
- Longer-stay line for 5+ nights
- Concierge form line for whole-property bookings only

Use only facts that come from the PMS record, this file, or project memory. Do not invent room features, prices, availability, driver or tour details. If a fact is missing, leave the sentence out.

### Step 4: Present to the operator for approval

Present every draft, then a short summary:

```
Pre-arrival outreach: <date>
Window: <days-min>-<days-max> days, <room filter>

Ready for approval (<n>)
1. <Guest name> | <room> | <check-in>, <nights> nights | <source>
   From: <inbox>  To: <address> (<direct / OTA relay>)
   Subject: <subject>
   <full message text>

Skipped (<n>)
- <Guest name>: <already contacted on <date> / cancelled / no address / has an open thread>

Needs your decision (<n>)
- <anything unclear: missing first name, unknown room type, conflicting data>
```

Then wait. **Never send without the operator's explicit approval.** Approval covers only the guests the operator names, with the text they saw. If the operator edits a message, show the edited version before sending it.

### Step 5: Create drafts and send approved messages

```bash
# Create the draft in the sending inbox (see Sending Rules)
{{DRAFT_NEW_TOOL}} --from {{INBOX_BOOKINGS}} --to "<guest_email>" \
  --subject "Looking forward to welcoming you on <date>" --body "<html>" --html

# Send only after approval
{{EMAIL_CLI}} {{INBOX_BOOKINGS}} drafts-send --id "<draft_id>"
```

If the operator prefers to send by hand, stop after creating the drafts and say which inbox they are in. If a send fails, report it and do not retry more than once; a duplicate welcome is worse than a late one.

### Step 6: Hand off to concierge

After sending, for suite guests and any guest the operator marks as high-value:

- Add them to the concierge / VIP tracker if the operator has one. Ask where it is the first time; if there is none, skip this.
- Record in project memory anything worth keeping (see `README.md`, "How memory works").
- Tell the operator who was handed off. When the guest replies with requests, the concierge agent takes over.

This skill does not write to the PMS.

## Message Template

> Adapt the wording to your property's voice, location and amenities. **Delete any paragraph for a service you do not offer** (private driver, excursions, guided tours, breakfast): the message must not promise something the hotel cannot deliver.

**Opening line by room type:**

| Room type | Opening sentence after "Thank you for choosing to stay with us" |
|---|---|
| Suite | `we're delighted to welcome you on {check_in_date} for {nights} nights in our {room_name}. It's a beautiful room and I think you'll love it.` |
| Other premium room | `we're looking forward to welcoming you on {check_in_date} for {nights} nights in our {room_name}.` Add `It's a lovely room with {key_feature}.` only when the feature is in the PMS room description or project memory. |
| Standard room (only with `--all-rooms`) | `we're looking forward to welcoming you on {check_in_date} for {nights} nights.` Keep the tone warm but plain. |

**Body:**

```
Hi {first_name},

Thank you for choosing to stay with us — {opening sentence from the table}

To make sure everything is perfectly arranged for your arrival, a few quick questions:

Arrival time — Could you let us know roughly when you'll be arriving so we can have everything ready for you?

Airport transfer — If you're flying into {{NEAREST_AIRPORT}}, we can arrange a private driver to collect you. Just let us know your flight details and we'll take care of it.

Getting around — If you won't have a car, our driver can also take you on excursions during your stay.

Breakfast — We serve a fresh breakfast each morning. Do you have any dietary requirements or preferences we should know about?

We'd also love to help plan your evenings and excursions:

{{LOCAL_RESTAURANT}} — A truly exceptional dining experience near us. Tables fill up quickly, so if you're interested, let us know and we'll request a table for you straight away.

Guided tours — We can arrange a private tour of the area's highlights at your convenience.

Just let us know what appeals to you and we'll take care of everything.

Looking forward to welcoming you,
{{OPERATOR_NAME}}
{{HOTEL_NAME}}
```

**Longer stay (5+ nights)** — add after the restaurant paragraph:

```
With a {nights}-night stay, we'd definitely recommend fitting in at least one dinner there.
```

**Whole-property bookings only** — add before the closing line:

```
To make your stay easy to plan, we've put together a short concierge form where you can tell us everything you'd like us to organise — arrival, transfers, dining, tours, dietary needs: {{CONCIERGE_FORM_URL}}
```

Never send the form link to individual hotel-room guests. If the property has no such form, leave the paragraph out.

## Subject Line

Always use: `Looking forward to welcoming you on {check_in_date_formatted}`

`{check_in_date_formatted}` is day + month, no year, e.g. "24 April". The already-contacted check in Step 2 searches for this subject, so do not vary it.

## HTML Formatting

When creating the email via `{{DRAFT_NEW_TOOL}} --html`, wrap each paragraph in `<p>` tags and bold the labels with `<b>`:

```html
<p>Hi {first_name},</p>
<p>Thank you for choosing to stay with us...</p>
<p><b>Arrival time</b> — Could you let us know...</p>
```

## Sending Rules

| Booking | Send from | Send to |
|---|---|---|
| Direct room booking (website, phone, walk-in) | `{{INBOX_BOOKINGS}}` | Guest's email on the booking |
| OTA room booking (Booking.com, Expedia, others) | `{{INBOX_BOOKINGS}}` | The OTA relay address on the booking (e.g. `xxx@guest.booking.com`) |
| Whole-property booking | `{{INBOX_RENTALS}}` | Guest's email on the booking |

For OTA bookings, use the relay address even if a personal email appears elsewhere: the guest gave that address to the OTA, not to the hotel. Relay channels can strip links and HTML, so keep OTA messages free of links.

## Rules

- **Approval first.** No message leaves without the operator's explicit approval of that message.
- **No double contact.** Always run the Step 2 checks before drafting.
- **No invented facts.** Room features, prices, availability, providers and opening times come from the PMS, this file or project memory, or they are left out.
- **Dietary question is mandatory.** It feeds breakfast planning, so keep it in every message (unless the property serves no breakfast).
- **Don't oversell standard rooms.** Enthusiastic room language is for premium tiers only.
- **Include the local restaurant recommendation** and offer to request a table, never state that a table is available.
- **Country context.** Mention the airport transfer for guests whose booking shows a foreign country or no country; for clearly local guests, drop that paragraph. Don't assume a hire car.
- **Language.** Write in English unless the operator has said otherwise for this guest or market.
- **Tone:** warm, personal, luxury-but-approachable. No emojis. Anticipate needs.
