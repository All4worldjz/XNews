#!/usr/bin/env python3
"""Generate standalone article pages from canonical issue data."""
import argparse
from datetime import date
from urllib.parse import urlsplit
from html import escape
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
SITE='https://all4worldjz.github.io/XNews/'

def render_article(issue,item):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',item['id']): raise ValueError('Invalid article ID')
    date.fromisoformat(issue['date'])
    for url in [source['url'] for source in item['sources']] + ([item['xPostUrl']] if item.get('xPostUrl') else []):
        parsed=urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password: raise ValueError('Article links must use HTTPS without credentials')
    e=escape
    xlink = ''
    if item.get('xPostUrl'):
        label = 'X 原帖链接（未直连核验）' if item.get('verification') in {'x-mirror', 'syndicated-source'} else '打开 X 原帖'
        xlink = f'<p><a href="{e(item["xPostUrl"],quote=True)}" rel="noopener noreferrer">{label} ↗</a></p>'

    sections=item['article']['sections']
    toc=''.join(f'<li><a href="#section-{n}">{e(s["heading"])}</a></li>' for n,s in enumerate(sections,1))
    body=''.join(f'<section id="section-{n}"><h2>{e(s["heading"])}</h2>'+''.join(f'<p>{e(p)}</p>' for p in s['paragraphs'])+'</section>' for n,s in enumerate(sections,1))
    sources=''.join(f'<li><a href="{e(s["url"],quote=True)}" rel="noopener noreferrer">{e(s["label"])}</a></li>' for s in item['sources'])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(item['title'])} · XNews</title><meta name="description" content="{e(item['summary'],quote=True)}"><link rel="canonical" href="{SITE}articles/{issue['date']}-{item['id']}.html"><link rel="alternate" type="application/rss+xml" title="XNews RSS" href="../feed.xml"><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="../article.css"></head>
<body class="article-page"><a class="skip" href="#article-body">跳到正文</a><header class="site-header wrap"><a class="brand" href="../"><span class="brand-icon">X</span>XNews<span class="brand-sub">AI DAILY</span></a><nav aria-label="主导航"><a href="../">返回简报</a></nav><a class="rss-nav" href="../feed.xml">RSS 订阅</a></header>
<main class="article-wrap"><header class="article-header"><p class="eyebrow">XNEWS / DEEP READ</p><p class="article-category">{e(item['category'])} · 深度解读</p><h1>{e(item['title'])}</h1><p class="article-deck">{e(item['summary'])}</p><p class="article-meta">XNews 编辑整理与分析 · 发布 {e(issue['date'])} · 来源日期 {e(item.get('sourcePublishedDate') or '未确认')}</p><p class="article-disclosure">{e(item['caveat'])}</p></header>
<nav class="article-toc" aria-label="本文目录"><strong>阅读导航</strong><ol>{toc}</ol></nav><article id="article-body" class="article-body">{body}</article><section class="article-sources" id="sources"><h2>来源与核验</h2><p>核验记录：{e(item.get('verifiedAt') or '未确认')}。事实材料与编辑分析分别标明，来源中的主张不等于独立验证结果。</p><ol>{sources}</ol>{xlink}</section><div class="article-end"><a href="../?date={issue['date']}#{item['id']}">← 回到本期简报</a><a href="../feed.xml">RSS 订阅 ↗</a></div></main><footer class="wrap"><a class="brand" href="../">XNews</a><p>事实有来源 · 解读有边界</p></footer></body></html>
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=json.loads((ROOT/'data/issues.json').read_text());count=0
    for issue in data['issues']:
        for item in issue['items']:
            if not item.get('article'): continue
            expected=render_article(issue,item); path=ROOT/'articles'/f"{issue['date']}-{item['id']}.html"; count+=1
            if args.check:
                if not path.exists() or path.read_text()!=expected: print(f'Stale article: {path}',file=sys.stderr);return 1
            else: path.parent.mkdir(exist_ok=True);path.write_text(expected)
    print(f'PASS: {count} article page(s) '+('match canonical data' if args.check else 'generated'));return 0
if __name__=='__main__':raise SystemExit(main())
