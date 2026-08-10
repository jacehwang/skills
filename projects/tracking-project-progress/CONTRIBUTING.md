# Contributing

Contributions are welcome when they keep the project small, portable, and interruption-safe.

## Development setup

The runtime uses only the Python standard library. Use Python 3.11 or newer for development and the Agent Skills reference validator.

```bash
git clone https://github.com/Byctor/tracking-project-progress.git
cd tracking-project-progress
python3 -m unittest discover -s tests -v
```

Validate the portable Skill:

```bash
uvx --python 3.11 --from skills-ref agentskills validate skills/tracking-project-progress
```

Validate the Claude Code plugin when Claude Code is installed:

```bash
claude plugin validate . --strict
```

## Change requirements

- Write a failing test before changing CLI or hook behavior.
- Run all tests and script compilation before opening a pull request.
- Keep `SKILL.md` below 500 lines and move detailed reference material into `references/`.
- When Skill instructions change, run the three scenarios in `evals/scenarios.md` with a fresh agent context and preserve the scored results.
- Add dependencies only when the standard library cannot provide a reliable solution.
- Do not add telemetry, external network calls, or secret collection.
- Update `CHANGELOG.md` for user-visible changes.

## Pull requests

Describe the observed problem, the behavioral or code change, and the exact verification commands and outcomes. Keep unrelated refactors out of the same pull request.

