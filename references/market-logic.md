# Market logic — diagnose before you ideate

Runs at the START of the strategist layer (SKILL.md step 3), before any insight work. Purpose: diagnose the market's actual logic and **configure the rest of the pipeline** from it — audience cells, portfolio mix, height ambition, series requirements, temperature. Everything below is a default with explicit break conditions, never dogma.

**Ask the person first.** Every axis is filled from the user interview before any research: the person running this usually knows their market's shape better than a web search does. User answers are primary evidence — tag them `user-sourced`. Research fills only the axes the user can't answer (tag with a source). An axis neither can fill gets `[assumption]`, and the tag survives into the deliverable.

## The seven axes

| Axis | Question | Extremes |
|---|---|---|
| **Purchase frequency & cycle** | How often, and how, is the category bought? | Continuous/subscription ↔ project-driven or rare (3–10 yr) |
| **TAM shape** | How many CAN buy? | Mass market (tens of thousands) ↔ ~50–500 named buyers |
| **In-market share** | What share is actively buying right now? | The 95/5 heuristic is a **testable hypothesis, not a law** — spec-driven project markets can be "always slightly in-market"; long-cycle contract markets can be more extreme than 95/5 |
| **Brand maturity** | Known or unknown to the audience? | Unknown challenger (must first become recognizable) ↔ established (can play, can afford implicit moves) |
| **Risk appetite & sacred cows** | What can the brand/organization tolerate? | Humor-tolerant challenger ↔ cautious corporation with a brand manual. List what must NOT be touched |
| **The channel's actual audience** | Who really sees the ads? | Broad feed reach ↔ an ABM list where every impression is a known person |
| **Production budget & access** | What is there to build with? | Photographer + production budgeted ↔ designer hours and stock. KEY QUESTION: is there site access (a real environment — the brand's or a customer's — to shoot in)? Cheapest high-authenticity route there is; decides whether the documentary track (mechanism 11) is a LOW or HIGH budget class |

## What the profile configures

Written as a short config block in the working document; the rest of the run reads from it:

1. **Which audience cells exist.** The default 2×2 (cold/warm × in/off-market, see [insight-foundation.md](insight-foundation.md)) — but an ABM market with 200 buyers has no meaningful "cold mass"; its axis becomes "knows us well ↔ doesn't know us at all".
2. **Portfolio mix.** The kill-gate's portfolio quotas are read FROM HERE, not from instinct. Defaults: broad market + hybrid demand → 60–70% memory-building, max 2 capture cells. Narrow TAM/spec-driven → weight toward recognition-over-time: series/device and insider truth outrank broad fame. Launch mode/unknown brand → distinctive assets and brand linkage get elevated weight in the gate. (The mechanical floors in `spec_check.py` are the default profile; a dry-first premium brief uses `--premium`, and any other profile-driven deviation is stated in the deliverable, never silent.)
3. **Height ambition.** Median ≥7 is the default floor. Break condition: at very narrow TAM the goal isn't fame but *"impossible to forget for the 200 who matter"* — level 7 then means "new territory for that audience", and shareability is down-weighted in favor of recognition + series stamina. **Novelty↔fluency ceiling:** at low brand awareness or mid-rebrand, mental availability accumulates through consistency and repetition, not reinvention — put the novelty ambition in the IDEA inside a CONSTANT asset system (same device/format/voice across the series). "New territory every time" is the wrong goal there; the profile must argue it away explicitly, and the tension is named in the deliverable when active.
4. **Series vs one-off.** Ongoing commitment + rare-purchase cycle → a series/device is mandatory among survivors. Time-boxed campaign/event → one-off logic is fine, the device requirement is released.
5. **Emotional palette & temperature.** Career-risk-heavy purchases (big investments, procurement) → recognition/safety/pride get more room. But the default temperature is PLAYFUL (the kill-gate's temperature quota) — dry understatement and documentary gravity are complement registers, not the starting point. Only explicit sacred cows or documented risk context lower the temperature, and then the profile says why.

## Two opposite example profiles (fictional — calibration only, never delivery material)

**Broad SaaS challenger:** subscription category, wide TAM, feed audience, brand unknown → full 2×2, series required, brand-linkage weight up, fluency ceiling ACTIVE (constant asset system), median ≥7 within it.

**Narrow industrial component maker:** spec-driven, engineers prescribe the part; TAM is a few hundred named specifiers; "in-market" follows project calendars — always someone, never many; brand known in the niche. → Audience axis becomes "specifies us by habit ↔ specifies the competitor by habit"; portfolio weights insider truth + series; broad shareability irrelevant, 6 cm recognition decides; level 7 = "nobody in the niche has said it like this".

## Output format

```
## Market logic — {brand} {date}
| Axis | Value | user-sourced / source / [assumption] |
...
**Config:** audience cells: {...} · portfolio mix: {...} · height floor: {...} ·
series requirement: {yes/no} · temperature: {...} · sacred cows: {...}
```

The config block is quoted in the kill-gate's portfolio assessment and in the deliverable summary — so the reader sees WHY the mix looks the way it does.
