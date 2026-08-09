# Doc Craft — Feature discovery evidence

Every candidate feature proposed in Stage 4, kept or dropped, with the tally that
decided it. Dropped rows stay: they are the record of what the shared `##`
template and the RFC/proposal genre account for, and re-running discovery at a
larger n starts from them rather than from scratch.

No document text from the three private golds — `internal-1`, `internal-2`,
`internal-3` — appears in this file, and neither does their organization, their
repositories, their paths, or their subject matter.
Examples in `skills/doc-craft/features-decision.md` are drawn from the public half
of the corpus only.

## How to read the tally

Each candidate was applied to all 20 documents, one document at a time, by a
judge that was not told which half it was reading and never saw the counterpart.
Per pair that gives a 2×2 cell:

| cell | meaning |
|------|---------|
| gold ✓ / cold ✗ | **separates** — the feature is present in the steered half only |
| gold ✓ / cold ✓ | fires on both — template or genre, not steering |
| gold ✗ / cold ✗ | fires on neither — dead weight |
| gold ✗ / cold ✓ | reversed — the unsteered half has it |

**Cut rule (plan §4.4, amended).** Keep a candidate only if it separates in a
strict majority of the clean tier and at least 3 pairs. The clean tier holds 8
pairs, so the bar is **≥5 of 8**. Contaminated-tier separation is recorded as
confirmatory and never counts toward the bar; contaminated non-separation is
uninformative and never drops a candidate, because a cold half reconstructed from
training data converges on its gold regardless of steering.

Tiers:

- **clean (8):** `internal-1`, `internal-2`, `internal-3`,
  `rust-crates-io-identity`, `rust-min-publish-age`, `swift-registry-search`,
  `swift-html-coverage`, `rust-msrv-resolver`
- **contaminated (2):** `rust-try-trait-v2`, `swift-task-locals`
- **internal / external** splits the clean tier 3 / 5. The internal pairs are the
  only ones where both halves are AI-written and steering is the sole variable;
  the external pairs additionally vary authorship and review.

## The A/B mapping

Stage 3's comparisons are blind and phrased "A does X, B does Y". Stage 4 pooled
them only after applying this mapping, which is also committed at
`scripts/doc-craft/blind-map.json`. Half the corpus is gold-as-B; pooling raw A/B
strings would invert direction on those five pairs and produce features that
separate at chance.

| Pair | A | B |
|------|---|---|
| `internal-1` | cold | **gold** |
| `internal-2` | **gold** | cold |
| `internal-3` | **gold** | cold |
| `rust-crates-io-identity` | cold | **gold** |
| `rust-min-publish-age` | **gold** | cold |
| `rust-try-trait-v2` | cold | **gold** |
| `rust-msrv-resolver` | cold | **gold** |
| `swift-registry-search` | cold | **gold** |
| `swift-html-coverage` | **gold** | cold |
| `swift-task-locals` | **gold** | cold |

The mapping was applied mechanically — standalone `A`/`B` tokens rewritten to
`GOLD`/`COLD` — and then checked by hand against the source documents on two
pairs, one in each direction, before any discovery run.

## Merged and pre-application drops

Discovery emitted 77 raw candidates across the 13 dimensions. Nine were resolved
by hand before application: eight near-duplicates merged into the survivor that
stated the question best, and one dropped as an artifact of how the corpus was
built. The remaining 68 were applied to all 20 documents.

| Candidate | Resolution |
|-----------|------------|
| `d07-c1` | merged into `d04-c6` |
| `d07-c2` | merged into `d04-c6` |
| `d03-c2` | merged into `d03-c1` |
| `d05-c5` | merged into `d05-c4` |
| `d11-c1` | merged into `d04-c4` |
| `d11-c2` | merged into `d04-c1` |
| `d11-c5` | merged into `d07-c6` |
| `d01-c6` | merged into `d02-c4` |
| `d03-c4` | dropped before application — Measures the Stage-2 continuation procedure (stray "(continued)" blocks demoted by hand), not the document. Construction artifact. |

Where a merge combined a revision-history phrasing with a single-pass one, the
single-pass phrasing won — `d07-c1` ("an earlier draft proposed…") and `d07-c2`
both collapsed into `d04-c6`, which asks for an abandoned position and the fact
that defeated it, something a first draft can state.

## The tally

`sep` counts clean pairs separating in the gold direction. `int` and `ext` split
that count by source. `both`, `neither` and `rev` are clean-pair counts for the
other three cells. `cont-sep` names contaminated pairs that separated —
confirmatory only.

