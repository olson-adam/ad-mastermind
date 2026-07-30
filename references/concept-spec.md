# Concept spec — the delivery format

Every delivered concept is written in this exact structure. The spec is what a designer or founder can act on without a meeting — and what the gauntlet can judge blind.

```markdown
### {n}. {concept name}

**One-liner:** {the idea in one sentence}
**Sketch:** {2–3 lines: what you SEE in the ad, which copy carries it, what the viewer completes themselves}
**Mechanism:** {which of the 12 — and if humor: which humor type}
**Register:** {documentary photographic | typographic wit | graphic system | artifact | photo-meme | …}
**Temperature:** {playful | dry}
**Insight:** {the field/brief insight it's built on, one line}
**Field convention broken:** {the named wallpaper phrase/format from field-stats it defies — or "in-convention" stated honestly}
**Nearest field neighbor:** {the running ad it could most be confused with, and why it can't be}
**Height:** {level}/10 — {one-line justification} · **Floor score:** {level if production turns out mediocre}
**Lemon profile:** right-brain: {traits present} · left-brain flags: {markers present or "none"}
**Series potential:** {does it hold 3 executions? 10? what's the recurring element?}
**Fragile flags:** {what kills it in production — e.g. "artifact must look found, not designed"}
**Thumbnail test:** {what survives at 6 cm — the element that carries on a phone screen}
```

## Delivery package

A full concepting run delivers:

1. **The field brief** (1 page): total ads analyzed, the wallpaper phrases with advertiser counts, the veterans (longest-running ads = the market's revealed preferences), CTA monoculture, and the white space the set attacks. Every number from `field_stats.py` output — no model-computed figures.
2. **5–8 concepts** in the spec format above, portfolio-rule-compliant (mechanism spread, voice diversity, temperature quota, floor-score spread).
3. **The kill log** (appendix): one line per killed raw concept, with the instrument that killed it. The log is proof the gate gripped — 20–30 raw, 5–8 delivered.
4. **Gauntlet scorecard** (if run): blind-judged heights alongside the field's real ads, with the mapping revealed only after all verdicts are in.

## Rules

- The spec never contains internal scoring residue beyond what's listed (no hygiene-scorecard numbers — those live in the kill log appendix).
- "Field convention broken" must QUOTE a phrase from `field-stats.json` — a convention the script found, not one asserted from memory.
- **The delivery is not done until `spec_check.py` passes:**
  `python3 <skill-dir>/scripts/spec_check.py --specs concepts.md --field-stats field-stats.json`
  It mechanically enforces the portfolio rules (mechanism spread, register diversity, temperature quota, floor spread, height median, test-cell logic, convention traceability). A failing check means fix the delivery, never the checker.
- Fictional sample specs in `examples/` use fictional brands only.
