# 05 — Discover candidate features, one dimension at a time

Input: the pooled divergence observations for **one** dimension, drawn from all
ten pairs and already unblinded. Every observation names `GOLD` (the steered or
published half) and `COLD` (the single-pass unsteered half). The pair name, its
tier (`clean` / `contaminated`) and its source (`internal` / `external`) prefix
each line.

Output: candidate features for that dimension — closed-form questions with
discrete answers, each of which a reader could apply to one document on its own,
without seeing its counterpart.

Do not weigh evidence, do not cut, do not rank. Proposing a candidate that later
fails to separate is cheap; the cut runs downstream over all 20 documents. What
is expensive is a candidate that is unusable by construction, which is what the
three constraints below rule out.

## Three constraints, all binding

1. **Depth, not presence.** Both halves were handed the same `##` scaffold, so
   every section exists on both sides. A candidate answerable by checking whether
   a section, heading or subsection exists measures the template, not the author.
   Reject it. The measurable thing is what fills a section.

   - Bad: *Is there an Alternatives section?*
   - Good: *Does each rejected option name a mechanism and the specific property
     or quantity that defeated it?*

   Test every candidate this way: could it be answered by `grep '^#'`? If yes,
   drop it or restate it as the depth question underneath it.

2. **Single-pass satisfiable.** The surviving features are loaded by a writing
   skill and must be actionable in one drafting pass. Reject any candidate a
   one-pass draft could not satisfy even if told to. A candidate that can only be
   true of a document that was revised, reviewed, or published — "records a
   position it held in an earlier revision", "cites review-thread feedback" —
   describes history, not text, and is unusable.

   Where an observation about revision points at something a first draft *could*
   do, restate it as that: not "argues against its own earlier position" but
   "states a position it considered and abandoned, with the thing that changed
   the answer".

3. **Not publication process.** Revision permalinks, review-manager front matter,
   status lines, forum-thread credits, retained template comments and pull-request
   numbers separate strongly on the external pairs and are pure genre artifact —
   the gold half of those pairs is a published document and the cold half is not.
   Any candidate keyed on them is dropped here rather than downstream. Content a
   review *produced* is fair game; the machinery recording that a review happened
   is not.

Also ignore raw length. Cold drafts were written to a different budget, ratios
run 0.52–1.24, so "longer", "more sections", "more bullets" measure generation
budget. Count-based candidates are allowed only when the count is of a *kind* of
content that scales with the argument rather than with the page — and even then,
prefer a threshold phrased per item ("each rejected option…") over a total.

## What a good candidate looks like

- **Closed-form.** Answerable yes/no, or by picking one of a small set of named
  levels. Never "how well does it…".
- **Applicable to one document alone.** No candidate may reference the other
  half of a pair, or compare to anything outside the document.
- **Grounded in the pooled observations**, not in general writing advice. Each
  candidate cites the observation(s) that suggested it by pair name.
- **Direction stated.** Which answer is the GOLD-side answer, per the pooled
  evidence.

## Output shape

A single JSON array. Each element:

```json
{
  "id": "d06-c1",
  "question": "Closed-form detect question, applicable to one document alone.",
  "answers": ["discrete answer 1", "discrete answer 2"],
  "gold_side_answer": "which answer the pooled observations put on the GOLD side",
  "evidence_pairs": ["rust-min-publish-age", "internal-2"],
  "why_not_presence": "one line: what a grep-for-heading check would miss here"
}
```

`id` is `d<NN>-c<n>` with `NN` the dimension number given in the input.

Propose between three and six candidates. Fewer is correct when the dimension's
observations converge; do not pad. Emit only the JSON array — no prose, no code
fence.
