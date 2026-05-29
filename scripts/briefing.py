#!/usr/bin/env python3
"""
The Ganja Club — Daily Briefing Automation Script
==================================================
Scrapes UK/EU/US medical cannabis news from public RSS feeds,
generates a daily briefing via the DeepSeek API, and appends
the result to posts.json.

Usage:
    python3 scripts/briefing.py

Requirements:
    pip install feedparser requests beautifulsoup4 python-dotenv
"""

import os
import sys
import json
import re
import html
import hashlib
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.dirname(SCRIPT_DIR)
POSTS_FILE = os.path.join(BLOG_DIR, "posts.json")
ENV_FILE = os.path.expanduser("~/.hermes/.env")

load_dotenv(ENV_FILE)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    print("ERROR: DEEPSEEK_API_KEY not found in ~/.hermes/.env", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Feed definitions
# ---------------------------------------------------------------------------

FEEDS = [
    {
        "name": "BBC Health",
        "url": "https://feeds.bbci.co.uk/news/health/rss.xml",
        "region": "UK",
        "type": "rss",
    },
    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/society/health/rss",
        "region": "UK",
        "type": "rss",
    },
    {
        "name": "NORML",
        "url": "https://norml.org/blog/feed/",
        "region": "USA",
        "type": "rss",
    },
    {
        "name": "MJBizDaily",
        "url": "https://mjbizdaily.com/feed/",
        "region": "USA",
        "type": "rss",
    },
    {
        "name": "Politico EU",
        "url": "https://www.politico.eu/feed/",
        "region": "Europe",
        "type": "rss",
    },
    {
        "name": "Leafly News",
        "url": "https://www.leafly.com/news/rss",
        "region": "USA",
        "type": "rss",
    },
]

