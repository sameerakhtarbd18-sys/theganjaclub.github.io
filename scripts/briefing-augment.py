#!/usr/bin/env python3
"""
Agent Reach augmentation for the TGC daily briefing pipeline.
Adds Jina Reader (full article text) and YouTube transcript extraction
as supplementary sources to the existing RSS feed scraper.

Usage:
    python3 scripts/briefing-augment.py          # fetch + print supplementary headlines
    python3 scripts/briefing-augment.py --json   # output as JSON for piping

Requirements (all already installed):
    pip install feedparser requests python-dotenv yt-dlp
"""

import os, sys, json, hashlib
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.expanduser("~/.hermes/.env")
load_dotenv(ENV_FILE)

# ── Cannabis keywords ──────────────────────────────────────────────
CANNABIS_KEYWORDS = [
    "cannabis", "cannabinoid", "THC", "CBD", "marijuana",
    "hemp", "medical cannabis", "ganja", "weed",
    "scheduling", "dispensary", "prescription cannabis",
    "cannabis-based", "Sativex", "Epidiolex", "Nabilone",
    "drug policy", "drug reform", "decriminali",
]

# ── YouTube cannabis news channels / search terms ──────────────────
YOUTUBE_SEARCH_TERMS = [
    "medical cannabis UK news",
    "cannabis policy reform 2026",
    "cannabis industry Europe",
]

# ── Web sources for Jina Reader deep-read ──────────────────────────
# These are cannabis news aggregators / portals that RSS doesn't cover well
WEB_SOURCES = [
    "https://cannabishealthnews.co.uk",
    "https://www.cannabiz.eu",
    "https://prohibitionpartners.com/news",
]


def is_cannabis_related(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in CANNABIS_KEYWORDS)


# ═══════════════════════════════════════════════════════════════════
# Jina Reader — deep-read any URL as clean markdown
# ═══════════════════════════════════════════════════════════════════

def jina_read(url: str) -> str | None:
    """Read a web page via Jina Reader AI (returns clean markdown)."""
    try:
        resp = requests.get(
            f"https://r.jina.ai/{url}",
            timeout=30,
            headers={"Accept": "text/markdown"}
        )
        resp.raise_for_status()
        text = resp.text
        # Strip Jina header block
        if "Markdown Content:" in text:
            text = text.split("Markdown Content:", 1)[1].strip()
        return text[:6000]  # cap for token budget
    except Exception as e:
        print(f"  [!] Jina read failed for {url}: {e}", file=sys.stderr)
        return None


def fetch_web_source(url: str) -> list[dict]:
    """Scrape a cannabis news portal homepage for headlines."""
    headlines = []
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "TheGanjaClub-Bot/1.0 (+https://theganjaclub.co.uk)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup.find_all(["h2", "h3", "a"]):
            text = tag.get_text(strip=True)
            href = tag.get("href", "")
            if not text or len(text) < 20:
                continue
            if not is_cannabis_related(text):
                continue
            if href and not href.startswith("http"):
                if href.startswith("/"):
                    base = url.rstrip("/")
                    href = f"{base}{href}"
                else:
                    continue
            headlines.append({
                "source": url.split("//")[1].split("/")[0],
                "title": text[:200],
                "url": href or url,
                "fetched": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        print(f"  [!] Web scrape failed for {url}: {e}", file=sys.stderr)

    return headlines[:5]  # top 5 per source


# ═══════════════════════════════════════════════════════════════════
# YouTube — search + transcript extraction
# ═══════════════════════════════════════════════════════════════════

def fetch_youtube_transcripts(max_per_term: int = 3) -> list[dict]:
    """Search YouTube for cannabis news and extract transcripts."""
    results = []
    try:
        import yt_dlp
    except ImportError:
        print("  [!] yt-dlp not available — install: pip install yt-dlp", file=sys.stderr)
        return results

    for term in YOUTUBE_SEARCH_TERMS:
        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "force_generic_extractor": False,
                "js_runtimes": {"node": {}},  # required per yt-dlp EJS
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{max_per_term}:{term}", download=False)
                for entry in info.get("entries", [])[:max_per_term]:
                    vid_id = entry.get("id", "")
                    title = entry.get("title", "")
                    if not is_cannabis_related(title):
                        continue
                    # Try to get transcript
                    transcript = ""
                    try:
                        t_opts = {"quiet": True, "writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": ["en"], "skip_download": True}
                        with yt_dlp.YoutubeDL(t_opts) as ydl2:
                            t_info = ydl2.extract_info(f"https://youtube.com/watch?v={vid_id}", download=False)
                            subs = t_info.get("subtitles", {}) or t_info.get("automatic_captions", {})
                            for lang in ["en", "en-GB", "en-US"]:
                                if lang in subs:
                                    sub_url = subs[lang][0]["url"]
                                    sub_resp = requests.get(sub_url, timeout=15)
                                    transcript = sub_resp.text[:3000]
                                    break
                    except Exception:
                        pass

                    results.append({
                        "source": "YouTube",
                        "title": title[:200],
                        "url": f"https://youtube.com/watch?v={vid_id}",
                        "transcript_snippet": transcript[:1000] if transcript else "",
                        "fetched": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"  [!] YouTube search failed for '{term}': {e}", file=sys.stderr)

    return results


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    as_json = "--json" in sys.argv

    if not as_json:
        print("=== Agent Reach — TGC Briefing Augmentation ===\n")

    all_headlines = []

    # 1. Web sources (Jina Reader + homepage scrape)
    if not as_json:
        print("🌐 Web sources:")
    for url in WEB_SOURCES:
        headlines = fetch_web_source(url)
        all_headlines.extend(headlines)
        if not as_json:
            print(f"  {url.split('//')[1]}: {len(headlines)} headlines")

    # 2. YouTube transcripts
    if not as_json:
        print("\n📺 YouTube:")
    yt_results = fetch_youtube_transcripts()
    all_headlines.extend(yt_results)
    if not as_json:
        print(f"  {len(yt_results)} videos with transcripts")

    if not as_json:
        print(f"\n📋 Total supplementary headlines: {len(all_headlines)}")
        for h in all_headlines:
            print(f"  [{h['source']}] {h['title'][:100]}")
            if h.get("transcript_snippet"):
                print(f"    transcript: {h['transcript_snippet'][:120]}...")
            print()
    else:
        print(json.dumps(all_headlines, indent=2))


if __name__ == "__main__":
    main()
