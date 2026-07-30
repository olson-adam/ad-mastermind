# Example run — fictional fleet-telematics category

Everything here uses fictional brands (TrackNord, FleetBase, Veholt; concepts for the fictional "Nordvik"). The raw fixture (`fixtures/meta-raw.json`) mirrors the verified live actor schema, so the whole chain runs offline:

```
python3 ../scripts/pull_ads.py --normalize-only fixtures/meta-raw.json --platform meta --output fixtures/field.json
python3 ../scripts/field_stats.py --ads fixtures/field.json --output fixtures/field-stats.json
```

## 1. The field brief

*Source: fixtures/field-stats.json — every number script-computed.*

7 active Meta ads · 3 advertisers · median 110 days running (57% ≥90d).
**Wallpaper phrases:** "full kontroll" — 5 ads across ALL 3 advertisers · "boka demo" — 4 ads, 2 advertisers.
**CTA mix:** Book a demo ×5, Learn more ×1, Get started ×1.
**Veterans:** "Fleet management made simple" (FleetBase, ~196d) · "Full kontroll på hela flottan" (TrackNord, ~170d).
**White space:** every ad speaks the *manager's control fantasy*; none shows the *driver's or coordinator's actual day*. Nobody uses humor. Nobody shows a real place.

## 2. Delivered concepts (excerpt — 2 of 6; full spec format in `../references/concept-spec.md`)

### 1. The morning radio check

**One-liner:** The dispatch radio's 07:02 chaos as the whole ad.
**Sketch:** A transcript, set like a radio log: "07:02 — Anyone seen trailer 14? · 07:04 — Kalle says it's in Västerås. · 07:09 — It is not in Västerås." One closing line: "Your fleet knows where everything is. Do you?"
**Mechanism:** 11, documentary observation
**Insight:** The coordinator's morning is an oral tradition, not a system.
**Field convention broken:** "full kontroll" (5/7 ads, all 3 advertisers) — this ad shows the opposite of control, verbatim.
**Nearest field neighbor:** TrackNord's "Full kontroll på hela flottan" — cannot be confused: theirs claims the fantasy, this stages the reality.
**Height:** 7/10 (provisional) — category-new recognition scene · **Floor:** 5 (dies if the log reads written, not transcribed)
**Lemon profile:** right: dialogue, characters with agency, captured moment · left flags: text-carried
**Series potential:** infinite — every morning is an episode. **Thumbnail test:** "It is not in Västerås."

### 2. The fuel receipt archaeology

**One-liner:** A year of one truck's crumpled fuel receipts, laid out as an archaeological find.
**Sketch:** Museum-style flat-lay photograph, specimen tags under each receipt ("Specimen 4: Shell, Örebro, purpose unknown"). One line: "Or: one row per fill-up, automatically."
**Mechanism:** 4, exaggeration (played dead straight)
**Insight:** Fuel admin is the job nobody admits is a job.
**Field convention broken:** the category's no-humor monoculture (0/7 field ads attempt a smile).
**Nearest field neighbor:** none — no field ad shows paper at all.
**Height:** 7/10 (provisional) · **Floor:** 6 — the deadpan museum framing survives mediocre photography
**Lemon profile:** right: found objects, wit, reader-completion · left flags: no people
**Series potential:** per-artifact (receipts, parking fines, wash tickets). **Thumbnail test:** the specimen tags.

## 3. Kill log (excerpt)

- "Dashboard before/after split" — killed by the field test: confusable with 3 running ads.
- "GPS dot as guardian angel" — killed by instrument 1: analogy first-instinct trap.
- "Sveriges mest spårade flotta" — killed by the uniqueness gate: any competitor could sign it.

## 4. Gauntlet

A real (non-fictional) gauntlet run of this toolchain — 5 generated concepts mixed blind with 5 real running ads, 3 wallpaper anchors and 2 canon benchmarks, judged by 3 fresh instances — produced: generated median 7, real field ads median 3, negative anchors 3 (discrimination valid), benchmarks 9/8 (calibration confirmed). Raw run data is working material and is not redistributed; the protocol and scripts to reproduce it on your own field are in this repo.
