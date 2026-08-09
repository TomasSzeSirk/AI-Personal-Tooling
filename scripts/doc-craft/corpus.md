# Doc Craft — Corpus Manifest

Thirteen technical decision documents, pinned by commit SHA. Ten form the
discovery corpus; three are held out for the Stage 7 evaluation of `write-doc`
and never enter feature discovery.

Document contents are not committed here — they are private or third-party.
Re-fetch any public row with:

```bash
gh api "repos/<repo>/contents/<path>?ref=<sha>" --jq '.content' | base64 -d
```

**The three internal rows are redacted.** `internal-1`, `internal-2` and
`internal-3` are unpublished documents from a private organization. Their repo,
path, commit SHA, subject matter and headings are deliberately absent from this
repository — only their structural properties (line count, tier, role, and the
measurements taken on them) are recorded. Their pins are held by the corpus owner
outside this repo, so those three rows are not re-fetchable from what is written
here. That is intentional and is the reason the taxonomy's examples are drawn
from the public half of the corpus only.

## Documents

| Name | Repo | Path | Role | Commit SHA | Lines | Tier | Selection reason |
|------|------|------|------|-----------|-------|------|------------------|
| `internal-1` | redacted (private) | redacted | discovery | redacted | 443 | clean | Steered internal design doc; surveys options, rejects several with reasons, records its own reversals. |
| `internal-2` | redacted (private) | redacted | discovery | redacted | 143 | clean | Sibling of `internal-1`, same house style; carries open questions and explicit scope boundaries. |
| `internal-3` | redacted (private) | redacted | discovery | redacted | 479 | clean | Goals / Non-goals / Alternatives considered / Open decisions / Recommendation — decision-doc genre, different subject domain from the other two internal docs. |
| `rust-crates-io-identity` | rust-lang/rfcs | `text/3946-crates-io-username-identity.md` | discovery | `792a2b5554f888ce93bf984e807f037503f1f44f` | 685 | clean | Registry identity policy, not language design. Rationale 64 lines, Unresolved 69. Probe negative. |
| `rust-min-publish-age` | rust-lang/rfcs | `text/3923-cargo-min-publish-age.md` | discovery | `0d32de51bd4a12c3740e1dd682048fbcbff0691a` | 541 | clean | Supply-chain policy for a package manager. Rationale 108 lines across 8 sub-alternatives, Drawbacks 27. Probe negative on design and argument. |
| `rust-try-trait-v2` | rust-lang/rfcs | `text/3058-try-trait-v2.md` | discovery | `f17e8623ee2e2854570dcdb936a9f4ab08c0fcd4` | 1172 | contaminated | Rationale 246, Unresolved 15; explicit successor to an earlier accepted design. Retained as a template-confound control (spec §5) after the recall probe failed. |
| `rust-msrv-resolver` | rust-lang/rfcs | `text/3537-msrv-resolver.md` | discovery | `f17e8623ee2e2854570dcdb936a9f4ab08c0fcd4` | 1306 | clean | Rationale 194, Unresolved 23; tooling rather than language. Draft re-run in a blinded context and re-probed negative on both axes — see the probe table. |
| `swift-registry-search` | apple/swift-evolution | `proposals/0536-registry-search.md` | discovery | `370a5f6f03d0127442779967253074d463fbe213` | 477 | clean | Niche package-registry tooling; `Accepted with modifications`, so a revision signal. Alternatives 24 lines, Future directions 34. Probe negative. |
| `swift-html-coverage` | apple/swift-evolution | `proposals/0501-swiftpm-html-coverage-report.md` | discovery | `4320dc413f271c1621462ffa1fd59f4470222980` | 295 | clean | Test-tooling report format; densest alternatives-per-line of the Swift candidates (34 of 295). Probe negative. |
| `swift-task-locals` | apple/swift-evolution | `proposals/0311-task-locals.md` | discovery | `d0e50d90a107e70ffc9a2a57ce182d82244bd642` | 1286 | contaminated | Carries both `Alternatives Considered` and a separate `Rejected Alternatives` section. Retained as a template-confound control after the recall probe failed. |
| `rust-default-field-values` | rust-lang/rfcs | `text/3681-default-field-values.md` | held-out | `f17e8623ee2e2854570dcdb936a9f4ab08c0fcd4` | 1977 | n/a | Meets the discovery bar (Drawbacks 49, Rationale 186, Unresolved 34); reserved for evaluation. |
| `swift-archival` | apple/swift-evolution | `proposals/0166-swift-archival-serialization.md` | held-out | `85bc3c7af4d6be324ce4353280599bdda1dac4f7` | 2205 | n/a | Alternatives 282 lines; serialization domain, unrepresented in the discovery set. |
| `k8s-object-storage` | kubernetes/enhancements | `keps/sig-storage/1979-object-storage-support/README.md` | held-out | `1ec1c257b6e4ef755035740576453a10acfb6158` | 2062 | n/a | Third template family (KEP), unrepresented in discovery — keeps the evaluation from rewarding scaffold familiarity. |

