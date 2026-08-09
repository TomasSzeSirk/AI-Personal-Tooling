# Doc Craft

A taxonomy of what makes a technical **decision document** good, discovered
rather than asserted, plus the skills that write and review against it.

The method: take ten decision documents that were steered — published RFCs and
internally reviewed design docs — extract a brief from each, and have a model
write a cold single-pass draft of the same brief under the same `##` section
scaffold. Then compare the halves across 13 candidate dimensions and keep only
the features that separate them. Anything both halves do is the template or the
genre, not a feature worth instructing.

Seven features survived. The corpus, prompts, and full candidate tally live under
`scripts/doc-craft/`.

## Units

| Unit | Role |
|------|------|
| `skills/doc-craft` | The taxonomy itself (`features-decision.md`) — reference, read by the other three. |
| `skills/write-doc` | Interactive drafting: search the repo, ask the author for what only they hold, then write against the taxonomy. |
| `skills/review-doc` | Check an existing document — dispatches `doc-reviewer`, collates findings. |
| `agents/doc-reviewer.md` | Read-only subagent; reports `file:line — shortfall — fix`, ranked most-severe first. |

## Install

- **Windows:** `pwsh -File scripts/doc-craft/install.ps1`
- **macOS/Linux:** `bash scripts/doc-craft/install.sh`

Validate with `scripts/doc-craft/validate.{sh,ps1}`.

## Run a review

```
review-doc docs/design/my-decision.md
```

Or dispatch the subagent directly (`subagent_type: doc-reviewer`) with a document
path. It loads `~/.claude/skills/doc-craft/features-decision.md` itself.

**Findings are flat-ranked, not grouped by dimension.** The grouping rule was
conditional on the taxonomy exceeding 10 features; it came in at 7, so grouping
would add a layer over one or two findings per group. Revisit if a re-run at
larger n pushes the count past 10.

## Never strip `write-doc` to its feature list

This is the load-bearing warning of the whole idea, not a footnote.

`write-doc` searches the repo and interviews the author *before* it drafts.
That is not ceremony. Three of the seven features — `d02-c5` (name a concrete
observed instance), `d10-c6` (quote an external source verbatim), and partly
`d04-c6` (record a position you abandoned) — require evidence from outside the
document. A model told to satisfy them with nothing to look up will **invent**
the evidence, and the invented version passes the feature check. `doc-reviewer`
scores it as satisfied.

A three-arm run on 2026-08-09 (`scripts/doc-craft/evidence.md`) measured exactly
that variant. The arm given the seven features with search and interview
suppressed scored **worse than the arm given no taxonomy at all** — 5.63 findings
per 100 lines against 4.58 — and fabricated four claims, including two invented
commit hashes inside a `git log` transcript it had no means to run. The arm that
could search and ask fabricated nothing across 16 checkable claims.

So there is no valid "just follow the seven features" shortcut: not as a prompt
snippet, not as a lint rule, not as seven bullets pasted into another skill.
Separated from the means to check, the features stop being standards and become
instructions to invent. Anyone who reads `features-decision.md` and thinks *I
could just paste these into my prompt* is the reader this section exists for.

## What the held-out evaluation found

Three briefs held out of discovery were each written twice — once by the plain
cold prompt, once with the seven features loaded and `write-doc`'s interview and
repo access suppressed — then reviewed blind. Full tables in
`scripts/doc-craft/evidence.md`.

**Pooled, it is a wash: 26 findings against 26** (1.72 vs 1.54 per 100 lines).
The acceptance check asked for the taxonomy arm to win on 2 of 3 documents with
none worse; it won one, tied one, lost one. The taxonomy was **not** tuned
against these documents to force a pass — that would have converted the only
independent evidence in the project into training data.

The aggregate hides two opposite movements, and they are the useful result:

- **Structure responded to instruction.** `d12-c1`, `d12-c5` and `d04-c6` fell
  from 7 findings to 3, and defects that map to no feature fell from 5 to 1.
- **Evidence went backwards.** `d02-c5` and `d10-c6` rose from 9 to 16. Told to
  name observed instances and quote sources with nothing to look up, the arm
  produced them in quantity and the reviewer flagged them as uncheckable.

