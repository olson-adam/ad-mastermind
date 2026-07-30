# ad-mastermind

**B2B ad concepting graded against the ads your market actually runs.** A Claude Code skill with three spines: a **field layer** that pulls competitors' live ads from the Meta and LinkedIn ad libraries and measures the category's wallpaper, a **concepting engine** with a 12-mechanism library and a kill-gate that murders its own output, and a **gauntlet** — a blind-judging protocol where generated concepts are scored anonymously alongside the market's real ads, with a discrimination control that invalidates flattery.

```
THE FIELD          THE CONCEPTS               THE GAUNTLET
live competitor ──▶ 12 mechanisms ──▶ kill-gate ──▶ blind judges score your
ads via Apify       (20–30 raw)      (5–8 live)    concepts MIXED with the
+ measured          each concept must name the     field's real ads — sealed
wallpaper           field convention it breaks     mapping, 3 fresh judges,
                                                   anchors that catch kindness
```

## Why this exists

- **AI concepting happens in a vacuum.** "Differentiated" is asserted, never measured. Here, differentiation is a number: the field layer finds the phrases 2+ competitors share, the CTA monoculture, the longest-running veterans — and every delivered concept must cite the measured convention it breaks. A concept confusable with a running competitor ad gets killed by data, not opinion.
- **AI scoring flatters.** Our logged finding: self-scoring runs 1–1.5 levels kinder than independent judgment. So the gauntlet exists: seeded blinding, sealed mapping, three fresh judge instances, canon benchmarks as calibration, and wallpaper anchors as a discrimination control — **if the judges score the anchors kindly, the whole run is declared invalid.** The gate cannot be sweet-talked.
- **Height without honesty is decoration.** The height ladder is a distinctiveness heuristic, openly labeled (it predicts standing out, not effectiveness — Field's IPA work on that decoupling is cited in the ladder itself), with floor scores for mediocre production and fragile-flags in every spec.

## A real run

We pointed the toolchain at one of B2B fintech's most celebrated creative brands. The field layer found: **85% of their live Meta ads use the same CTA**, median 50 days in market, and house phrases repeated across ten-plus ads. Five concepts generated against that measured field, then blind-judged mixed with their real ads: **generated median 7, the running ads median 3, discrimination control valid** (anchors at 3, canon benchmarks at 8–9). One generated concept scored 6 — and the judges' reasoning matched the kill-gate's own doubts about it. The gate grades; it doesn't cheerlead.

(Scraped field data is working material and never ships in this repo — the [example run](examples/example-run.md) uses fictional brands and reproduces offline.)

## Install

```bash
npx skills add olson-adam/ad-mastermind
```

Or clone into `~/.claude/skills/ad-mastermind/`. Requires [Claude Code](https://claude.com/claude-code), Python 3 (stdlib only), and — for live field pulls — an [Apify](https://apify.com) token (`APIFY_API_TOKEN`; a 200-ad competitive sweep costs a couple of dollars). No token → the skill runs brief-only concepting and says so honestly.

## Use

```
you: what are our competitors running?          → field scan + field brief
you: ad concepts for {brand}                    → full run: field → concepts → kill log
you: critique these ads                         → height + Lemon + scorecard per ad
you: run the gauntlet on these                  → blind verdict vs the field's real ads
```

Deliverables: a field brief where every number is script-computed, 5–8 concept specs (mechanism, field convention broken, height + floor score, Lemon profile, fragile flags, thumbnail test), a kill log proving the gate gripped, and — if you run the gauntlet — a scorecard with sealed-mapping integrity.

## What it deliberately doesn't do

No media buying, no account writes, no image generation, no effectiveness claims (height ≠ effect, and the ladder says so itself). Scraped ads are analyzed under working-material discipline, never redistributed. One category per run.

## Origins

The height ladder, mechanism library, kill-gate and gauntlet protocol were developed in production agency work and hardened by blind-testing them against awarded canon and real category wallpaper — including the protocol's own failures, which are logged in [references/gauntlet.md](references/gauntlet.md) because a quality gate you can't audit is theater.

## License

MIT