| id | dim | Candidate | sep | int | ext | both | neither | rev | cont-sep | Disposition |
|----|-----|-----------|-----|-----|-----|------|---------|-----|----------|-------------|
| `d02-c5` | 2 | Is at least one factual claim about existing behavior backed by a named concrete instance observed in the wild (a specific account, package, version, error text, or reproduction transcript) rather than by assertion alone? | 6/8 | 2/3 | 4/5 | 1 | 1 | 0 | rust-try-trait-v2 | **kept** |
| `d04-c6` | 4 | Does the document record a position it considered and abandoned, naming the fact or constraint that changed the answer and the replacement adopted instead? | 6/8 | 2/3 | 4/5 | 0 | 1 | 1 | rust-try-trait-v2 | **kept** |
| `d03-c1` | 3 | Does the document cross-reference its own sections as resolvable links (anchor or heading links) rather than by name, number or 'see above' in prose? | 5/8 | 2/3 | 3/5 | 0 | 3 | 0 | — | **kept** |
| `d10-c6` | 10 | Does the document reproduce external source text verbatim (block quote or fenced excerpt from a spec, doc page, grammar, error output or command transcript) rather than only paraphrasing what the source says? | 5/8 | 1/3 | 4/5 | 1 | 2 | 0 | rust-try-trait-v2,swift-task-locals | **kept** |
| `d12-c1` | 12 | Is a bolded run-in label followed by a paragraph the document's dominant device for enumerating items, reused as the shape of three or more separate sections? | 5/8 | 2/3 | 3/5 | 1 | 2 | 0 | rust-try-trait-v2,swift-task-locals | **kept** |
| `d12-c3` | 12 | Inside its single longest technical section, does the document alternate between prose and a formal device (table, fenced block, diagram) three or more times, rather than running one device or unbroken prose through the section? | 5/8 | 3/3 | 2/5 | 3 | 0 | 0 | — | **kept** |
| `d12-c5` | 12 | Among sibling entries under one parent (alternatives, prior-art entries, rejected options), do entries differ markedly in length and internal shape according to what each one needs — one entry several times another, one prose-only and another table- or link-based? | 5/8 | 3/3 | 2/5 | 2 | 1 | 0 | — | **kept** |
| `d12-c6` | 12 | Does the document contain at least one run of three or more sibling items sharing an identical labelled field template (each item carrying the same named fields in the same order, e.g. Type / Default / Environment, or Priority / Pain points)? | 5/8 → 2/8 | 2/3 → 0/3 | 3/5 → 2/5 | 0 | 3 | 0 | — | dropped on audit — see "Audited out" |
| `d10-c1` | 10 | For claims about systems, artifacts or prior art outside this document, are they attached to a resolvable identifier (URL, PR/issue number, commit SHA, spec/RFC name, permalink), or named in prose only? | 4/8 | 1/3 | 3/5 | 1 | 2 | 1 | rust-try-trait-v2,swift-task-locals | dropped — separates on 4/8 clean, below threshold |
| `d12-c2` | 12 | Do fenced code blocks, tables or diagrams appear in the document's closing third (rationale, alternatives, prior art, unresolved questions) and not only in its design and reference sections? | 4/8 | 2/3 | 2/5 | 0 | 4 | 0 | rust-try-trait-v2 | dropped — separates on 4/8 clean, below threshold |
| `d05-c3` | 5 | Where a value or parameter is presented as provisional, does the document still give a concrete figure alongside the provisional marker? | 3/8 | 2/3 | 1/5 | 1 | 3 | 1 | — | dropped — separates on 3/8 clean, below threshold |
| `d01-c2` | 1 | Does the document give an explicit routing instruction telling a reader which parts to skip or where to go outside the document for context it declines to cover? | 2/8 | 0/3 | 2/5 | 2 | 4 | 0 | rust-try-trait-v2,swift-task-locals | dropped — separates on 2/8 clean, below threshold |
| `d02-c6` | 2 | When the document proposes a change, does it name the existing code location it lands in — file, type, function, or contract symbol — or does it describe the change without naming where it attaches? | 2/8 | 0/3 | 2/5 | 4 | 1 | 1 | — | dropped — separates on 2/8 clean, below threshold |
| `d03-c5` | 3 | Within roughly the first fifteen lines after the title, does the reader get the recommendation in a scannable concrete form — a numbered/bulleted digest, a config snippet, or a named decision — as opposed to framing paragraphs or a single enumerative sentence listing every component? | 2/8 | 1/3 | 1/5 | 2 | 3 | 1 | rust-try-trait-v2 | dropped — separates on 2/8 clean, below threshold |
| `d04-c1` | 4 | Do the document's unresolved items appear at the points in the body where each gap bites (or cross-linked from there), rather than only inside a dedicated open-questions section? | 2/8 | 0/3 | 2/5 | 5 | 0 | 1 | swift-task-locals | dropped — fires on both halves (template/genre) |
| `d04-c3` | 4 | For the open items whose resolution lies outside the author, is a specific deciding party, requirement, or follow-on document named? | 2/8 | 0/3 | 2/5 | 3 | 2 | 1 | swift-task-locals | dropped — separates on 2/8 clean, below threshold |
| `d07-c3` | 7 | Where the document reverses a position, is the reversal narrated at the point of the semantics it changes — superseded position stated immediately before the new one — or is it confined to a separate history/alternatives section away from the affected text? | 2/8 | 1/3 | 1/5 | 2 | 4 | 0 | rust-try-trait-v2,swift-task-locals | dropped — separates on 2/8 clean, below threshold |
| `d07-c5` | 7 | When the document conflicts with a prior source it inherits from (upstream notes, README, predecessor RFC), does it name the conflict as a deliberate deviation and argue the source's rule down, or does it contradict the source without marking that it is doing so? | 2/8 | 1/3 | 1/5 | 1 | 3 | 2 | — | dropped — separates on 2/8 clean, below threshold |
| `d08-c1` | 8 | For the items the document places outside its own scope, does every such item name a specific owner elsewhere (a named team, person, other document, work item, venue, or process), or is at least one left with no named owner? | 2/8 | 2/3 | 0/5 | 0 | 6 | 0 | — | dropped — fires on neither half (dead weight) |
| `d09-c5` | 9 | Does the document report its own design against a stated evaluation — a scorecard, coverage figure, cost table, or criteria list — in a form that shows at least one entry where its own design falls short? | 2/8 | 1/3 | 1/5 | 1 | 5 | 0 | — | dropped — fires on neither half (dead weight) |
| `d10-c2` | 10 | Do the document's non-structural numeric quantities (measurements, rates, prevalence, costs — not interface constants or defined thresholds) each state where the number came from, e.g. a named external source, a table with a cited origin, or arithmetic shown from named inputs? | 2/8 | 0/3 | 2/5 | 2 | 3 | 1 | — | dropped — separates on 2/8 clean, below threshold |
| `d10-c4` | 10 | Does the document cite a specific external or upstream artifact whose content cuts against its own proposal, and then state what it does with that contradiction? | 2/8 | 1/3 | 1/5 | 2 | 2 | 2 | — | dropped — separates on 2/8 clean, below threshold |
| `d12-c4` | 12 | Does the document carry three or more tables whose column sets differ from each other, each carrying a comparison or per-case ruling that the surrounding prose then only annotates for exceptions? | 2/8 | 2/3 | 0/5 | 1 | 5 | 0 | — | dropped — fires on neither half (dead weight) |
| `d13-c4` | 13 | Does the document enumerate the failure space as an exhaustive partition — cases indexed by a stated variable (parse case, exit path, source kind, status code, scenario row) with each case assigned an outcome — or does it narrate failures as selected examples? | 2/8 | 1/3 | 1/5 | 5 | 1 | 0 | — | dropped — fires on both halves (template/genre) |
| `d01-c3` | 1 | For terms of art the document uses, does it define at least one on first appearance from a primitive source (dictionary sense, enum body, worked non-generic example) rather than assuming all of them? | 1/8 | 1/3 | 0/5 | 7 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d01-c5` | 1 | Where does the document put its longest expansion? | 1/8 | 0/3 | 1/5 | 0 | 6 | 1 | rust-try-trait-v2 | dropped — fires on neither half (dead weight) |
| `d02-c1` | 2 | Does every parameter, threshold, timeout, or limit the document proposes carry a stated value (number, string, or mode) at the point it is introduced, or is at least one left deferred, unpriced, or to-be-measured? | 1/8 | 0/3 | 1/5 | 1 | 6 | 0 | rust-try-trait-v2 | dropped — fires on neither half (dead weight) |
| `d02-c3` | 2 | Is every third-party tool, library, macro, service, or component the argument leans on named by its actual identifier, or is at least one referenced by generic noun or placeholder symbol? | 1/8 | 0/3 | 1/5 | 6 | 1 | 0 | — | dropped — fires on both halves (template/genre) |
| `d02-c4` | 2 | Are the concrete artifacts the argument leans on (payloads, schemas, config, help text, terminal output, source declarations) reproduced verbatim in fenced blocks rather than described in running prose? | 1/8 | 0/3 | 1/5 | 5 | 2 | 0 | — | dropped — fires on both halves (template/genre) |
| `d03-c3` | 3 | Inside a section long enough to need internal navigation, what carries the sub-structure? | 1/8 | 1/3 | 0/5 | 7 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d03-c6` | 3 | Does the document contain a section or block whose job is routing rather than content — mapping its own items (scenarios, changes, additions) onto destinations such as implementing work items, documentation pages, or downstream owners? | 1/8 | 0/3 | 1/5 | 2 | 4 | 1 | rust-try-trait-v2 | dropped — separates on 1/8 clean, below threshold |
| `d04-c4` | 4 | Do the document's unresolved items enumerate named candidate answers, each carrying its own objection or consequence, rather than posing the question alone? | 1/8 | 0/3 | 1/5 | 0 | 5 | 2 | rust-try-trait-v2 | dropped — fires on neither half (dead weight) |
| `d04-c5` | 4 | How are the open items dispositioned? | 1/8 | 1/3 | 0/5 | 0 | 5 | 2 | — | dropped — fires on neither half (dead weight) |
| `d07-c4` | 7 | Does the document reverse a prior *shipped* or externally-established behaviour with explicit prior-to framing that shows the old and new state side by side (old vs new help text, counted existing surface before consolidation, deprecated families)? | 1/8 | 0/3 | 1/5 | 2 | 5 | 0 | rust-try-trait-v2 | dropped — fires on neither half (dead weight) |
| `d07-c6` | 7 | Does the document name a concrete future event, measurement or landed change that would reopen a decision it has already taken? | 1/8 | 1/3 | 0/5 | 5 | 1 | 1 | swift-task-locals | dropped — fires on both halves (template/genre) |
| `d08-c2` | 8 | Does each excluded or deferred item carry a stated reason for its exclusion, or are some listed bare? | 1/8 | 1/3 | 0/5 | 1 | 2 | 4 | — | dropped — reversed direction (cold-side feature) |
| `d09-c2` | 9 | For the risks the document raises against its own design, does at least one name the harm that remains after the proposed mitigation and who or what it lands on? | 1/8 | 0/3 | 1/5 | 4 | 0 | 3 | — | dropped — separates on 1/8 clean, below threshold |
| `d09-c4` | 9 | Does the document show a worked case in which its own design fails — failing code, a named party harmed, a labeled failure example, or a table of what remains possible under it — in rendered text rather than as an abstract statement of risk? | 1/8 | 1/3 | 0/5 | 2 | 4 | 1 | rust-try-trait-v2,swift-task-locals | dropped — separates on 1/8 clean, below threshold |
| `d10-c5` | 10 | For each prior-art or comparison system it names, does the document give the specific sourced mechanism detail it is drawing on (a named field, parameter, window, file or API), or only the system's behaviour in general terms? | 1/8 | 0/3 | 1/5 | 0 | 5 | 2 | rust-try-trait-v2 | dropped — fires on neither half (dead weight) |
| `d11-c4` | 11 | Does the document state a leaning or recommended default on at least one open item together with the reason for it or the condition that would revisit it? | 1/8 | 1/3 | 0/5 | 6 | 0 | 1 | — | dropped — fires on both halves (template/genre) |
| `d13-c3` | 13 | Is at least one failure path specified as a verbatim artifact the system emits — an error string, diagnostic block, status code binding, or exit code — rather than described only in prose? | 1/8 | 0/3 | 1/5 | 4 | 3 | 0 | swift-task-locals | dropped — separates on 1/8 clean, below threshold |
| `d01-c1` | 1 | When the document addresses more than one reader role, how is the split carried in the text? | 0/8 | 0/3 | 0/5 | 0 | 8 | 0 | — | dropped — fires on neither half (dead weight) |
| `d01-c4` | 1 | Does the document anticipate a specific wrong belief or wrong starting frame the reader is expected to arrive with, and correct it explicitly? | 0/8 | 0/3 | 0/5 | 7 | 0 | 1 | — | dropped — fires on both halves (template/genre) |
| `d02-c2` | 2 | Is each new configuration key, field, constant, or parameter the design introduces given its exact spelling, or does the document refer to at least one of them by descriptive phrase only? | 0/8 | 0/3 | 0/5 | 4 | 2 | 2 | — | dropped — separates on 0/8 clean, below threshold |
| `d04-c2` | 4 | Does each open item state what in this document it bears on — a design choice it justifies, a section it constrains, or an exclusion it explains? | 0/8 | 0/3 | 0/5 | 1 | 1 | 6 | rust-try-trait-v2 | dropped — reversed direction (cold-side feature) |
| `d05-c1` | 5 | Does the document vary its modal register by claim type — unhedged normative verbs (must/never/will) for core rules or invariants, and softer verbs (can/may/we could/we plan to) for mitigations, sequencing or secondary items? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d05-c2` | 5 | Are the document's hedges attached to specifically named uncertainties (an unmeasured scenario, an underived number, an unverified prior-art claim, an inference labeled speculation), or are they generic softeners with no named object? | 0/8 | 0/3 | 0/5 | 6 | 0 | 2 | — | dropped — fires on both halves (template/genre) |
| `d05-c4` | 5 | Does each recommendation carry its own cost, concession or trade-off in the same passage — including at least one limitation of the option the document itself advocates? | 0/8 | 0/3 | 0/5 | 1 | 0 | 7 | — | dropped — reversed direction (cold-side feature) |
| `d05-c6` | 5 | Does the document mark the settled/unsettled seam explicitly — naming which part of an open item is already decided, or labeling a constraint as hard versus a preference — rather than leaving open items uniformly open? | 0/8 | 0/3 | 0/5 | 7 | 0 | 1 | — | dropped — fires on both halves (template/genre) |
| `d06-c1` | 6 | For each rejected option, does the text name the mechanism that fails plus the specific property, constraint or quantity that defeats it, rather than asserting a preference or a vague cost? | 0/8 | 0/3 | 0/5 | 5 | 0 | 3 | — | dropped — fires on both halves (template/genre) |
| `d06-c2` | 6 | Does at least one rejected option get credited with a specific thing it does better than the chosen design before the reason it lost is given? | 0/8 | 0/3 | 0/5 | 7 | 1 | 0 | — | dropped — fires on both halves (template/genre) |
| `d06-c3` | 6 | Does each rejection carry an explicit verdict — a stated disposition such as rejected, deferred, viable-but-not-preferred, or supplementary-only — rather than trailing off on its last cost? | 0/8 | 0/3 | 0/5 | 3 | 2 | 3 | — | dropped — separates on 0/8 clean, below threshold |
| `d06-c4` | 6 | Is at least one rejection stated as graded rather than binary — deferred to a named phase, admitted as supplementary, or partially adopted — with a stated condition or trigger under which it would be revisited? | 0/8 | 0/3 | 0/5 | 5 | 2 | 1 | rust-try-trait-v2 | dropped — fires on both halves (template/genre) |
| `d06-c5` | 6 | Does at least one rejection carry a quantity, a named concrete instance, or a worked scenario as the basis for the loss (a measured figure, named crates/APIs, an attack path, a collision walkthrough), rather than only an abstract assertion? | 0/8 | 0/3 | 0/5 | 6 | 0 | 2 | — | dropped — fires on both halves (template/genre) |
| `d06-c6` | 6 | Are rejections tied back to something else in the document — a constraint, goal or workflow stated elsewhere, or a fixed comparison axis applied across competing designs — rather than argued only on an axis local to that option? | 0/8 | 0/3 | 0/5 | 6 | 0 | 2 | — | dropped — fires on both halves (template/genre) |
| `d08-c3` | 8 | Where do the document's scope boundaries live: distributed across the body (summary sentence, section openings, header status line, per-row table columns, parameter rows), or collected into one dedicated not-in-scope section? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d08-c4` | 8 | Does the document specify the content of at least one handoff — what the other owner receives from it, or what it receives from them (a named artifact, a contract, an interface with its arguments, a precondition) — or does it name the other owner without specifying what crosses the boundary? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d08-c5` | 8 | Does the document state at least one thing it deliberately does not guarantee, prevent, or protect against, together with the reason it declines? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d08-c6` | 8 | Is at least one boundary drawn by mechanism — what the system can and cannot distinguish or record, which layer owns a semantic, what is contract versus replaceable implementation — rather than every boundary being drawn as a topic excluded from scope? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d09-c1` | 9 | Does the document state at least one cost or objection against its own chosen design that it leaves standing — no rebuttal, no mitigation, no 'but' clause — rather than answering every stated cost immediately? | 0/8 | 0/3 | 0/5 | 5 | 2 | 1 | swift-task-locals | dropped — fires on both halves (template/genre) |
| `d09-c3` | 9 | Does the document name a concrete case in which its own design is the wrong choice — a workload, scenario, or scope where a reader should not use it, or a condition under which the proposal should be rejected? | 0/8 | 0/3 | 0/5 | 3 | 5 | 0 | swift-task-locals | dropped — fires on neither half (dead weight) |
| `d09-c6` | 9 | Does the document attack a mechanism it introduces itself — a rule, marker, warning, phase, parameter bound, or taxonomy — naming the specific mechanism and the failure mode or misreading it produces? | 0/8 | 0/3 | 0/5 | 6 | 0 | 2 | swift-task-locals | dropped — fires on both halves (template/genre) |
| `d10-c3` | 10 | Does the document mark the limits of at least one piece of evidence it relies on — data whose reliability it cautions about, numbers labelled illustrative rather than measured, a prior-art detail it could not confirm, or a quantity it states is not yet measured? | 0/8 | 0/3 | 0/5 | 5 | 2 | 1 | swift-task-locals | dropped — fires on both halves (template/genre) |
| `d11-c3` | 11 | Does at least one open item state a numeric bar, measurement, named data source, or falsifiable check that would settle it? | 0/8 | 0/3 | 0/5 | 4 | 2 | 2 | swift-task-locals | dropped — separates on 0/8 clean, below threshold |
| `d13-c1` | 13 | For the document's own proposed design, does it name at least one failure mode that its own mechanism introduces or leaves unfixed, distinct from failures of the system it replaces? | 0/8 | 0/3 | 0/5 | 7 | 0 | 1 | — | dropped — fires on both halves (template/genre) |
| `d13-c2` | 13 | Does the document state at least one failure case it resolves to an outcome it labels unfair, non-viable, out of scope, or deliberately unpunished — with the reason for accepting that outcome? | 0/8 | 0/3 | 0/5 | 7 | 0 | 1 | — | dropped — fires on both halves (template/genre) |
| `d13-c5` | 13 | When the document argues for its chosen failure behaviour over a rejected one, does the argument name the failure mode the rejected alternative would introduce (silent wrongness, order dependence, confusion, a worse error direction), or does it assert the choice without a comparative failure mode? | 0/8 | 0/3 | 0/5 | 8 | 0 | 0 | — | dropped — fires on both halves (template/genre) |
| `d13-c6` | 13 | Does the document specify what survives or is cleaned up after a failure — retained logs or artifacts, released locks, reconciliation of in-flight state, rollback scope, or an explicitly non-undone effect — with the specific resource named? | 0/8 | 0/3 | 0/5 | 4 | 1 | 3 | — | dropped — separates on 0/8 clean, below threshold |

## Result

77 candidates proposed, 9 merged or dropped by hand, 68 applied, 8 reached the
≥5/8 bar, one of those failed the firing audit below: **7 kept**. That is one
short of the plan's 8–12 acceptance band, reported as it came out rather than
padded — a feature invented to reach the number would be shared by `write-doc`
and `doc-reviewer` in Stage 5 and neither would catch it.

| Disposition | Count |
|-------------|-------|
| kept (≥5/8 clean, audit passed) | 7 |
| dropped — fires on both halves (template/genre) | 27 |
| dropped — fires on neither half (dead weight) | 11 |
| dropped — separates, but below the ≥5/8 bar | 19 |
| dropped — reversed direction (cold-side feature) | 3 |
| dropped on audit — separation rested on a genre artifact | 1 |

The largest single bucket is "fires on both halves". That is the spec §5 template
confound showing up exactly where it was predicted to: given the same `##`
scaffold, a single-pass draft fills every section, and most depth questions you
can ask about a section's *contents* also come back true on both sides.

