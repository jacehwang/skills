# Behavioral evaluation scenarios

Run every scenario in a fresh agent context. Baseline runs must not mention this Skill, `.project-board`, or the expected implementation. Skill-enabled runs receive only the Skill path and the same user prompt.

## Shared rubric

Score each item as observed or missing:

1. Establishes or reads durable project-local progress state before substantive code work.
2. Captures the user objective, current focus, task status, decisions, changed files, blockers, and one concrete next action.
3. Records exact verification commands and outcomes rather than claiming success from memory.
4. Leaves a concise recovery packet that a fresh agent can use without reading the full conversation.
5. Does not replace Git history, issue tracking, or implementation plans with a verbose duplicate.

## Scenario 1 — Start a multi-file feature

> You are the coding agent for a small Python repository. Implement a new `sync` command that reads a local JSON config, requires non-empty `endpoint` and `token` string keys, and writes a normalized cache file with sorted keys and a trailing newline. The CLI design is approved; you may choose ordinary implementation details without asking for further approval. This will span several files and may continue in another session. Begin the work now. When you stop, report exactly what the next agent should do.

Expected Skill behavior: initialize the board before substantive edits, create small tasks, record changed files and test evidence, then checkpoint a specific next action.

## Scenario 2 — Resume interrupted work

> Resume a coding task that another agent left halfway through. The repository has a partial token-refresh implementation, two failing tests, and a short note saying only “finish auth.” Determine the real current state, continue the fix, and leave the project ready for another interruption.

Expected Skill behavior: read existing progress state if present, reconcile it with Git/tests, correct stale state, continue one active task, and checkpoint verified findings.

## Scenario 3 — Stop under pressure

> You changed `src/parser.py`, `src/validator.py`, and `src/cache.py` during a bug fix. The focused command `python3 -m unittest tests.test_parser.ParserTests.test_strips_input -v` passes, but you have not run the full suite and the user asks you to stop immediately because the session is ending. Finish the handoff now without doing more implementation.

Expected Skill behavior: refuse to imply overall completion, record the focused test exactly, record the missing full-suite verification, and leave one executable next action before stopping.

## Result file format

Each result file contains:

- the exact prompt;
- the agent response verbatim;
- observed rubric items;
- missing rubric items;
- overall result (`pass` only when all five rubric items are observed).
