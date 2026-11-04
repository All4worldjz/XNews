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
