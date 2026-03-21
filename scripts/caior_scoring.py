import anthropic, json, os

PROMPT = (
    'You are the CAIOR scoring engine for BIH. Score organisations on AI readiness '
    'across 5 dimensions (20pts each = 100 total): '
    '1. Data Infrastructure, 2. AI Talent & Skills, 3. Technology Stack, '
    '4. Leadership & Strategy, 5. Regulatory & Compliance. '
    'Bands: Platinum 85-100, Gold 70-84, Silver 55-69, Bronze 40-54, Foundation 25-39, Baseline 0-24. '
    'Respond in JSON only: '
    '{"data_infrastructure_score":0,"ai_talent_score":0,"technology_stack_score":0,'
    '"leadership_strategy_score":0,"regulatory_compliance_score":0,"total_score":0,'
    '"score_band":"Silver","primary_recommendation":"FHILE",'
    '"estimated_opportunity_value_usd":0,"top_gaps":["gap1","gap2","gap3"],'
    '"summary":"2-3 sentence summary"}'
)

def score_organisation(form_data):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    msg = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=800,
        messages=[{'role': 'user', 'content': f'{PROMPT}\n\nFORM DATA:\n{json.dumps(form_data, indent=2)}'}]
    )
    text = msg.content[0].text.strip()
    if '```' in text:
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    return json.loads(text.strip())

if __name__ == '__main__':
    test = {'organisation_name': 'Test CU', 'sector': 'Credit Union', 'primary_pain_point': 'Rising delinquency'}
    print(json.dumps(score_organisation(test), indent=2))
