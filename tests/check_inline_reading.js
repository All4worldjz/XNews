'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/issues.json'), 'utf8'));
const issue = data.issues[0];
const item = issue.items[0];
item.reading = {background: ['背景 needle_background'], sourceSummary: ['正文 needle_summary <script>alert(1)</script>'], commentary: ['观点 needle_commentary'], updatedAt: '2026-11-07T11:00:00Z'};
const nodes = new Map();
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {value: id === 'category' ? 'all' : '', innerHTML: '', textContent: '', events: {}, addEventListener(type, fn) {this.events[type] = fn;}, querySelectorAll() {return [];}});
  return nodes.get(id);
}
const context = {document: {getElementById: node}, URL, URLSearchParams, location: {href: 'https://example.org/XNews/', search: '', hash: ''}, history: {pushState() {}}, window: {addEventListener() {}}, fetch: async () => ({ok: true, json: async () => data}), navigator: {}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8'), context);
setImmediate(() => {
  const html = node('articles').innerHTML;
  assert.ok(html.includes('先看懂背景'), 'background must render inside the card');
  assert.ok(html.includes('原文要点 · 中文整理'), 'source summary must render inside the card');
  assert.ok(html.includes('XNews 解读'), 'commentary must render inside the card');
  assert.ok(html.includes('needle_background') && html.includes('needle_summary') && html.includes('needle_commentary'));
  assert.ok(!html.includes('<details'), 'reader should not need to expand the content');
  assert.ok(html.includes('&lt;script&gt;alert(1)&lt;/script&gt;'), 'inline text must be escaped');
  assert.ok(!html.includes('<script>alert(1)</script>'));
  for (const query of ['needle_background', 'needle_summary', 'needle_commentary']) {
    node('search').value = query;
    node('search').events.input();
    assert.ok(node('articles').innerHTML.includes(item.id), 'search must include ' + query);
    assert.ok(node('result-count').textContent.startsWith('1 条'));
  }
  node('search').value = 'no_such_news_12345';
  node('search').events.input();
  assert.ok(node('articles').innerHTML.includes('没有符合条件'));
  node('search').value = '';
  node('search').events.input();
  assert.ok(node('result-count').textContent.startsWith(issue.items.length + ' 条'));
  console.log('PASS: inline reading, escaping, searching and reset');
});
