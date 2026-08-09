# 03 — Structure one document into per-dimension JSON

Input: one technical decision document (`$SCRATCH/doc-craft/{gold,cold}/<name>.md`).
Output: `$SCRATCH/doc-craft/structured/<name>.{gold,cold}.json`.

The point of this stage is to strip surface wording. Later stages must reason
about what the document *does*, never about how it phrases things. Record
behaviour on each axis; quote only as evidence.

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

## Output shape

A single JSON object with **exactly these 13 keys**, spelled as in the table:

```
"Reader model", "Referential specificity", "Entry points & navigation",
"Open threads", "Stance & hedging", "Alternatives & rejection depth",
"Self-supersession", "Boundary ownership", "Adversarial self-attack",
"Grounding & provenance", "Live openness", "Structural rhythm",
"Failure treatment"
```

Each value is an object with exactly these three fields:

```json
{
  "behavior": "one to three sentences describing what the document does on this axis, in structural terms",
  "observations": ["discrete structural facts, one per string"],
  "evidence": [{"heading": "the ## or ### section it sits under", "line": 123, "span": "a short verbatim quote"}]
}
```

- `behavior` and `observations` are **descriptions of moves**, not quotes and not
  paraphrases-that-are-really-quotes. Write "names three rejected options and
  gives a measured cost for one of them", not "says the ledger approach is too
  expensive".
- `evidence` is where verbatim text is allowed, and only there. Two to five
  spans per dimension, each under 25 words. The document is supplied with every
  line prefixed by its line number and a tab; `line` is that number, and the
  prefix is not part of the document.
- A dimension the document does nothing on still gets all three fields:
  `behavior` says so plainly, `observations` records what is absent, `evidence`
  may be `[]`.

## Rules

- Never use a quoted span as the value of `behavior` or an `observations` entry.
- Describe, do not grade. No "good", "weak", "thorough", "shallow", "well
  argued". Say what is present and at what granularity; the judgement happens
  later and on other evidence.
- Count when counting is possible — how many options are rejected, how many
  quantities carry a source, how many headings at each depth. Counts are
  structure; adjectives are not.
- Do not speculate about who wrote the document, how it was produced, or how
  many passes it took.
- Read the document once and write the JSON. Do not revise.
- Emit only the JSON object. No prose before or after, no code fence.
