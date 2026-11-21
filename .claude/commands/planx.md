---
description: Turn a build phase or idea into a self-contained slice plan in docs/build/ for another agent to execute
argument-hint: [phase, module, or goal]
---

# /planx

Plan only. No engine code. The executor needs only the plan and the docs it cites.

## Goal
$ARGUMENTS

## Steps
1. Read `CLAUDE.md`, `docs/build/README.md`, the matching phase doc, its linked idea docs, and `docs/build/open-questions.md`.
2. Stop and report if an open question blocks the goal. Do not silently decide a one-way door.
3. Write `docs/build/<phase>-<NN>-<slug>.md`. Example: `phase-0-02-memory.md`. Slug is kebab-case, max 5 words.
4. Link it from the phase doc and `docs/build/README.md`.

## Slice format
```markdown
# <Title>
> Phase: <link>. Depends on: <slices>.

## Goal
## Design source
Links to the owning idea doc sections. Do not copy them.
## Files to create or change
## Steps
Each step ends with `verify:` and an observable check.
## Must not happen
## Done when
```

## Rules
- Fragments, not essays. Reference, do not paste.
- Every check is observable. Mark unstated business rules `ASSUMPTION:`.
- One slice is one PR.