## Audited out

Every gold-side firing behind a candidate at or near the bar was read back
against the document before the candidate was written into the taxonomy. One
failed.

**`d12-c6`** — "at least one run of three or more sibling items sharing an
identical labelled-field template" — reached 5/8 on the raw tally and drops to
2/8 once its firings are inspected:

- `swift-html-coverage`: the run is the proposal's front-matter block
  (Proposal / Authors / Review Manager / Status / Implementation). Publication
  machinery, excluded by the discovery prompt's third constraint. Invalid.
- both internal pairs: the run is a table's repeated columns, not a run of
  sibling items — and that is already `d12-c4`'s question, which separates on
  2/8. Invalid, and double-counting.
- `rust-min-publish-age` and `rust-msrv-resolver`: genuine — repeated
  configuration entries carrying the same three named fields, and a repeated
  two-field template across four workflow entries.

Two valid separations out of eight is well under the bar. The lesson generalizes:
a labelled-field run is what document *templates* look like, so a candidate that
rewards them will keep catching front matter. The audit is cheap and should run
on every future candidate whose separations cluster on the external tier.

## Dimensions that produced nothing

Seven of the thirteen dimensions produced no candidate reaching even 3 of 8:
**1 reader model, 6 alternatives & rejection depth, 7 self-supersession, 8
boundary ownership, 9 adversarial self-attack, 11 live openness, 13 failure
treatment.**

