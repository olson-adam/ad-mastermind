#!/usr/bin/env python3
"""Mechanically enforce the kill-gate's portfolio rules on a delivered spec file.

The model writes the specs; this script refuses to let it self-report compliance.
Usage:
    python3 spec_check.py --specs concepts.md --field-stats field-stats.json

Parses `### n. name` blocks with `**Key:** value` lines (the concept-spec format)
and exits 1 unless ALL of these hold:
  - 5–8 concepts
  - ≥4 distinct mechanisms
  - ≥2 distinct registers            (from the **Register:** field)
  - ≥50% playful temperature         (from the **Temperature:** field; pass --premium to invert)
  - ≥50% robust (floor score ≥6)
  - median height ≥7
  - no two concepts share mechanism AND insight
  - every spec has ALL template fields filled, a mechanism from the library and a
    register from the approved list (max 2 pure-text registers per set)
  - every **Field convention broken:** value QUOTES (in quotation marks) a phrase that
    exists in field-stats.json (wallpaper/house/CTA — boilerplate excluded) or honestly
    says "in-convention"
"""
import argparse
import json
import re
import statistics
import sys


def parse_specs(text: str) -> list[dict]:
    blocks = re.split(r"^### +\d+\.", text, flags=re.M)[1:]
    specs = []
    for b in blocks:
        spec = {"_name": b.strip().splitlines()[0].strip() if b.strip() else "?"}
        for m in re.finditer(r"\*\*([A-Za-z -]+):\*\*\s*([^*\n]+)", b):
            spec[m.group(1).strip().lower()] = m.group(2).strip()
        specs.append(spec)
    return specs


def first_int(s: str) -> int | None:
    m = re.search(r"\d+", s or "")
    return int(m.group(0)) if m else None


