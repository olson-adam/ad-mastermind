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


def is_template(s: str) -> bool:
    return "{{" in s  # dynamic product ads carry {{product.name}}-style variables


def normalize_meta_adlib(raw: dict) -> dict | None:
    """Extractor verified live against curious_coder~facebook-ads-library-scraper
    (2026-07-30). Dynamic product ads keep their real content in snapshot.cards[]."""
    snap = raw.get("snapshot") or {}
    cards = snap.get("cards") or []
    card = cards[0] if cards else {}

    def first_real(*vals):
        vals = [as_text(v) for v in vals if v not in (None, "", [], {})]
        real = [v for v in vals if v and not is_template(v)]
        return real[0] if real else (vals[0] if vals else "")

    body = snap.get("body") or {}
    text = first_real(card.get("body"), body.get("text") if isinstance(body, dict) else body,
                      snap.get("link_description"), card.get("link_description"))
    media, media_type = [], "unknown"
    for c in cards or [snap]:
        if c.get("video_sd_url") or c.get("video_hd_url"):
            media_type = "video"
            media.append(as_text(c.get("video_preview_image_url") or c.get("video_sd_url")))
        elif c.get("original_image_url") or c.get("resized_image_url") or c.get("image_url"):
            media_type = "image" if media_type == "unknown" else media_type
            media.append(as_text(c.get("original_image_url") or c.get("resized_image_url") or c.get("image_url")))
    start = raw.get("start_date_formatted") or raw.get("start_date")
    imp = raw.get("impressions_with_index") or {}
    return {
        "platform": "meta",
        "advertiser": as_text(raw.get("page_name")),
        "page_id": as_text(raw.get("page_id")),
        "ad_id": as_text(raw.get("ad_archive_id") or raw.get("ad_id")),
        "text": text,
        "headline": first_real(card.get("title"), snap.get("title")),
        "cta": as_text(snap.get("cta_text") or card.get("cta_text") or snap.get("cta_type")),
        "media_type": media_type,
        "media_urls": media[:5],
        "start_date": as_text(start),
        "days_running": days_running(raw.get("start_date") or start),
        "is_active": raw.get("is_active"),
        "publisher_platforms": raw.get("publisher_platform") or [],
        "dynamic_template": is_template(as_text((body or {}).get("text", "") if isinstance(body, dict) else "")),
        "impressions_range": as_text(imp.get("impressions_text") or ""),
    }


def normalize(raw_items: list[dict], platform: str) -> list[dict]:
    out = []
    for raw in raw_items:
        if platform == "meta" and ("snapshot" in raw or "ad_archive_id" in raw):
            row = normalize_meta_adlib(raw)
            if row:
                out.append(row)
            continue
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


def build_input(platform: str, advertiser: str | None, keyword: str | None, max_items: int, country: str = "US", page_id: str | None = None) -> dict:
    """Input builders verified against the default actors' input schemas
    (via /builds/default/openapi.json). Other actors: pass --input-json."""
    term = advertiser or keyword
    if platform == "meta":
        # curious_coder~facebook-ads-library-scraper requires Ad Library URLs.
        # Keyword search is noisy — prefer --page-id (find it in a keyword pull's
        # page_id field) for a clean single-advertiser pull.
        if page_id:
            adlib = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
                     f"&country={country}&view_all_page_id={page_id}")
        else:
            adlib = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
                     f"&country={country}&q={urllib.parse.quote(term or '')}&search_type=keyword_unordered&media_type=all")
        return {"urls": [{"url": adlib}], "count": max_items, "limitPerSource": max_items,
                "scrapeAdDetails": False}
    # linkedin default actor: generic term input, tolerant keys
    return {"searchTerms": [term], "companyName": term, "query": term,
            "maxItems": max_items, "count": max_items}


def main():
    ap = argparse.ArgumentParser(description="Pull + normalize ad library ads via Apify")
    ap.add_argument("--platform", required=True, choices=["meta", "linkedin"])
    ap.add_argument("--advertiser")
    ap.add_argument("--keyword")
    ap.add_argument("--page-id", help="Meta page id for a clean single-advertiser pull (found in keyword-pull output)")
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
        if not (args.advertiser or args.keyword or args.page_id):
            ap.error("--advertiser, --keyword or --page-id required (unless --normalize-only)")
        token = os.environ.get("APIFY_API_TOKEN") or sys.exit("error: set APIFY_API_TOKEN")
        actor = args.actor or DEFAULT_ACTORS[args.platform]
        run_input = json.loads(args.input_json) if args.input_json else build_input(
            args.platform, args.advertiser, args.keyword, args.max_items, page_id=args.page_id)
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
