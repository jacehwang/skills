# Chinese README Design

## Goal

Add a fully Chinese `README_CN.md` that gives Chinese-speaking users the same product, installation, usage, CLI, portability, safety, limitation, development, and license information as `README.md`.

## Approved approach

Maintain a hand-authored Chinese document with the same section order and command examples as the English README. Add a compact language switch at the top of both files so readers can move between English and Simplified Chinese.

Alternatives considered:

- A short Chinese quick-start would be easier to maintain but would omit safety, limitations, and contributor information.
- A generated machine translation would reduce authoring effort but make terminology and Markdown quality less predictable.

The full hand-authored mirror is preferred because this is a small repository and both audiences should receive complete, intentional documentation.

## Content rules

- Translate explanatory prose, headings, table descriptions, comments, and example objective text into natural Simplified Chinese.
- Keep commands, paths, identifiers, package names, plugin names, URLs, and filenames executable and unchanged.
- Preserve the English README's information architecture and all current installation methods.
- Use consistent terms: “项目进展看板”, “恢复信息包”, “检查点”, “阻塞项”, and “变更文件”.
- Link `README.md` to `README_CN.md` and link `README_CN.md` back to `README.md`.
- Record the new localized documentation in `CHANGELOG.md` under version `0.1.0` without changing runtime or plugin versions.

## Verification

Extend repository metadata tests to require:

- `README_CN.md` exists and contains substantial Chinese text;
- both README files contain reciprocal language links;
- both README files contain every supported installation command;
- the Chinese README names `state.json`, `board.md`, and `events.jsonl`;
- neither README contains unresolved template markers.

Run the full unit suite, script compilation, Agent Skills validation, Claude plugin strict validation, and `git diff --check` before publishing.

## Non-goals

- Translating contributor, security, changelog, Skill instruction, or schema files in this change.
- Adding a documentation generator or translation dependency.
- Changing runtime behavior, plugin metadata, or the `v0.1.0` release tag.
