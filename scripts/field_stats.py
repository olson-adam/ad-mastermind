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


STOPWORDS = set("""a an and are as at be but by for from get has have how i if in is it its my no not of on or our
so that the their them they this to was we what when where which who will with you your yours can
en ett och att av data det din ditt du er för från har hur i inte kan med när på om oss så som till upp ut var vi vår
""".split())


def sentences(text: str) -> list[str]:
    """Split into sentence-ish segments — n-grams must never cross these
    boundaries (crossing manufactures phrases that don't exist, like
    'stack northwind' from '…finance stack. Northwind Card is…')."""
    parts = re.split(r"[.!?\n]+|\s\|\s|[•·]", text)
    return [p.strip() for p in parts if p.strip()]


def norm_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\såäöüéèê']", " ", s.lower())).strip()


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^\w\såäöüéèê']", " ", text)
    return [w for w in text.split() if len(w) > 1]


def ngrams(tokens: list[str], n: int) -> list[str]:
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def detect_boilerplate_sentences(ads: list[dict]) -> set[str]:
    """Structural boilerplate detection: a sentence appearing (normalized) in
    >60% of one advertiser's ads (advertiser has ≥5 ads) is a repeated block —
    legal disclaimers, taglines-as-signatures — and is stripped BEFORE
    n-gramming so neither it nor its neighbors can occupy convention slots.
    Works cross-advertiser too: a disclaimer shared by three advertisers is
    detected per advertiser and stripped for each."""
    from collections import Counter as C, defaultdict as dd
    per_adv_counts: dd[str, C] = dd(C)
    per_adv_ads: C = C()
    for a in ads:
        per_adv_ads[a["advertiser"]] += 1
        seen = set()
        for s in sentences(f"{a.get('headline','')}\n{a.get('text','')}"):
            ns = norm_sentence(s)
            if len(ns.split()) >= 3 and ns not in seen:
                seen.add(ns)
                per_adv_counts[a["advertiser"]][ns] += 1
    boiler: set[str] = set()
    for adv, counts in per_adv_counts.items():
        n_ads = per_adv_ads[adv]
        if n_ads < 5:
            continue
        for ns, c in counts.items():
            if c / n_ads > 0.6:
                boiler.add(ns)
    return boiler


