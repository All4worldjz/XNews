'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl = value => { try { const url = new URL(value); return url.protocol === 'https:' ? url.href : null; } catch { return null; } };
  const labels = {'syndicated-source':'署名转载与官方资料 · X 原帖未直连核验', 'verified':'X 原帖已核验', 'x-mirror':'X 镜像记录 · 原帖未直连核验', 'official-source':'官方来源 · 非 X 原帖', 'official-source-sample':'官方来源样例 · 非 X 热榜'};
  const readingSections = [['background', '先看懂背景'], ['sourceSummary', '原文要点 · 中文整理'], ['commentary', 'XNews 解读']];
  function inlineReading(reading) {
    if (!reading) return '';
    const sections = readingSections.map(([key, title]) => `<section class="reading-section reading-${key}"><h4>${title}</h4>${reading[key].map(p => `<p>${escape(p)}</p>`).join('')}</section>`).join('');
    return `<div class="inline-reading"><p class="reading-note">依据下方署名来源独立整理，非逐字全文转载。背景帮助理解；解读为 XNews 观点，不代表原作者结论。</p>${sections}<p class="reading-updated">正文整理更新：<time datetime="${escape(reading.updatedAt)}">${escape(reading.updatedAt)}</time></p></div>`;
  }
  let data, selected;
  function render() {
    const issue = data.issues.find(i => i.date === selected) || data.issues[0];
    if (!issue) { $('articles').innerHTML = '<p class="empty">尚无已发布简报。</p>'; $('result-count').textContent = '0 条'; return; }
    selected = issue.date;
    $('issue-date').textContent = issue.date + ' · ' + data.timezone;
    $('coverage-text').textContent = issue.coverage;
    $('x-count').textContent = issue.items.filter(i => i.verification === 'verified' && safeUrl(i.xPostUrl)).length;
    $('official-count').textContent = issue.items.filter(i => ['official-source-sample', 'official-source'].includes(i.verification)).length;
    $('syndicated-count').textContent = issue.items.filter(i => i.verification === 'syndicated-source').length;
    $('mirror-count').textContent = issue.items.filter(i => i.verification === 'x-mirror').length;
    $('trends-status').textContent = issue.trends?.reason || '尚无可比时间窗口的真实观测，暂不发布涨速排名。';
    $('keywords').textContent = (data.keywords || ['AI', 'Enterprise Agentic AI']).join(' · ');
    const categories = [...new Set(issue.items.map(i => i.category))];
    const previousCategory = $('category').value;
    $('category').innerHTML = '<option value="all">全部主题</option>' + categories.map(c => `<option value="${escape(c)}">${escape(c)}</option>`).join('');
    $('category').value = categories.includes(previousCategory) ? previousCategory : 'all';
    const query = $('search').value.trim().toLowerCase();
    const category = $('category').value;
    const items = issue.items.filter(i => (category === 'all' || i.category === category) && [i.title,i.summary,i.category,i.whyItMatters,...readingSections.flatMap(([key]) => i.reading?.[key] || [])].join(' ').toLowerCase().includes(query));
    $('result-count').textContent = `${items.length} 条${issue.status === 'sample' ? '样例' : '新闻'} · 按编辑顺序展示，非热度排名`;
    $('articles').innerHTML = items.length ? items.map(item => {
      const sources = item.sources.map((s, index) => { const url = safeUrl(s.url); return url ? `<a class="source-link" href="${escape(url)}" target="_blank" rel="noopener noreferrer">[${index + 1}] ${escape(s.label)} ↗</a>` : ''; }).join('<br>');
      const xUrl = safeUrl(item.xPostUrl);
      return `<article class="news-card" id="${escape(item.id)}"><div class="card-top"><span class="tag">${escape(item.category)}</span><span class="tag sample-tag">${escape(labels[item.verification] || '待核验')}</span></div><h3>${escape(item.title)}</h3><p class="summary">${escape(item.summary)}</p>${item.article ? `<a class="read-article" href="./articles/${encodeURIComponent(issue.date)}-${encodeURIComponent(item.id)}.html">阅读全文与解读 →</a>` : ""}<div class="date-grid"><span>来源发布 ${escape(item.sourcePublishedDate || '未确认')}</span><span>事件日期 ${escape(item.eventDate || '未确认')}</span><span>核验 ${escape(item.verifiedAt || '未核验')}</span></div>${item.reading ? inlineReading(item.reading) : `<div class="insight"><p>${escape(item.whyItMatters)}</p></div>`}<p class="caveat">${escape(item.caveat)}</p>${sources}<div class="x-status">${xUrl ? `<a href="${escape(xUrl)}" target="_blank" rel="noopener noreferrer">${['x-mirror', 'syndicated-source'].includes(item.verification) ? 'X 原帖链接（未直连核验）' : '查看 X 原帖'} ↗</a> · 互动数据：未获取` : 'X 原帖：未核验 · 互动数据：未获取'}</div></article>`;
    }).join('') : '<p class="empty">没有符合条件的内容。试试其他关键词或「全部主题」。</p>';
    $('archive-list').innerHTML = data.issues.map(i => `<button class="archive-button" data-date="${escape(i.date)}" aria-pressed="${i.date === selected}"><span>${escape(i.date)}</span><span>${i.status === 'sample' ? '样例' : '日报'} · ${i.items.length} 条</span></button>`).join('');
    $('archive-list').querySelectorAll('button').forEach(button => button.addEventListener('click', () => { selected = button.dataset.date; const url = new URL(location.href); url.searchParams.set('date', selected); history.pushState({}, '', url); $('search').value = ''; $('category').value = 'all'; render(); }));
  }
  $('search').addEventListener('input', () => data && render());
  $('category').addEventListener('change', () => data && render());
  window.addEventListener('popstate', () => { selected = new URLSearchParams(location.search).get('date'); if (data) render(); });
  fetch('./data/issues.json?v=inline-reading-v1', {cache: 'no-cache'}).then(r => { if (!r.ok) throw new Error('读取失败'); return r.json(); }).then(value => { if (!Array.isArray(value.issues)) throw new Error('数据格式错误'); data = value; selected = new URLSearchParams(location.search).get('date'); render(); if (location.hash) { const target = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (target) target.scrollIntoView(); } }).catch(() => { $('result-count').textContent = '内容暂时无法读取'; $('articles').innerHTML = '<p class="empty">未能加载日报数据。请通过本地 HTTP 预览打开，或稍后刷新重试。</p>'; });
})();

// A normal feed link remains available when clipboard permission is unavailable.
document.getElementById('copy-feed').addEventListener('click', async () => {
  const url = new URL('./feed.xml', location.href).href;
  const status = document.getElementById('copy-status');
  try {
    await navigator.clipboard.writeText(url);
    status.textContent = '已复制。将地址粘贴到你的 RSS 阅读器即可订阅。';
  } catch {
    status.textContent = '订阅地址：' + url;
  }
});
