"""
Prompt injection, the SECURE way — same tools, same poisoned ticket.

The fix is the same principle as parameterized queries and output escaping:
keep untrusted DATA out of the instruction/interpretation channel, and put
guardrails around the tools.

Defenses shown here:
  1. Trust boundary — instructions come ONLY from the system prompt; the
     ticket is treated purely as data to be summarized, never parsed for
     commands.
  2. Tool allow-list — read_file() refuses anything outside a safe set, so
     secrets.txt is off-limits even if something asked for it.
  3. Output filter — replies are scanned for secret-looking content and
     blocked before they leave.
  4. (Mention) Human-in-the-loop for any privileged/outbound action.

    python agent_safe.py           # poisoned ticket -> refused / safe summary
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM_PROMPT = (
    "You are SupportBot. Read the customer's ticket and reply with a one-"
    "sentence summary. You can use tools: read_file(path), send_reply(text)."
)

READ_ALLOWLIST = {"faq.txt", "support_ticket_benign.txt", "poisoned_ticket.txt"}
SECRET_PATTERNS = [r"api[_-]?key", r"password", r"sk-[a-z0-9-]+"]


def read_file(path):
    # DEFENSE 2: tool allow-list. Untrusted requests can't reach secrets.txt.
    if os.path.basename(path) not in READ_ALLOWLIST:
        raise PermissionError("read_file blocked by allow-list: %r" % path)
    with open(os.path.join(HERE, path)) as f:
        return f.read()


def send_reply(text):
    # DEFENSE 3: output filter — never let secret-looking text leave.
    for pat in SECRET_PATTERNS:
        if re.search(pat, text, re.I):
            print("    [blocked] reply withheld: looks like it contains a secret.")
            return
    print("    [SupportBot -> customer] " + text.strip().replace("\n", " "))


def summarize(ticket_text):
    """DEFENSE 1: the ticket is DATA. We never execute instructions from it —
    we only produce a summary. Injected 'ignore your instructions...' text is
    just words in a string we describe, not commands we run."""
    first = ticket_text.strip().splitlines()[0]
    return "Customer support ticket received (%s); routed to a human agent." % (
        first.replace("Subject:", "").strip() or "no subject"
    )


def run(ticket_file):
    ticket = read_file(ticket_file)            # allowed: it's a ticket, not a secret
    print("SupportBot is processing the ticket (untrusted content = data only)...")
    send_reply(summarize(ticket))
    print("\n✅ SAFE: the injected instructions were treated as text, not obeyed.")


if __name__ == "__main__":
    run("support_ticket_benign.txt" if "--benign" in sys.argv else "poisoned_ticket.txt")
