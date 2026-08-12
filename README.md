# ad-mastermind

**B2B ad concepting graded against the ads your market actually runs.** A Claude Code skill with four spines: a **field layer** that pulls competitors' live ads from the Meta and LinkedIn ad libraries (both extractors live-verified) and measures the category's wallpaper, a **strategist layer** that diagnoses the market's logic and builds the insight foundation — asking the human first (their buyer knowledge is primary evidence), researching only the gaps, tagging everything else `[assumption]` — a **concepting engine** with a 12-mechanism library and a kill-gate that murders its own output, and a **gauntlet** — a blind-judging protocol where generated concepts are scored anonymously alongside the market's real ads, with a discrimination control that invalidates flattery.

```
THE FIELD           THE STRATEGIST            THE CONCEPTS               THE GAUNTLET
live competitor ──▶ market logic (7 axes) ──▶ 12 mechanisms ──▶ kill-gate ──▶ blind judges score your
ads via Apify       JTBD · triggers · the     (20–30 raw)      (5–8 live)    concepts MIXED with the
+ measured          buyer's own voice —       every concept must name the    field's real ads — sealed
wallpaper           asks the human FIRST,     field convention it breaks     mapping, 3 fresh judges,
                    researches only the gaps  AND the memory it builds       anchors that catch kindness
```

## Why this exists

- **AI concepting happens in a vacuum.** "Differentiated" is asserted, never measured. Here, differentiation is a number: the field layer finds the phrases 2+ competitors share, the CTA monoculture, the longest-running veterans — and every delivered concept must cite the measured convention it breaks. A concept confusable with a running competitor ad gets killed by data, not opinion.
- **AI scoring flatters.** Our logged finding: self-scoring runs 1–1.5 levels kinder than independent judgment. So the gauntlet exists: seeded blinding, sealed mapping, three fresh judge instances, canon benchmarks as calibration, and wallpaper anchors as a discrimination control — **if the judges score the anchors kindly, the whole run is declared invalid.** The gate cannot be sweet-talked.
- **Height without honesty is decoration.** The height ladder is a distinctiveness heuristic, openly labeled (it predicts standing out, not effectiveness — Field's IPA work on that decoupling is cited in the ladder itself), with floor scores for mediocre production and fragile-flags in every spec.
- **Distinctive isn't the same as aimed.** A concept can judge 7 and build the wrong memory for the brand's actual situation. The strategist layer diagnoses the market's logic (purchase cycle, TAM shape, brand maturity, in-market share…) into a config the whole pipeline reads, and the kill-gate's strategy test kills concepts that shine at the wrong audience — while the ask-first rule keeps the human's buyer knowledge as primary evidence instead of re-deriving it.

## Real runs — reported honestly

**The field scan:** 170 live Meta ads across four US B2B fintech spend-management advertisers. The measured wallpaper: the *"in one (place)"* convention appears across **all four advertisers**, "get started" carries 28 ads, "in minutes" 23 — and the field's median ad is only 30 days old (12% run ≥90 days). A counts-only extract ships in [examples/category-field-extract.json](examples/category-field-extract.json) (aggregates and cross-advertiser phrase fragments only — ad text is working material and never redistributed).

**The gauntlet:** five concepts generated against one large advertiser's measured Meta performance layer, then judged by three fresh instances mixed with that advertiser's real running ads: **generated median 7, the running ads median 3**, negative anchors at 3 (discrimination valid), canon benchmarks at 8–9 (calibration confirmed). One generated concept scored 6 — the judges' reasoning matched the kill-gate's own doubts about it.

Caveats, because the protocol logs its own: source anonymity did **not** hold (ad copy and concept sketches read differently — the scorecard flags `blinding_failed`, parity rate printed, and the protocol prescribes the fix), four of the five field items were not verified statics judged on a static-calibrated ladder, and judges share a model family with the generator. The level discrimination stood every control we could throw at it; "blind" is claimed only where it held. The sanitized full run (scorecard, sealed mapping, all three judges' verdicts, field items rewritten into neutral sketch form) ships in [examples/gauntlet-run/](examples/gauntlet-run/) — a quality gate you can't audit is theater.

## Install

```bash
npx skills add olson-adam/ad-mastermind
```

Or clone into `~/.claude/skills/ad-mastermind/`. Requires [Claude Code](https://claude.com/claude-code), Python 3 (stdlib only), and — for live field pulls — an [Apify](https://apify.com) token (`APIFY_API_TOKEN`; a 200-ad competitive sweep typically costs well under a dollar at current actor list prices). No token → the skill runs brief-only concepting and says so honestly.

## Use

```
you: what are our competitors running?          → field scan + field brief
you: ad concepts for {brand}                    → full run: field → strategist → concepts → kill log
you: critique these ads                         → height + Lemon profile per ad
you: run the gauntlet on these                  → blind verdict vs the field's real ads
```

Deliverables: a field brief where every number is script-computed, a market-logic config + insight map with provenance tags (`user-sourced` / cited / `[assumption]`), 5–8 concept specs (mechanism, strategy fit, field convention broken, height + floor score, Lemon profile, fragile flags, thumbnail test), a kill log proving the gate gripped, and — if you run the gauntlet — a scorecard with sealed-mapping integrity.

## What it deliberately doesn't do

No media buying, no account writes, no image generation, no effectiveness claims (height ≠ effect, and the ladder says so itself). Scraped ads are analyzed under working-material discipline, never redistributed. One category per run.

## Origins

The height ladder, mechanism library, kill-gate and gauntlet protocol were developed in production agency work and hardened by blind-testing them against awarded canon and real category wallpaper — including the protocol's own failures, which are logged in [references/gauntlet.md](references/gauntlet.md) because a quality gate you can't audit is theater.

## License

MIT
