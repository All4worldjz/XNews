"""Run with python3 -m unittest discover -s tests -p 'test_rss.py'."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/build_feed.py'

class RSSTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'RSS generator must exist')
        spec = importlib.util.spec_from_file_location('build_feed', SCRIPT)
        self.feed = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.feed)
        self.data = json.loads((ROOT / 'data/issues.json').read_text())

    def test_all_items_have_exact_issue_links_and_rfc_dates(self):
        channel = ET.fromstring(self.feed.build_feed(self.data)).find('channel')
        expected = [(issue, item) for issue in self.data['issues'] for item in issue['items']]
        self.assertEqual(len(channel.findall('item')), len(expected))
        actual = {item.findtext('link'): item for item in channel.findall('item')}
        for issue, item in expected:
            link = f"https://all4worldjz.github.io/XNews/?date={issue['date']}#{item['id']}"
            node = actual[link]
            self.assertEqual(node.findtext('title'), item['title'])
            self.assertEqual(parsedate_to_datetime(node.findtext('pubDate')).date().isoformat(), issue['date'])
            description = node.findtext('description')
            self.assertIn(item.get('sourcePublishedDate') or '未确认', description)
            self.assertIn('来源发布日期', description)
            self.assertIn('简报发布日期', description)
            if issue['status'] == 'sample':
                self.assertIn('样例', description)
                self.assertIn('非 X 热榜', description)
        atom = channel.find('{http://www.w3.org/2005/Atom}link')
        self.assertEqual(atom.attrib, {'href': 'https://all4worldjz.github.io/XNews/feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})

    def test_escaping_and_stable_unique_guids_across_issues(self):
        data = copy.deepcopy(self.data)
        data['issues'][0]['items'][0]['title'] = 'A & B <C> "D"'
        data['issues'][0]['items'][0]['summary'] = '<script>alert("x")</script> & useful'
        duplicate = copy.deepcopy(data['issues'][0])
        duplicate['date'] = '2026-11-05'
        data['issues'].append(duplicate)
        first = self.feed.build_feed(data)
        nodes = ET.fromstring(first).findall('./channel/item')
        self.assertEqual(nodes[0].findtext('title'), 'A & B <C> "D"')
        self.assertIn('&lt;script&gt;', nodes[0].findtext('description'))
        guids = {n.findtext('guid') for n in nodes}
        self.assertEqual(len(guids), len(data['issues'][0]['items']) * 2)
        data['issues'].reverse()
        self.assertEqual(first, self.feed.build_feed(data))
        self.assertEqual(first, self.feed.build_feed(data))

    def test_checked_in_feed_is_current(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_rejects_changed_data_without_regeneration(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'issues.json', Path(folder) / 'feed.xml'
            source.write_text(json.dumps(self.data))
            command = [sys.executable, str(SCRIPT), '--data', str(source), '--output', str(output)]
            subprocess.run(command, check=True, capture_output=True)
            self.data['issues'][0]['items'][0]['title'] += ' changed'
            source.write_text(json.dumps(self.data))
            result = subprocess.run(command + ['--check'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('stale', result.stderr)

if __name__ == '__main__':
    unittest.main()
