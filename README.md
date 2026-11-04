# XNews 测试预览

纯静态 HTML/CSS/JavaScript 网站。当前仅为版式与发布测试，展示一条明确标记的官方来源样例，不是 X 热门日报；没有已核验 X 原帖或互动指标。

每日采集与自动发布尚未启用，待用户验收。页面保留 noindex。

本地预览：python3 -m http.server 8080

检查：node --check app.js && python3 validate.py

数据位于 data/issues.json；历史期数可保留归档。不得编造 X 原帖、互动数或覆盖范围。

## RSS 订阅

订阅地址：https://all4worldjz.github.io/XNews/feed.xml

RSS 2.0 来自同一份 `data/issues.json`，包含归档各期的全部条目。每条链接携带期数 `?date=YYYY-MM-DD` 和文章 `#id`，GUID 由期数与文章 ID 构成，重建不变，同 ID 在不同期数为独立条目。请不要修改已发布条目的日期或 ID。

当前订阅内容也是明确标记的官方来源样例，非 X 热榜。RSS `pubDate` 使用简报日期的 UTC 00:00（日期精度，不代表实际发稿时刻）；正文分别保留来源发布日期、事件日期、核验时间及来源链接。`lastBuildDate` 同样使用最新一期的日期，构建不注入当前时间，保证结果可重复。

手工更新数据后、发布前执行：

```sh
python3 scripts/build_feed.py
python3 scripts/build_feed.py --check
python3 -m unittest discover -s tests -p 'test_rss.py'
node --check app.js && python3 validate.py
```

必须一并提交更新后的 `data/issues.json` 与 `feed.xml`。`--check` 与 RSS 测试会拒绝过期或缺失的 feed；测试也验证真实数据链接、日期、样例标记、HTML/XML 转义和跨期 GUID。生成器只写本地静态文件，不联网、不发布。未增加工作流，自动采集与定时发布继续关闭。