## Heading normalization

Scaffolds handed to the cold writer carry **H2 headings only**. Headings below H2
are where the argument lives: in `internal-1` several H3s are full sentences
asserting the document's central finding — that one of the two candidate
locations for a mechanism is unworkable without a protocol change — so passing
them on would leak the finding, the rejected option, and the recommendation
together.

Surviving H2s were then tested against two rules — does the heading state a
proposition that could be true or false, and does it name a solution or mechanism
*this document invented*. Every rewrite:

| Document | Original heading | Normalized to | Rule |
|----------|-----------------|---------------|------|
| `internal-1` | redacted — a numbered topic heading carrying a parenthetical | topic, parenthetical dropped | The parenthetical named the recommended location, which is the document's central finding. |
| `internal-2` | redacted — a heading naming an artifact the document invented, down to its case labels | the generic topic of that artifact | Names a construct this document introduced. |
| `swift-archival` | `` ## `JSONSerialization` Friction and Third-Party Solutions (Motivation) `` | `## Existing-API friction (Motivation)` | Asserts the motivating claim and names the specific API the proposal displaces. |
| `internal-3` | redacted — four headings naming the proposed architecture's own components | collapsed to one `## Design details` | Together the four hand over the design's decomposition. |

Five further `internal-3` headings were **kept**: they name concerns any design
in that space must address — concurrency, authentication, failure handling,
recovery, and security invariants — rather than components this design invented.
That is the line drawn: the first kind is the document's answer, the second is
genre scaffold, and removing the second would strip legitimate structure. The
kept headings are described here rather than quoted, since they are still text
from a private document.

That line is a judgement call, which is why every rewrite is recorded here rather
than applied silently. Scaffold sizes after normalization: `internal-3` 16,
`swift-task-locals` 14, `swift-archival` 11, `k8s-object-storage` /
`rust-msrv-resolver` / `rust-try-trait-v2` / `rust-default-field-values` /
`rust-crates-io-identity` / `rust-min-publish-age` 9, `internal-1` /
`swift-registry-search` 8, `internal-2` / `swift-html-coverage` 7.

The four replacement documents needed **no** normalization. Their H2s are the
unmodified Rust RFC and Swift Evolution templates — `Summary` / `Motivation` /
`Drawbacks` / `Rationale and alternatives` / `Prior art` / `Unresolved questions`
/ `Future possibilities`, and `Introduction` / `Motivation` / `Proposed solution`
/ `Detailed design` / `Security` / `Impact on existing packages` / `Alternatives
considered` / `Future directions`. None states a proposition; none names an
invented mechanism.

## Recall probes

Two probes per external document, per Stage 1.4 and Stage 2.6.

**Selection probe** (before pinning): the candidate's title and its `Motivation`
section only were handed to a fresh model context with no document and no web
access, which was asked to state the accepted mechanism, its actual names, and
the alternatives the document rejected, labelling each claim RECALL or INFERENCE.

**Draft probe** (after writing): the finished cold draft was grepped for the
identifiers and coinages its gold introduced, and the two `Alternatives` /
`Rationale` sections were compared for shared rejections in shared order.

