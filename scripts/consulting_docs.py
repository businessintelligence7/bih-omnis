import anthropic
import os
import argparse

PROMPT = (
    "You are BIH Consulting Documentation AI. "
    "Convert meeting notes into a structured consulting document.

"
    "Sections:
"
    "MEETING SUMMARY (date, attendees, objective, outcome)
"
    "CLIENT PAIN POINTS (ranked by urgency)
"
    "AUTOMATION OPPORTUNITIES (description, BIH product match, estimated value, effort)
"
    "ACTION ITEMS (action | owner | deadline | priority)
"
    "PROPOSED NEXT STEPS (max 3)
"
    "CLIENT FOLLOW-UP EMAIL (ready to send from Omaro Hutchinson)

"
    "Plain text. CAPS headers."
)


def generate_docs(notes, client_name):
    ai = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    content = PROMPT + "

CLIENT: " + client_name + "

NOTES:
" + notes
    msg = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": content}]
    )
    return msg.content[0].text


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--notes", required=True)
    p.add_argument("--client", required=True)
    args = p.parse_args()
    print(generate_docs(args.notes, args.client))