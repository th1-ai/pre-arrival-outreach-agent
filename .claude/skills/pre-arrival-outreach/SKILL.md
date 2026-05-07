# Skill: Pre-Arrival Outreach

> **Template note:** Replace `{{INBOX_*}}`, `{{EMAIL_CLI}}`, `{{PMS_LOOKUP_TOOL}}`, `{{PRE_ARRIVAL_TOOL}}`, `{{OPERATOR_NAME}}`, `{{HOTEL_NAME}}`, `{{CONCIERGE_FORM_URL}}` and similar placeholders with the wrappers and identifiers your setup uses. See `README.md` for guidance.

## Trigger

Use proactively when:
- Operator asks to check for upcoming guests to contact
- During the morning routine, to flag guests approaching the outreach window
- Operator says "pre-arrival", "welcome messages", "reach out to upcoming guests"

## Purpose

Proactively identify upcoming premium bookings and send personalised pre-arrival welcome messages. This builds the guest relationship before arrival, drives concierge revenue (transfers, tours, restaurants), and sets the tone for a luxury experience.

## Workflow

### Step 1: Scan for qualifying guests

Run the scanner to find guests checking in within the outreach window (default: 7-21 days out):

```bash
{{PRE_ARRIVAL_TOOL}} --format json
```

**Qualifying criteria (default):**
- Room type: premium tiers only (e.g. Suite, Sea-View King)
- Check-in: 7-21 days from today
- Any booking source (direct, OTA, walk-in)

Use `--all-rooms` to include standard rooms, `--days-min` / `--days-max` to adjust the window. Tune the qualifying criteria to your property's room mix.

### Step 2: Check who's already been contacted

Before drafting, check whether you've already sent a pre-arrival message:

```bash
# Search the sent folder for prior outreach to this guest
{{EMAIL_CLI}} {{INBOX_BOOKINGS}} messages-list --query "in:sent to:<guest_email> subject:welcoming" --max 5
```

Skip any guest who already has a sent message matching this pattern.

### Step 3: Draft messages using templates

Use the appropriate template below based on room type. Personalise each message with:
- Guest's first name
- Exact check-in date
- Number of nights
- Room description
- Country-appropriate references (nearest airport for international guests)

**Always add the dietary requirements question** — this is operationally valuable for breakfast planning.

### Step 4: Present to the operator for approval

Show all drafted messages in a clear format:
- Guest name, room, dates, email, source
- The full message text
- Whether it goes via OTA relay or direct email

**Never send without the operator's explicit approval.**

### Step 5: Send approved messages

```bash
# Direct bookings — send from {{INBOX_BOOKINGS}}
{{DRAFT_NEW_TOOL}} --account stays --to "<guest_email>" \
  --subject "Looking forward to welcoming you on <date>" --body "<html>" --html

# Send the draft after approval
{{EMAIL_CLI}} {{INBOX_BOOKINGS}} drafts-send --id "<draft_id>"
```

### Step 6: Hand off to concierge

After sending, if the guest is high-value (above your threshold, or a suite guest):
- Add to your VIP guest tracker
- Update project memory
- The concierge agent will pick up from here when the guest replies

## Message Templates

> Adapt these to your property's voice, location, and amenities. Replace placeholders like `{{HOTEL_NAME}}`, `{{NEAREST_AIRPORT}}`, `{{LOCAL_RESTAURANT}}` with values that fit your area.

### Suite Guest Template

```
Hi {first_name},

Thank you for choosing to stay with us — we're delighted to welcome you on {check_in_date} for {nights} nights in our {suite_name}. It's a beautiful room and I think you'll love it.

To make sure everything is perfectly arranged for your arrival, a few quick questions:

Arrival time — Could you let us know roughly when you'll be arriving so we can have everything ready for you?

Airport transfer — If you're flying into {{NEAREST_AIRPORT}}, we can arrange a private driver to collect you. Just let us know your flight details and we'll take care of it.

Getting around — If you won't have a car, our driver can also take you on excursions during your stay.

Breakfast — We serve a fresh breakfast each morning. Do you have any dietary requirements or preferences we should know about?

We'd also love to help plan your evenings and excursions:

{{LOCAL_RESTAURANT}} — A truly exceptional dining experience near us. Tables fill up quickly, so if you're interested, let us know and we'll book a table for you straight away.

Guided tours — We can arrange a private tour of the area's highlights at your convenience.

Just let us know what appeals to you and we'll take care of everything.

Looking forward to welcoming you,
{{OPERATOR_NAME}}
{{HOTEL_NAME}}
```

