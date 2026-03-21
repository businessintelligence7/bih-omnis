import anthropic
import json
import os

PROMPT = (
    "You are the CAIOR scoring engine for BIH. "
    "Score organisations on AI readiness across 5 dimensions (20pts each = 100 total): "
    "1. Data Infrastructure, 2. AI Talent and Skills, 3. Technology Stack, "
    "4. Leadership and Strategy, 5. Regulatory and Compliance. "
    "Bands: Platinum 85-100, Gold 70-84, Silver 55-69, Bronze 40-54, Foundation 25-39, Baseline 0-24. "
    "Respond in JSON only with keys: data_infrastructure_score, ai_talent_score, "
    "technology_stack_score, leadership_strategy_score, regulatory_compliance_score, "
    "total_score, score_band, primary_recommendation, estimated_opportunity_value_usd, "
    "top_gaps (list of 3), summary."
)


def score_organisation(form_data):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    content = PROMPT + "

FORM DATA:
" + json.dumps(form_data, indent=2)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": content}]
    )
    text = msg.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


if __name__ == "__main__":
    test = {
        "organisation_name": "Test Credit Union",
        "sector": "Credit Union",
        "primary_pain_point": "Rising delinquency, manual processes"
    }
    result = score_organisation(test)
    print(json.dumps(result, indent=2))