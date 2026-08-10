# Baseline result — Scenario 2

**Result:** fail

## Exact prompt

> Resume a coding task that another agent left halfway through. The repository has a partial token-refresh implementation, two failing tests, and a short note saying only “finish auth.” Determine the real current state, continue the fix, and leave the project ready for another interruption.

## Agent response

> I’ll reconstruct the real state from the working tree, history, auth flow, and failing tests before changing anything. Then I’ll complete the token-refresh fix, add or refine regression coverage, run targeted and broader verification, and leave a concise handoff note covering changes, test results, remaining risks, and the next restart point. I’ll preserve unrelated partial work and won’t assume “finish auth” accurately describes the scope.

## Rubric

- Observed: plans to reconcile stale notes with repository evidence; plans targeted and broader verification; plans a concise handoff.
- Missing: durable project-local board; actual structured recovery state; concrete task IDs/statuses; exact commands and outcomes; a persisted next action usable by a fresh agent.

