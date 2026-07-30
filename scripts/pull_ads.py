#!/usr/bin/env python3
"""Pull live ads from the Meta Ad Library and LinkedIn Ad Library via Apify
actors, and normalize them into one unified schema for field analysis.

Usage:
    python3 pull_ads.py --platform meta --advertiser "Acme Fleet" --output acme-meta.json
    python3 pull_ads.py --platform linkedin --advertiser "Acme Fleet" --output acme-li.json
    python3 pull_ads.py --platform meta --keyword "fleet management" --max-items 100 --output field.json
    python3 pull_ads.py --normalize-only raw.json --platform meta --output ads.json   # re-map a saved raw dump

Requires APIFY_API_TOKEN (paid per result — a 200-ad competitive sweep is a
couple of dollars). Default actors are configurable via --actor: ad-library
actor schemas differ and change; run with --dump-raw first on a new actor,
inspect, and extend FIELD_CANDIDATES if a field comes back empty.

Unified output schema (one object per ad):
    platform, advertiser, ad_id, text, headline, cta, media_type,
    media_urls, start_date, days_running, impressions_range
"""
import argparse
import datetime
import json
import os
import sys
import time

import urllib.request
import urllib.parse

BASE_URL = "https://api.apify.com/v2"

DEFAULT_ACTORS = {
    "meta": "curious_coder~facebook-ads-library-scraper",
    "linkedin": "ivanvs~linkedin-ad-library-scraper",
}

# Candidate raw-field names per unified field, tried in order. Actor outputs
# vary; extend rather than edit when adopting a new actor.
FIELD_CANDIDATES = {
    "advertiser": ["page_name", "pageName", "advertiser", "advertiserName", "companyName", "company_name"],
    "ad_id": ["ad_archive_id", "adArchiveID", "adArchiveId", "id", "adId", "ad_id", "adUrn"],
    "text": ["ad_creative_bodies", "adCreativeBodies", "body", "adCopy", "ad_copy", "text", "commentary", "description"],
    "headline": ["ad_creative_link_titles", "adCreativeLinkTitles", "headline", "title", "linkTitle"],
    "cta": ["cta_text", "ctaText", "cta", "callToAction", "cta_type", "ctaType"],
    "start_date": ["ad_delivery_start_time", "adDeliveryStartTime", "startDate", "start_date", "firstShown", "first_shown"],
    "impressions_range": ["impressions", "impressionsRange", "impressions_range", "impressions_text"],
    "media_urls": ["ad_creative_link_urls", "images", "imageUrls", "videos", "videoUrls", "media", "mediaUrls"],
}


def pick(raw: dict, field: str):
    for key in FIELD_CANDIDATES[field]:
        if key in raw and raw[key] not in (None, "", [], {}):
            return raw[key]
    # one level of nesting is common (e.g. snapshot.*)
    for nest in ("snapshot", "adAnalytics", "details"):
        inner = raw.get(nest)
        if isinstance(inner, dict):
            for key in FIELD_CANDIDATES[field]:
                if key in inner and inner[key] not in (None, "", [], {}):
                    return inner[key]
    return None


def as_text(value):
    if isinstance(value, list):
        return " | ".join(str(v) for v in value[:3])
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)[:200]
    return str(value) if value is not None else ""


def days_running(start_date: str | None) -> int | None:
    if not start_date:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            start = datetime.datetime.strptime(str(start_date)[:26], fmt.replace("%z", "")) if "%z" not in fmt else None
            if start:
                return max(0, (datetime.datetime.now() - start).days)
        except ValueError:
            continue
    # epoch seconds?
    try:
        ts = float(start_date)
        if ts > 1_000_000_000:
            return max(0, (datetime.datetime.now() - datetime.datetime.fromtimestamp(ts)).days)
    except (ValueError, TypeError):
        pass
    return None


