#!/usr/bin/env python3
"""
TGC Weekly Newsletter Generator
================================
Gathers articles from the last 7 days, formats a clean HTML email,
and sends it via Gmail API.

Usage: python3 newsletter.py [--dry-run]
"""

import json, urllib.request, urllib.parse, os, base64, re, sys, glob
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Paths ──────────────────────────────────────────────────────────
HOME = os.path.expanduser("~")
CONTENT_DIR = os.path.join(HOME, "Projects", "the-ganja-club", "blog", "astro-site", "src", "content", "posts")
TP = os.path.join(HOME, ".hermes", "google_token.json")
SITE_URL = "https://theganjaclub.co.uk"

# ── Gmail token ────────────────────────────────────────────────────
with open(TP) as f:
    token_data = json.load(f)

now = datetime.now(timezone.utc)
expiry = datetime.fromisoformat(token_data["expiry"].replace("Z", "+00:00"))
if now > expiry:
    rd = urllib.parse.urlencode({
        "client_id": token_data["client_id"],
        "client_secret": token_data["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=rd)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = urllib.request.urlopen(req)
    nt = json.loads(resp.read())
    token_data["token"] = nt["access_token"]
    token_data["expiry"] = (now + timedelta(seconds=nt.get("expires_in", 3600))).isoformat()
    with open(TP, "w") as f:
        json.dump(token_data, f, indent=2)
    AT = token_data["token"]
else:
    AT = token_data["token"]

# ── Article gathering ──────────────────────────────────────────────
def parse_frontmatter(path):
    """Parse YAML frontmatter from a markdown file."""
    with open(path) as f:
        content = f.read()
    if not content.startswith("---"):
        return {}, ""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, ""
    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            frontmatter[key] = val
    return frontmatter, parts[2].strip()

def get_articles_since(days=7):
    """Get articles from the last N days, sorted newest first."""
    cutoff = datetime.now() - timedelta(days=days)
    articles = []

    for path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.md")), reverse=True):
        fm, body = parse_frontmatter(path)

        # Parse date
        date_str = fm.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%d %B %Y")
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

        if date_obj < cutoff:
            continue

        # Skip drafts
        if fm.get("draft") == "true":
            continue

        slug = fm.get("slug", os.path.basename(path).replace(".md", ""))

        # Extract first paragraph of body (after stripping HTML)
        body_plain = re.sub(r"<[^>]+>", " ", body)
        body_plain = re.sub(r"\s+", " ", body_plain).strip()
        preview = body_plain[:200] + "..." if len(body_plain) > 200 else body_plain

        articles.append({
            "title": fm.get("title", "Untitled"),
            "slug": slug,
            "date": date_obj,
            "date_display": date_obj.strftime("%A, %-d %B"),
            "excerpt": fm.get("excerpt", preview[:200]),
            "region": fm.get("region", "global"),
            "tags": fm.get("tags", ""),
            "url": f"{SITE_URL}/post/{slug}/",
        })

    return articles

# ── HTML email ─────────────────────────────────────────────────────
def build_email_html(articles, week_label):
    """Build a clean, responsive HTML newsletter."""
    article_rows = ""
    for a in articles:
        article_rows += f"""
        <tr>
            <td style="padding: 24px 0; border-bottom: 1px solid #e8ece9;">
                <p style="margin: 0 0 6px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #059669;">
                    {a['date_display'].upper()}  ·  {a.get('region', '').upper()}
                </p>
                <h3 style="margin: 0 0 8px; font-family: Georgia, 'Times New Roman', serif; font-size: 20px; line-height: 1.25; color: #1E3932;">
                    <a href="{a['url']}" style="color: #1E3932; text-decoration: none;">{a['title']}</a>
                </h3>
                <p style="margin: 0; font-size: 15px; line-height: 1.6; color: #4a5565;">
                    {a['excerpt']}
                </p>
                <p style="margin: 10px 0 0;">
                    <a href="{a['url']}" style="color: #059669; font-weight: 600; font-size: 13px; text-decoration: none;">Read full article →</a>
                </p>
            </td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Ganja Club — {week_label}</title>
</head>
<body style="margin: 0; padding: 0; background: #f5f7f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #f5f7f5;">
  <tr>
    <td align="center" style="padding: 40px 20px;">
      <table width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="padding: 40px 40px 24px; background: #1E3932; text-align: center;">
            <p style="margin: 0 0 8px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #C9A84C;">The Ganja Club</p>
            <h1 style="margin: 0; font-family: Georgia, 'Times New Roman', serif; font-size: 28px; color: #ffffff; font-weight: normal;">
              {week_label}
            </h1>
            <p style="margin: 12px 0 0; font-size: 14px; color: #D4E9E2;">
              The week in medical cannabis — news, policy, and research
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding: 16px 40px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {article_rows}
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding: 24px 40px 32px; background: #f9faf9; text-align: center; border-top: 1px solid #e8ece9;">
            <p style="margin: 0 0 8px; font-size: 13px; color: #4a5565;">
              <a href="{SITE_URL}" style="color: #059669; text-decoration: none;">theganjaclub.co.uk</a>
            </p>
            <p style="margin: 0; font-size: 12px; color: #9ca3af;">
              The Ganja Club · Bradford, UK · AP Collective Ltd<br>
              <a href="{SITE_URL}/about" style="color: #9ca3af;">Editorial policy & medical disclaimer</a>
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>"""

# ── Gmail send ─────────────────────────────────────────────────────
def send_via_gmail(to, subject, html_body):
    """Send an email via Gmail API."""
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = "The Ganja Club <contact@apcollective.ltd>"
    msg["Subject"] = subject

    plain = re.sub(r"<[^>]+>", " ", html_body)
    plain = re.sub(r"\s+", " ", plain).strip()

    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    req_body = json.dumps({"raw": raw}).encode()
    url = "https://www.googleapis.com/gmail/v1/users/me/messages/send"
    req = urllib.request.Request(url, data=req_body, method="POST")
    req.add_header("Authorization", f"Bearer {AT}")
    req.add_header("Content-Type", "application/json")

    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result.get("id", "unknown")

# ── Main ───────────────────────────────────────────────────────────
def main():
    dry_run = "--dry-run" in sys.argv

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    week_label = f"Week of {start_date.strftime('%-d %B')} – {end_date.strftime('%-d %B %Y')}"

    print(f"📰 TGC Weekly Newsletter — {week_label}")

    articles = get_articles_since(7)
    print(f"   Articles found: {len(articles)}")

    if not articles:
        print("   No articles in the last 7 days. Exiting.")
        return

    html = build_email_html(articles, week_label)

    # Save to file for inspection
    out_path = os.path.join(HOME, "Projects", "the-ganja-club", "blog", "scripts", "newsletter-output.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"   HTML saved: {out_path}")

    if dry_run:
        print("\n   DRY RUN — not sending. Preview the HTML above.")
        return

    # Send to self first for review
    subject = f"The Ganja Club — {week_label}"
    to = "contact@apcollective.ltd"

    msg_id = send_via_gmail(to, subject, html)
    print(f"\n   Sent to {to}")
    print(f"   Message ID: {msg_id}")
    print(f"\n   Next step: once reviewed, add subscriber list and set up the weekly cron.")

if __name__ == "__main__":
    main()
