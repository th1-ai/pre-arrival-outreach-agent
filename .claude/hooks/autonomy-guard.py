#!/usr/bin/env python3
"""PreToolUse guard for the pre-arrival outreach skill.

Reads the Bash command Claude Code is about to run (hook JSON on stdin) and
checks it against the single `Level:` line of AUTONOMY.md in the project root
(value 0, 1, 2, 3 or PAUSED):

  create a draft   needs Level 2 or higher, otherwise the call needs a human
  send an email    needs Level 3, inside the send window, under the daily cap,
                   otherwise the call needs a human or is blocked
  PAUSED           blocks both. A missing file, a missing Level line or any
                   other value counts as PAUSED

"Needs a human" is the hook decision "ask": an interactive session shows a
permission prompt, a non-interactive `claude -p` run denies the call.
Commands that neither draft nor send pass through untouched.

The script only reads AUTONOMY.md and keeps a per-day send counter in runs/.
It counts attempts, not delivered mail, so the cap errs on the low side.
"""
import datetime
import json
import os
import re
import sys

# Edit these two lists so they match YOUR tools. Regular expressions, searched
# anywhere in the command text. The defaults match the reference commands in
# SKILL.md (Step 5).
SEND_PATTERNS = [r"\bdrafts-send\b", r"\bmessages-send\b"]
DRAFT_PATTERNS = [r"create_draft_email", r"\bdrafts-create\b"]


def decide(decision, reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": "autonomy-guard: " + reason,
        }
    }))
    sys.exit(0)


def count(patterns, text):
    return sum(len(re.findall(p, text)) for p in patterns)


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        decide("ask", "could not read the hook input, so a human must approve this call.")
    if event.get("tool_name") != "Bash":
        sys.exit(0)
    command = (event.get("tool_input") or {}).get("command") or ""
    sends = count(SEND_PATTERNS, command)
    drafts = count(DRAFT_PATTERNS, command)
    if not sends and not drafts:
        sys.exit(0)

    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    try:
        with open(os.path.join(root, "AUTONOMY.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        text = ""

    lines = re.findall(r"^Level:[ \t]*(.*?)[ \t]*$", text, re.M)
    if len(lines) != 1 or lines[0] not in ("0", "1", "2", "3"):
        if lines == ["PAUSED"]:
            why = "AUTONOMY.md says Level: PAUSED"
        elif not text:
            why = "AUTONOMY.md is missing or unreadable, which counts as PAUSED"
        else:
            why = "AUTONOMY.md needs exactly one 'Level:' line with 0, 1, 2, 3 or PAUSED; anything else counts as PAUSED"
        decide("deny", why + ". Nothing is drafted or sent until the operator sets a level.")
    level = int(lines[0])
    where = "AUTONOMY.md is at Level %d" % level

    if sends:
        if level < 3:
            decide("ask", where + ". Sending without the operator needs Level 3. Leave the draft and list it under 'Needs you'.")
        window = re.search(r"^Send window:\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$", text, re.M)
        cap = re.search(r"^Daily send cap:\s*(\d+)\s*$", text, re.M)
        if not window or not cap:
            decide("deny", "Level 3 needs a 'Send window: HH:MM-HH:MM' line and a 'Daily send cap: N' line in AUTONOMY.md.")
        now = datetime.datetime.now()
        h1, m1, h2, m2 = (int(x) for x in window.groups())
        minute = now.hour * 60 + now.minute
        if not (h1 * 60 + m1 <= minute < h2 * 60 + m2):
            decide("deny", "outside the send window %s. Leave the draft for the next run." % window.group(0)[13:].strip())
        counter = os.path.join(root, "runs", ".sends-" + now.strftime("%Y-%m-%d"))
        try:
            with open(counter, encoding="utf-8") as fh:
                used = int(fh.read().strip() or 0)
        except (OSError, ValueError):
            used = 0
        limit = int(cap.group(1))
        if used + sends > limit:
            decide("deny", "daily send cap reached (%d of %d used today). Leave the draft and list it under 'Needs you'." % (used, limit))
        try:
            os.makedirs(os.path.dirname(counter), exist_ok=True)
            with open(counter, "w", encoding="utf-8") as fh:
                fh.write(str(used + sends))
        except OSError:
            decide("deny", "could not write the send counter in runs/, so the daily cap cannot be enforced.")
        sys.exit(0)

    if level < 2:
        decide("ask", where + ". Creating drafts without the operator needs Level 2. Put the proposed message in the report instead.")
    sys.exit(0)


if __name__ == "__main__":
    main()