| Document | Selection probe | Draft probe — vocabulary | Draft probe — argument | Tier |
|----------|-----------------|--------------------------|------------------------|------|
| `rust-crates-io-identity` | Negative. Got the general direction (decouple the account from the GitHub login) — which the `Motivation` states outright — and no names. Its guessed rejection list (provider-prefixed handles, numeric IDs, free renames) matches none of the document's. | No gold coinage present. The draft invents `username_history`, `username_normalized`, `crates_io_url`. Shared, not in brief: `linked_accounts` is a gold API field (3× in the draft) and the brief does not carry it — a plausible field name for the feature, but recorded rather than dismissed. Other shared tokens are pre-existing ones the brief carries (`oauth_github`, `github:org:team`). | Gold argues one alternative; the draft argues nine. No shared rejection. | clean |
| `rust-min-publish-age` | Negative on design and argument. Overlapped the actual config key at the *title* level only — the RFC is titled "min publish age", so any guess reproduces the phrase. Named `minimum-release-age` and `min-age`, not `min-publish-age`. Guessed rejections (registry-side delay, default-on, third-party tools) match 2 of the gold's 8, out of order. | Draft says `minimum-publish-age`; gold says `min-publish-age`. Gold's `global-min-publish-age`, `incompatible-publish-age`, `deny`/`warn` levels: absent. `cooldown` and `exclude-newer` appear in both but are prior-art names the brief carries. | 3 of the gold's 8 axes recur (duration-vs-timestamp, config naming, config placement), in a different order, and the gold's other five do not appear. Convergence on the obvious axes of the design space, not reproduction. | clean |
| `swift-registry-search` | Negative. Guessed `GET /search?q=` and `swift package-registry search` — both appear in the `Motivation` handed to the probe, so neither counts. Guessed rejections (central cross-registry index, reuse the list endpoint, client-side search) match none of the gold's three. | Shared: `Content-Version` and `/availability` are brief-carried (1× each). `GET /search` and `swift package-registry search` are **not** in the brief — they are forced by the CLI namespace and REST convention the brief does name (`swift package-registry publish`, `cargo search`, `npm search`), so a search endpoint has essentially one available spelling. Draft's parameters are `page`/`limit`; gold's are cursor-based with `sort`. | Gold rejects three things (query string vs parameters, cursor pagination, full release metadata); the draft rejects six, none of them those. | clean |
| `swift-html-coverage` | Negative. Guessed a `--coverage-format` flag, which is the gold's actual spelling — the strongest single hit in the set, and derivable from the existing `--enable-code-coverage` surface. Guessed rejections match none of the gold's. | Draft spells it `--show-code-coverage-report` / `--code-coverage-report`, not `--coverage-format` or `--show-coverage-path`. `llvm-cov` appears 37 times in the draft against 13 in the gold, but the brief names it 6 times as the existing tooling — brief-carried, not contamination. | Gold argues one alternative; the draft argues fourteen. No shared rejection. | clean |
| `rust-try-trait-v2` | Not run — pinned before the probe existed. | **Fails.** Counted against the final concatenated draft, as every other row is: `FromResidual` 44 (gold 48), `from_residual` 20 (41), `ControlFlow` 51 (107), `from_output` 16 (26), `branch` 29 (32). `FromResidual`, `from_residual` and `from_output` are absent from the brief and carry the row on their own. | **Fails.** Reproduces the gold's residual-versus-error argument. Two items previously cited here — the `ControlFlow` justification and the reductionist/essentialist framing — are **withdrawn**: both appear in `rust-try-trait-v2.brief.md:17`, so they are brief-carried and subtract out the same way `oauth_github`, `llvm-cov` and `cooldown` do elsewhere in this table. | contaminated |
| `swift-task-locals` | Not run — pinned before the probe existed. | **Fails**, and fails harder on the re-run blinded draft: `TaskLocal` 33 against the gold's 29, `@TaskLocal` 16 against 11, `withValue` 32, `inherit` 27 — none of them in the brief. | Rejections diverge; only the vocabulary is recalled. | contaminated |
| `rust-msrv-resolver` | Not run — pinned before the probe existed. | Negative, re-run against the blinded draft. Every gold coinage absent: `tbd-name-representing-currently-running-rust-toolchain` (31 in gold), `CARGO_RESOLVER_PRECEDENCE` (11), `resolver.precedence` (7), `--update-rust-version` (15), `workspace.rust-version` (3) all score 0. Shared, not in brief: `--ignore-rust-version` 6× against 19 in the gold — a cargo flag that shipped years before this RFC, which extends it rather than coining it. | Negative. One of the gold's six axes recurs (hard-error versus preference), the most obvious axis in the space, and out of order — the gold argues it last as an H4, the draft leads with it. The gold's other five (registry index data quality, resolver-mode config placement, `workspace.rust-version`, opt-in versus opt-out, precedence default) do not appear; the draft's other eight are its own. | clean |

