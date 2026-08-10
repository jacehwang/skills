from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "tracking-project-progress"
SKILL_MD = SKILL_ROOT / "SKILL.md"


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_is_discoverable_for_coding_and_resume_tasks(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]

        self.assertRegex(frontmatter, r"(?m)^name: tracking-project-progress$")
        description_match = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
        self.assertIsNotNone(description_match)
        description = description_match.group(1).lower()
        for keyword in ("feature", "bug", "refactor", "resume", "interrupted", "project board"):
            self.assertIn(keyword, description)

    def test_skill_is_concise_and_contains_no_template_markers(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")

        self.assertLess(len(text.splitlines()), 500)
        self.assertNotRegex(text, r"\b(?:TODO|TBD|PLACEHOLDER)\b")
        self.assertFalse((SKILL_ROOT / "README.md").exists())

    def test_relative_markdown_references_resolve(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        targets = re.findall(r"\[[^]]+\]\((?!https?://)([^)#]+)(?:#[^)]+)?\)", text)

        self.assertIn("references/board-schema.md", targets)
        for target in targets:
            self.assertTrue((SKILL_ROOT / target).exists(), target)

    def test_cli_help_is_executable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / "project_board.py"), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("ensure", "resume", "task-add", "record-file", "checkpoint", "validate"):
            self.assertIn(command, result.stdout)

    def test_openai_interface_metadata_invokes_the_skill(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn('display_name: "Project Progress Board"', metadata)
        self.assertIn("$tracking-project-progress", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)


if __name__ == "__main__":
    unittest.main()