Fabrications, verified against the real sources: the arm's Rust quotations were
**verbatim correct**, but it invented a five-entry implementation history (the
real KEP records different dates and a different release) and invented an
abandonment history — "held for the first two drafts of this document" — for a
document written in one pass. That last one is `d04-c6` satisfied by fabrication,
scored by the blind reviewer as merely unverifiable. It is the precise failure
the interview exists to prevent, now observed on a document that did not shape
the taxonomy. The control arm invented dated milestones too, in the section the
KEP template solicits them for, so that class of invention is not the taxonomy's
doing.

**Spec §11.1 is settled: `write-doc` loads all seven survivors.** The
shallow-compliance failure the question guarded against — findings moving from
"absent" to "present but thin" while the count holds — did not appear. Where the
features could be satisfied from what the writer had, findings dropped outright;
where they could not, findings rose rather than flattening. Subsetting would drop
exactly the structural features that worked.

**One feature is instruction-resistant on this evidence.** `d03-c1` failed four
times in the taxonomy arm, and two of those were pointer/destination mismatches
the draft had everything it needed to catch. The instruction produced the form of
a resolvable reference without the check behind it. A single-pass writer
forbidden from re-reading cannot verify a destination it has not written yet, so
the fix is procedural — resolve links in a final pass — not a stronger wording.
Three documents cannot tell "instruction cannot reach it" from "the instruction
was worded badly", so this is a candidate, not a conclusion.

## What the evidence supports

**The taxonomy rests on 10 pairs, 8 of them clean. A feature holding in 5 of 8 is
suggestive, not measured.** Specific limits worth carrying:

- Two of the ten pairs are **contaminated** — the model could partly reconstruct
  the public gold from training data, so its cold half converges on the gold
  regardless of steering. Non-separation there is uninformative and never drops a
  candidate.
- The public pairs conflate two variables: their gold half is human-written *and*
  reviewed, the cold half is AI *and* single-pass. A feature separating there
  could be authorship rather than steering. The three internal pairs are the clean
  comparison — both halves AI, only steering differs.
- `d12-c3` and `d12-c5` agree on 18 of 20 corpus documents; read the
  dimension-12 family as one instruction, not three.
- `d10-c6` separates on only 1 internal pair and may be partly a habit of
  documents written against a public specification.
- The three-arm run is n=1 subject with one arm per condition — an observation,
  not a measurement, and arm C confounds taxonomy, interview, and repo access.
- The held-out evaluation is n=3 documents, one draft per arm, one reviewer that
  shares a model family with both writers. Its per-feature movements (7 → 3, 9 →
  16) rest on single-digit counts.
- Both evaluations suppress `write-doc`'s interview so the arms differ in one
  thing. The interview itself is therefore **unmeasured**: it needs someone who
  knows the problem domain without having read the gold, and anyone reading the
  gold to answer would leak it. The only evidence for it is the three-arm run's
  arm C and everyday use.

## Re-run discovery at larger n

The pipeline is five prompts under `scripts/doc-craft/prompts/`, run in-session
by an agent; there is no API script, deliberately — reproducibility comes from
the prompts plus the SHAs pinned in `corpus.md`.

1. Extend `corpus.md` with new gold documents pinned by commit SHA. Prefer
   **niche tooling and policy documents over famous language-design ones**:
   contamination tracks fame, not publication date.
2. Recall-probe every external candidate before pinning — with no document in
   context, ask the model to state the design the title and problem statement
   point at. If it names the accepted mechanism, the candidate is contaminated.
3. `01-extract-brief.md` per gold, then `02-write-cold.md` per brief **in a fresh
   context that never held the gold**, with the normalized H2 scaffold and a
   length target within ±20% of gold.
4. `03-structure.md` over every document, `04-compare.md` per pair with A/B
   randomized and the comparator blind to which half is gold.
5. `05-discover.md` once per dimension over the pooled observations, then apply
   every candidate to every document and keep those separating in a strict
   majority of clean pairs and at least 3 of them.

Record kept *and* dropped candidates in `evidence.md` — the dropped ones are the
record of what the template already accounts for. Never add a feature to reach a
target count: an invented feature is shared by `write-doc` and `doc-reviewer`, so
neither catches it and every evaluation scores it as agreement.
