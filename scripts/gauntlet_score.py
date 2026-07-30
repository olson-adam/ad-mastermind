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
    bench = medians("benchmark")

    discrimination_ok = neg["median"] is not None and neg["median"] <= 5
    # calibration floor: if canon benchmarks are in the mix, judges must place them high —
    # otherwise the scale is compressed and 'valid discrimination' is one-sided
    calibration_ok = bench["median"] is None or bench["median"] >= 8
    level_ok = (gen["median"] is not None and gen["median"] >= 7
                and (field["median"] is None or gen["median"] >= field["median"]))

    # Parity — descriptive; 100% correct guessing = the blinding failed, and the
    # scorecard must say so even when levels pass
    parity_pool = [i for i in items if i["source"] == "generated" and not i["excluded_from_parity"]]
    guesses = [g for i in parity_pool for g in i["guesses"] if g != "can't tell"]
    correct = sum(1 for i in parity_pool for g in i["guesses"] if g == "generated")
    blinding_failed = bool(guesses) and correct == len(guesses) and len(guesses) >= 6

    run_valid = discrimination_ok and calibration_ok
    scorecard = {
        "seed": mapping.get("seed"),
        "mix": mapping.get("counts"),
        "run_valid": run_valid,
        "blinding_failed": blinding_failed,
        "verdict": (
            "INVALID — judges too kind (negative anchors median > 5); fix calibration and rerun"
            if not discrimination_ok else
            "INVALID — judges miscalibrated (benchmark median < 8); fix calibration and rerun"
            if not calibration_ok else
            "PASS — level floor met" if level_ok else
            "DID NOT PASS — generated set below the level floor"
        ),
        "levels": {"generated": gen, "field": field, "negative_anchor": neg, "benchmark": bench},
        "parity_descriptive": {
            "guessable_generated_items": len(parity_pool),
            "non_abstain_guesses": len(guesses),
            "guessed_generated_correctly": correct,
            "note": "descriptive telemetry — confounded by style-clustering and item shape. "
                    "blinding_failed=true means source anonymity did NOT hold: the level comparison "
                    "stands (discrimination/calibration gates passed) but 'blind' may not be claimed.",
        },
        "spread_flags": [i["number"] for i in items if i["spread_flag"]],
        "items": items,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2, ensure_ascii=False)

    print(f"GAUNTLET — seed {scorecard['seed']} · mix {scorecard['mix']}")
    print(f"generated: median {gen['median']} (n={gen['n']}) · field: median {field['median']} · "
          f"anchors: median {neg['median']} · benchmarks: median {bench['median']}")
    if blinding_failed:
        print("⚑ BLINDING FAILED — every source guess on generated items was correct; "
              "report the level result, do not call it blind")
    print(f"spread flags (human review): {scorecard['spread_flags'] or 'none'}")
    print(f"→ {scorecard['verdict']}")
    # exit codes: 0 pass · 1 invalid run · 2 valid run, level floor not met
    sys.exit(0 if (run_valid and level_ok) else (1 if not run_valid else 2))


if __name__ == "__main__":
    main()
