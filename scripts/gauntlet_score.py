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
    ap.add_argument("--verdicts", nargs="+", required=True, help="exactly three judge files")
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if len(args.verdicts) != 3:
        print(f"error: exactly three judge files required, got {len(args.verdicts)}", file=sys.stderr)
        sys.exit(3)
    judges, payload_hashes = [], set()
    import hashlib
    for path in args.verdicts:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        h = hashlib.sha256(raw.encode()).hexdigest()
        if h in payload_hashes:
            print(f"error: {path} is byte-identical to another judge file — three INDEPENDENT judges required", file=sys.stderr)
            sys.exit(3)
        payload_hashes.add(h)
        judges.append({v["number"]: v for v in json.loads(raw)})
    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)

    items = []
    for m in mapping["items"]:
        n = m["number"]
        verdicts = [j.get(n) for j in judges]
        if any(v is None for v in verdicts):
            print(f"error: item {n} missing from at least one judge — all judges score all items (input error)", file=sys.stderr)
            sys.exit(3)
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
    parity_rate = (correct / len(guesses)) if guesses else None
    blinding_failed = parity_rate is not None and len(guesses) >= 6 and parity_rate >= 0.8

    complete_mix = (field["n"] or 0) >= 3 and (bench["n"] or 0) >= 2
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
            ("PASS — level floor met" if complete_mix else
             "PASS (PARTIAL MIX) — level floor met but field comparison/calibration gate never ran")
            if level_ok else
            "DID NOT PASS — generated set below the level floor"
        ),
        "complete_mix": complete_mix,
        "levels": {"generated": gen, "field": field, "negative_anchor": neg, "benchmark": bench},
        "parity_descriptive": {
            "guessable_generated_items": len(parity_pool),
            "non_abstain_guesses": len(guesses),
            "guessed_generated_correctly": correct,
            "parity_rate": parity_rate,
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
    if parity_rate is not None:
        print(f"parity rate: {parity_rate:.0%} correct source guesses on generated items (n={len(guesses)})")
    if blinding_failed:
        print("⚑ BLINDING FAILED (parity ≥80%, n≥6) — report the level result, do not call the run blind")
    print(f"spread flags (human review): {scorecard['spread_flags'] or 'none'}")
    print(f"→ {scorecard['verdict']}")
    # exit codes: 0 full pass · 1 invalid run · 2 valid but below floor OR partial mix · 3 input error
    sys.exit(0 if (run_valid and level_ok and complete_mix) else (1 if not run_valid else 2))


if __name__ == "__main__":
    main()