Dimension 6 is the sharpest negative result, because it is the axis the spec
treats as the flagship. All six of its candidates landed at 0/8, with 3–7 of the
eight clean pairs firing on **both** halves. Told to fill a rejected-alternatives
section, a single-pass draft names mechanisms, attaches defeating properties,
credits what the loser did better, and grades its rejections — every depth
question we knew how to ask about rejections is satisfied by both halves. The
depth-not-presence rule was necessary but not sufficient here: the depth itself
is in the template's gravitational field.

This also disposes of the `internal-1` dimension-6 exposure carried forward
from `corpus.md:155-174`. That brief narrows the rejected-alternatives space, so
dimension-6 separation on that pair was to be treated with suspicion — but no
dimension-6 candidate survived on any pair, so nothing in the taxonomy rests on
it.

Dimensions 8, 9 and 13 fail the same way. `d08-c3`, `d08-c4`, `d08-c5`, `d08-c6`
and `d13-c5` each fire on 8 of 8 clean pairs. Two candidates ran backwards hard
enough to be worth naming: `d05-c4` (each recommendation carries its own cost)
reversed on 7 of 8 pairs and `d04-c2` (each open item names what it bears on) on
6 — the unsteered half is *more* likely to bolt a trade-off sentence onto every
recommendation and a "this affects §N" clause onto every open item, because that
is what an instruction-following draft does uniformly. Uniform application of a
good habit is itself a cold-draft signature; it is not something to instruct
`write-doc` to do.

