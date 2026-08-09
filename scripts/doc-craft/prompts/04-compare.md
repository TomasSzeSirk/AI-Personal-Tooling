# 04 — Compare a pair of documents, per dimension

Inputs: two structured representations produced by `03-structure.md`, presented
as **document A** and **document B**. Output:
`$SCRATCH/doc-craft/structured/<name>.compare.json`.

A and B cover the same subject and were given the same `##` section scaffold.
Which is which is randomized per pair and is not disclosed here. Do not guess,
do not state a guess, and do not let a guess shape the report. Report only what
each side does: "A does X, B does Y".

## The 13 dimensions

| # | Dimension | Measures |
|---|---|---|
| 1 | Reader model | Who is addressed; what competence is assumed; whether depth is allocated by what the reader already knows |
| 2 | Referential specificity | Named paths, symbols, versions, and commands versus generic nouns |
| 3 | Entry points & navigation | Where a reader lands, whether the recommendation precedes the argument, internal anchor density relative to length |
| 4 | Open threads | What is admitted unknown, deferred, or unresolved — and whether the admission is load-bearing |
| 5 | Stance & hedging | Distribution of confidence; whether advice carries its cost |
| 6 | Alternatives & rejection depth | Whether rejected options name a mechanism and the specific reason it lost |
| 7 | Self-supersession | Whether the document records and argues against its own earlier position |
| 8 | Boundary ownership | Whether it names what it does *not* decide, and who does |
| 9 | Adversarial self-attack | Whether it attacks its own recommendation and publishes where it loses |
| 10 | Grounding & provenance | Whether quantities and claims trace to an artifact a reader can check, including artifacts it contradicts |
| 11 | Live openness | Whether open questions name the actual live choice, versus a decorative future-work section |
| 12 | Structural rhythm | Variance in section shape and length; degree of mechanical parallelism |
| 13 | Failure treatment | How errors, edge cases, and the honest non-viable cases are handled |

## What is not a divergence

Three exclusions. Each removes an artifact of how the pair was constructed.

1. **`##` heading presence.** Both documents were handed the same `##` scaffold,
   so both have the same top-level sections. That a section exists on both sides
   — or that both use the same section names — is never a finding. Only what
   fills a section is.
2. **Raw length.** The two halves were written to different length budgets, and
   ratios across the corpus run from roughly half to a quarter over. "A is
   longer", "A's section 4 has more paragraphs", "B is more detailed throughout"
   are all measurements of budget, not of the document. Report divergences in
   *kind*: what a section does, not how much of it there is. Where a difference
   really is only volume, say the dimension does not diverge.
3. **Subject-matter differences.** The two describe different technical answers
   to the same question. That they chose differently is the premise, not a
   finding.

## What IS a divergence

**`###` and deeper.** Neither document was given any sub-structure. Whether one
side invented sub-headings, how deep it went, and whether those sub-headings
carry argument or only labels is real signal and belongs to **dimension 12,
Structural rhythm**. Record it there.

Everything else the dimensions cover, judged as kind rather than amount:
granularity of reference, whether a rejection carries the specific thing that
killed the option, whether an admission is load-bearing or decorative, whether a
quantity traces to something checkable, and so on.

## Output shape

A single JSON object with **exactly these 13 keys**, spelled as in the table
above. Each value is an object with exactly these fields:

```json
{
  "diverges": true,
  "observations": [
    "A does X; B does Y."
  ]
}
```

- **At least one observation per dimension, always** — including when
  `diverges` is `false`, where the observation states what both sides do in
  common. Never emit an empty array.
- Each observation names both sides in the same string, as one contrast.
- Neutral wording. No "better", "stronger", "richer", "more mature". Say what
  each side does and let the difference stand.
- Do not name which side you believe was steered, revised, or human-written, in
  any field.

Emit only the JSON object. No prose before or after, no code fence.