`rust-msrv-resolver` was **promoted from contaminated to clean.** Its original
draft was produced under the pre-swap procedure, in which one context held the
gold and then wrote the draft, so its negative probe could not distinguish "no
recall" from "recall the grep missed", and the conservative reading was to keep
it contaminated. The draft has since been re-run in a blinded context
(`run/rust-msrv-resolver.draft.prompt.txt`) and the probe re-run against it. It
stays negative on both axes, and there is no longer a procedural reason to
discount that.

The two contaminated pairs are kept deliberately. Spec §5 needs a
template-confound control — a set of pairs where both halves share the genre
template and the design — and a pair whose cold half reconstructs its gold is
exactly that control.

## Deviations from the plan

**The plan's third internal document was dropped.** Its structure turned out to
be a work-item inventory and delivery plan — an epic inventory running 645 lines,
plus release-breakdown, effort-estimation and per-release delivery sections. That
is a different genre from an options-and-recommendation design doc, and including
it would have taught the taxonomy to detect project plans.

**`internal-3` replaced it**, found by scanning the same private organization's
repositories for design-shaped filenames. This preserves three internal pairs — the only pairs
where both halves are AI-authored and steering is the sole variable (plan open
question 1).

**`internal-2` is 143 lines**, well under the 400-line floor applied to the
external candidates. It is kept because internal pairs are scarce and it shares
the house style being measured, but it is the thinnest document in the corpus and
features resting mainly on it should be treated with suspicion at the Stage 4 cut.

**Four external documents were swapped out after their recall probes failed.**
`rust-needle` (2500), `rust-if-let-chains` (2497), `swift-atomics` (0410) and
`swift-actor-isolation` (0336) were dropped. They are the four longest and most
discussed public documents in the corpus, and the contamination they carry is
measurable rather than suspected: the finished `rust-try-trait-v2` cold draft —
the same class of document — reproduces `FromResidual` 44 times against the gold's
48, with the term absent from its brief, and replays the gold's
residual-versus-error argument. A cold half reconstructed from training
data converges on its gold no matter how the brief is written, which biases every
comparison toward the null and makes a real steering feature fail to separate for
reasons that have nothing to do with steering.

Their replacements are `rust-crates-io-identity`, `rust-min-publish-age`,
`swift-registry-search` and `swift-html-coverage` — registry policy, supply-chain
policy, package discovery, and test tooling. All four are niche rather than
language design, all four pass the probe, and all four sit in the 200–700 line
band, which also removes the length-undershoot the long documents caused.

**Two briefs were regenerated for leakage.** `rust-try-trait-v2`'s brief adopted
`residual`, a word the gold coined, which prompt 01 forbids.
`internal-1`'s brief stated a preference for reusing an existing subsystem over
building a new one; that is a stance, not a pre-existing fact, and together with
an adjacent bullet it determined the gold's recommendation. Both were regenerated
from the gold under prompt 01 unchanged and both drafts were re-run from the new
briefs.