def normalize(raw_items: list[dict], platform: str) -> list[dict]:
    out = []
    for raw in raw_items:
        start = pick(raw, "start_date")
        media = pick(raw, "media_urls") or []
        if isinstance(media, dict):
            media = list(media.values())
        if not isinstance(media, list):
            media = [media]
        media = [as_text(m) for m in media][:5]
        out.append({
            "platform": platform,
            "advertiser": as_text(pick(raw, "advertiser")),
            "ad_id": as_text(pick(raw, "ad_id")),
            "text": as_text(pick(raw, "text")),
            "headline": as_text(pick(raw, "headline")),
            "cta": as_text(pick(raw, "cta")),
            "media_type": ("video" if any("video" in m.lower() for m in media) else "image" if media else "unknown"),
            "media_urls": media,
            "start_date": as_text(start),
            "days_running": days_running(start),
            "impressions_range": as_text(pick(raw, "impressions_range")),
        })
    return out


def api(path: str, token: str, payload=None, params=None):
    qs = urllib.parse.urlencode({"token": token, **(params or {})})
    url = f"{BASE_URL}{path}?{qs}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def run_actor(token: str, actor_id: str, run_input: dict, timeout: int = 600) -> list[dict]:
    print(f"starting actor {actor_id}...", file=sys.stderr)
    run = api(f"/acts/{actor_id}/runs", token, payload=run_input)
    run_id = run["data"]["id"]
    deadline = time.time() + timeout
    status_data = None
    while time.time() < deadline:
        status_data = api(f"/acts/{actor_id}/runs/{run_id}", token)
        status = status_data["data"]["status"]
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            sys.exit(f"actor run {status}")
        time.sleep(5)
    else:
        sys.exit(f"actor run did not finish within {timeout}s")
    dataset_id = status_data["data"]["defaultDatasetId"]
    items = api(f"/datasets/{dataset_id}/items", token, params={"format": "json"})
    print(f"fetched {len(items)} raw items", file=sys.stderr)
    return items


def build_input(platform: str, advertiser: str | None, keyword: str | None, max_items: int) -> dict:
    # Minimal, actor-agnostic input; most ad-library actors accept these names.
    # If a chosen actor needs different input keys, pass --input-json.
    base = {"maxItems": max_items, "count": max_items}
    if advertiser:
        base.update({"searchTerms": [advertiser], "companyName": advertiser, "query": advertiser})
    if keyword:
        base.update({"searchTerms": [keyword], "query": keyword})
    return base


def main():
    ap = argparse.ArgumentParser(description="Pull + normalize ad library ads via Apify")
    ap.add_argument("--platform", required=True, choices=["meta", "linkedin"])
    ap.add_argument("--advertiser")
    ap.add_argument("--keyword")
    ap.add_argument("--max-items", type=int, default=50)
    ap.add_argument("--actor", help="override the default Apify actor id")
    ap.add_argument("--input-json", help="raw JSON string used verbatim as actor input")
    ap.add_argument("--output", required=True)
    ap.add_argument("--dump-raw", help="also save the raw actor output here")
    ap.add_argument("--normalize-only", help="skip Apify; normalize a saved raw dump file")
    args = ap.parse_args()

    if args.normalize_only:
        with open(args.normalize_only, encoding="utf-8") as f:
            raw_items = json.load(f)
    else:
        if not (args.advertiser or args.keyword):
            ap.error("--advertiser or --keyword required (unless --normalize-only)")
        token = os.environ.get("APIFY_API_TOKEN") or sys.exit("error: set APIFY_API_TOKEN")
        actor = args.actor or DEFAULT_ACTORS[args.platform]
        run_input = json.loads(args.input_json) if args.input_json else build_input(
            args.platform, args.advertiser, args.keyword, args.max_items)
        raw_items = run_actor(token, actor, run_input)
        if args.dump_raw:
            with open(args.dump_raw, "w", encoding="utf-8") as f:
                json.dump(raw_items, f, indent=2, ensure_ascii=False)

    ads = normalize(raw_items, args.platform)
    empty_text = sum(1 for a in ads if not a["text"] and not a["headline"])
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ads, f, indent=2, ensure_ascii=False)
    print(f"normalized {len(ads)} ads → {args.output}")
    if ads and empty_text / len(ads) > 0.5:
        print(f"WARNING: {empty_text}/{len(ads)} ads have no text/headline — the actor's field names "
              f"probably aren't in FIELD_CANDIDATES yet. Re-run with --dump-raw, inspect, extend the map.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
