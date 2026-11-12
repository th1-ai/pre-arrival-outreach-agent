# runs/

The skill keeps its memory here. Everything in this folder except this file and `.gitkeep` is ignored by git, because it holds guest names and email addresses. Do not commit it and do not share it.

| File | Written by | Read by |
|---|---|---|
| `LOG.md` | The skill, one entry per run, newest at the bottom. The last entry is the latest run summary | The next run (to skip work already done), you, and `morning-routine-agent` |
| `handoff/pre-arrival-outreach-agent.md` | The skill, one row per guest whose welcome was sent | `concierge-agent`, `arrival-time-check-agent` |
| `.sends-YYYY-MM-DD` | The guard hook, if you enabled it: the number of sends it let through that day | The guard hook |
| `cron.log` | Your scheduler, if you use the cron example in the README | You |

The skill only appends to `LOG.md` and `handoff/pre-arrival-outreach-agent.md`. It never rewrites or deletes entries. Delete old entries yourself when you no longer need them; keep at least the last 30 days, because the "already contacted" check reads them.

## `LOG.md` entry format

```
## 2030-04-03 08:00 | scheduled | Level: 2
Needs you:
- R-10234 Sample Guest: open thread from the guest since 1 April, no standard welcome drafted
Checked: scan 7-21 days, premium rooms: 4 guests. Mailbox search: 4 guests.
Done:
- drafted | R-10231 | Example Guest | Suite | check-in 14 April | bookings inbox | draft ID d-0001
Proposed: none
Skipped:
- R-10229: already contacted on 28 March
Errors: none
```

Rules:

- The first line is `## <date> <time> | <on request / scheduled> | Level: <0, 1, 2, 3 or PAUSED>`.
- `Needs you:` is always the first block. Write `Needs you: nothing` when it is empty.
- Each `Done` line starts with one of `sent`, `drafted`, `would send (shadow)`, then the reservation ID.
- A run that stopped at the start (`PAUSED`, Level 0 on a schedule, unfilled placeholder, tool error) still writes an entry, with the reason on the `Checked:` line.

## `handoff/pre-arrival-outreach-agent.md` row format

A markdown table. The skill creates the file with this header the first time:

```
| Sent on | Reservation ID | Guest | Room | Check-in | Nights | Mailbox | Asked | Sent by |
|---|---|---|---|---|---|---|---|---|
| 2030-04-03 | R-10231 | Example Guest | Suite | 2030-04-14 | 4 | bookings | arrival time, transfer, diet, restaurant, tours | operator |
```

`Asked` lists the questions that were in the message, so the next agent knows which answers to expect. `Sent by` is `operator` or `skill (Level 3)`.
