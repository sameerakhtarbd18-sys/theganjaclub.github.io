#!/usr/bin/env python3
"""
TGC Social Auto-Poster
Posts the latest daily briefing to Instagram (and X when configured).
"""

import json, os, sys, re, glob, subprocess

H = os.path.expanduser("~")
CD = os.path.join(H, "Projects", "the-ganja-club", "blog", "astro-site", "src", "content", "posts")
SU = "https://theganjaclub.co.uk"
IP = os.path.join(H, ".hermes", "scripts", "ig-post.py")

def parse_fm(path):
    with open(path) as f:
        c = f.read()
    if not c.startswith("---"): return {}, ""
    p = c.split("---", 2)
    if len(p) < 3: return {}, ""
    fm = {}
    for line in p[1].strip().split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, p[2].strip()

def find_latest():
    bfs = sorted([f for f in glob.glob(os.path.join(CD, "daily-briefing-*.md"))], reverse=True)
    return bfs[0] if bfs else None

def get_info(path):
    fm, body = parse_fm(path)
    t = fm.get("title", "Daily Briefing")
    ex = fm.get("excerpt", "")
    img = fm.get("image", "")
    bp = re.sub(r"<[^>]+>", " ", body)
    bp = re.sub(r"\s+", " ", bp).strip()
    h2m = re.search(r"<h2[^>]*>(.*?)</h2>", body)
    fs = re.sub(r"<[^>]+>", "", h2m.group(1) if h2m else t)
    return {"title": t, "excerpt": ex[:200] if ex else bp[:200], "image": img, "slug": fm.get("slug", ""), "first_story": fs}

def build_cap(info):
    return "\n".join([
        info["first_story"][:120],
        "",
        "Full briefing at theganjaclub.co.uk — link in bio.",
        "",
        "#MedicalCannabis #CannabisNews #UKCannabis #TheGanjaClub",
    ])

def post_ig(img_url, caption):
    r = subprocess.run([sys.executable, IP, img_url, "CANNABIS"], input=caption, capture_output=True, text=True, timeout=60)
    try: return json.loads(r.stdout.strip())
    except: return {"status": "error", "message": r.stderr or r.stdout}

def post_x(text, url):
    try:
        r = subprocess.run(["xurl", "post", f"{text}\n{url}"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            d = json.loads(r.stdout)
            return {"status": "ok", "post_id": d.get("data", {}).get("id", "?")}
        return {"status": "error", "message": r.stderr.strip()}
    except FileNotFoundError:
        return {"status": "skipped", "message": "xurl not installed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def xurl_ready():
    try:
        r = subprocess.run(["xurl", "auth", "status"], capture_output=True, text=True, timeout=10)
        return "oauth2:" in r.stdout.lower() and "(none)" not in r.stdout
    except: return False

def main():
    dr = "--dry-run" in sys.argv
    io = "--ig-only" in sys.argv

    print("TGC Social Auto-Poster")
    bp = find_latest()
    if not bp:
        print("No daily briefing found.")
        return
    info = get_info(bp)
    iu = info["image"]
    if iu.startswith("/"): iu = SU + iu
    cap = build_cap(info)
    pu = f"{SU}/post/{info['slug']}/"

    print(f"Article: {info['title'][:80]}")
    print(f"Caption:\n{cap}\n")

    if dr:
        print("DRY RUN — not posting.")
        return

    igr = post_ig(iu, cap)
    if igr.get("status") == "ok":
        print(f"IG: {igr.get('post_id', 'ok')}")
    else:
        print(f"IG FAILED: {igr.get('message', '?')}")

    if not io and xurl_ready():
        xr = post_x(f"{info['first_story'][:200]}\n\nFull briefing:", pu)
        if xr.get("status") == "ok":
            print(f"X: {xr.get('post_id', 'ok')}")
        else:
            print(f"X skipped: {xr.get('message', '?')}")
    elif not io:
        print("X: not configured")

    ok = igr.get("status") == "ok"
    msg = f"IG post {'live' if ok else 'FAILED'}: {info['title'][:80]}"
    print(msg)

if __name__ == "__main__":
    main()
