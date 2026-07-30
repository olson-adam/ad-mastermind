#!/usr/bin/env python3
"""Score a gauntlet run from three judges' verdicts + the sealed mapping.

Usage:
    python3 gauntlet_score.py --verdicts j1.json j2.json j3.json --mapping mapping.json --output scorecard.json

Each verdict file: [{"number": 1, "height": 7, "justification": "...",
                     "source_guess": "real ad|generated|can't tell"}, ...]

Computes per-item medians, per-source level stats, the discrimination control
(negative anchors must median ≤5 or the run is INVALID), spread flags (judge
disagreement ≥3), and descriptive parity. Exit 1 when the run is invalid.
"""
import argparse
import json
import statistics
import sys


def main():
    ap = argparse.ArgumentParser(description="Score a gauntlet run")
    ap.add_argument("--verdicts", nargs=3, required=True, help="exactly three judge files")
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    judges = []
    for path in args.verdicts:
        with open(path, encoding="utf-8") as f:
            judges.append({v["number"]: v for v in json.load(f)})
    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)

    items = []
    for m in mapping["items"]:
        n = m["number"]
        verdicts = [j.get(n) for j in judges]
        if any(v is None for v in verdicts):
            sys.exit(f"error: item {n} missing from at least one judge — all judges score all items")
        heights = [int(v["height"]) for v in verdicts]
        items.append({
            "number": n,
            "source": m["source"],
            "median": statistics.median(heights),
            "heights": heights,
            "spread_flag": max(heights) - min(heights) >= 3,
            "guesses": [v.get("source_guess", "can't tell") for v in verdicts],
            "excluded_from_parity": m.get("impossible_to_deidentify", False),
        })

    def medians(source):
        vals = [i["median"] for i in items if i["source"] == source]
        return {
            "n": len(vals),
            "median": statistics.median(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
        }

    gen, field, neg = medians("generated"), medians("field"), medians("negative-anchor")

    discrimination_ok = neg["median"] is not None and neg["median"] <= 5
    level_ok = (gen["median"] is not None and gen["median"] >= 7
                and (field["median"] is None or gen["median"] >= field["median"]))

    # Parity — descriptive only
    parity_pool = [i for i in items if i["source"] == "generated" and not i["excluded_from_parity"]]
    guesses = [g for i in parity_pool for g in i["guesses"] if g != "can't tell"]
    correct = sum(1 for i in parity_pool for g in i["guesses"] if g == "generated")

    scorecard = {
        "seed": mapping.get("seed"),
        "mix": mapping.get("counts"),
        "run_valid": discrimination_ok,
        "verdict": (
            "INVALID — judges too kind (negative anchors median > 5); fix calibration and rerun"
            if not discrimination_ok else
            "PASS — level floor met" if level_ok else
            "DID NOT PASS — generated set below the level floor"
        ),
        "levels": {"generated": gen, "field": field, "negative_anchor": neg,
                   "benchmark": medians("benchmark")},
        "parity_descriptive": {
            "guessable_generated_items": len(parity_pool),
            "non-abstain_guesses": len(guesses),
            "guessed_generated_correctly": correct,
            "note": "descriptive telemetry only — confounded when the generated set style-clusters",
        },
        "spread_flags": [i["number"] for i in items if i["spread_flag"]],
        "items": items,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2, ensure_ascii=False)

    print(f"GAUNTLET — seed {scorecard['seed']} · mix {scorecard['mix']}")
    print(f"generated: median {gen['median']} (n={gen['n']}) · field: median {field['median']} · negative anchors: median {neg['median']}")
    print(f"spread flags (human review): {scorecard['spread_flags'] or 'none'}")
    print(f"→ {scorecard['verdict']}")
    sys.exit(0 if discrimination_ok else 1)


if __name__ == "__main__":
    main()
