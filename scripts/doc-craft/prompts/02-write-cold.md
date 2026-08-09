# 02 — Write a decision document from a brief and a scaffold

Inputs:

- `$SCRATCH/doc-craft/cold/<name>.brief.md` — the brief.
- `$SCRATCH/doc-craft/gold/<name>.scaffold.txt` — the section scaffold.
- `TARGET_LINES` — a number, supplied per document.

Output: `$SCRATCH/doc-craft/cold/<name>.md`.

## Task

Write the decision document the brief calls for.

## Sections

The scaffold is the ordered list of `##` headings the document uses. Emit every
one of them, verbatim, in the order given, and no other `##` heading. Below `##`
the document is yours: any heading depth, any number of them, or none.

Start the file with a single `#` title of your choosing.

## Length

Write `TARGET_LINES` lines, ± 20%. Count every line in the file, blank lines
included. Distribute the length across the sections as the material warrants;
there is no per-section budget.

## Process

Single pass. Write the document from beginning to end and stop.

- Do not outline first.
- Do not re-read what you have written.
- Do not revise, tighten, expand, or reorder anything already written.
- Do not critique the draft, and do not append notes about the draft.
- Do not ask questions or state assumptions about the task itself.

Emit only the document.