The regenerated `internal-1` brief carries a **residual risk that was accepted,
not resolved.** Three of its facts are pre-existing properties of the deployed
system — prompt 01 admits pre-existing facts, and the system cannot be described
without them — but together they narrow the design space toward the gold's
answer. Described without their content: one is an asymmetry in the deployed
system that points at the location the gold recommends; one is a
setup-time-immutability property that is the premise of the gold's central
*rejection*; and one is the existence of a subsystem the gold's mechanism reuses.

So the exposure is not confined to the location question: on this pair, any
Stage 4 feature resting on **dimension 6 (rejected alternatives)** should be
treated with suspicion, because part of the rejection's reasoning is in the brief
rather than discovered by the writer. The brief was not hand-edited to remove
them — editing them out would describe a system that does not exist.

**Cold-draft length ratios.** Ratios against gold line count, all ten:

| Document | Ratio | Continuation |
|----------|-------|--------------|
| `internal-3` | redacted (private) | redacted | discovery | redacted | 479 | clean | Goals / Non-goals / Alternatives considered / Open decisions / Recommendation — decision-doc genre, different subject domain from the other two internal docs. |
| `internal-2` | redacted (private) | redacted | discovery | redacted | 143 | clean | Sibling of `internal-1`, same house style; carries open questions and explicit scope boundaries. |
| `internal-1` | redacted (private) | redacted | discovery | redacted | 443 | clean | Steered internal design doc; surveys options, rejects several with reasons, records its own reversals. |
| `swift-task-locals` | 0.81 | none — first pass inside the band |
| `rust-msrv-resolver` | 0.77 | one |
| `rust-min-publish-age` | 0.77 | one |
| `swift-html-coverage` | 0.76 | one |
| `swift-registry-search` | 0.74 | one |
| `rust-try-trait-v2` | 0.53 | one |
| `rust-crates-io-identity` | 0.52 | one |

`rust-try-trait-v2` and `rust-crates-io-identity` are below the 60% floor and
carry into Stage 4 as covariates. The two over-target drafts were left alone:
Stage 2.2 permits appending, never cutting, so an over-length first pass has no
remedy that does not break the single-pass rule.

Three continuations emitted `##` headings despite the instruction not to —
duplicates of scaffold headings in `rust-min-publish-age`, `X (continued)`
restatements in `rust-try-trait-v2`, and four `Appendix:` headings in
`swift-registry-search`. Each was demoted to `###` before the continuation was
appended. This is mechanical, applied without reading the prose, and it is the
only post-hoc edit any cold draft received.

**Each cold draft was written in a context that never held its gold.** Briefs
were extracted in one set of fresh `claude -p` contexts and drafts written in a
second set whose only inputs were the brief, the scaffold and `TARGET_LINES`.
Every draft prompt is retained at
`$SCRATCH/doc-craft/run/<name>.draft.prompt.txt` — ten of them, one per
discovery document — and that file is the evidence for the claim.

Four drafts — `internal-2`, `internal-3`, `swift-task-locals` and
`rust-msrv-resolver` — were originally written under the pre-swap procedure, in
which one context held the gold and then wrote the draft. All four were
**discarded and re-run blinded**; the ratios and probes above are the re-run
drafts. Their briefs were not regenerated, because brief extraction requires the
gold by design and only the draft context needs blinding.

The re-run is what makes one `internal-3` observation interpretable. The blinded
draft converged on the same mechanism the gold prefers for its first
implementation, using vocabulary the brief does not contain. Under the pre-swap
draft this was indistinguishable from recall. Under a draft written without the
gold in context it reads as convergence instead: the design space that problem
admits is small and the shared mechanism is its obvious floor. Recorded rather
than dismissed, since
`internal-3` is one of the three internal pairs the clean-tier cut leans on.

**Three Rust SHAs are identical** (`f17e8623ee2e2854570dcdb936a9f4ab08c0fcd4`,
covering `rust-try-trait-v2`, `rust-msrv-resolver` and
`rust-default-field-values`). The pin resolves the most recent commit touching
each path, and one repo-wide commit touched all of them. The two replacement Rust
RFCs are newer than that commit and carry their own SHAs. Every pin is still
exact for re-fetching.
