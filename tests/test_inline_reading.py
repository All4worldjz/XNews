"""Inline source summaries must be readable on the homepage and in RSS."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from validate import validate_data

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_feed_inline', ROOT / 'scripts/build_feed.py')
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)


def sample_reading():
    return {'background': ['用通俗语言解释背景。'],
            'sourceSummary': ['来源要点 <script>unsafe</script> & 中文整理。'],
            'commentary': ['独立评论，不冒充原作者观点。'],
            'updatedAt': '2026-11-07T11:00:00Z'}


class InlineReadingTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/issues.json').read_text())
        self.issue = self.data['issues'][0]
        self.item = self.issue['items'][0]

    def test_new_format_requires_reading_for_every_item(self):
        self.issue['contentFormat'] = 'inline-reading-v1'
        for item in self.issue['items']:
            item['reading'] = sample_reading()
        validate_data(self.data)
        self.item.pop('reading')
        with self.assertRaisesRegex(ValueError, 'reading'):
            validate_data(self.data)

    def test_rejects_missing_empty_or_nontext_sections(self):
        for key in ('background', 'sourceSummary', 'commentary'):
            for invalid in (None, [], [''], [42]):
                with self.subTest(key=key, invalid=invalid):
                    self.item['reading'] = sample_reading()
                    self.item['reading'][key] = invalid
                    with self.assertRaises(ValueError):
                        validate_data(self.data)

    def test_reading_update_time_requires_timezone(self):
        self.item['reading'] = sample_reading()
        self.item['reading']['updatedAt'] = '2026-11-07T11:00:00'
        with self.assertRaises(ValueError):
            validate_data(self.data)

    def test_feed_contains_separate_escaped_reading_sections(self):
        self.item['reading'] = sample_reading()
        content = feed.description(self.issue, self.item)
        for title in ('先看懂背景', '原文要点 · 中文整理', 'XNews 解读'):
            self.assertIn(title, content)
        for key in ('background', 'commentary'):
            self.assertIn(self.item['reading'][key][0], content)
        self.assertIn('&lt;script&gt;unsafe&lt;/script&gt; &amp;', content)
        self.assertNotIn('<script>unsafe</script>', content)
        self.assertIn('非逐字全文转载', content)
        self.assertIn('2026-11-07T11:00:00Z', content)

    def test_november_seventh_items_have_substantial_inline_reading(self):
        issue = next(i for i in self.data['issues'] if i['date'] == '2026-11-07')
        self.assertEqual(issue.get('contentFormat'), 'inline-reading-v1')
        for item in issue['items']:
            with self.subTest(item=item['id']):
                reading = item.get('reading', {})
                self.assertGreaterEqual(len(reading.get('background', [])), 2)
                self.assertGreaterEqual(len(reading.get('sourceSummary', [])), 3)
                self.assertGreaterEqual(len(reading.get('commentary', [])), 3)

    def test_homepage_renders_and_searches_inline_reading(self):
        result = subprocess.run(['node', str(ROOT / 'tests/check_inline_reading.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
