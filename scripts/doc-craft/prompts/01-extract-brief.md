# 01 — Extract a design brief from a gold document

Input: one technical decision document (`$SCRATCH/doc-craft/gold/<name>.md`).
Output: `$SCRATCH/doc-craft/cold/<name>.brief.md`.

A brief is the situation *before* the document was written. It describes what
had to be decided and what constrained the decision — never what was decided.

## What to emit

Markdown, 200–500 words, exactly these four sections:

```markdown
# Brief: <name>

## Problem
## System context
## Constraints
## Decision required
```

- **Problem.** The situation that made a decision necessary. Observable facts
  about the current state — what exists today, what it fails to do, who is
  affected.
- **System context.** The surrounding system a reader needs in order to reason:
  components, actors, existing interfaces, terminology already in use, the
  release or compatibility regime the decision sits inside.
- **Constraints.** What any acceptable answer must respect — compatibility
  guarantees, performance or cost envelopes, security or trust boundaries,
  platform limits, timelines, prior commitments. Constraints that existed
  independently of this document only.
- **Decision required.** One or two sentences naming the question to be
  answered and the scope of the answer, phrased as an open question.

## Exclusions — this is the point of the prompt

The brief must NOT contain, in any form including paraphrase:

- The chosen option, the recommendation, or the direction the document lands on.
- Any option the document rejected, and any reason for rejecting it.
- The document's open questions, unresolved questions, or future work.
- Any mechanism, API, algorithm, type, keyword, or artifact the document
  *invented* — including its name, its shape, and its parameters.
- Trade-off framing that only makes sense once you know the answer ("since
  X is too expensive, ...").
- Section-by-section structure of the source document.

Facts about the world that predate the document belong in the brief. Anything
the document produced does not.

Two checks before writing the file:

1. Could a competent engineer read this brief and arrive at a *different*
   answer than the document did, without noticing they had diverged? If not,
   the brief is steering — cut whatever narrows it.
2. Grep the brief for the distinctive nouns of the document's answer. Any hit
   is a leak; rewrite the sentence in terms of the underlying requirement.

## Rules

- Do not read the brief back against the document to "improve accuracy". One
  pass over the source, one brief.
- Prefer the source's own vocabulary for pre-existing things, so the brief
  reads as though written by someone in that system. Do not adopt vocabulary
  the document coined.
- No headings other than the four above. No bulleted summary of the source.
