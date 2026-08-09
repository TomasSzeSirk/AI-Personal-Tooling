---
name: write-doc
description: Write a technical decision document driven by the Doc Craft feature taxonomy — search the repo for evidence first, then interview the user one question at a time for what only they hold, then draft. Never invents an instance or a source. Use before writing any design or assessment doc.
---

# write-doc

Use this for a design, decision, or assessment document. It is **interactive**:
it gathers evidence before it writes, because three of the taxonomy's features
cannot be satisfied by writing more carefully.

Load `~/.claude/skills/doc-craft/features-decision.md` **before drafting** and
treat each feature as a constraint on the draft, not a checklist applied
afterwards. Derive the questions below from that file rather than from this one —
if the taxonomy changes, this skill follows it.

**Features are satisfied by content, never by adding a heading.** A section
titled for a feature and left thin fails it exactly as an absent section does.

## Why the interview exists

`d02-c5` (a named instance observed in the wild), `d04-c6` (a position this
document held and abandoned), and `d10-c6` (external source text quoted verbatim)
all require evidence from outside the document. A model told to name a concrete
instance with nothing to draw on **invents** one — and fabricated specificity is
worse than the vagueness it replaces: unfalsifiable to the reader, and it passes
the feature check. `doc-reviewer` would score it as satisfied.

**This was measured, not assumed.** A three-arm run on one subject (recorded in
`scripts/doc-craft/evidence.md`) wrote the same document three ways. The arm given
these features *without* the search-and-ask steps scored worse than the arm given
no features at all — 5.63 findings per 100 lines against 4.58 — and invented four
claims, including two fabricated commit hashes inside a `git log` transcript it
had no means to run. The arm that could search and ask fabricated nothing across
16 checkable claims.

**So do not strip this skill down.** There is no valid "just follow the seven
features" shortcut — not as a prompt snippet, not as a lint rule, not as a
paragraph pasted into another skill. Separated from the means to check, these
features stop being standards and become instructions to invent. If you cannot
search the repo and cannot ask the author, do not use this skill; write without
it and leave the claims honestly vague.

## The order is fixed

### 1. Search first

Grep the repo, read the code, follow the references, fetch the docs the brief
names. Anything findable is found, never asked about. Asking the user for
something already on disk spends their attention on work you could have done and
is the fastest way to get an interactive skill abandoned.

Search covers most of `d02-c5` (real error strings, real versions, real call
sites) and most of `d10-c6` (the spec, the help text, the command transcript —
run the command and paste its output).

### 2. Ask only for what is missing

Each unsatisfied feature becomes **one question**. One at a time, multiple choice
where the options are knowable. Skip a question entirely once the search
answered it. The shapes:

- `d02-c5` — "what is a real case where this actually happened?"
- `d04-c6` — "did you hold a different position first, and what changed it?"
- `d10-c6` — "which spec or doc should I quote directly, and where does it live?"

**`d04-c6` is the question no repository can answer.** An abandoned position
exists only in the author's memory or in the conversation that produced the
document. Searching cannot reach it, so asking is the only way to obtain it — and
the answer wanted is both halves: the position held, and the fact or constraint
that defeated it. If nothing was abandoned, say so in the document; that is
better than manufacturing a reversal.

### 3. Never invent

If evidence is unavailable and the user cannot supply it, write the claim as
explicitly unsourced — "unverified; no instance found in this repo" — rather than
inventing a plausible one. An honest gap is a finding for the reader. A
fabricated instance is a defect that survives review.

## Drafting notes

- **Structural rhythm is one instruction, not three.** `d12-c3` (alternation
  inside the longest section) and `d12-c5` (sibling entries varying by weight)
  agree on 18 of 20 corpus documents — they are near-collinear. Treat the
  dimension-12 family as a single instruction: let shape follow what each piece of
  material needs, and stop. Issuing them separately over-corrects layout and
  produces mechanical variation, which is not the point.
- **Do not chase uniform good habits.** Attaching a cost to every recommendation,
  and having every open item name what it bears on, both ran *backwards* in
  discovery: uniform application of the habit is the unsteered signature. Do it
  where it carries weight, not everywhere.
- Self-references must resolve — check that the destination actually says what
  the pointer claims, then link it. **Do this as a pass at the end**, not while
  drafting: a pointer written before its destination exists cannot be checked
  when it is written. In the held-out evaluation this was the one feature that
  failed despite being instructed, and it failed as pointers whose destination
  said something else — a defect the draft had everything it needed to catch.

## After drafting

Offer to run `review-doc` on the result. Findings that come back about invented
or unverifiable evidence mean step 3 was skipped, not that the wording needs
softening.