def main():
    ap = argparse.ArgumentParser(description="Field stats over normalized ads")
    ap.add_argument("--ads", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    ads = []
    for path in args.ads:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list) or (data and not isinstance(data[0], dict) or (data and "advertiser" not in data[0])):
            sys.exit(f"error: {path} is not a normalized ads file (expected a JSON array from pull_ads.py) — "
                     f"did a stats/output file land in your --ads glob?")
        ads.extend(data)
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

    boiler_sentences = detect_boilerplate_sentences(ads)
    phrase_counts: Counter = Counter()
    phrase_advertisers: defaultdict[str, set] = defaultdict(set)
    boiler_counts: Counter = Counter()
    boiler_advertisers: defaultdict[str, set] = defaultdict(set)
    for a in ads:
        seen_creative: set[str] = set()
        seen_boiler: set[str] = set()
        for s in sentences(f"{a.get('headline','')}\n{a.get('text','')}"):
            ns = norm_sentence(s)
            target = seen_boiler if ns in boiler_sentences else seen_creative
            tokens = tokenize(s)
            for n in (2, 3):
                target.update(ngrams(tokens, n))
        for g in seen_creative:
            phrase_counts[g] += 1
            phrase_advertisers[g].add(a["advertiser"])
        for g in seen_boiler:
            boiler_counts[g] += 1
            boiler_advertisers[g].add(a["advertiser"])

    def content_bearing(g: str) -> bool:
        """Drop pure function-word fragments — a convention must carry meaning."""
        words = g.split()
        return sum(1 for w in words if w not in STOPWORDS) >= max(1, len(words) - 1) and \
            not (words[0] in STOPWORDS and words[-1] in STOPWORDS)

    BOILERPLATE = re.compile(
        r"\b(terms|conditions|issued by|fdic|member|bank|apply|rights reserved|privacy|villkor|gäller|utges av)\b")

    def is_boilerplate(g: str) -> bool:
        """Legal/compliance fragments are a real field fact but not creative conventions —
        they get their own bucket instead of eating the wallpaper/house slots."""
        return bool(BOILERPLATE.search(g))

    def dedupe_contained(rows: list[dict]) -> list[dict]:
        """Collapse a phrase into a higher-ranked one when it's a substring OR
        shares all-but-one of its words (overlap clustering — stops one long
        sentence from occupying five slots as sliding n-gram variants)."""
        kept: list[dict] = []
        for r in rows:
            rw = set(r["phrase"].split())
            def same_cluster(k):
                kw = set(k["phrase"].split())
                shorter = min(len(rw), len(kw))
                return (r["phrase"] in k["phrase"] or k["phrase"] in r["phrase"]
                        or len(rw & kw) >= max(2, shorter - 1))
            if any(same_cluster(k) for k in kept):
                continue
            kept.append(r)
        return kept

    # wallpaper phrases: shared by 2+ advertisers — ranked by advertiser BREADTH first,
    # then ad count, BEFORE any truncation (a convention 3 advertisers each use once
    # must beat a fragment one advertiser spams).
    wp_candidates = sorted(
        (g for g in phrase_counts if len(phrase_advertisers[g]) >= 2 and content_bearing(g)
         and not is_boilerplate(g)),
        key=lambda g: (-len(phrase_advertisers[g]), -phrase_counts[g], g),  # alphabetical tiebreak = determinism
    )
    wallpaper = dedupe_contained([
        {"phrase": g, "ads": phrase_counts[g], "advertisers": sorted(phrase_advertisers[g])}
        for g in wp_candidates
    ])[:args.top]
    # house phrases: recurring within a single advertiser (≥3 ads) — their own conventions/fatigue
    house = dedupe_contained([
        {"phrase": g, "ads": phrase_counts[g], "advertiser": next(iter(phrase_advertisers[g]))}
        for g in sorted(
            (g for g in phrase_counts if len(phrase_advertisers[g]) == 1
             and phrase_counts[g] >= 3 and content_bearing(g) and not is_boilerplate(g)),
            key=lambda g: (-phrase_counts[g], g),
        )
    ])[:args.top]
    # boilerplate: reported as whole repeated BLOCKS (one field fact each), never fragments
    block_ads: Counter = Counter()
    block_advs: defaultdict[str, set] = defaultdict(set)
    for a in ads:
        hit = {norm_sentence(s) for s in sentences(f"{a.get('headline','')}\n{a.get('text','')}")} & boiler_sentences
        for ns in hit:
            block_ads[ns] += 1
            block_advs[ns].add(a["advertiser"])
    boiler = [
        {"phrase": ns, "ads": c, "advertisers": sorted(block_advs[ns])}
        for ns, c in sorted(block_ads.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    ]

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
        "house_phrases": house,
        "boilerplate_phrases": boiler,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"=== FIELD: {len(ads)} ads · {len(by_advertiser)} advertisers · platforms {dict(by_platform)}")
    print(f"longevity: median {longevity['median_days']}d · {longevity['share_over_90d']} run ≥90d")
    print("wallpaper phrases (2+ advertisers):")
    for w in wallpaper[:8]:
        print(f"  “{w['phrase']}” × {w['ads']} ads ({len(w['advertisers'])} advertisers)")
    if house:
        print("house phrases (single advertiser, ≥3 ads):")
        for h in house[:8]:
            print(f"  “{h['phrase']}” × {h['ads']} ads ({h['advertiser']})")
    if boiler:
        print(f"compliance boilerplate (reported separately): {len(boiler)} pattern(s), e.g. “{boiler[0]['phrase']}” × {boiler[0]['ads']}")
    print(f"saved → {args.output}")


if __name__ == "__main__":
    main()
