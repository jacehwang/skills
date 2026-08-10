import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from scripts import generate


class GenerateHtmlTests(unittest.TestCase):
    def test_escapes_feed_content_and_rejects_unsafe_links(self):
        payload = '<img src=x onerror="alert(1)">'
        weather = {
            "cities": [{
                "name": payload,
                "days": [{
                    "label": payload,
                    "weather": payload,
                    "temp_min": 1,
                    "temp_max": 2,
                }],
            }]
        }
        item = {"title": payload, "description": payload, "url": "javascript:alert(1)"}
        safe_item = {
            "title": payload,
            "description": payload,
            "url": "https://example.com/news?a=1&b=2",
        }
        html = generate.generate_html(
            "unused",
            payload,
            weather,
            [{
                "name": payload,
                "description": payload,
                "description_cn": "",
                "language": payload,
                "stars_today": payload,
                "url": "javascript:alert(1)",
            }],
            [{
                "name": payload,
                "description": payload,
                "description_cn": "",
                "maker": payload,
                "url": "javascript:alert(1)",
            }],
            [safe_item],
            [item],
            (payload, payload),
        )

        self.assertNotIn(payload, html)
        self.assertNotIn('href="javascript:', html)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", html)
        self.assertIn(
            'href="https://example.com/news?a=1&amp;b=2"',
            html,
        )


class TranslationBacklogTests(unittest.TestCase):
    def test_matches_by_repository_name_and_preserves_unmatched_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            backlog_path = data_dir / "translate_backlog.json"
            backlog_path.write_text(json.dumps([
                {"index": 0, "name": "alpha", "text": "Alpha", "cn": "甲"},
                {"index": 1, "name": "missing", "text": "Missing", "cn": "缺失"},
            ]), encoding="utf-8")
            trending = [
                {"name": "beta", "description": "Beta"},
                {"name": "alpha", "description": "Alpha"},
            ]

            with patch.object(generate, "DATA_DIR", data_dir):
                generate._apply_translation_backlog(trending)

            self.assertNotIn("description_cn", trending[0])
            self.assertEqual(trending[1]["description_cn"], "甲")
            remaining = json.loads(backlog_path.read_text(encoding="utf-8"))
            self.assertEqual([entry["name"] for entry in remaining], ["missing"])


class XinhuanetTests(unittest.TestCase):
    def test_accepts_article_links_from_the_current_year(self):
        class FakeDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return cls(2027, 1, 2, tzinfo=tz)

        class Response:
            def __init__(self, text):
                self.text = text
                self.content = text.encode()

            def raise_for_status(self):
                return None

        listing = '<a href="/2027/01/02/c_123.htm">这是一个足够长的新华社新闻标题</a>'
        article = '<meta name="description" content="这是一个比新闻标题更长的新华社新闻正文摘要，用于测试。">'

        def fake_get(url, **_kwargs):
            return Response(article if "c_123" in url else listing)

        with patch.object(generate, "datetime", FakeDateTime), patch.object(
            generate.requests, "get", side_effect=fake_get
        ):
            items = generate._scrape_xinhuanet(1)

        self.assertEqual(len(items), 1)
        self.assertIn("/2027/", items[0]["url"])


class SummaryTests(unittest.TestCase):
    def test_index_links_to_the_markdown_date_heading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            summary = Path(temp_dir) / "summary.md"
            with patch.object(generate, "SUMMARY_FILE", summary):
                generate.update_summary("briefing", "2026-08-11")

            content = summary.read_text(encoding="utf-8")
            self.assertIn("[2026-08-11](#2026-08-11)", content)


class MainTests(unittest.TestCase):
    def test_render_failure_makes_generation_fail(self):
        weather = {"cities": []}
        with tempfile.TemporaryDirectory() as temp_dir, ExitStack() as stack:
            root = Path(temp_dir)
            stack.enter_context(patch.object(generate, "DAILY_DIR", root / "daily"))
            stack.enter_context(patch.object(generate, "IMAGES_DIR", root / "images"))
            stack.enter_context(patch.object(generate, "DATA_DIR", root / "data"))
            stack.enter_context(patch.object(generate, "NEWS_INPUT_FILE", root / "missing.json"))
            stack.enter_context(patch.object(generate, "SUMMARY_FILE", root / "summary.md"))
            stack.enter_context(patch.object(generate, "fetch_weather", return_value=weather))
            stack.enter_context(patch.object(generate, "fetch_github_trending", return_value=[]))
            stack.enter_context(patch.object(generate, "fetch_producthunt", return_value=[]))
            stack.enter_context(patch.object(generate, "fetch_ai_news_live", return_value=[]))
            stack.enter_context(patch.object(generate, "fetch_domestic_news_live", return_value=[]))
            stack.enter_context(patch.object(generate, "fetch_quote", return_value=("Quote", "Author")))
            stack.enter_context(patch.object(
                generate,
                "generate_markdown",
                return_value=("briefing", "2026-08-11", "8月11日"),
            ))
            stack.enter_context(patch.object(generate, "generate_html", return_value="<html></html>"))
            stack.enter_context(patch.object(generate, "update_summary"))
            stack.enter_context(patch.object(
                generate,
                "pil_render_card",
                side_effect=RuntimeError("render failed"),
            ))

            with self.assertRaisesRegex(RuntimeError, "render failed"):
                generate.main()


if __name__ == "__main__":
    unittest.main()
