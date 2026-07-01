#!/bin/bash
# The Ganja Club — Automated Daily Briefing Pipeline
# Runs briefing.py, commits the result, and pushes to deploy.
# Called by Hermes cron job.
# Stdout (lines starting with 📰) is captured for delivery.
set -euo pipefail

BLOG_DIR="/Users/sameer/Projects/the-ganja-club/blog"
ASTRO_DIR="$BLOG_DIR/astro-site"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"
LOG_FILE="$BLOG_DIR/scripts/briefing.log"

# Redirect all diagnostics to log file
exec 3>&1 4>&2  # save original stdout/stderr
exec 1>>"$LOG_FILE" 2>&1

log() { echo "$@"; }
deliver() { echo "$@" >&3; }  # write to original stdout for cron delivery

log "=============================================="
log "  TGC Daily Briefing — $(date '+%Y-%m-%d %H:%M:%S')"
log "=============================================="

# 1. Pull latest to avoid conflicts
cd "$ASTRO_DIR"
git pull --ff-only origin main 2>&1 || log "[!] git pull had issues, continuing anyway"

# 2. Run the briefing generator
cd "$BLOG_DIR"
if ! $PYTHON scripts/briefing.py; then
    log "[!] Briefing generation failed"
    deliver "❌ Daily briefing FAILED — check briefing.log"
    exit 1
fi

# 3. Check if there's a new file to commit
NEW_POST=$(git -C "$ASTRO_DIR" status --short -- src/content/posts/daily-briefing-*.md 2>/dev/null | grep '^??' | head -1 | awk '{print $2}')

if [ -z "$NEW_POST" ]; then
    log "[~] No new briefing to commit (already exists or no headlines)"
    deliver "📰 Daily briefing: nothing new to publish today"
    exit 0
fi

# 4. Commit and push
cd "$ASTRO_DIR"
git add "$NEW_POST"
COMMIT_MSG="Daily briefing: $(date '+%-d %B %Y') (automated)"
git commit -m "$COMMIT_MSG"
git push origin main

log "[✓] Committed and pushed: $NEW_POST"
log "[✓] Cloudflare Pages will auto-deploy"

deliver "📰 Daily briefing deployed: $(basename "$NEW_POST")"
deliver "https://theganjaclub.co.uk"

# 5. Post to social media
log "[→] Triggering social auto-post..."
cd "$BLOG_DIR"
if python3 scripts/auto-social.py --ig-only 2>&1; then
    log "[✓] Social post completed"
    deliver "📱 Also posted to Instagram"
else
    log "[!] Social post had issues (check log)"
fi
