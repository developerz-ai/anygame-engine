---
description: Write or revise AnyGame docs end to end, check them, and open a PR
argument-hint: <doc or topic to write or revise>
---

# /feature

Docs only until the repo gains code. Read `CLAUDE.md` first.

## Request
$ARGUMENTS

## Steps
1. Find the owning doc in `docs/idea/` or `docs/build/`. Revise it rather than adding a duplicate.
2. Check `docs/build/open-questions.md`. If the change settles one, update it.
3. Write: design goes in `docs/idea/`, sequence and exit checks in `docs/build/`.
4. Add new docs to the folder `README.md`.
5. Gate:
   - Every relative link resolves.
   - Claims about other engines are dated and sourced, or marked unverified.
   - Targets are labelled as targets.
   - No secrets, private hostnames, client names, leaked or decompiled material.
6. Branch from `main`, commit with a conventional message, open a PR. Merge only if asked.

Report what you checked and what you did not.
