import copy
import json
from pathlib import Path
import unittest
from validate import validate_data

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).resolve().parents[1] / 'data/issues.json').read_text())
    def test_current_data(self):
        validate_data(self.data)
    def test_reject_false_x_verification(self):
        d = copy.deepcopy(self.data)
        d['issues'][0]['items'][0].update(verification='verified', xPostUrl='https://example.org/status/123')
        with self.assertRaises(ValueError): validate_data(d)
    def test_reject_unknown_verification(self):
        d = copy.deepcopy(self.data)
        d['issues'][0]['items'][0]['verification'] = 'trust-me'
        with self.assertRaises(ValueError): validate_data(d)
    def test_unavailable_trends_cannot_have_ranks(self):
        d = copy.deepcopy(self.data)
        d['issues'][0]['trends'] = {'status':'unavailable', 'reason':'No baseline', 'items':[{'rank':1}]}
        with self.assertRaises(ValueError): validate_data(d)
    def test_release_requires_explicit_trends_state(self):
        d = copy.deepcopy(self.data)
        d['mode'] = 'published'
        d['issues'][0]['status'] = 'published'
        d['issues'][0].pop('trends', None)
        with self.assertRaises(ValueError): validate_data(d)
    def test_syndicated_source_requires_republication_evidence(self):
        # The newest published issue can be an executive-only brief, with no X posts.
        # This evidence rule should not depend on whichever issue was published last.
        item = {
            'id': 'republication-fixture',
            'title': 'Syndicated article',
            'summary': 'Summary',
            'whyItMatters': 'Context',
            'caveat': 'X post not fetched directly',
            'category': 'AI',
            'verification': 'syndicated-source',
            'xPostUrl': 'https://x.com/example/status/123',
            'verifiedAt': '2026-01-01T12:00:00Z',
            'sourcePublishedDate': '2026-01-01',
            'sources': [{'label': 'Author page', 'url': 'https://example.org/author', 'type': 'official'}],
        }
        data = {
            'schemaVersion': 1,
            'timezone': 'UTC',
            'mode': 'published',
            'issues': [{
                'date': '2026-01-01',
                'status': 'published',
                'coverage': 'Syndicated evidence fixture',
                'trends': {'status': 'unavailable', 'reason': 'No baseline', 'items': []},
                'items': [item],
            }],
        }
        with self.assertRaisesRegex(ValueError, 'Republication source must be disclosed'):
            validate_data(data)
        item['sources'].append({
            'label': 'Signed republication',
            'url': 'https://example.org/article',
            'type': 'republication',
        })
        validate_data(data)
    def test_rejects_out_of_range_visual_placement(self):
        d=copy.deepcopy(self.data);item=d['issues'][0]['items'][0]
        item['article']={'sections':[{'heading':'Main','paragraphs':['Context']}]}
        item['article']['figures']=[{'src':'assets/test.svg','alt':'test','caption':'test','afterSection':999}]
        with self.assertRaises(ValueError):validate_data(d)
