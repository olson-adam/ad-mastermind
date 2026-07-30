# The Gauntlet — blind evaluation protocol

Answers *measured, not felt*: *do the generated concepts stand indistinguishable next to real work?* Two sub-questions: **level** (do they land in the target score band?) and **parity** (can a judge tell which items are generated vs real?). The protocol exists because self-scoring is provably too kind — our testing found self-scores run 1–1.5 steps above independent judgment.

**The field twist:** the comparison set isn't only awarded classics — it's the field's REAL running ads (pulled in step 1). Beating the market you'll actually appear next to is the honest bar; beating Think Small is not the assignment.

## Step 0 — Building `items.json`

Recommended mix: **5 generated · 5 field · ≥3 negative anchors · 2 benchmarks** (prep enforces ≥2 anchors; without them the discrimination control can't run).

- `generated` — the delivered concepts.
- `field` — real ads from the field pull. **Normalize them into the SAME shape as concept sketches** (one-liner + what-you-see sketch), never as raw ad copy with CTA lines — our logged run proved that ad-copy-shaped items are instantly recognizable and the blinding fails (learning 5 below). Video ads: describe the visible concept, and either mark them `impossible_to_deidentify` or exclude them when the ladder's static calibration matters.
- `negative-anchor` — wallpaper-pattern items **written fresh** (not copied from benchmarks.md's band 3–4 list, which judges receive as calibration — an anchor the judge has just read the answer to tests obedience, not judgment). **Anchor difficulty is author-set, so don't soften the control with strawmen:** anchors should be *competent* wallpaper (well-made dashboard-hero, polished testimonial), because a control that only catches garbage validates nothing.
- `benchmark` — canon mechanisms, de-identified. Must be DIFFERENT entries from the 6 calibration examples handed to judges (those never appear in a test set).
- **Entity scrub:** build a forbid-list from the field corpus's advertiser names, the normalized ads' `paid_by` values, and any banks/partners/people in the copy, then run `gauntlet_prep.py --forbid entities.txt`. Our logged run leaked a card-issuer name that identified the advertiser in one search.

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

**De-identification limits:** world-famous campaigns are recognizable from the idea itself — acceptable; the judge scores the idea as if new today, and recognition shows up in the parity metric as information. Items impossible to de-identify are marked in the mapping (benchmark/field only — prep rejects the flag on generated items, which would exempt your own concepts from parity).

## Step 2 — Judges

- **3 fresh instances** (subagents with no session context — never the session that generated the concepts).
- Each judge receives: (a) [height-ladder.md](height-ladder.md) in full, (b) **6 calibration examples** from [benchmarks.md](benchmarks.md) (2× band 8–10, 2× band 6–7, 2× band 3–4 — never part of the test set), (c) the blinded list.
- Per item, the judge returns: **height 1–10** (integer) + one-line justification + **Lemon profile** + **source guess**: `real ad` / `generated` / `can't tell`.

**Judge prompt template** (fill the brackets; whole final response must be the JSON array only):

> You are an independent creative judge for static B2B advertising. You have no other context and should use none.
> STEP 1: Read [absolute path to height-ladder.md] in full.
> STEP 2: Calibrate against these six scored examples (answer key — NOT in your test set): [six calibration examples with facit levels]. Assume your instinct scores too kindly — anchor hard against these.
> STEP 3: Judge all [N] items below. Your ENTIRE response must be ONLY a strict JSON array, no markdown fences:
> `[{"number": 1, "height": 7, "justification": "…", "lemon": "right: …; left: …", "source_guess": "real ad|generated|can't tell"}, …]`
> THE ITEMS: [paste the blinded list]

**Verdict file schema** (what `gauntlet_score.py` requires — one file per judge): a JSON array where every item has integer `number`, integer `height`, and `source_guess`; `justification` and `lemon` are kept for the record but not scored.

## Step 3 — Scoring (deterministic, scripted)

```
python3 <skill-dir>/scripts/gauntlet_score.py --verdicts j1.json j2.json j3.json \
    --mapping mapping.json --output scorecard.json
```

| Metric | Definition | Pass |
|---|---|---|
| **Height** | median of 3 judges per item | generated set's median ≥7, and ≥ the field ads' median (beating the market is the floor) |
| **Discrimination** | negative anchors' (wallpaper items') median | ≤5 — otherwise the judges are too kind and **the whole run is invalid** |
| **Spread flag** | judge disagreement ≥3 levels on one item | flagged for human review — the human's taste is the answer key; the protocol adjusts, not their verdict |
| **Parity** | correct source guesses on generated items (excl. `can't tell`) | descriptive, not pass/fail — but a parity rate ≥80% (with ≥6 non-abstain guesses) sets `blinding_failed: true` on the scorecard: the height comparison stands (its gates passed), and the word "blind" may not be used about the run |

## Integrity rules

- The generating session NEVER judges its own concepts. Judges are always fresh instances.
- Benchmark scores are never sent to judges except the 6 calibration examples.
- Mapping and all raw verdicts are saved to the run directory (`field-data/gauntlet-runs/{date}-{run}/` — under the gitignored working area, never in version control); no summary numbers without traceable raw data.
- Every run's scorecard states its seed, item counts per source, and any excluded items — silent exclusions invalidate the run.
- If discrimination fails (anchors > 5) or calibration fails (benchmarks < 8), the run is INVALID — fix, rerun, never cherry-pick. `gauntlet_score.py` exit codes: 0 full pass · 1 invalid run · 2 valid but below the floor OR partial mix (prep's `--partial`) · 3 input error (broken/duplicate verdict files — fix inputs, not calibration). Duplicate judge files are rejected by hash: three INDEPENDENT judges, always.

## Logged protocol learnings (kept because they're the point)

1. Self-scoring runs 1–1.5 levels kind vs independent judges — every self-score is provisional until judged blind.
2. A generous normalizer can lift weak items 2+ levels — normalization describes, never sells.
3. Text-format blind testing systematically underrates craft-carried concepts (premium/materiality work): for those, the blind score is a floor, not a ceiling — note it on the scorecard.
4. Parity is confounded when the generated subset style-clusters; treat it as descriptive telemetry.
5. **(2026-07-30 run):** parity is also confounded by *item shape* — real ads normalized from ad copy ("Video ad. Copy: … CTA: Learn more") read as ads, concept sketches read as concepts, and judges guessed source correctly on every item while still discriminating quality cleanly (anchors 3, classics 8–9). Fix candidates for future runs: normalize both directions into one shape (rewrite real ads as concept sketches too). Until then, parity stays descriptive and level is the metric.
6. **(2026-07-30 run):** judge model family = generator model family is an affinity risk that can't be excluded from within the run; mitigations observed working: hard negative anchors (scored 3), benchmark facit reproduced (9/8), and a generated item the gate itself doubted landing at 6. Cross-model judging is the structural fix when available.
