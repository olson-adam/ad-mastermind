#!/usr/bin/env python3
"""Deterministic field statistics over normalized ads (pull_ads.py output).

The model never computes these numbers — this script does. Model judgment
starts AFTER this output exists (message-code classification, white space).

Usage:
    python3 field_stats.py --ads field.json [more.json ...] --output field-stats.json
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\såäöüéèê']", " ", text)
    return [w for w in text.split() if len(w) > 1]


def ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def main():
    ap = argparse.ArgumentParser(description="Field stats over normalized ads")
    ap.add_argument("--ads", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    ads = []
    for path in args.ads:
        with open(path, encoding="utf-8") as f:
            ads.extend(json.load(f))
    if not ads:
        sys.exit("error: no ads")

    by_advertiser = Counter(a["advertiser"] or "(unknown)" for a in ads)
    by_platform = Counter(a["platform"] for a in ads)
    by_media = Counter(a["media_type"] for a in ads)
    by_cta = Counter(a["cta"].strip().lower() for a in ads if a.get("cta"))

    running = [a["days_running"] for a in ads if a.get("days_running") is not None]
    longevity = {
        "ads_with_start_date": len(running),
        "median_days": statistics.median(running) if running else None,
        "max_days": max(running) if running else None,
        "share_over_90d": round(sum(1 for d in running if d >= 90) / len(running), 2) if running else None,
        "share_under_14d": round(sum(1 for d in running if d < 14) / len(running), 2) if running else None,
    }
    # veterans: the ads that have run longest — the market's revealed preferences
    veterans = sorted((a for a in ads if a.get("days_running")), key=lambda a: -a["days_running"])[:10]

    phrase_counts: Counter = Counter()
    phrase_advertisers: defaultdict[str, set] = defaultdict(set)
    for a in ads:
        tokens = tokenize(f"{a.get('headline','')} {a.get('text','')}")
        for n in (2, 3):
            for g in set(ngrams(tokens, n)):
                phrase_counts[g] += 1
                phrase_advertisers[g].add(a["advertiser"])
    # wallpaper phrases: used by 2+ different advertisers — the category's shared language
    wallpaper = [
        {"phrase": g, "ads": c, "advertisers": sorted(phrase_advertisers[g])}
        for g, c in phrase_counts.most_common(200)
        if len(phrase_advertisers[g]) >= 2
    ][:args.top]

    result = {
        "total_ads": len(ads),
        "by_advertiser": dict(by_advertiser.most_common()),
        "by_platform": dict(by_platform),
        "by_media_type": dict(by_media),
        "top_ctas": dict(by_cta.most_common(args.top)),
        "longevity": longevity,
        "veterans": [
            {"advertiser": a["advertiser"], "days_running": a["days_running"],
             "headline": a.get("headline", "")[:80], "text": a.get("text", "")[:120]}
            for a in veterans
        ],
        "wallpaper_phrases": wallpaper,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"=== FIELD: {len(ads)} ads · {len(by_advertiser)} advertisers · platforms {dict(by_platform)}")
    print(f"longevity: median {longevity['median_days']}d · {longevity['share_over_90d']} run ≥90d")
    print("wallpaper phrases (2+ advertisers):")
    for w in wallpaper[:8]:
        print(f"  “{w['phrase']}” × {w['ads']} ads ({len(w['advertisers'])} advertisers)")
    print(f"saved → {args.output}")


if __name__ == "__main__":
    main()
