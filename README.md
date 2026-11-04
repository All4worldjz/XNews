# XNews · AI 与 Enterprise Agentic AI 编辑简报

纯静态 HTML/CSS/JavaScript 网站。来源明确区分直接核验 X 原帖、公开镜像线索及官方来源。编辑顺序不是平台热度排名。不能编造原帖、互动量、涨速或覆盖范围。

## 本期与覆盖

2026-11-04 正式发布：10 条公开镜像内容编辑精选，包含新闻、技术分享和计划推广；另保留已发布的 1 条官方来源样例与原有 RSS GUID。另新增 1 篇 Agent Autoloop 深度文章（署名转载正文与官方仓库交叉核对）。真实 X 原帖直连核验数为 0。文章逐条显示证据、日期依据与限制。热点涨速 Top 10 当前不可用，不以编辑精选替代。

监控关键词包括 AI、Enterprise Agentic AI、企业智能体、Agent 安全、模型与研究。连续观测和自动采集尚未在仓库内实现；定时任务状态以任务配置为准，页面不承诺已运行的自动采集。

## 本地预览与验证

运行 `python3 -m http.server 8080` 后打开本地页面。

发布前运行：

```sh
python3 scripts/build_articles.py
python3 scripts/build_feed.py
python3 scripts/build_feed.py --check
python3 -m unittest discover -s tests
node --check app.js
python3 validate.py
```

## 数据与 RSS 一致性

订阅地址：https://all4worldjz.github.io/XNews/feed.xml

`data/issues.json` 是网站和 RSS 的唯一来源。必须一起提交数据与生成的 feed.xml，RSS 检查拒绝过期内容。GUID 按日期和文章 ID 构成；不要更改已发布条目的日期或 ID。RSS pubDate 是简报日期的 UTC 00:00，仅表示日期精度，不是实际发稿时刻。正文另外标注来源日期、事件日期、核验时刻及证据。

verification 支持 verified（直连 X 已核验）、x-mirror（第三方镜像，原帖未直连核验）、official-source（官方来源）、official-source-sample（保留样例）。第三方镜像时间可能是最后编辑时间；根据 status ID 推算时间必须明确记录 timestampBasis 并披露。互动数保持 null。

## 发布门槛

不足十条就发布实际核验数量，不凑榜。没有统一采样范围、可比较窗口和真实带时间计数，不发布“上升最快”结论。当前 validator 仅接受 unavailable 的 trends，且拒绝排名或互动数；接入可验证测量系统后须先扩展测试再改此门槛。仓库无定时工作流或 API 凭证。

## 深度文章

条目的可选 `article.sections` 保存正文（heading 与 paragraphs），由 `scripts/build_articles.py` 生成不依赖 JavaScript 的独立页面。RSS 包含同一份完整正文与文章链接，原有 GUID 不变。修改正文后同时生成文章与 RSS；`validate.py` 会检查两者是否过期。文章样式包含移动端、目录、键盘焦点与打印排版。

`syndicated-source` 表示署名转载正文与官方资料交叉核对，必须包含 republication 类型来源；不计入直接 X 核验或镜像精选。来源日期使用转载页日期，原帖访问限制另行说明。

## 知识债专题与信息图

新增知识债专题报告，区分研究证据、概念框架和治理建议。正文配备两幅信息图、移动端流程图和五项研究证据对照表。图像保留文字说明；文章与 RSS 同源生成。渲染器支持 visuals、figures、tables、subheadings，发布验证检查位置与图像文件。
