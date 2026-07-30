# Example run — fictional fleet-telematics category

Everything here uses fictional brands (TrackNord, FleetBase, Veholt; concepts for the fictional "Nordvik"). The raw fixtures mirror the live-verified actor schemas for both platforms, and dates are frozen with `--as-of 2026-07-30`, so the whole chain reproduces offline, byte for byte:

```
python3 ../scripts/pull_ads.py --normalize-only fixtures/meta-raw.json --platform meta --as-of 2026-07-30 --output fixtures/field.json
python3 ../scripts/pull_ads.py --normalize-only fixtures/linkedin-raw.json --platform linkedin --as-of 2026-07-30 --output fixtures/linkedin.json
python3 ../scripts/field_stats.py --ads fixtures/field.json fixtures/linkedin.json --output fixtures/field-stats.json
```

## 1. The field brief

*Source: fixtures/field-stats.json — every number script-computed from the commands above.*

9 active ads (7 Meta + 2 LinkedIn) · 3 advertisers · median 89 days running (44% ≥90d) · media mix 8 image / 1 video.
**Wallpaper phrases:** "full kontroll" — 6 ads across ALL 3 advertisers · "boka demo" — 4 ads, 2 advertisers.
**CTA mix:** Book a demo ×6, Learn more ×2, Get started ×1.
**Veterans:** FleetBase ~196d ("Fleet management made simple") · TrackNord ~170d ("Full kontroll på hela flottan").
**White space:** every ad speaks the *manager's control fantasy*; none shows the *coordinator's actual day*. Nobody uses humor. Nobody shows a real place.

## 2. Delivered concepts (excerpt — 2 of 6, so `spec_check.py` is not expected to pass on this file; full spec format in `../references/concept-spec.md`)

### 1. The morning radio check

**One-liner:** The dispatch radio's 07:02 chaos as the whole ad.
**Sketch:** A transcript, set like a radio log: "07:02 — Anyone seen trailer 14? · 07:04 — Kalle says it's in Västerås. · 07:09 — It is not in Västerås." One closing line: "Your fleet knows where everything is. Do you?"
**Mechanism:** 11, documentary observation
**Register:** documentary photographic
**Temperature:** playful
**Insight:** The coordinator's morning is an oral tradition, not a system.
**Field convention broken:** "full kontroll" (6/9 ads, all 3 advertisers) — this ad shows the opposite of control, verbatim.
**Nearest field neighbor:** TrackNord's "Full kontroll på hela flottan" — cannot be confused: theirs claims the fantasy, this stages the reality.
**Height:** 7/10 (provisional) — category-new recognition scene · **Floor score:** 5 (dies if the log reads written, not transcribed)
**Lemon profile:** right: dialogue, characters with agency, captured moment · left flags: text-carried
**Series potential:** infinite — every morning is an episode.
**Fragile flags:** the log must read transcribed, not written.
**Thumbnail test:** "It is not in Västerås."

### 2. The fuel receipt archaeology

**One-liner:** A year of one truck's crumpled fuel receipts, laid out as an archaeological find.
**Sketch:** Museum-style flat-lay photograph, specimen tags under each receipt ("Specimen 4: Shell, Örebro, purpose unknown"). One line: "Or: one row per fill-up, automatically."
**Mechanism:** 4, exaggeration (played dead straight)
**Register:** photo-meme
**Temperature:** playful
**Insight:** Fuel admin is the job nobody admits is a job.
**Field convention broken:** "boka demo" CTA monoculture (6 of 9 ads) — and the category's no-humor default.
**Nearest field neighbor:** none — no field ad shows paper at all.
**Height:** 7/10 (provisional) · **Floor score:** 6 — the deadpan museum framing survives mediocre photography
**Lemon profile:** right: found objects, wit, reader-completion · left flags: no people
**Series potential:** per-artifact (receipts, parking fines, wash tickets).
**Fragile flags:** must look found, not styled.
**Thumbnail test:** the specimen tags.

## 3. Kill log (excerpt)

- "Dashboard before/after split" — killed by the field test: confusable with 3 running ads.
- "GPS dot as guardian angel" — killed by instrument 1: analogy first-instinct trap.
- "Sveriges mest spårade flotta" — killed by the uniqueness gate: any competitor could sign it.

## 4. The real thing

Two non-fictional artifacts ship alongside this example:

- [`../examples/category-field-extract.json`](category-field-extract.json) — a counts-only extract of a real 4-advertiser field scan (170 Meta ads, US B2B fintech spend management): the "in one (place)" convention measured across all four advertisers, "get started" ×28, median 30 days, 12% ≥90d. Ad text withheld per the working-data policy; aggregates and cross-advertiser phrase fragments shipped.
- [`gauntlet-run/`](gauntlet-run/) — a sanitized real gauntlet run: generated median 7, one advertiser's real running ads median 3, anchors 3 (discrimination valid), benchmarks 8/9 (calibration confirmed), and an honest `blinding_failed` flag because item shape gave sources away. Re-verify the arithmetic with `gauntlet_score.py`.
