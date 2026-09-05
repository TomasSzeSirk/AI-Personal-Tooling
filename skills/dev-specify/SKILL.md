---
name: dev-specify
description: Turn an already-defined user story (As a / I want / so that, acceptance criteria, technical notes) into an approved spec — explore and analyse the story against the repo, resolve ambiguities with the user, validate the analysis, then write the spec to the working repo's docs/specs/. Use when the requirement is given rather than up for design.
---

# specify

Use this instead of `dev-brainstorm` when the work arrives as a **defined user
story** — an objective (`As a … I want … so that …`), acceptance criteria, and
technical notes to honour — rather than as an idea to be shaped. The
requirement is already decided; your job is to check it against the repo,
resolve what is ambiguous, and write it down as a spec `dev-plan` can consume
— not to redesign it.

If the story has no real acceptance criteria, or its objective is a wish rather
than a requirement, say so and route to `dev-brainstorm` instead: there is
nothing here to analyse against.

## Hard gate

Do **not** write the spec, write code, or hand off to `dev-plan` until the user
has validated the analysis and every **blocking** ambiguity is resolved. An
acceptance criterion you silently interpreted becomes a plan stage and then a
commit — ask instead.

## Steps

1. **Collect the story** — you need all three parts verbatim: the objective
   (`As a <role>, I want <capability>, so that <outcome>`), the **acceptance
   criteria**, and the **technical notes**. Ask for whichever is missing; if
   the user says a part doesn't exist, record that rather than inventing it.
   Never author acceptance criteria on the user's behalf.
2. **Explore context** — read `CLAUDE.md` / `AGENTS.md` (including any
   `## Constitution` section), the files the story touches, and recent commits
   in that area; dispatch `code-explorer` (Agent tool, `subagent_type:
   code-explorer`) for anything spanning more files than you can read directly.
   Ground every later claim in what is actually there.
3. **Analyse the story against the repo** — produce, item by item:
   - **each acceptance criterion** → where it lands in the code (`file:line`),
     what already satisfies it, what has to change, and whether it is
     verifiable as written (could it be phrased as a failing test?).
   - **each technical note** → whether the repo can honour it as stated, and
     whether it conflicts with an existing convention, a dependency, or the
     constitution.
   - **gaps** → behaviour the objective implies that no criterion covers.
4. **Raise ambiguities** — ask **one question at a time**, multiple-choice
   where possible, and separate them:
   - *blocking* — different readings produce different code (an unspecified
     error case, an undefined boundary, a criterion that can't be verified, a
     technical note that contradicts the repo). These must be answered.
   - *non-blocking* — a reasonable default exists; state the default you would
     take and carry it into the spec as an explicit assumption.

   If the analysis exposes a genuine design fork the story doesn't settle,
   dispatch `design-explorer` (`subagent_type: design-explorer`) and put the
   options to the user as one blocking question — don't pick for them. If the
   story spans several independent subsystems, flag it and propose splitting it
   before going further.
5. **Present the analysis for validation** — the criterion-by-criterion
   mapping, the technical notes' verdicts, the answers you got, the assumptions
   you are carrying, and anything the story asks for that is already
   implemented. Get the user's approval on the analysis before writing
   anything.
6. **Write the spec** — save it to the working repo's `docs/specs/<topic>.md`
   (create the directory if absent; never edit the repo's `.gitignore`), in the
   shape below. Same location and shape `dev-brainstorm` and `dev-debug` write
   to, so nothing downstream needs special handling.
7. **Hand off** — invoke the `dev-plan` skill to turn the spec into a staged
   plan.

## Spec shape

- **Story** — the objective verbatim, plus its source reference (ticket ID or
  similar) when there is one.
- **Requirements** — one `R1, R2, …` per acceptance criterion, in the story's
  order, each stated as a verifiable outcome. Keep the original wording where
  it is already verifiable; where step 4 sharpened it, use the sharpened
  wording and note what changed. A criterion that yields more than one
  independently testable outcome gets more than one ID. Name the criterion each
  ID came from, so a stage can be traced back to the story.
- **Technical constraints** — the technical notes, as constraints on *how* the
  requirements are met. They get no `R` IDs: they modify stages rather than
  creating them. A note that actually demands its own observable behaviour is a
  requirement — give it an ID and say so.
- **Assumptions** — every non-blocking default carried from step 4, so a
  reviewer can challenge it.
- **Out of scope** — what the story does not cover, especially anything the
  user ruled out while answering questions.

## Principles

- The story is ground truth — you don't get to improve it. If a criterion is
  wrong, say so and let the user amend it; never quietly ship a better one.
- One question at a time.
- No invented acceptance criteria. Anything not in the story and not answered
  by the user is either an assumption, written down as one, or an open
  question — never a silent addition.
- An acceptance criterion that can't be phrased as a failing test is
  under-specified. Resolve it here; `dev-plan`'s testability gate bounces it
  back otherwise.
- Report what is already implemented instead of re-specifying it.
- No code here — this skill ends at an approved spec.
