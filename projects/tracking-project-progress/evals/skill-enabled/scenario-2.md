# Skill-enabled result — Scenario 2

**Result:** pass

## Exact prompt

> Resume a coding task that another agent left halfway through. The repository has a partial token-refresh implementation, two failing tests, and a short note saying only “finish auth.” Determine the real current state, continue the fix, and leave the project ready for another interruption.

## Agent response

> Finished the interrupted auth work.
>
> - `refresh_session` now preserves the existing refresh token when the response omits it.
> - Missing `access_token` now raises `ValueError` instead of leaking `KeyError`.
> - All 2 auth tests pass; compile and diff checks also pass.
> - Added and validated `.project-board/` with the completed state, decisions, verification, and next action.
>
> Changes remain uncommitted in `src/auth.py` and `.project-board/`, ready for review or another interruption.

## Rubric

- Observed: created durable state before substantive changes and reconciled the vague note with Git and failing tests.
- Observed: captured the objective, focus, two task statuses, a consequential decision, `src/auth.py`, no blockers, and a concrete review/commit next action.
- Observed: recorded exact commands and outcomes for the full unit suite, `compileall`, and `git diff --check`.
- Observed: left a concise, validated `.project-board/` recovery packet that a fresh agent can resume.
- Observed: kept the board to two implementation/verification tasks rather than duplicating Git history or a full plan.
- Missing: none.
