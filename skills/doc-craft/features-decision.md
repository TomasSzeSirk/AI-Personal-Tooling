# Feature taxonomy — technical decision documents

Seven features, discovered rather than asserted. Each one separates a steered or
published decision document from an unsteered single-pass draft of the same brief
under the same section scaffold, in at least 5 of the 8 clean corpus pairs. The
tally behind every entry — and every candidate that did not survive — is in
`scripts/doc-craft/evidence.md`.

**These are content constraints, not headings.** Every one of them was chosen
because adding a section cannot satisfy it. Both halves of the corpus were given
the same `##` scaffold, so any feature answerable by `grep '^#'` measures the
template and was cut. A document that adds a subsection titled "Abandoned
positions" and leaves it thin fails `d04-c6` exactly as a document without the
subsection does.

**Seven, not the eight to twelve the plan hoped for.** Twenty-seven of the
sixty-eight candidates fired on *both* halves — including every candidate on
rejected-alternatives depth, the axis the design expected to be strongest. A
single-pass draft that is handed a Rationale and Alternatives heading writes real
rejections with real defeating properties. That is a finding about how little
headroom the template leaves, not a gap to be filled with invented features.

Examples are drawn from the public half of the corpus (rust-lang RFCs, Swift
evolution proposals) or paraphrased; the private documents in the corpus are not
quoted.

---

## Dimension 2 — Referential specificity

### d02-c5 — Claims about existing behaviour name an observed instance

**Detect.** Is at least one factual claim about how things behave today backed by
a named concrete instance observed in the wild — a specific account, package,
version, error string, or reproduction transcript — rather than by assertion
alone?

**Passing.** The claim carries the thing it was drawn from. A registry-identity
proposal arguing that display names collide does not say collisions are possible;
it names an existing account whose handle contains two consecutive hyphens and
shows how the database renders it. The reader can go and look.

**Failing.** The same claim as received wisdom: "other registries have seen
supply-chain incidents", "this pattern is common in the ecosystem", "users find
this confusing". True, unsourced, and unfalsifiable — and the shape an unsteered
draft produces by default, because it is reasoning from what it knows rather than
from what it checked.

**Separates 6/8 clean (2 internal, 4 external).**

---

## Dimension 3 — Entry points & navigation

### d03-c1 — Self-references are resolvable, not prose

**Detect.** When the document points at another of its own sections, does it use
a resolvable link (anchor or heading link), or does it say "see above", "as
discussed below", "the security section forbids"?

**Passing.** `See [Starting with the strict default](#starting-with-the-strict-default)`
— the pointer lands. Anchors defined on the sections that get referred to, links
inline in the body where the reader needs them.

**Failing.** "The drawbacks section warns about this", "sketched above",
"covered in the reference section". Every unsteered draft in the corpus that
failed this one referred across its own sections in prose only. The information
is there; navigating to it is left to the reader's scroll wheel.

This is the one survivor that looks like formatting rather than substance. It is
kept because it is not: an unresolved pointer means the author did not check that
the destination says what the pointer claims, and in three of the corpus's cold
drafts the destination did not.

**Separates 5/8 clean (2 internal, 3 external).**

---

## Dimension 4 — Open threads

### d04-c6 — A position the document itself abandoned, with what defeated it

**Detect.** Does the document record a position *it* considered and abandoned,
naming both the fact or constraint that changed the answer and the replacement
adopted instead?

**Passing.** A resolver proposal strikes through its own earlier recommendation
that a version floor be written into new packages by default, and states the
finding that killed it: the value goes stale and nothing forces it to be
revisited. Old position visible, defeating fact named, replacement stated.

Also passing: an identity proposal that first proposed exposing rename history
publicly, records that reviewers showed the public history re-exposes exactly the
information a rename is meant to retire, and adopts administrator-only tracking
instead.

**Failing.** A rejected-alternatives section only. Options the document never
held, listed and dismissed, is a different thing — every draft in the corpus does
that, steered or not. This feature asks for a position the document *did* hold.

**Single-pass note.** This does not require the document to have been revised. A
first draft can and should record the option it worked with for two sections
before the constraint that killed it turned up. If nothing was abandoned during
drafting, saying so is better than manufacturing a reversal.

