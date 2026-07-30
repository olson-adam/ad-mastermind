#!/usr/bin/env python3
"""Blind a mixed item set for gauntlet judging: seeded shuffle, source column
stripped, mapping written separately (opened only after all verdicts are in).

Usage:
    python3 gauntlet_prep.py --items items.json --seed 42 --blinded blinded.json --mapping mapping.json

items.json: [{"source": "generated|field|benchmark|negative-anchor",
              "one_liner": "...", "sketch": "...", "category": "...",
              "impossible_to_deidentify": false}, ...]
"""
import argparse
import json
import random
import sys

import re

REQUIRED = ("source", "one_liner", "sketch", "category")
SOURCES = {"generated", "field", "benchmark", "negative-anchor"}
# Protocol vocabulary only — ordinary English ("next level", "through one lens")
# must pass. Matched as word-bounded patterns.
BANNED_PATTERNS = [
    # protocol form only: "height: 7", "level=8", "7/10" — plain "Level 2 support" passes
    (r"\b(?:height|level)\s*[:=]\s*\d", "self-grade (height/level + number)"),
    (r"\b\d{1,2}\s*/\s*10\b", "self-grade (n/10)"),
    (r"\bmechanism\s*\d", "mechanism tag"),
    (r"\blens\s*\d", "mechanism tag"),
    (r"\baward(?:ed|-winning)?\b", "award reference"),
    (r"\bcannes\b|\bgrand prix\b|\bd&ad\b|\bguldägget\b", "award reference"),
]


def main():
    ap = argparse.ArgumentParser(description="Blind a gauntlet item set")
    ap.add_argument("--items", required=True)
    ap.add_argument("--seed", type=int, required=True, help="stated on the scorecard; makes the shuffle reproducible")
    ap.add_argument("--blinded", required=True)
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--partial", action="store_true",
                    help="allow a mix without field/benchmark items — the scorecard will say those gates never ran")
    ap.add_argument("--forbid", help="file with forbidden entity names (brands, banks, people), one per line — "
                                     "preload it from the field corpus's advertiser names + any entities in the copy")
    args = ap.parse_args()

    with open(args.items, encoding="utf-8") as f:
        items = json.load(f)

    forbidden_entities = []
    if args.forbid:
        with open(args.forbid, encoding="utf-8") as f:
            forbidden_entities = [w.strip().lower() for w in f if w.strip() and not w.startswith("#")]

    errors = []
    for i, item in enumerate(items):
        for key in REQUIRED:
            if not item.get(key):
                errors.append(f"item {i}: missing '{key}'")
        if item.get("source") not in SOURCES:
            errors.append(f"item {i}: source must be one of {sorted(SOURCES)}")
        text = f"{item.get('one_liner','')} {item.get('sketch','')} {item.get('category','')}".lower()
        for pattern, label in BANNED_PATTERNS:
            if re.search(pattern, text):
                errors.append(f"item {i}: neutral format violated — {label}")
        for ent in forbidden_entities:
            if re.search(rf"\b{re.escape(ent)}\b", text):
                errors.append(f"item {i}: de-identification leak — contains entity '{ent}'")
    counts = {s: sum(1 for it in items if it.get("source") == s) for s in SOURCES}
    if counts["generated"] == 0:
        errors.append("no generated items — nothing to evaluate")
    if counts["negative-anchor"] < 2:
        errors.append("need ≥2 negative anchors — without them the discrimination control can't run")
    if not args.partial:
        if counts["field"] < 3:
            errors.append("need ≥3 field items for the market comparison (or run with --partial and "
                          "accept a scorecard that says the field gate never ran)")
        if counts["benchmark"] < 2:
            errors.append("need ≥2 benchmark items for the calibration gate (or run with --partial)")
    for i, item in enumerate(items):
        if item.get("source") == "generated" and item.get("impossible_to_deidentify"):
            errors.append(f"item {i}: impossible_to_deidentify is not allowed on generated items — "
                          f"it would exempt your own concepts from the parity metric")
    if errors:
        print("BLOCKED:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)

    rng = random.Random(args.seed)
    order = list(range(len(items)))
    rng.shuffle(order)

    blinded, mapping = [], []
    for num, idx in enumerate(order, 1):
        it = items[idx]
        blinded.append({
            "number": num,
            "one_liner": it["one_liner"],
            "sketch": it["sketch"],
            "category": it["category"],
        })
        mapping.append({
            "number": num,
            "source": it["source"],
            "impossible_to_deidentify": bool(it.get("impossible_to_deidentify")),
            "original_index": idx,
        })

    with open(args.blinded, "w", encoding="utf-8") as f:
        json.dump(blinded, f, indent=2, ensure_ascii=False)
    with open(args.mapping, "w", encoding="utf-8") as f:
        json.dump({"seed": args.seed, "counts": counts, "items": mapping}, f, indent=2, ensure_ascii=False)
    print(f"blinded {len(items)} items (seed {args.seed}) → {args.blinded}; mapping sealed → {args.mapping}")
    print(f"mix: {counts}")


if __name__ == "__main__":
    main()