# Cannabis-related keywords for filtering headlines
CANNABIS_KEYWORDS = [
    "cannabis", "cannabinoid", "THC", "CBD", "marijuana",
    "hemp", "medical cannabis", "ganja", "weed", "pot",
    "scheduling", "dispensary", "prescription cannabis",
    "cannabis-based", "Sativex", "Epidiolex", "Nabilone",
    "drug policy", "drug reform", "decriminali",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def is_cannabis_related(text: str) -> bool:
    """Check if a headline/summary is cannabis-related."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in CANNABIS_KEYWORDS)


def fetch_feed(feed_info: dict, max_age_hours: int = 72) -> list[dict]:
    """
    Fetch and parse a single RSS feed. Returns a list of headline dicts:
    {source, title, url, published, summary}
    Handles failures gracefully.
    """
    name = feed_info["name"]
    url = feed_info["url"]
    region = feed_info["region"]
    headlines = []

    try:
        resp = requests.get(url, timeout=20, headers={
            "User-Agent": "TheGanjaClub-Bot/1.0 (+https://theganjaclub.com)"
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"  [!] {name}: fetch failed — {e}", file=sys.stderr)
        return headlines

    try:
        parsed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"  [!] {name}: parse failed — {e}", file=sys.stderr)
        return headlines

    if parsed.bozo and not parsed.entries:
        print(f"  [!] {name}: invalid or empty feed", file=sys.stderr)
        return headlines

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for entry in parsed.entries[:30]:  # only process first 30 entries per feed
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        summary = entry.get("summary", "").strip()
        published_raw = entry.get("published", "") or entry.get("updated", "")

        if not title:
            continue

        # Parse publication date
        published = None
        if published_raw:
            try:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                try:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass

        # Fallback: include if no date available
        if published and published < cutoff:
            continue

        if not is_cannabis_related(f"{title} {summary}"):
            continue

        # Clean summary — strip HTML tags
        clean_summary = ""
        if summary:
            try:
                clean_summary = BeautifulSoup(summary, "html.parser").get_text()
                clean_summary = " ".join(clean_summary.split())[:300]
            except Exception:
                clean_summary = summary[:300]

        headlines.append({
            "source": name,
            "region": region,
            "title": title,
            "url": link,
            "published": published_raw or "unknown",
            "summary": clean_summary,
        })

    if headlines:
        print(f"  [✓] {name}: {len(headlines)} cannabis-related headlines")
    else:
        print(f"  [~] {name}: no relevant headlines in recent window")

    return headlines


def scrape_all_feeds() -> list[dict]:
    """Scrape all configured feeds and return deduplicated headlines."""
    print("\n📡 Scraping RSS feeds...\n")
    all_headlines = []
    seen = set()

    for feed in FEEDS:
        headlines = fetch_feed(feed)
        for h in headlines:
            # Deduplicate by normalised title hash
            key = hashlib.md5(h["title"].lower().strip().encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                all_headlines.append(h)

    print(f"\n✅ Total unique headlines: {len(all_headlines)}\n")
    return all_headlines


def format_headlines_for_prompt(headlines: list[dict]) -> str:
    """Format scraped headlines into a clean text block for the AI prompt."""
    lines = []
    for i, h in enumerate(headlines, 1):
        lines.append(f"{i}. [{h['source']} — {h['region']}] {h['title']}")
        if h["summary"]:
            lines.append(f"   Summary: {h['summary']}")
        lines.append(f"   URL: {h['url']}")
        lines.append("")
    return "\n".join(lines)


def call_deepseek(headlines_text: str) -> str:
    """
    Call the DeepSeek API to generate a daily briefing in house style.
    Returns the generated HTML body.
    """
    system_prompt = """You are a medical cannabis journalist and editor for The Ganja Club, a respected UK-based publication covering medical cannabis news, patient advocacy, policy reform, cannabinoid research, and cannabis culture. Your daily briefings are the publication's most-read feature.

HOUSE STYLE — YOU MUST FOLLOW THESE RULES EXACTLY:

1. BRITISH ENGLISH SPELLING: use 'organisation' not 'organization', 'colour' not 'color', 'licence' (noun) not 'license', 'centre' not 'center', 'realise' not 'realize', 'whilst' not 'while', 'analyse' not 'analyze', etc. Use UK punctuation conventions.

2. TONE: Factual, measured, and calm. You are a journalist, not an activist. No hype, no sensationalism, no editorialising. Present the facts clearly and let them speak. Avoid phrases like "game-changer", "revolutionary", "shocking", or "unbelievable". You are trustworthy and sober in tone.

3. STRUCTURE: 
   - Open with: "<p>Good evening. Here's what's moving in the world of medical cannabis today.</p>"
   - Then 3-5 story sections, each beginning with an <h2> subheading that's a concise, factual newspaper-style headline for the story (e.g. "CQC raises concerns over private clinic standards" or "New meta-analysis strengthens case for THC in chronic pain").
   - Under each h2, 1-3 <p> paragraphs of factual reporting (2-4 sentences each). Include specific details where available: numbers, dates, names of organisations, countries, legislation.
   - Total output should be 300-500 words.
   - Use HTML tags only: <p>, <h2>, <em>, <strong>. No markdown. No other HTML.

4. CONTENT PRIORITIES:
   - UK medical cannabis stories first (policy, clinics, NHS, patient rights, CQC, MHRA, Home Office).
   - Then major EU/European developments (Germany, EU policy, European Parliament).
   - Then significant US/international stories (federal policy, research, industry).
   - Skip celebrity gossip, pure recreational stories, and anything not related to medical cannabis or cannabis policy.

5. OUTPUT: Return ONLY valid HTML body content — no preamble, no commentary, no markdown code fences. Start directly with <p>Good evening."""

    user_prompt = f"""Write today's daily briefing based on these real news headlines from RSS feeds. Select the most important and newsworthy 3-5 stories. Prioritise UK and European medical cannabis news first, then significant US/international stories.

IMPORTANT: Only write about stories that are genuinely reflected in these headlines. Do not invent details. If the headlines provide limited information, keep your reporting brief and factual — do not speculate or pad.

HEADLINES:
{headlines_text}

Generate the body HTML now (300-500 words):"""

    print("🤖 Calling DeepSeek API...\n")

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            timeout=120,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: DeepSeek API request failed — {e}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()

    if "choices" not in data or not data["choices"]:
        print("ERROR: DeepSeek returned no choices", file=sys.stderr)
        print(f"Response: {json.dumps(data, indent=2)[:500]}", file=sys.stderr)
        sys.exit(1)

    body = data["choices"][0]["message"]["content"].strip()

    # Clean up — remove any markdown code fences if DeepSeek wraps it
    body = re.sub(r"^```html?\s*\n?", "", body)
    body = re.sub(r"\n?```\s*$", "", body)

    print(f"✅ Generated {len(body.split())} words\n")
    return body


def extract_excerpt(body: str, max_chars: int = 200) -> str:
    """Extract a plain-text excerpt from the HTML body, 150-200 chars."""
    # Strip HTML tags
    try:
        text = BeautifulSoup(body, "html.parser").get_text()
    except Exception:
        text = re.sub(r"<[^>]+>", "", body)

    # Skip the opening preamble ("Good evening...")
    text = re.sub(r"^Good (evening|morning).*?today\.\s*", "", text)
    text = " ".join(text.split())  # normalise whitespace

    # Take first ~200 chars, break at word boundary
    excerpt = text[:max_chars].rsplit(" ", 1)[0]
    # If excerpt is too short after cleanup, use more
    if len(excerpt) < 100 and len(text) > max_chars:
        excerpt = text[:max_chars + 50].rsplit(" ", 1)[0]

    return excerpt


def extract_tags(body: str, headlines: list[dict]) -> str:
    """Generate a comma-separated tag string from regions and content analysis."""
    # Collect regions from headlines
    regions = set()
    for h in headlines:
        regions.add(h["region"])

    # Order regions in a sensible way
    region_order = ["UK", "Europe", "USA", "Americas", "Asia-Pacific", "Global"]
    ordered_regions = [r for r in region_order if r in regions]

    # Determine topic tags from body content
    topic_keywords = {
        "Policy": ["policy", "legislation", "government", "parliament", "regulation", "home office", "mhra", "cqc", "nice", "scheduling", "rescheduling", "reform", "legal"],
        "Research": ["research", "study", "clinical trial", "meta-analysis", "evidence", "science", "journal", "published"],
        "Health": ["nhs", "prescribing", "clinic", "patient", "treatment", "health", "prescription", "doctor", "gp"],
        "Industry": ["market", "industry", "business", "revenue", "investment", "dispensary", "licence"],
        "Reform": ["reform", "legalisation", "decriminalisation", "legalization", "decriminalization", "cannabis club", "adult-use"],
    }

    body_lower = body.lower()
    matched_topics = set()
    for topic, keywords in topic_keywords.items():
        if any(kw in body_lower for kw in keywords):
            matched_topics.add(topic)

    # Always include Briefing
    tags = ["Briefing"] + ordered_regions + sorted(matched_topics)
    return ", ".join(tags)


def count_words(html_body: str) -> int:
    """Count words in HTML body (stripping tags)."""
    text = re.sub(r"<[^>]+>", "", html_body)
    return len(text.split())


def create_post(headlines: list[dict], body: str) -> dict:
    """Build a post dict from the generated body and metadata."""
    now = datetime.now()
    date_display = now.strftime("%-d %B %Y")  # "21 May 2026"
    date_slug = now.strftime("%d-%m-%Y")       # "21-05-2026"
    date_id = now.strftime("%Y-%m-%d")          # "2026-05-21"

    word_count = count_words(body)
    read_time = max(1, round(word_count / 200))  # ~200 words/min, minimum 1

    title = f"The Daily Briefing — {date_display}"
    slug = f"daily-briefing-{date_slug}"
    post_id = f"daily-briefing-{date_id}"
    excerpt = extract_excerpt(body)
    tags = extract_tags(body, headlines)

    return {
        "id": post_id,
        "title": title,
        "slug": slug,
        "date": date_display,
        "readTime": read_time,
        "tags": tags,
        "excerpt": excerpt,
        "body": body,
    }


def append_to_posts_json(post: dict) -> bool:
    """Append a new post to posts.json. Skips if ID already exists."""
    posts = []

    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                posts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"WARNING: Could not read {POSTS_FILE}: {e}", file=sys.stderr)
            print("Starting with empty posts array.", file=sys.stderr)
            posts = []

    # Check for duplicate
    for existing in posts:
        if existing.get("id") == post["id"]:
            print(f"⚠️  Post with id '{post['id']}' already exists — skipping.")
            return False

    # Prepend to maintain reverse chronological order (newest first)
    posts.insert(0, post)

    # Write back with proper formatting
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"📝 Appended new post '{post['id']}' to {POSTS_FILE}")
    return True


def append_to_astro_markdown(post: dict) -> bool:
    """
    Also write the post as an Astro markdown file for the SSG.
    Path: astro-site/src/content/posts/{slug}.md
    """
    import random
    ASTRO_POSTS_DIR = os.path.join(BLOG_DIR, "astro-site", "src", "content", "posts")
    os.makedirs(ASTRO_POSTS_DIR, exist_ok=True)

    md_path = os.path.join(ASTRO_POSTS_DIR, f"{post['slug']}.md")

    if os.path.exists(md_path):
        print(f"⚠️  Astro markdown {md_path} already exists — skipping.")
        return False

    # Pick a random image for variety
    flower_imgs = [f for f in os.listdir(os.path.join(BLOG_DIR, "astro-site", "public", "images", "flower"))
                   if f.endswith('.webp')] if os.path.exists(os.path.join(BLOG_DIR, "astro-site", "public", "images", "flower")) else []
    ind_imgs = [f for f in os.listdir(os.path.join(BLOG_DIR, "astro-site", "public", "images", "industrial-weed"))
                if f.endswith('.webp')] if os.path.exists(os.path.join(BLOG_DIR, "astro-site", "public", "images", "industrial-weed")) else []
    
    img = ""
    if flower_imgs:
        img = f"/images/flower/{random.choice(flower_imgs)}"
    elif ind_imgs:
        img = f"/images/industrial-weed/{random.choice(ind_imgs)}"

    # Region: use the first non-Briefing tag that matches a region
    tags = [t.strip() for t in post["tags"].split(",")]
    region_map = {"UK": "uk", "Europe": "europe", "USA": "usa", "Global": "global"}
    region = "global"
    for t in tags:
        if t in region_map:
            region = region_map[t]
            break

    md_content = f"""---
title: "{post['title'].replace(chr(34), chr(92)+chr(34))}"
slug: "{post['slug']}"
date: "{post['date']}"
region: "{region}"
excerpt: "{post['excerpt'].replace(chr(34), chr(92)+chr(34))}"
image: "{img}"
category: "news"
tags:
"""
    for t in tags:
        md_content += f"  - {t}\n"
    
    md_content += "---\n\n"
    md_content += post["body"]
    md_content += "\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"📝 Astro markdown written: {md_path}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  The Ganja Club — Daily Briefing Generator")
    print(f"  {datetime.now().strftime('%A, %d %B %Y %H:%M')}")
    print("=" * 60)

    # 1. Scrape feeds
    headlines = scrape_all_feeds()

    if not headlines:
        print("⚠️  No cannabis-related headlines found today. Skipping briefing generation.")
        sys.exit(0)

    # 2. Format for DeepSeek
    headlines_text = format_headlines_for_prompt(headlines)
    print(f"📋 Sending {len(headlines)} headlines to DeepSeek...\n")

    # 3. Generate briefing body
    body = call_deepseek(headlines_text)

    # Validate body
    if not body or len(body.strip()) < 50:
        print("ERROR: DeepSeek returned insufficient content", file=sys.stderr)
        sys.exit(1)

    # 4. Build post object
    post = create_post(headlines, body)

    # 5. Print summary
    print("─" * 60)
    print(f"  Title:   {post['title']}")
    print(f"  ID:      {post['id']}")
    print(f"  Slug:    {post['slug']}")
    print(f"  Words:   {count_words(body)}")
    print(f"  Read:    {post['readTime']} min")
    print(f"  Tags:    {post['tags']}")
    print(f"  Excerpt: {post['excerpt'][:120]}...")
    print("─" * 60)

    # 6. Append to posts.json
    success = append_to_posts_json(post)

    # 7. Also write Astro markdown
    astro_success = append_to_astro_markdown(post)

    if success or astro_success:
        print("\n🎉 Daily briefing generated and appended successfully!")
    else:
        print("\n⚠️  Briefing was not appended (may already exist for today).")

    sys.exit(0)


if __name__ == "__main__":
    main()