### Premium Room Template

```
Hi {first_name},

Thank you for choosing to stay with us — we're looking forward to welcoming you on {check_in_date} for {nights} nights in our {room_name}. It's a lovely room with {key_feature}.

To make sure everything is perfectly arranged for your arrival, a few quick questions:

Arrival time — Could you let us know roughly when you'll be arriving so we can have everything ready for you?

Airport transfer — If you're flying into {{NEAREST_AIRPORT}}, we can arrange a private driver to collect you. Just let us know your flight details and we'll take care of it.

Getting around — If you won't have a car, our driver can also take you on excursions during your stay. The area is stunning and there's a lot to discover.

Breakfast — We serve a fresh breakfast each morning. Do you have any dietary requirements or preferences we should know about?

We'd also love to help plan your evenings and excursions:

{{LOCAL_RESTAURANT}} — A truly exceptional dining experience near us. Tables fill up quickly, so if you're interested, let us know and we'll book a table for you straight away.

Guided tours — We can arrange a private tour of the area's highlights at your convenience.

Just let us know what appeals to you and we'll take care of everything.

Looking forward to welcoming you,
{{OPERATOR_NAME}}
{{HOTEL_NAME}}
```

### Longer Stay Additions (5+ nights)

For guests staying 5+ nights, add after the local restaurant mention:

```
With a {nights}-night stay, we'd definitely recommend fitting in at least one dinner there.
```

## HTML Formatting

When creating the email via `{{DRAFT_NEW_TOOL}} --html`, wrap each paragraph in `<p>` tags and bold labels with `<b>`:

```html
<p>Hi {first_name},</p>
<p>Thank you for choosing to stay with us...</p>
<p><b>Arrival time</b> — Could you let us know...</p>
```

## Whole-Property Renter Concierge Form (whole-property rentals only)

For **whole-property renters**, include a concierge form link in the pre-arrival email so they can submit all requests in one place:

**URL:** `{{CONCIERGE_FORM_URL}}`

- **Use for:** bookings covering the whole property / whole-villa product
- **Never send to:** individual hotel-room guests
- Wording suggestion: "To make your stay easy to plan, we've put together a short concierge form where you can tell us everything you'd like us to organise — arrival, transfers, dining, tours, dietary needs: {{CONCIERGE_FORM_URL}}"

## Sending Rules

| Booking source | Send from | Send to |
|----------------|-----------|---------|
| Direct (Website, Walk-In, Phone) | `{{INBOX_BOOKINGS}}` | Guest's personal email |
| Booking.com | `{{INBOX_BOOKINGS}}` | Booking.com relay (`xxx@guest.booking.com`) |
| Expedia | `{{INBOX_BOOKINGS}}` | Expedia relay |

## Subject Line

Always use: `Looking forward to welcoming you on {check_in_date_formatted}`

Where `{check_in_date_formatted}` is like "24 April" (day + month, no year).

## Rules

- **NEVER send without the operator's approval** — always present drafts first
- **Always check sent folder** before drafting to avoid double-contacting
- **Dietary question is mandatory** — always include the breakfast question
- **Don't oversell standard rooms** — only use enthusiastic language for premium tiers
- **Local-restaurant recommendation** — always include the operator's primary local recommendation; it drives the best guest experience
- **Country context** — assume international guests will fly in. Don't assume a hire car.
- **Guest communication tone:** warm, personal, luxury-but-approachable. No emojis. Anticipate needs.
