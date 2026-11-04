import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
class ArticleTests(unittest.TestCase):
    def test_full_sections_are_present_and_escaped_in_feed(self):
        spec = importlib.util.spec_from_file_location('feed', ROOT/'scripts/build_feed.py')
        feed = importlib.util.module_from_spec(spec); spec.loader.exec_module(feed)
        data = json.loads((ROOT/'data/issues.json').read_text()); issue=data['issues'][0]; item=issue['items'][0]
        item['article']={'sections':[{'heading':'Analysis <script>', 'paragraphs':['Full body & context']} ]}
        result=feed.description(issue,item)
        self.assertIn('Analysis &lt;script&gt;',result)
        self.assertIn('Full body &amp; context',result)
        self.assertIn('articles/'+issue['date']+'-'+item['id']+'.html',result)
    def test_article_render_has_static_body_navigation_and_canonical(self):
        script=ROOT/'scripts/build_articles.py'
        self.assertTrue(script.exists(), 'Article generator is required')
        spec=importlib.util.spec_from_file_location('articles',script); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data=json.loads((ROOT/'data/issues.json').read_text()); issue=data['issues'][0]; item=issue['items'][0]
        item['article']={'sections':[{'heading':'Analysis <script>', 'paragraphs':['Full body & context']} ]}
        result=module.render_article(issue,item)
        for value in ['Full body &amp; context','Analysis &lt;script&gt;','name="viewport"','rel="canonical"','href="#section-1"','../feed.xml']:
            self.assertIn(value,result)
    def test_validation_rejects_empty_or_nontext_article_sections(self):
        from validate import validate_data
        data=json.loads((ROOT/'data/issues.json').read_text()); item=data['issues'][0]['items'][0]
        for article in [{'sections':[]},{'sections':[{'heading':'Test','paragraphs':[]}]},{'sections':[{'heading':'Test','paragraphs':[3]}]}]:
            item['article']=article
            with self.assertRaises(ValueError):validate_data(data)
    def test_article_identity_includes_issue_date(self):
        spec=importlib.util.spec_from_file_location('articles',ROOT/'scripts/build_articles.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data=json.loads((ROOT/'data/issues.json').read_text());issue=data['issues'][0];item=issue['items'][0];item['article']={'sections':[{'heading':'A','paragraphs':['B']}]}
        self.assertIn('articles/'+issue['date']+'-'+item['id']+'.html',module.render_article(issue,item))
    def test_article_rejects_unsafe_urls(self):
        spec=importlib.util.spec_from_file_location('articles',ROOT/'scripts/build_articles.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data=json.loads((ROOT/'data/issues.json').read_text());issue=data['issues'][0];item=issue['items'][0];item['article']={'sections':[{'heading':'A','paragraphs':['B']}]};item['sources'][0]['url']='javascript:alert(1)'
        with self.assertRaises(ValueError):module.render_article(issue,item)
