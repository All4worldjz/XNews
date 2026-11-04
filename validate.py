"""Validate canonical issue data without making network or publishing calls."""
import datetime
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent
VERIFICATIONS = {'syndicated-source', 'verified', 'x-mirror', 'official-source', 'official-source-sample'}

def require(value, message):
    if not value: raise ValueError(message)

def https(value):
    url = urlsplit(value or '')
    return url.scheme == 'https' and bool(url.hostname) and not url.username and not url.password

def validate_data(data):
    require(data.get('mode') in {'preview', 'published'}, 'Unknown publication mode')
    require(data.get('schemaVersion') == 1 and data.get('timezone') == 'UTC', 'Unsupported schema/timezone')
    dates = set()
    for issue in data['issues']:
        datetime.date.fromisoformat(issue['date'])
        require(issue['date'] not in dates, 'Duplicate issue date')
        dates.add(issue['date'])
        require(issue.get('coverage'), 'Coverage is required')
        require(issue.get('status') in {'sample', 'published'}, 'Unknown issue status')
        trends = issue.get('trends')
        if issue['status'] == 'published': require(trends, 'Published issue needs an explicit trends state')
        if trends:
            require(trends.get('status') == 'unavailable', 'Measured rankings are not supported without a validated measurement pipeline')
            require(trends.get('reason') and not trends.get('items'), 'Unavailable trends cannot contain rankings')
        ids = set()
        for item in issue['items']:
            require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', item['id']) and item['id'] not in ids, 'Invalid or duplicate item ID')
            ids.add(item['id'])
            for key in ['title', 'summary', 'whyItMatters', 'caveat', 'category']:
                require(isinstance(item.get(key), str) and item[key].strip(), f'Missing {key}')
            for key in ['sourcePublishedDate', 'eventDate']:
                if item.get(key): datetime.date.fromisoformat(item[key])
            if item.get('verifiedAt'):
                stamp = datetime.datetime.fromisoformat(item['verifiedAt'].replace('Z', '+00:00'))
                require(stamp.tzinfo is not None, 'Verification timestamp needs timezone')
            verification = item.get('verification')
            require(verification in VERIFICATIONS, 'Unknown verification state')
            require(item.get('sources'), 'Sources are required')
            for source in item['sources']: require(https(source['url']) and source.get('label'), 'Invalid source')
            if verification in {'verified', 'x-mirror', 'syndicated-source'}:
                url = urlsplit(item.get('xPostUrl') or '')
                require(https(item.get('xPostUrl')) and url.hostname in {'x.com','www.x.com','twitter.com','www.twitter.com'} and re.fullmatch(r'/[A-Za-z0-9_]+/status/[0-9]+/?', url.path), 'Invalid X permalink')
                require(item.get('verifiedAt') and item.get('sourcePublishedDate'), 'X evidence needs timestamp and source date')
                if verification == 'syndicated-source': require(any(s.get('type') == 'republication' for s in item['sources']), 'Republication source must be disclosed')
                if verification == 'x-mirror': require(any(s.get('type') == 'mirror' for s in item['sources']), 'Mirror source must be disclosed')
            else:
                require(item.get('xPostUrl') is None, 'Official-only item cannot imply X verification')
            if 'article' in item:
                article = item['article']
                require(isinstance(article, dict), 'Article must be an object')
                sections = article.get('sections')
                require(isinstance(sections, list) and sections, 'Article needs sections')
                for kind in ['visuals','figures','tables']:
                    entries=article.get(kind,[])
                    require(isinstance(entries,list), 'Article extras must be lists')
                    for entry in entries:
                        require(isinstance(entry,dict) and type(entry.get('afterSection',0)) is int and 0 <= entry.get('afterSection',0) <= len(sections), 'Invalid article placement')
                        if kind == 'figures':
                            for field in ['src','mobileSrc']:
                                if entry.get(field):require(re.fullmatch(r'assets/[a-z0-9][a-z0-9-]*\.(svg|png|webp|jpg)',entry[field]), 'Invalid figure path')
                            require(entry.get('src') and entry.get('alt') and entry.get('caption'), 'Figure needs path, alt and caption')
                        if kind == 'tables':
                            require(entry.get('title') and entry.get('columns') and entry.get('rows'), 'Table needs title, columns and rows')
                            require(all(len(row)==len(entry['columns']) for row in entry['rows']), 'Table rows must match columns')
                for section in sections:
                    require(isinstance(section, dict) and isinstance(section.get('heading'), str) and section['heading'].strip(), 'Article section needs heading')
                    paragraphs = section.get('paragraphs')
                    require(isinstance(paragraphs, list) and paragraphs and all(isinstance(p, str) and p.strip() for p in paragraphs), 'Article paragraphs must be nonempty text')
            require(item.get('engagement') is None, 'Engagement publishing awaits validated measurement pipeline')
    return data

def main():
    data = validate_data(json.loads((ROOT / 'data/issues.json').read_text()))
    for name in ['app.js', 'style.css', 'article.css', 'index.html', '.nojekyll']: require((ROOT / name).exists(), f'Missing {name}')
    for issue in data['issues']:
        for item in issue['items']:
            for figure in item.get('article',{}).get('figures',[]):
                for field in ['src','mobileSrc']:
                    if figure.get(field):require((ROOT / figure[field]).is_file(), 'Missing figure asset: '+figure[field])
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_feed.py'), '--check'], check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_articles.py'), '--check'], check=True)
    print(f'PASS: {len(data["issues"])} issue(s), schema, dates, evidence labels, static files and RSS')

if __name__ == '__main__': main()
