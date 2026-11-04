#!/usr/bin/env python3
"""Build the static RSS feed from canonical issue data. No network or publishing."""
import argparse
from datetime import datetime, time, timezone, date
from email.utils import format_datetime
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import quote, urlencode, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://all4worldjz.github.io/XNews/'
ATOM = 'http://www.w3.org/2005/Atom'
ET.register_namespace('atom', ATOM)


def publication_date(issue):
    """Date-only issues have publication precision of one UTC day, not source time."""
    return datetime.combine(date.fromisoformat(issue['date']), time.min, timezone.utc)


def description(issue, item):
    paragraphs = []
    if issue.get('status') == 'sample' or item.get('verification') == 'official-source-sample':
        paragraphs.append('官方来源样例 · 非 X 热榜；不代表完整每日简报。')
    paragraphs.extend([issue['coverage'], item['summary'], item['whyItMatters'], item['caveat'],
                       f"简报发布日期：{issue['date']}（UTC，日期精度）",
                       f"来源发布日期：{item.get('sourcePublishedDate') or '未确认'}",
                       f"事件日期：{item.get('eventDate') or '未确认'}",
                       f"核验时间：{item.get('verifiedAt') or '未核验'}"])
    content = ''.join(f'<p>{escape(str(value))}</p>' for value in paragraphs)
    for source in item.get('sources', []):
        url = source['url']
        if urlsplit(url).scheme != 'https' or not urlsplit(url).netloc:
            raise ValueError('Source links must be absolute HTTPS URLs')
        content += f'<p>来源：<a href="{escape(url, quote=True)}">{escape(source["label"])}</a></p>'
    x_url = item.get('xPostUrl')
    if x_url and urlsplit(x_url).scheme == 'https' and urlsplit(x_url).netloc:
        content += f'<p><a href="{escape(x_url, quote=True)}">查看 X 原帖</a></p>'
    else:
        content += '<p>X 原帖：未核验 · 互动数据：未获取</p>'
    return content


def build_feed(data):
    if data.get('timezone') != 'UTC':
        raise ValueError('RSS publication date convention requires UTC issue data')
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    for tag, value in [('title', 'XNews · AI 科技简报'), ('link', SITE),
                       ('description', 'XNews 编辑简报。当前为预览样例，非 X 热榜；来源日期与简报发布日期分别标注。'),
                       ('language', 'zh-CN')]:
        ET.SubElement(channel, tag).text = value
    ET.SubElement(channel, f'{{{ATOM}}}link', {'href': SITE + 'feed.xml', 'rel': 'self', 'type': 'application/rss+xml'})
    issues = sorted(data['issues'], key=lambda issue: issue['date'], reverse=True)
    if issues:
        ET.SubElement(channel, 'lastBuildDate').text = format_datetime(publication_date(issues[0]), usegmt=True)
    seen = set()
    for issue in issues:
        for item in issue['items']:
            link = SITE + '?' + urlencode({'date': issue['date']}) + '#' + quote(item['id'], safe='')
            if link in seen:
                raise ValueError(f'Duplicate issue/item identity: {link}')
            seen.add(link)
            node = ET.SubElement(channel, 'item')
            for tag, value in [('title', item['title']), ('link', link),
                               ('description', description(issue, item)), ('category', item['category']),
                               ('pubDate', format_datetime(publication_date(issue), usegmt=True))]:
                ET.SubElement(node, tag).text = value
            ET.SubElement(node, 'guid', {'isPermaLink': 'true'}).text = link
    ET.indent(rss, space='  ')
    return ET.tostring(rss, encoding='utf-8', xml_declaration=True) + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'data/issues.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'feed.xml')
    parser.add_argument('--check', action='store_true', help='Fail if feed is missing or differs from canonical data')
    args = parser.parse_args()
    expected = build_feed(json.loads(args.data.read_text(encoding='utf-8')))
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != expected:
            print('RSS feed is missing or stale; run python3 scripts/build_feed.py', file=sys.stderr)
            return 1
        print('PASS: RSS feed matches canonical issue data')
    else:
        args.output.write_bytes(expected)
        print(f'Generated {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
