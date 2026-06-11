#!/usr/bin/env bash
# migrate-media-to-r2.sh
# Moves reels/ and carousels/ out of the Astro build and into Cloudflare R2.
# Run from the repo root: ~/Projects/the-ganja-club/blog
# Requires: wrangler authenticated against the Cloudflare account (wrangler whoami)

set -euo pipefail

BUCKET="tgc-media"
REELS_DIR="astro-site/public/reels"
CAROUSELS_DIR="astro-site/public/carousels"

echo "==> Checking wrangler auth"
npx wrangler whoami

echo "==> Creating R2 bucket: $BUCKET (no-op if it exists)"
npx wrangler r2 bucket create "$BUCKET" || true

echo "==> Enabling public r2.dev access on $BUCKET"
# Newer wrangler versions support this directly; if this fails, enable it in
# the dashboard: R2 > tgc-media > Settings > Public access > Allow (r2.dev subdomain)
npx wrangler r2 bucket dev-url enable "$BUCKET" || \
  echo "    (enable public access manually in the dashboard, then re-run to confirm)"

echo "==> Uploading reels"
for f in "$REELS_DIR"/*.mp4; do
  name=$(basename "$f")
  npx wrangler r2 object put "$BUCKET/reels/$name" --file "$f" --content-type "video/mp4"
done

echo "==> Uploading carousels"
find "$CAROUSELS_DIR" -type f | while read -r f; do
  rel=${f#"$CAROUSELS_DIR"/}
  case "$f" in
    *.webp) ct="image/webp" ;;
    *.png)  ct="image/png" ;;
    *.jpg|*.jpeg) ct="image/jpeg" ;;
    *.mp4)  ct="video/mp4" ;;
    *)      ct="application/octet-stream" ;;
  esac
  npx wrangler r2 object put "$BUCKET/carousels/$rel" --file "$f" --content-type "$ct"
done

echo "==> Done. Get the public base URL:"
npx wrangler r2 bucket dev-url get "$BUCKET" || \
  echo "    Find it in the dashboard under R2 > $BUCKET > Settings > Public access"

echo ""
echo "NEXT STEPS (manual, after verifying uploads):"
echo "1. Update Instagram posting scripts to use the new R2 public URLs"
echo "   (grep ~/.hermes and any posting scripts for 'theganjaclub.netlify.app')"
echo "2. Test one URL: curl -sI <public-url>/reels/hf-crewneck.mp4  (expect 200)"
echo "3. Only after step 2 passes: git rm -r $REELS_DIR $CAROUSELS_DIR && commit"
echo ""
echo "NOTE: r2.dev URLs are rate-limited and fine for Instagram's fetcher at this"
echo "volume, but when a custom domain is purchased, attach it to the bucket"
echo "(R2 > Settings > Custom domains) and update the posting scripts again."