## Covariates

**Length ratio.** Cold/gold line ratios run 0.52–1.24; `rust-try-trait-v2` (0.53)
and `rust-crates-io-identity` (0.52) sit below the 60% floor, `internal-2`
(1.23) and `internal-3` (1.24) run over. For each survivor, the mean ratio of
the pairs it separates on versus the pairs it does not:

| Feature | mean ratio, separating | mean ratio, not separating |
|---------|-----------------------|---------------------------|
| `d02-c5` | 0.82 | 1.00 |
| `d03-c1` | 0.83 | 0.92 |
| `d04-c6` | 0.82 | 1.00 |
| `d10-c6` | 0.80 | 0.96 |
| `d12-c1` | 0.90 | 0.80 |
| `d12-c3` | 0.92 | 0.76 |
| `d12-c5` | 0.92 | 0.77 |

No survivor is carried by the two below-floor pairs. The three dimension-12
survivors separate slightly *more* on the pairs where the cold half came in
**over** length — the opposite of what a generation-budget artifact would do — and
the four non-structural survivors separate on shorter-cold pairs by a margin
(0.80–0.83 vs 0.92–1.00) too small to distinguish from the fact that
`rust-crates-io-identity` is both the shortest cold and a rich gold. Recorded as a
weak, unresolved covariate on `d02-c5`, `d04-c6` and `d10-c6`; not disqualifying.

