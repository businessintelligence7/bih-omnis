import feedparser
import anthropic
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.finextra.com/rss/headlines.aspx",
    "https://www.jis.gov.jm/feed/",
    "https://jamaicaobserver.com/feed/",
    "https://jamaica-gleaner.com/feed",
    "https://www.imf.org/en/News/rss",
]

BIH_CONTEXT = (
    "You are OMNIS - market intelligence engine of BIH, a Jamaican AI consulting firm. "
    "Products: FHILE (AI lending intelligence) and CAIOR (AI readiness scoring). "
    "Target: credit unions, commercial banks, DFIs in Jamaica and Caribbean. "
    "Pipeline: FHCCU (proposal pending JMD 6M-10M), First Global Bank (demo scheduled), "
    "DBJ (active JMD 9.6M/yr). Expansion: Jamaica 2026, T&T + Barbados 2027, Cayman 2028."
)


def fetch_articles():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                title = entry.get("title", "")
                raw = entry.get("summary", entry.get("description", ""))
                summary = raw[:350]
                source = feed.feed.get("title", url)
                row = "TITLE: " + title + "
" + "SUMMARY: " + summary + "
" + "SOURCE: " + source
                articles.append(row)
        except Exception as e:
            print("Feed error: " + str(e))
    return "

---

".join(articles[:28])


def generate_brief(articles):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    week = datetime.now().strftime("%B %d, %Y")
    sections = (
        "1. JAMAICA & CARIBBEAN (Top 5 - headline, source, summary, BIH relevance, action)
"
        "2. GLOBAL AI & FINTECH TRENDS (Top 3 - trend, why it matters, BIH response)
"
        "3. FHILE PIPELINE INTELLIGENCE
"
        "4. LINKEDIN THOUGHT LEADERSHIP HOOKS (5 opening lines)
"
        "5. OMNIS RECOMMENDATIONS (Top 3 actions this week)
"
    )
    prompt = (
        BIH_CONTEXT
        + "

Articles:
" + articles
        + "

Generate OMNIS Weekly Brief for week of " + week + ".

"
        + "Sections:
" + sections
        + "
Plain text only. CAPS for section headers. No markdown."
    )
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


def send_email(brief):
    week = datetime.now().strftime("%B %d, %Y")
    msg = MIMEMultipart()
    msg["From"] = os.environ["GMAIL_USER"]
    msg["To"] = os.environ["GMAIL_USER"]
    msg["Subject"] = "OMNIS Weekly Brief - Week of " + week
    msg.attach(MIMEText(brief, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
        s.send_message(msg)
    print("Brief sent for week of " + week)


if __name__ == "__main__":
    print("Fetching articles...")
    a = fetch_articles()
    print("Generating brief with Claude...")
    b = generate_brief(a)
    print("Sending email...")
    send_email(b)
    print("Done.")