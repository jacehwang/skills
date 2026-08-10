from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/Byctor/tracking-project-progress"


class RepositoryMetadataTests(unittest.TestCase):
    def test_claude_plugin_manifest_and_marketplace_are_consistent(self) -> None:
        plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )

        self.assertEqual(plugin["name"], "tracking-project-progress")
        self.assertEqual(plugin["version"], "0.1.0")
        self.assertEqual(plugin["license"], "Apache-2.0")
        self.assertEqual(plugin["repository"], REPOSITORY_URL)
        self.assertEqual(marketplace["name"], "tracking-project-progress")
        self.assertEqual(len(marketplace["plugins"]), 1)
        self.assertEqual(marketplace["plugins"][0]["name"], plugin["name"])
        self.assertEqual(marketplace["plugins"][0]["source"], ".")

    def test_readme_documents_all_supported_install_paths_and_board_files(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            f"npx skills add {REPOSITORY_URL} --skill tracking-project-progress",
            readme,
        )
        self.assertIn("/plugin marketplace add Byctor/tracking-project-progress", readme)
        self.assertIn(
            "/plugin install tracking-project-progress@tracking-project-progress",
            readme,
        )
        self.assertIn("claude --plugin-dir ./tracking-project-progress", readme)
        for filename in ("state.json", "board.md", "events.jsonl"):
            self.assertIn(filename, readme)

    def test_localized_readmes_are_complete_and_reciprocal(self) -> None:
        english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        chinese_path = REPO_ROOT / "README_CN.md"

        self.assertTrue(chinese_path.exists())
        chinese = chinese_path.read_text(encoding="utf-8")
        self.assertIn("[简体中文](README_CN.md)", english)
        self.assertIn("[English](README.md)", chinese)
        self.assertGreater(len(re.findall(r"[\u4e00-\u9fff]", chinese)), 500)

        commands = (
            f"npx skills add {REPOSITORY_URL} --skill tracking-project-progress",
            "/plugin marketplace add Byctor/tracking-project-progress",
            "/plugin install tracking-project-progress@tracking-project-progress",
            "claude --plugin-dir ./tracking-project-progress",
        )
        for command in commands:
            self.assertIn(command, english)
            self.assertIn(command, chinese)
        for filename in ("state.json", "board.md", "events.jsonl"):
            self.assertIn(filename, chinese)

    def test_open_source_policy_files_are_present(self) -> None:
        license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
        contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        self.assertIn("python3 -m unittest discover -s tests -v", contributing)
        self.assertIn("security vulnerability", security.lower())
        self.assertIn("## [0.1.0]", changelog)

    def test_ci_runs_behavior_and_spec_validation(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("agentskills validate skills/tracking-project-progress", workflow)
        self.assertRegex(workflow, r"3\.11")
        self.assertRegex(workflow, r"3\.13")

    def test_repository_files_have_no_unresolved_template_markers(self) -> None:
        forbidden = re.compile(r"\b(?:TODO|TBD|PLACEHOLDER)\b|<repository-url>|<repository-path>")
        checked = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "README_CN.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / "SECURITY.md",
            REPO_ROOT / "CHANGELOG.md",
            REPO_ROOT / ".claude-plugin" / "plugin.json",
            REPO_ROOT / ".claude-plugin" / "marketplace.json",
        ]
        for path in checked:
            self.assertIsNone(forbidden.search(path.read_text(encoding="utf-8")), str(path))


if __name__ == "__main__":
    unittest.main()
