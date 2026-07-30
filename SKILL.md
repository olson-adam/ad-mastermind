---
name: ad-mastermind
description: B2B ad concepting graded against the ads your market actually runs. Pulls competitors' live ads from the Meta and LinkedIn ad libraries (via Apify), maps the category's wallpaper (shared phrases, formats, CTA monoculture, longest-running veterans), generates concepts through a 12-mechanism library with a height ladder and kill-gate — every concept must name the field convention it breaks — and can blind-judge generated concepts mixed with the market's real ads. Use when the user wants ad concepts or creative concepts for a B2B brand, a competitive ad/creative analysis, a field scan of what competitors are running, a critique of existing ads, or a blind evaluation of creative work.
---

# ad-mastermind

Creative concepting with two spines most AI concepting lacks: **evidence about the field** (what the market actually runs, pulled live) and **an honest quality gate** (a height ladder calibrated against awarded work, a kill-gate that murders its own output, and a blind-judging protocol that can't be sweet-talked). The deliverable is concepts a designer can act on — each one citing the measured field convention it defies.

## Modes

| User wants | Mode |
|---|---|
| "what are competitors running?" / competitive creative analysis | **Field scan** (steps 1–2, deliver the field brief) |
| ad concepts for a brand | **Full run** (steps 1–5) |
| judge/critique existing ads | **Critique**: height + Lemon profile per ad, with left-brain hits called out (the hygiene scorecard stays internal — see kill-gate.md) |
| blind-evaluate concepts (ours or anyone's) | **Gauntlet**: [references/gauntlet.md](references/gauntlet.md) |

## The full run

### 1. The field
Collect the brand's 3–6 nearest competitors (ask, or derive from the brand's site and confirm). Pull their live ads:

Work in a `field-data/` directory (keep it out of version control — add it to .gitignore if the user's project has git):

```
mkdir -p field-data
python3 <skill-dir>/scripts/pull_ads.py --platform meta --advertiser "{name}" --output field-data/{name}-ads.json
```

On Meta, `--advertiser` runs a small probe first, resolves the advertiser's page_id by name match, and re-pulls page-scoped (keyword search alone is noisy — a "Ramp" search returns boat-ramp vendors). If the probe can't match the name it stops and tells the user to supply `--page-id`. **LinkedIn caveats (live-verified 2026-07-30)**: keyword search matches ad TEXT, so filter output by advertiser name (or pass a company-scoped ad-library URL via `--input-json`), and a share of ads lack start dates — the script warns when longevity stats will be partial.

Requires `APIFY_API_TOKEN` (a 200-ad sweep typically costs well under a dollar at current actor pricing). No token → ask the user to either set one up or paste/export ads manually; the run degrades to brief-only concepting with the field test waived — say so honestly in the deliverable. New actor schemas: use `--dump-raw`, inspect, extend the field map in the script.

### 2. Field analysis
```
python3 <skill-dir>/scripts/field_stats.py --ads field-data/*-ads.json --output field-data/field-stats.json
```
(The `-ads.json` suffix keeps stats files out of the glob; the script also refuses non-ad files with a readable error.)
The script computes everything numeric (wallpaper phrases shared by 2+ advertisers, longevity, veterans, CTA/format mix) — **never compute or estimate figures yourself**. On top of the stats, classify the field's *message codes* (the recurring promise types: control, simplicity, speed, trust…) and write the **field brief**: what everyone says, what has run longest (revealed preferences), and the white space — what nobody says. Every claim in the brief traces to `field-stats.json` or a specific ad.

### 3. Insights
From the field brief + the user's knowledge of their buyer (ask 3–5 sharp questions: what do buyers say verbatim? when does the need actually arise? what does everyone in the industry know but not say?), write 3–5 prioritized insights. An insight is a buyer-truth with tension — not a product feature.

### 4. Concepting
Read [references/mechanisms.md](references/mechanisms.md) and run the three rounds (mechanism sweep with first-instinct traps struck, collisions, off-script — the FUN round is mandatory): 20–30 raw concepts. Then [references/kill-gate.md](references/kill-gate.md): adversarial protocol, the instruments (including **the field test** — every survivor names the wallpaper convention it breaks and its nearest field neighbor), push-pass, portfolio rules. Calibrate all height scores against [references/height-ladder.md](references/height-ladder.md) + [references/benchmarks.md](references/benchmarks.md) — assume self-scores run 1–1.5 steps kind.

### 5. Delivery
Write concepts in the [references/concept-spec.md](references/concept-spec.md) format: field brief + 5–8 specs + kill log. **Then run the mechanical portfolio check — the delivery is not done until it passes:**

```
python3 <skill-dir>/scripts/spec_check.py --specs concepts.md --field-stats field-data/field-stats.json
```

It enforces mechanism spread, register diversity, the temperature quota, floor-score spread, the height median, test-cell logic, and that every claimed field convention actually exists in `field-stats.json`. A failing check means fix the delivery — never the checker. Finally, offer the gauntlet as verification: judge the delivered concepts mixed with real ads from the field.

## Non-negotiables

- **No field numbers from the model.** Stats come from scripts; the model classifies and judges, never counts.
- **Self-scores are provisional.** Any height claim shown to the user says so until a gauntlet run has judged blind.
- **The examples in the reference files are spent.** Recreating them = kill. Same for benchmark entries.
- **Scraped field ads are working data, never redistributed.** They live in the user's working directory (`field-data/`, gitignored by convention), quoted in analysis under fair-use-style brevity, and never shipped in this repo or its examples — examples use fictional brands.
- **Honest degradation.** No Apify token, thin field data, or PMax-style opacity → state it in the deliverable instead of pretending.
