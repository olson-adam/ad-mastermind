# The Gauntlet — blind evaluation protocol

Answers *measured, not felt*: *do the generated concepts stand indistinguishable next to real work?* Two sub-questions: **level** (do they land in the target score band?) and **parity** (can a judge tell which items are generated vs real?). The protocol exists because self-scoring is provably too kind — our testing found self-scores run 1–1.5 steps above independent judgment.

**The field twist:** the comparison set isn't only awarded classics — it's the field's REAL running ads (pulled in step 1). Beating the market you'll actually appear next to is the honest bar; beating Think Small is not the assignment.

## Step 1 — Blinding (deterministic, scripted)

```
python3 <skill-dir>/scripts/gauntlet_prep.py --items items.json --seed 42 \
    --blinded blinded.json --mapping mapping.json
```

`items.json`: `[{"source": "generated|field|benchmark|negative-anchor", "one_liner": …, "sketch": …, "category": …}, …]`. The script shuffles (seeded, reproducible), strips the source column, and writes the mapping separately. **The mapping is not opened until all verdicts are in.**

Before prep, every item is rewritten to **neutral format** by an instance that does not know the item's source:

- One-liner: the idea in one sentence
- Sketch: 2–3 lines — what you SEE, which copy carries, what the viewer completes
- Category/sender type (never brand names)

**Forbidden in neutral format:** brand names, awards, self-grades, mechanism tags, years, sources — and *selling* the mechanism: "what the viewer completes" describes neutrally, never advocates (our logged failure: a generous normalizer lifted weak items 2+ levels).

**De-identification limits:** world-famous campaigns are recognizable from the idea itself — acceptable; the judge scores the idea as if new today, and recognition shows up in the parity metric as information. Items impossible to de-identify are marked in the mapping and excluded from parity (kept for level calibration).

## Step 2 — Judges

- **3 fresh instances** (subagents with no session context — never the session that generated the concepts).
- Each judge receives: (a) [height-ladder.md](height-ladder.md) in full, (b) **6 calibration examples** from [benchmarks.md](benchmarks.md) (2× band 8–10, 2× band 6–7, 2× band 3–4 — never part of the test set), (c) the blinded list.
- Per item, the judge returns: **height 1–10** (integer) + one-line justification + **Lemon profile** + **source guess**: `real ad` / `generated` / `can't tell`.

## Step 3 — Scoring (deterministic, scripted)

```
python3 <skill-dir>/scripts/gauntlet_score.py --verdicts j1.json j2.json j3.json \
    --mapping mapping.json --output scorecard.json
```

| Metric | Definition | Pass |
|---|---|---|
| **Level** | median of 3 judges per item | generated set's median ≥7, and ≥ the field ads' median (beating the market is the floor) |
| **Discrimination** | negative anchors' (wallpaper items') median | ≤5 — otherwise the judges are too kind and **the whole run is invalid** |
| **Spread flag** | judge disagreement ≥3 levels on one item | flagged for human review — the human's taste is the answer key; the protocol adjusts, not their verdict |
| **Parity** | correct source guesses on generated items (excl. `can't tell`) | descriptive, not pass/fail — our logged learning: when a generated set clusters stylistically, judges detect "a generated suite" regardless of quality, so source-classification doesn't correlate with quality judgment |

## Integrity rules

- The generating session NEVER judges its own concepts. Judges are always fresh instances.
- Benchmark scores are never sent to judges except the 6 calibration examples.
- Mapping and all raw verdicts are saved to the run directory (`gauntlet-runs/{date}-{run}/`); no summary numbers without traceable raw data.
- Every run's scorecard states its seed, item counts per source, and any excluded items — silent exclusions invalidate the run.
- If discrimination fails, report "run invalid — judges too kind", fix calibration, rerun. Never cherry-pick the kinder run.

## Logged protocol learnings (kept because they're the point)

1. Self-scoring runs 1–1.5 levels kind vs independent judges — every self-score is provisional until judged blind.
2. A generous normalizer can lift weak items 2+ levels — normalization describes, never sells.
3. Text-format blind testing systematically underrates craft-carried concepts (premium/materiality work): for those, the blind score is a floor, not a ceiling — note it on the scorecard.
4. Parity is confounded when the generated subset style-clusters; treat it as descriptive telemetry.
5. **(2026-07-30 run):** parity is also confounded by *item shape* — real ads normalized from ad copy ("Video ad. Copy: … CTA: Learn more") read as ads, concept sketches read as concepts, and judges guessed source correctly on every item while still discriminating quality cleanly (anchors 3, classics 8–9). Fix candidates for future runs: normalize both directions into one shape (rewrite real ads as concept sketches too). Until then, parity stays descriptive and level is the metric.
6. **(2026-07-30 run):** judge model family = generator model family is an affinity risk that can't be excluded from within the run; mitigations observed working: hard negative anchors (scored 3), benchmark facit reproduced (9/8), and a generated item the gate itself doubted landing at 6. Cross-model judging is the structural fix when available.
