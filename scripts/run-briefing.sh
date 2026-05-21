#!/bin/bash
# Daily briefing runner — called by cron at 6pm UK
# 1. Runs the briefing generator
# 2. If new content was added, commits and pushes to deploy

set -e
cd ~/theganjaclub-blog

# Run briefing script
python3 scripts/briefing.py

# Check if posts.json changed
if git diff --quiet posts.json; then
    echo "$(date): No new briefing generated today."
    exit 0
fi

# Commit and push
git add posts.json
git commit -m "Daily briefing — $(date '+%d %B %Y')"
git push origin main
echo "$(date): Daily briefing deployed."
