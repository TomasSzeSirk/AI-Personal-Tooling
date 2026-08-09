---
name: doc-craft
description: The feature taxonomy for technical decision documents — seven content constraints discovered by comparing steered documents against unsteered drafts of the same brief. Read as reference; use write-doc to draft against it and review-doc to check a document with it.
---

# doc-craft

This skill holds one artifact: `features-decision.md`, the taxonomy of seven
features that separate a steered or published technical decision document from an
unsteered single-pass draft of the same brief under the same section scaffold.

It is **reference, not a workflow**. The two skills that consume it:

| Skill | Use |
|-------|-----|
| `write-doc` | Draft a decision document against the taxonomy — searches the repo, interviews the author for what only they hold, then writes. |
| `review-doc` | Check an existing document against the taxonomy via the `doc-reviewer` subagent. |

## Reading it directly

Fine for understanding what the features are. **Not fine as a substitute for
`write-doc`.** Three of the seven (`d02-c5` named instance, `d10-c6` verbatim
external source, and partly `d04-c6` abandoned position) are satisfiable by
invention. A writer that cannot search a repo and cannot ask the author will
manufacture the evidence they ask for, and the manufactured version passes the
feature check. A measured run of exactly that variant scored *worse than writing
with no taxonomy at all* — see the three-arm run in
`scripts/doc-craft/evidence.md`.

So: do not paste these seven into a prompt, a lint rule, or another skill. They
are safe only in the hands of something that can go and check.

## Provenance

Discovered from 10 gold/cold document pairs, 8 of them clean of recall
contamination. A feature holding in 5 of 8 pairs is suggestive, not measured.
Every candidate — kept and dropped — with its tally is in
`scripts/doc-craft/evidence.md`; the corpus and its pinned commit SHAs are in
`scripts/doc-craft/corpus.md`.