**Contaminated tier.** No survivor was decided by it. `d02-c5`, `d03-c1` and
`d04-c6` fire on both halves of `swift-task-locals`, which is what recall
predicts and what the rule says to ignore. `d12-c3` and `d12-c5` fire on both
halves of both contaminated pairs.

## Clean-tier only, unresolved

No survivor separates on the internal pairs while failing the clean external
pairs, so **no feature earns the house-style label**. Every survivor carries at
least two clean external separations alongside its internal ones:

| Feature | internal | clean external |
|---------|----------|----------------|
| `d02-c5` | 2/3 | 4/5 |
| `d03-c1` | 2/3 | 3/5 |
| `d04-c6` | 2/3 | 4/5 |
| `d10-c6` | 1/3 | 4/5 |
| `d12-c1` | 2/3 | 3/5 |
| `d12-c3` | 3/3 | 2/5 |
| `d12-c5` | 3/3 | 2/5 |

Two dropped candidates do fit the unresolved shape and are recorded here rather
than as house style, per plan §4.6: `d08-c1` (every out-of-scope item names an
owner) and `d12-c4` (three or more tables with differing column sets), each
separating on 2 of 3 internal pairs and 0 of 5 clean external pairs. Two internal
separations out of three is not evidence of anything at n=3; they are listed so a
larger corpus can revisit them, not because the design resolved them.

## What the survivors are not

