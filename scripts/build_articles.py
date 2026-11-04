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

def render_table(table):
    headers=''.join(f'<th scope="col">{escape(c)}</th>' for c in table['columns'])
    rows=''.join('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in row)+'</tr>' for row in table['rows'])
    return f'<div class="report-table" role="region" aria-label="{escape(table["title"],quote=True)}" tabindex="0"><table><caption>{escape(table["title"])}</caption><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div><p class="table-note">小屏幕可横向滚动查看完整表格。不同研究对象与指标不可直接相加或抵消。</p>'

def render_figure(figure):
    if not re.fullmatch(r'assets/[a-z0-9][a-z0-9-]*\.(svg|png|webp|jpg)',figure['src']): raise ValueError('Invalid figure asset path')
    if figure.get('mobileSrc') and not re.fullmatch(r'assets/[a-z0-9][a-z0-9-]*\.(svg|png|webp|jpg)',figure['mobileSrc']): raise ValueError('Invalid mobile figure path')
    if not figure.get('alt') or not figure.get('caption'): raise ValueError('Figure needs alt text and caption')
    mobile=f'<source media="(max-width: 600px)" srcset="../{escape(figure["mobileSrc"],quote=True)}">' if figure.get('mobileSrc') else ''
    return f'<figure class="article-figure"><a href="../{escape(figure["src"],quote=True)}" aria-label="打开信息图原图"><picture>{mobile}<img src="../{escape(figure["src"],quote=True)}" alt="{escape(figure["alt"],quote=True)}" loading="lazy"></picture></a><figcaption>{escape(figure["caption"])} · 点按图片查看原图。</figcaption></figure>'

def render_visual(visual):
    if visual.get('kind') not in {'evidence', 'flow', 'briefing'}: raise ValueError('Unknown article visual')
    e=escape
    cards=''.join(f'<li><span class="visual-label">{e(c["label"])}</span><h3>{e(c["headline"])}</h3><p>{e(c["text"])}</p></li>' for c in visual['cards'])
    return f'<figure class="report-visual visual-{visual["kind"]}"><figcaption><h2>{e(visual["title"])}</h2><p>{e(visual["caption"])}</p></figcaption><ol>{cards}</ol></figure>'

def render_article(issue,item):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',item['id']): raise ValueError('Invalid article ID')
    date.fromisoformat(issue['date'])
    for url in [source['url'] for source in item['sources']] + ([item['xPostUrl']] if item.get('xPostUrl') else []):
        parsed=urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password: raise ValueError('Article links must use HTTPS without credentials')
    e=escape
    def paragraph(text):
        return re.sub(r'\[(\d+)\]', lambda m: f'<a class="citation" href="#source-{m[1]}" aria-label="来源 {m[1]}">[{m[1]}]</a>' if 1 <= int(m[1]) <= len(item['sources']) else m[0], e(text))
    xlink = ''
    if item.get('xPostUrl'):
        label = 'X 原帖链接（未直连核验）' if item.get('verification') in {'x-mirror', 'syndicated-source'} else '打开 X 原帖'
        xlink = f'<p><a href="{e(item["xPostUrl"],quote=True)}" rel="noopener noreferrer">{label} ↗</a></p>'

    sections=item['article']['sections']
    toc=''.join(f'<li><a href="#section-{n}">{e(s["heading"])}</a></li>' for n,s in enumerate(sections,1))
    visuals=item['article'].get('visuals', [])
    figures=item['article'].get('figures', [])
    tables=item['article'].get('tables', [])
    body=''.join(render_visual(v) for v in visuals if v.get('afterSection',0)==0)
    body += ''.join(render_figure(f) for f in figures if f.get('afterSection',0)==0)
    body += ''.join(render_table(t) for t in tables if t.get('afterSection',0)==0)
    for n,section in enumerate(sections,1):
        body += f'<section id="section-{n}"><h2>{e(section["heading"])}</h2>'
        for index, text in enumerate(section['paragraphs']):
            body += ''.join(f'<h3>{e(h["title"])}</h3>' for h in section.get('subheadings',[]) if h['beforeParagraph']==index)
            body += f'<p>{paragraph(text)}</p>'
        body += '</section>'
        body += ''.join(render_visual(v) for v in visuals if v.get('afterSection',0)==n)
        body += ''.join(render_figure(f) for f in figures if f.get('afterSection',0)==n)
        body += ''.join(render_table(t) for t in tables if t.get('afterSection',0)==n)

    sources=''.join(f'<li id="source-{n}"><a href="{e(s["url"],quote=True)}" rel="noopener noreferrer">{e(s["label"])}</a></li>' for n,s in enumerate(item['sources'],1))
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