**Separates 6/8 clean (2 internal, 4 external).**

---

## Dimension 10 — Grounding & provenance

### d10-c6 — External sources are quoted, not summarized

**Detect.** Does the document reproduce external source text verbatim — a block
quote or fenced excerpt from a specification, documentation page, grammar, error
output, or command transcript — rather than only paraphrasing what the source
says?

**Passing.** A block quote of the package manager's own documentation giving the
exact wording of the retention setting under discussion. A verbatim excerpt of
the earlier proposal's sentence that this one is narrowing. Reproduced help text
next to the change being proposed to it.

**Failing.** Every fenced block in the document is the document's own proposed
output. External sources appear as "the specification requires that…", which is a
summary the reader has to trust. All five unsteered drafts of public documents in
the corpus fenced their own examples and quoted nobody.

**Separates 5/8 clean (1 internal, 4 external).** The internal split is thin;
this feature may be partly a habit of documents written against a public
specification.

---

## Dimension 12 — Structural rhythm

The three features below share a suspicion: a single-pass draft picks one shape
and applies it everywhere. They ask different questions and separate on partly
different pairs, so they are listed separately, but treat them as one
family — satisfying them by mechanically varying formatting is not the point.

### d12-c1 — No single enumeration device runs the whole document

**Detect.** Is a bolded run-in label followed by a paragraph the document's
dominant device for enumerating items, reused as the shape of three or more
separate sections?

**Passing.** Enumeration carried by whatever fits the material — subheadings
where the items are big, plain bullets where they are small, a table where they
are comparable. At most two sections run on the run-in-label shape.

**Failing.** Drawbacks, prior art, unresolved questions and future possibilities
all rendered as `**Label.** One paragraph.` runs. This is the most reliable
single tell in the corpus: four of the five public unsteered drafts did exactly
this, in the same four sections.

**Separates 5/8 clean (2 internal, 3 external).**

### d12-c3 — The longest section alternates prose and formal devices

**Detect.** Inside its single longest technical section, does the document
alternate between prose and a formal device (table, fenced block, diagram) three
or more times, rather than running one device or unbroken prose end to end?

**Passing.** A query-syntax section that runs explanation, then the syntax
itself, then a table of qualifiers, then more explanation, then a table of
operators. Each device carries what prose does badly and stops where it stops
helping.

**Failing.** A reference-level section that is prose and bullets throughout, or a
detailed-design section holding one code block at the top and nothing after. The
material is the same; the reader has to hold it all in prose.

**Separates 5/8 clean (3 internal, 2 external).**

### d12-c5 — Sibling entries vary in shape by what each one needs

**Detect.** Among sibling entries under one parent — alternatives considered,
prior-art entries, rejected options — do entries differ markedly in length and
internal shape, one several times another, one prose-only and another carrying a
table, code, or a link?

**Passing.** In an alternatives section, the pagination alternative runs long and
carries a code sketch because it is the one that nearly won; the
full-metadata-response alternative is three sentences because it lost on a single
point. Shape tracks how much argument each option actually needed.

**Failing.** Every alternative a bold label plus one paragraph of near-identical
length. Uniformity here is the visible signature of an author who allocated
attention evenly instead of by weight — and it usually means the option that
deserved four paragraphs got one.

**Separates 5/8 clean (3 internal, 2 external).**

---

## What is deliberately absent

Do not read the gaps as "these do not matter". They mean an unsteered draft
already does them when handed the heading:

- **Rejection depth.** All six candidates on naming the mechanism and the
  defeating property fired on both halves.
- **Boundary ownership**, **adversarial self-attack**, **failure treatment**.
  Several candidates fired on 8 of 8 pairs.
- **Costs attached to recommendations** and **open items naming what they bear
  on** ran *backwards*: the unsteered half attaches them more reliably, because
  it applies the habit uniformly. Instructing for them would push a draft toward
  the cold-side signature, not away from it.

The taxonomy rests on 10 pairs, 8 of them clean. A feature holding in 5 of 8 is
suggestive, not measured.