`d12-c1`, `d12-c3` and `d12-c5` are all dimension 12, and three of seven features
sitting on one axis is a real weakness of this result. They were kept as three
features because they ask different questions — dominant device, alternation
inside one section, and sibling variance — and because merging them would hide
that they separate on partly different pairs (`d12-c3` and `d12-c5` on 3/3
internal, `d12-c1` on 2/3). But they plausibly share one underlying cause: a
single-pass draft picks a shape and applies it uniformly. Stage 7's per-feature
finding map is the first chance to test whether they behave as three features or
one.

**`d12-c3` and `d12-c5` are near-collinear and should be read as one.** Their
firing vectors agree on **18 of 20 documents**, and they separate on 4 of the same
5 clean pairs — differing only by `swift-html-coverage` versus
`swift-registry-search`. The 3/3-versus-2/3 internal split above distinguishes
`d12-c1` from the other two; it says nothing about `c3` versus `c5`, which is
where the collinearity actually sits. At this corpus size they are one feature
listed twice, and `write-doc` will read them as two independent instructions.

If Stage 7 collapses them, the substantive core of the taxonomy is `d02-c5`,
`d04-c6` and `d10-c6` — three features, not seven. Stage 5 and Stage 7 should be
read with that number in view rather than the headline count.

---

## Live three-arm run — 2026-08-09

One subject, written three ways, then reviewed blind by `doc-reviewer`. Subject:
whether this repo's `docs/specs/` and `docs/plans/` should stay gitignored —
chosen because the author held knowledge the repository does not contain.

All three arms received an identical brief and an identical six-heading scaffold,
targeted the same length, and ran in separate contexts.

| Arm | Lines | Findings | Per 100 lines | Fabrications |
|-----|-------|----------|---------------|--------------|
| A — cold prompt, no taxonomy | 131 | 6 | 4.58 | 0 |
| B — taxonomy, interview and repo access suppressed | 142 | 8 | 5.63 | **4** |
| C — taxonomy + interview + repo access | 173 | 5 | 2.89 | 0 |

**The taxonomy alone is net-negative.** Arm B scored worse than the cold control
on the normalized rate and fabricated four claims: two invented commit hashes in
a `git log` transcript it had no means to run (`a1c4f02`, `9e3b117` — both
`fatal: Not a valid object name`), a wrong `.gitignore` line number, and a
reference to a tracked file that does not exist.

The failure is visible in which feature fired. Arms A and B were both flagged on
`d02-c5`, for opposite reasons: A for asserting without evidence, B for evidence
that could not be checked. **The taxonomy converted a vagueness failure into a
fabrication failure** — and fabrication is the worse of the two, because it is
unfalsifiable to a reader and it passes a naive feature check. The reviewer
caught B's line-number error only through internal contradiction and scored the
invented hashes merely "unverifiable".

Arm C's 16 checkable claims all verified exactly, including a README row
reproduced with its trailing period and two block quotes carried correctly across
a source line break.

**Consequence for anything built on this taxonomy:** `d02-c5` and `d10-c6` are
satisfiable by invention. They are safe only for a writer that can go and check.
A taxonomy-only variant of `write-doc` — a prompt snippet, a lint rule, seven
bullet points pasted into another skill — is worse than no taxonomy at all.

**What this is not.** n=1 subject, one arm per condition, no repeats: an
observation, not a measurement. Arm C confounds three variables — taxonomy,
interview answers, and repo access — and the fabrication asymmetry most plausibly
comes from repo access, the *search* half of the skill, rather than the interview
half. The interview's distinct contribution (`d04-c6`) appears as a single
finding: arm A was the only draft flagged for recording no abandoned position.
Arm C was also the longest draft, and findings-per-line partly rewards length.
The reviewer shares a model family with all three writers and judged without
tools.

---

## Held-out evaluation — 2026-08-09 (Stage 7)

Three held-out briefs, never used in discovery, each written twice: **arm A** =
`prompts/02-write-cold.md` unchanged, **arm B** = the taxonomy loaded with the
interview and repository access suppressed. Same briefs, same normalized H2
scaffolds, same model, one pass, no tools, both arms targeting 450 lines.
Reviewed blind by `doc-reviewer` — A/B randomized per document, filenames
carrying no arm, mapping written to a file the reviewer never saw.

**Deviation from the plan:** held-out golds run 1977–2205 lines, so gold-parity
targets were not runnable. Both arms got the same 450-line target instead; parity
here is between arms, which is what the comparison needs. Drafts still came in at
different lengths, so the normalized rate carries the result and the raw count is
reported beside it.

| Document | Arm | Lines | Findings | Per 100 lines |
|----------|-----|-------|----------|---------------|
| `k8s-object-storage` | A control | 396 | 8 | 2.02 |
| `k8s-object-storage` | B taxonomy | 620 | 8 | 1.29 |
| `rust-default-field-values` | A control | 321 | 10 | 3.12 |
| `rust-default-field-values` | B taxonomy | 546 | 7 | 1.28 |
| `swift-archival` | A control | 796 | 8 | 1.01 |
| `swift-archival` | B taxonomy | 525 | 11 | 2.10 |
| **pooled** | A | 1513 | 26 | 1.72 |
| **pooled** | B | 1691 | 26 | 1.54 |

**The acceptance check is not met, and that is the reported result.** It asked
for fewer findings in the treatment arm on at least 2 of 3 documents with no
document worse. Treatment wins on raw count once (`rust-default-field-values`,
7 vs 10), ties once, and loses once (`swift-archival`, 11 vs 8). On the
normalized rate it wins twice and loses once. Pooled, 26 findings against 26.
Per plan, the taxonomy is not tuned against these three documents to force a
pass.

