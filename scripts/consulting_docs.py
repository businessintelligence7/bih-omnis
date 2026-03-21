import anthropic, os, argparse

PROMPT = (
    'You are BIH Consulting Documentation AI. Convert meeting notes into a structured document.\n\n'
    'Sections:\n'
    'MEETING SUMMARY (date, attendees, objective, outcome)\n'
    'CLIENT PAIN POINTS (ranked by urgency)\n'
    'AUTOMATION OPPORTUNITIES (description, BIH product match, estimated value, effort)\n'
    'ACTION ITEMS (action | owner | deadline | priority)\n'
    'PROPOSED NEXT STEPS (max 3)\n'
    'CLIENT FOLLOW-UP EMAIL (ready to send from Omaro Hutchinson)\n\n'
    'Plain text. CAPS headers.'
)

def generate_docs(notes, client_name):
    ai = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    msg = ai.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': f'{PROMPT}\n\nCLIENT: {client_name}\n\nNOTES:\n{notes}'}]
    )
    return msg.content[0].text

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--notes', required=True)
    p.add_argument('--client', required=True)
    args = p.parse_args()
    print(generate_docs(args.notes, args.client))
