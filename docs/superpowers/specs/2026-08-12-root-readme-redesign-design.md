# Root README Redesign Design

## Goal

Redesign the repository root `README.md` so a visitor can understand the four canonical Skills, choose the relevant package, see the existing Daily News visual output, and install a Skill without opening multiple files first.

## Approved Direction

Use a Chinese-first README with a compact English summary in a collapsed `<details>` section. The presentation should be polished but restrained: a centered title and short tagline, lightweight navigation, clear Markdown sections, limited emoji as wayfinding, and no decorative badge wall.

The design draws on three public repository patterns:

- OpenAI Codex: concise hero copy followed quickly by a practical quick start.
- Anthropic Skills: explain the repository model and make each self-contained package easy to discover.
- GitHub Spec Kit: centered opening, clear navigation, progressive disclosure, and strong section hierarchy.

## Information Architecture

The root README will use this order:

1. Centered repository title, Chinese and English one-line positioning, and four-skill navigation.
2. A short canonical-repository note linking to `MIGRATION.md`.
3. A compact overview table comparing all four Skills by purpose and trigger.
4. Four consistent Skill sections containing:
   - one-sentence value proposition;
   - three concise capability bullets;
   - typical trigger scenarios;
   - one copyable example prompt;
   - links to that package's README and `SKILL.md`.
5. The existing `daily-news-briefing/assets/sample-card.png`, placed in a collapsed visual preview so its 1200×6286 aspect ratio does not dominate the document.
6. Shared installation instructions plus the extra Python dependency step for Daily News.
7. A compact repository tree and migration/source-of-record note.
8. A collapsed English summary with the four-Skill comparison and installation commands.

## Skill Content Sources

All claims must be derived from the current canonical package files.

- `tracking-project-progress`: durable `.project-board/` state, objective/tasks/decisions/files/verification/blockers/next action, and resume/handoff workflows.
- `frontend-ui-visual-gate`: visual gate A, optional 2–4 concept images, explicit direction selection gate B, and the visual decision brief before frontend implementation.
- `notion-worklog`: low-friction capture into daily Notion notes, weekly/monthly leader-facing synthesis, traceability to source notes, and avoidance of generic article-memory triggers.
- `daily-news-briefing`: warm-toned PNG generation, multi-city weather, GitHub Trending/Product Hunt/AI-tech/domestic news, quote fallback, configurable Python pipeline, and the bundled sample card.

## Visual Rules

- Use native GitHub Markdown and conservative HTML supported by GitHub.
- Keep the four Skill sections structurally parallel so the page feels cohesive.
- Use one emoji per Skill heading only; do not add custom logos that do not exist in the repository.
- Reuse the existing Daily News sample image. Do not generate or fabricate images for the other three Skills because they have no image assets.
- Put the tall sample card behind a `<details>` disclosure and render it centered at a readable width.
- Keep relative links valid from the repository root.

## Content and Safety Rules

- Do not claim a capability that is absent from the current package README or `SKILL.md`.
- Do not imply that every Skill has runtime dependencies; only Daily News requires the listed Python packages.
- Keep the monorepo as the canonical source and link migration provenance without repeating the full migration history.
- Preserve the existing install model: copy a selected `skills/<name>` directory into `~/.codex/skills/` or `~/.agents/skills/`.

## Verification

Completion requires all of the following evidence:

- the root README names and links all four canonical Skills;
- every Skill section includes purpose, capabilities, triggers, an example prompt, and detail links;
- the Daily News sample image path exists and is referenced by the README;
- all local Markdown links in the root README resolve to existing repository paths or anchors;
- HTML `<details>`, `<summary>`, `<div>`, `<p>`, `<a>`, and `<img>` tags are balanced;
- `git diff --check` passes;
- all four packages pass `skills-ref agentskills validate`;
- the Daily News test suite passes because its package is referenced as a working installable Skill.