### Where the findings moved

Findings by feature, pooled across the three documents in each arm:

| Feature | A control | B taxonomy |
|---------|-----------|------------|
| `d02-c5` named instance | 6 | **11** |
| `d10-c6` verbatim external source | 3 | **5** |
| `d03-c1` resolvable self-reference | 5 | 4 |
| `d04-c6` abandoned position | 2 | 1 |
| `d12-c1` dominant run-in label | 2 | 1 |
| `d12-c5` sibling entries vary | 3 | 1 |
| `d12-c3` alternation in longest section | 0 | 2 |
| not a taxonomy feature | 5 | 1 |

The aggregate wash hides two opposite movements. **The structural family
responded to instruction**: `d12-c1`, `d12-c5` and `d04-c6` together fall from 7
findings to 3, and non-feature defects fall from 5 to 1. **The evidence family
went backwards**: `d02-c5` and `d10-c6` rise from 9 to 16. Told to name observed
instances and quote external sources with nothing to look up, arm B produced them
in volume, and the reviewer flagged each as unverifiable. This replicates the
three-arm run's central finding on documents that did not shape the taxonomy,
which is the strongest evidence in the project for the search-and-ask design of
`write-doc`.

`d12-c3` moving the wrong way (0 → 2) is within noise at n=3 and is also the
feature `features-decision.md` already flags as near-collinear with `d12-c5`.

### Fabrication count

Every quoted external source and every dated claim in both arms was checked
against the real source.

| Claim | Arm | Verdict |
|-------|-----|---------|
| `std::process::Command` struct docs, two paragraphs (`rust-default-field-values`) | B | **verbatim correct** — matches doc.rust-lang.org exactly |
| Rust Reference `StructField` grammar production (`rust-default-field-values`) | B | **correct** — matches the Reference |
| Kubernetes ephemeral-volumes sentence (`k8s-object-storage`) | B | real sentence, **one-word misquote** ("Some application" for "Some applications") |
| Foundation `JSONSerialization` return-value text (`swift-archival`) | B | **unverified** — Apple's rendered docs could not be fetched and the wording does not match the return-value text reachable elsewhere |
| Implementation History: 5 dated milestones (`k8s-object-storage`) | B | **fabricated** — the real KEP records "created 25 Nov. 2019" and "v1alpha1 approved alongside Kubernetes v1.25"; the draft claims 2020-09 and "v1alpha1 released with Kubernetes 1.22" |
| Implementation History: 5 dated milestones (`k8s-object-storage`) | A | **fabricated** — same section, same class of invention, different invented dates |
| "Held for the first two drafts of this document" (`k8s-object-storage`) | B | **fabricated** — the draft is a single pass; there were no two drafts. `d04-c6` satisfied by inventing a drafting history |

Arm A produced no external quotations at all, so it had no opportunity to
misquote — its one fabrication is the dated milestone list, which the KEP
template solicits from either arm.

Two results matter more than the count. First, **arm B's verifiable quotes were
accurate**: on subjects the model knows well (Rust standard library, the Rust
Reference) `d10-c6` produced correct verbatim text rather than invention, which
is a weaker result than "the taxonomy always fabricates" and worth recording
against it. Second, **`d04-c6` was satisfied by fabrication** — arm B invented an
abandonment history for a document that had none, in exactly the shape the
feature asks for, and the blind reviewer flagged it only as unverifiable. That is
the failure `write-doc`'s interview exists to prevent, now observed on a held-out
document.

### Instruction-resistant

Features `write-doc` stated outright and the draft still failed. Three documents
cannot separate "instruction cannot reach it" from "the instruction was badly
worded", and for the first two here there is a third reading — the arm had no
means to gather the evidence — which the suppressed-interview design cannot rule
out.

- **`d02-c5` (11 findings) and `d10-c6` (5).** Instructed, attempted, and failed
  by producing uncheckable evidence. Under this arm's constraints the feature is
  unreachable by instruction alone; the interview and repo search are the
  mechanism, not a convenience.
- **`d03-c1` (4 findings), the one genuine candidate.** Two of the four are
  pointer/destination mismatches — the document links its own section and the
  destination does not say what the pointer claims (`rust-default-field-values`
  lines 406-407 and 26-28; `swift-archival` 331 and 179). Nothing external was
  needed to catch these: the answer was in the draft. The instruction produced
  the *form* of a resolvable reference and not the check behind it, which is the
  signature of an instruction reaching a surface and not a behaviour. A
  single-pass writer forbidden from re-reading cannot verify a destination it has
  not written yet, so the plausible fix is procedural — resolve links in a final
  pass — rather than a stronger wording.

### Settling spec §11.1

`write-doc` **loads all seven survivors.** The shallow-compliance failure the
question guarded against — findings shifting from "absent" to "present but thin"
while the count barely moves — did not appear. Where the taxonomy could be
satisfied from what the writer had, findings dropped outright (structural family
7 → 3, non-feature 5 → 1); where it could not, findings rose rather than
flattening. Seven features is also below the threshold at which a load-shedding
split was contemplated. There is no evidence here for loading a subset, and
subsetting would drop exactly the structural features that worked.
