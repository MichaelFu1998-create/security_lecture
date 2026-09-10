"""
Prompt injection, the VULNERABLE way — a deterministic, offline demo.

Slide 42's point, made runnable: prompt injection is the SAME class of bug as
SQL injection and XSS. Untrusted input (a support ticket) is concatenated into
the SAME channel the "model" reads its instructions from, so the attacker's
text is obeyed as if it were a developer instruction.

No API key and no network: a tiny deterministic stand-in for an LLM makes the
demo behave identically every time. (An optional --live path is described in
README.md for anyone who wants to try it against a real model.)

    python agent_unsafe.py                 # attacker's ticket  -> secret leaks
    python agent_unsafe.py --benign        # normal ticket      -> safe summary
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM_PROMPT = (
    "You are SupportBot. Read the customer's ticket and reply with a one-"
    "sentence summary. You can use tools: read_file(path), send_reply(text)."
)


# --- the agent's tools ---------------------------------------------------
def read_file(path):
    with open(os.path.join(HERE, path)) as f:
        return f.read()


def send_reply(text):
    print("    [SupportBot -> customer] " + text.strip().replace("\n", " "))


# --- a deterministic stand-in for an LLM ---------------------------------
def mock_llm(text):
    """
    A naive 'model': it reads everything it is handed and follows any
    imperative it finds. This is exactly how a real LLM gets steered by
    injected instructions. Returns an ordered list of (tool, arg) actions.
    """
    actions, hijacked = [], False
    if re.search(r"ignore .*instructions", text, re.I):
        hijacked = True  # the injected text has taken over
    m = re.search(r"read the file\s+([\w./-]+)", text, re.I)
    if m:
        actions.append(("read_file", m.group(1)))
    if re.search(r"\b(reply with|send|forward|exfiltrate)\b", text, re.I) and m:
        actions.append(("send_secret", None))
    return actions, hijacked


def run(ticket_file):
    ticket = read_file(ticket_file)                      # <- UNTRUSTED input
    # ⚠️ THE BUG: untrusted content is glued into the instruction channel.
    prompt = SYSTEM_PROMPT + "\n\n--- CUSTOMER TICKET ---\n" + ticket
    actions, hijacked = mock_llm(prompt)

    print("SupportBot is processing the ticket...")
    if hijacked:
        print("    (the ticket's text overrode SupportBot's instructions)")

    leaked = None
    for tool, arg in actions:
        if tool == "read_file":
            leaked = read_file(arg)
            print("    [tool] read_file(%r) -> %d bytes" % (arg, len(leaked)))
        elif tool == "send_secret" and leaked is not None:
            send_reply("Here is the requested configuration:\n" + leaked)

    if leaked is not None:
        print("\n💀 COMPROMISED: the secret file was exfiltrated to the attacker.")
    else:
        send_reply("Customer reports profile-picture uploads failing over ~2 MB.")
        print("\n✅ Nothing sensitive happened (benign ticket).")


if __name__ == "__main__":
    run("support_ticket_benign.txt" if "--benign" in sys.argv else "poisoned_ticket.txt")
