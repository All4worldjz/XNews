import json, pathlib, datetime, urllib.parse
root = pathlib.Path(__file__).parent
d = json.loads((root/'data/issues.json').read_text())
assert d['mode'] == 'preview'
assert d['schemaVersion'] == 1
assert d['timezone'] == 'UTC'
seen = set()
for issue in d['issues']:
    datetime.date.fromisoformat(issue['date'])
    assert issue['date'] not in seen
    seen.add(issue['date'])
    assert issue['coverage']
    ids = set()
    for item in issue['items']:
        assert item['id'] not in ids
        ids.add(item['id'])
        for key in ['title','summary','whyItMatters','caveat','category']:
            assert item[key]
        for key in ['sourcePublishedDate','eventDate']:
            if item[key]: datetime.date.fromisoformat(item[key])
        if item['verifiedAt']: datetime.datetime.fromisoformat(item['verifiedAt'].replace('Z','+00:00'))
        assert item['sources']
        for source in item['sources']:
            assert urllib.parse.urlparse(source['url']).scheme == 'https'
        if item['verification'] == 'verified':
            url = urllib.parse.urlparse(item['xPostUrl'])
            assert url.hostname in ['x.com','www.x.com','twitter.com','www.twitter.com'] and '/status/' in url.path
        if item['verification'] == 'official-source-sample': assert item['xPostUrl'] is None
for filename in ['app.js','style.css','index.html','.nojekyll']:
    assert (root/filename).exists()
assert not (root/'.github/workflows').exists()
print(f'PASS: {len(d["issues"])} issue(s), schema, dates, links, labels, static files, no workflows')