def main():
    ap = argparse.ArgumentParser(description="Enforce portfolio rules on delivered specs")
    ap.add_argument("--specs", required=True)
    ap.add_argument("--field-stats", required=True)
    ap.add_argument("--premium", action="store_true", help="invert the temperature quota (dry-first briefs)")
    args = ap.parse_args()

    with open(args.specs, encoding="utf-8") as f:
        specs = parse_specs(f.read())
    with open(args.field_stats, encoding="utf-8") as f:
        stats = json.load(f)

    # boilerplate is deliberately EXCLUDED — legal text is not a creative convention to break
    known_phrases = {w["phrase"].lower() for w in stats.get("wallpaper_phrases", [])}
    known_phrases |= {h["phrase"].lower() for h in stats.get("house_phrases", [])}
    known_phrases |= {c.lower() for c in stats.get("top_ctas", {})}

    MECHANISMS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
                  "analogy", "juxtaposition", "dramatized", "exaggeration", "culture",
                  "villain", "insider", "pun", "device", "demonstration", "documentary", "artifact"}
    REGISTERS = {"documentary photographic", "typographic wit", "graphic system",
                 "artifact", "photo-meme", "illustration", "photography"}
    TEXT_REGISTERS = {"typographic wit"}
    REQUIRED_FIELDS = ["one-liner", "sketch", "mechanism", "register", "temperature", "insight",
                       "field convention broken", "nearest field neighbor", "height",
                       "lemon profile", "series potential", "fragile flags", "thumbnail test"]

    fails, warns = [], []
    if not 5 <= len(specs) <= 8:
        fails.append(f"{len(specs)} concepts — the delivery is 5–8")

    for s in specs:
        missing = [f for f in REQUIRED_FIELDS if not s.get(f)]
        if missing:
            fails.append(f"'{s['_name']}': missing spec fields: {', '.join(missing)} — every template field is mandatory")

    mechanisms = [s.get("mechanism", "").split(",")[0].strip().lower() for s in specs]
    for s, m in zip(specs, mechanisms):
        token = m.split()[0] if m else ""
        if token not in MECHANISMS and not any(name in m for name in MECHANISMS if not name.isdigit()):
            fails.append(f"'{s['_name']}': mechanism '{m}' is not one of the 12 in mechanisms.md")
    if len({m for m in mechanisms if m}) < 4:
        fails.append(f"only {len(set(mechanisms))} distinct mechanisms — portfolio rule requires ≥4")

    registers = [s.get("register", "").strip().lower() for s in specs]
    if any(not r for r in registers):
        fails.append("missing **Register:** field on one or more specs (documentary/typographic/graphic/artifact/…)")
    else:
        for s, r in zip(specs, registers):
            if not any(known in r for known in REGISTERS):
                fails.append(f"'{s['_name']}': register '{r}' is not in the concept-spec register list")
        if len(set(registers)) < 2:
            fails.append("only 1 register across the set — voice-diversity rule requires ≥2")
        text_count = sum(1 for r in registers if any(k in r for k in TEXT_REGISTERS))
        if text_count > 2:
            fails.append(f"{text_count} pure text concepts — portfolio rule caps at 2 per set")

    temps = [s.get("temperature", "").strip().lower() for s in specs]
    if any(not t for t in temps):
        fails.append("missing **Temperature:** field on one or more specs (playful|dry)")
    else:
        playful = sum(1 for t in temps if "playful" in t)
        quota_met = (playful * 2 >= len(specs)) if not args.premium else ((len(specs) - playful) * 2 >= len(specs))
        if not quota_met:
            fails.append(f"temperature quota failed: {playful}/{len(specs)} playful "
                         f"({'≥50% playful required' if not args.premium else '≥50% dry required (--premium)'})")

    floors = [first_int(s.get("floor score") or s.get("floor", "")) for s in specs]
    if any(f is None for f in floors):
        fails.append("missing/unparsable **Floor score:** on one or more specs")
    elif sum(1 for f in floors if f >= 6) * 2 < len(specs):
        fails.append(f"floor-score spread failed: only {sum(1 for f in floors if f >= 6)}/{len(specs)} robust (floor ≥6)")

    heights = [first_int(s.get("height", "")) for s in specs]
    if any(h is None for h in heights):
        fails.append("missing/unparsable **Height:** on one or more specs")
    elif statistics.median(heights) < 7:
        fails.append(f"height median {statistics.median(heights)} < 7 (remember: self-scores are provisional AND kind)")

    pairs = set()
    for s, m in zip(specs, mechanisms):
        key = (m, re.sub(r"\W+", " ", s.get("insight", "").lower()).strip()[:60])
        if key in pairs:
            fails.append(f"test-cell violation: '{s['_name']}' shares mechanism+insight with another concept")
        pairs.add(key)

    for s in specs:
        conv = s.get("field convention broken", "")
        if not conv:
            fails.append(f"'{s['_name']}': missing **Field convention broken:** field")
            continue
        if "in-convention" in conv.lower():
            warns.append(f"'{s['_name']}' is declared in-convention — allowed, but it must earn its place on height alone")
            continue
        quoted = [q.lower() for q in re.findall(r"[\"“']([^\"“”']{3,60})[\"”']", conv)]
        if not quoted:
            fails.append(f"'{s['_name']}': field convention must QUOTE a phrase (in quotation marks) from field-stats.json")
        elif not any(q in known_phrases for q in quoted):
            fails.append(f"'{s['_name']}': quoted convention {quoted} not found in field-stats.json "
                         f"(wallpaper/house/CTA — boilerplate does not count) — conventions come from measurement, not memory")

    print(f"spec-check: {len(specs)} concepts · mechanisms {sorted(set(m for m in mechanisms if m))}")
    for w in warns:
        print(f"  note: {w}")
    if fails:
        print("PORTFOLIO RULES FAILED:", file=sys.stderr)
        for f_ in fails:
            print(f"  ✗ {f_}", file=sys.stderr)
        sys.exit(1)
    print("all portfolio rules hold")


if __name__ == "__main__":
    main()
