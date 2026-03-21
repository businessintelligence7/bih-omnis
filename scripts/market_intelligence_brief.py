import feedparser, anthropic, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

RSS_FEEDS = [
    'https://techcrunch.com/feed/',
    'https://www.finextra.com/rss/headlines.aspx',
    'https://www.jis.gov.jm/feed/',
    'https://jamaicaobserver.com/feed/',
    'https://jamaica-gleaner.com/feed',
    'https://www.imf.org/en/News/rss',
]

BIH_CONTEXT = (
    'You are OMNIS - market intelligence engine of BIH, a Jamaican AI consulting firm. '
    'Products: FHILE (AI lending intelligence) and CAIOR (AI readiness scoring). '
    'Target: credit unions, commercial banks, DFIs in Jamaica and Caribbean. '
    'Pipeline: FHCCU (proposal pending JMD 6M-10M), First Global Bank (demo scheduled), DBJ (active JMD 9.6M/yr). '
    'Expansion: Jamaica 2026, T&T + Barbados 2027, Cayman 2028.'
)

def fetch_articles():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))[:350]
                source = feed.feed.get('title', url)
                articles.append(f'TITLE: {title}\nSUMMARY: {summary}\nSOURCE: {source}')
        except Exception as e:
            print(f'Feed error {url}: {e}')
    return '\n\n---\n\n'.join(articles[:28])

def generate_brief(articles):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    week = datetime.now().strftime('%B %d, %Y')
    prompt = (
        f'{BIH_CONTEXT}\n\nArticles:\n{articles}\n\n'
        f'Generate OMNIS Weekly Brief for week of {week}.\n\n'
        'Sections:\n'
        '1. JAMAICA & CARIBBEAN (Top 5 - headline, source, summary, BIH relevance, action)\n'
        '2. GLOBAL AI & FINTECH TRENDS (Top 3 - trend, why it matters, BIH response)\n'
        '3. FHILE PIPELINE INTELLIGENCE\n'
        '4. LINKEDIN THOUGHT LEADERSHIP HOOKS (5 opening lines)\n'
        '5. OMNIS RECOMMENDATIONS (Top 3 actions this week - name people, institutions, deadlines)\n\n'
        'Plain text. CAPS headers.'
    )
    msg = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=2500,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return msg.content[0].text

def send_email(brief):
    week = datetime.now().strftime('%B %d, %Y')
    msg = MIMEMultipart()
    msg['From'] = os.environ['GMAIL_USER']
    msg['To'] = os.environ['GMAIL_USER']
    msg['Subject'] = f'OMNIS Weekly Brief - Week of {week}'
    msg.attach(MIMEText(brief, 'plain'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(os.environ['GMAIL_USER'], os.environ['GMAIL_APP_PASSWORD'])
        s.send_message(msg)
    print(f'Brief sent for week of {week}')

if __name__ == '__main__':
    print('Fetching articles...')
    a = fetch_articles()
    print('Generating brief...')
    b = generate_brief(a)
    print('Sending email...')
    send_email(b)
    print('Done.')
