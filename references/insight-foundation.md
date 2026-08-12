# Insight foundation — the raw material concepts are made of

Runs after [market-logic.md](market-logic.md), before concepting. This is the phase that prevents the pipeline's most common failure: jumping straight to "what do we want to say" (inside-out, message-first, rational-by-default). Field stats tell you what the category ADVERTISES; this phase builds what the BUYER lives.

## ASK THE PERSON FIRST (the layer's first rule)

Before researching anything, interview the user. They may be sitting on months of buyer contact that no scrape can match:

- What do buyers say VERBATIM — in sales calls, support tickets, interviews, onboarding? (Exact lines, not summaries.)
- When does the need actually arise — what happened right before the last five deals?
- Who exactly is the buyer, and who is it NOT? What does everyone in the industry know but not say?
- What strategy/ICP/research documents already exist? (Ingest them — never re-derive what's written down.)
- Sacred cows: what must the ads never touch? And: is there site access for documentary photography?

**Provenance is a first-class tag, on every fact in this layer:** `user-sourced` (the user said it — primary evidence, never overwritten by model reasoning) · a source (research found it — cite it) · `[assumption]` (neither — the tag survives into the deliverable). If the user has nothing and research finds nothing, the deliverable says the insight base is thin — honest degradation, same rule as a missing Apify token.

## HARD RULE: product quarantine

Throughout this phase, **product names, features, platform words and the company's own phrasings are FORBIDDEN.** Everything is written from the buyer's world: situations, frustrations, jobs, risks, ambitions. Litmus test per line: *"could a person in the audience say this out loud without ever having heard of the product?"* No = inside-out, rewrite. Messages are written in concepting, as answers to insights — never as the starting point.

## 1. Triggers / category entry points — when does the need arise?

Map the situations that precede buying interest with the W-questions:

| Question | What it surfaces |
|---|---|
| **When** (time/phase)? | Project start, audit, a hire quitting mid-project, an incident |
| **Where** (place/context)? | The site meeting, the commute, the home office at 9pm |
| **While** (doing what)? | Hunting for the latest version, writing the status report, onboarding a contractor |
| **With/for whom?** | The client calling, the auditor requesting records, the new colleague |
| **Feeling what?** | Panic ("which file is current?"), shame (can't find it), fatigue (fifth tool today) |
| **Why** (underlying goal)? | Not being the one who made the mistake; showing control upward |

Output: 5–10 entry points, each as **a concrete scene** (not an abstraction). "Scattered information" is not an entry point. "The meeting where three people have three different versions of the same drawing" is.

## 2. Jobs to be done — three levels, all required

Per prioritized persona (the pipeline stalls in functional-land otherwise):

- **Functional job**: what must get done? ("keep project records searchable")
- **Emotional job**: what do they want to feel / stop feeling? ("lose the knot in the stomach before the audit", "feel like I have the picture")
- **Social job**: how do they want to be seen? ("the one who has it together", "not the one blocking the rollout")

The emotional and social jobs are concept gold — that's where advertising that FEELS gets built. Functional jobs produce feature copy.

## 3. Pains — dramatizable scenes only

List 5–8 pains, each required to be **dramatizable**: a pain qualifies only if it can become a scene, an image, or a recognizable spoken line. Format per pain:

- **The scene**: what happens, who's there, what breaks
- **The line**: what someone actually says/thinks in the moment ("check the email... no wait, it was in the chat")
- **The cost**: what it leads to (delay, a hard conversation, overtime, risk)

Strongest source: a verbatim line from the user or from [conversation-scan.md](conversation-scan.md) with a URL — a real quote beats a constructed one and **removes the `[assumption]` tag**.

## 4. Documentary scouting — artifacts, places, walls

Evidence from our testing: concepts built on real observations reached 7 blind; concepts built on borrowed formats ceilinged at 6. So the buyer's PHYSICAL reality is inventoried as its own raw material, feeding mechanisms 11 and 12:

- **The artifacts:** which documents/forms/tables does the category OWN? (title blocks, inspection forms, site diaries, the survey deck.) Which one carries an unsaid truth in its structure? → mechanism 12.
- **The places:** where do the decisive moments actually happen? (the site shed, the parking lot, the elevator queue.) → mechanism 11.
- **The walls/surfaces:** what is literally pinned up in the buyer's world? (the noticeboard, the laminated schedule, the whiteboard nobody erases.)
- **The site-access question** (asked in the interview, harvested here): a real environment is the cheapest high-authenticity production there is. The answer goes into the market-logic profile's budget/access axis.

Sources: the user's material, site photos, the scan's finds, the industry's own standard documents (hunt down the REAL forms — an authentic original is a spec requirement for mechanism 12). Without a verified artifact/place: `[assumption]` tag as usual.

## 5. The edge check — who does the joke hit?

When an insight dramatizes a system failure, check WHO the edge lands on: **the buyer is never the villain.** The funniest category truths often make the buyer the culprit — kill or re-aim those. The edge points at the silence, the system, the tool gap; the buyer is the one who ESCAPES being the villain thanks to the sender. Tag every prioritized insight with who its edge hits.

## 6. Audience split — which cell does each insight serve?

**The axes and their proportions come from the market-logic config — not from a fixed template.** Default 2×2 when the profile doesn't say otherwise:

| | **Off-market** | **In-market** |
|---|---|---|
| **Cold audience** | Build memory: dramatized entry point, emotion, distinctiveness. NO arguments. | Break into consideration: convention breaks, villain, insider truth |
| **Warm audience** (knows the brand) | Entertain the relationship: series, humor, culture-borrowing — deepen the memory structure | Convert: rational proof, social proof, demo live here — and only here |

A concept batch must NEVER sit in only one of the profile's cells — that's how the "always rational, always in-market" pipeline happens.

## 7. Output: the insight map

```
## Insight map — {brand} {date}
### Entry points (scenes)
1. [scene] — feeling: [x] — cell: [cold/warm × in/off]
### JTBD
| Persona | Functional | Emotional | Social |
### Pains (dramatizable)
1. Scene / Line / Cost — provenance: [user-sourced / source / assumption] — edge hits: [x]
### Documentary scouting
Artifacts: [...] · Places: [...] · Walls: [...] · Site access: [yes/no/unclear]
### Prioritized insights (3–6 go to concepting)
Each: the buyer-truth with tension · provenance · the field convention it collides with
(quote the phrase from field-stats.json) · cell(s) served
```

An insight is a buyer-truth with tension — not a product feature. Every prioritized insight cites BOTH layers: a provenance from this phase AND the measured field convention it collides with. Assumptions are allowed as concept ground but must be visible in the deliverable.
