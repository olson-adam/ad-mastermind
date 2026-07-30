# Shipped gauntlet run (sanitized) — 2026-07-30

The real run behind the README's numbers: 5 generated concepts vs 5 real running ads
from one advertiser's Meta library, 3 fresh negative anchors, 2 canon benchmarks,
judged by 3 fresh instances. Everything an auditor needs is here — scorecard, sealed
mapping (seed 730), and all three judges' full verdicts — with ONE redaction: verbatim
field-ad text is replaced by placeholders, per the repo's working-data policy
(scraped ads are analyzed, never redistributed). Scores, sources, and reasoning are
untouched.

Verify the arithmetic yourself:
    python3 ../../scripts/gauntlet_score.py --verdicts j1.json j2.json j3.json --mapping mapping.json --output /tmp/recheck.json

Known honest flaws of this run, logged in ../../references/gauntlet.md (learnings 5–6):
the blinding failed on item shape (scorecard says so), three field items were video
ads judged from copy, and judges share a model family with the generator.
