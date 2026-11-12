# XNews · AI 与 Enterprise Agentic AI 编辑简报

纯静态 HTML/CSS/JavaScript 网站。来源明确区分直接核验 X 原帖、公开镜像线索及官方来源。编辑顺序不是平台热度排名。不能编造原帖、互动量、涨速或覆盖范围。

## 本期与覆盖

本期收录 5 条直接核验 X 原帖并与官方资料交叉核对的编辑精选：Databricks Genie 插件、Gemini Decisions API、ElevenLabs 企业语音生态、Qwen4-Max 预览及 Grok Bot 团队协作。采样窗口为北京时间 2026-11-11 08:00 至 2026-11-12 08:00（UTC 2026-11-11T00:00:00Z 至 2026-11-12T00:00:00Z，结束时刻不包含）。原帖公开 HTML 正文和原生时间可读；搜索阅读器的访问限制逐条披露。Grok 官方文章日期与 X 发帖不同，明确保留差异，不称当日首发。编辑抽样不代表完整覆盖 X 或热度排名，不足十条不凑数；每条提供原创中文梳理与独立解读，不发布未经验证的互动量。 既往各期、宝玉内容、独立专题和高管简报及其 RSS 条目保持不变。

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

## Services 与中国 FDE 专题

新增红杉 Services 论纲与中国 FDE 经营研究，包含24个来源、3张原生数据表、3幅信息图与移动端版本。统计口径、预测与实际值、假设经济模型分别披露。表格与信息图支持正文原位插入；RSS保留表格注释与图像说明。

## 新闻内文与普通读者阅读

自 2026-11-07 期起，每条新闻默认在首页卡片内完整展示三部分：`reading.background`（通俗背景）、`reading.sourceSummary`（署名来源的原创中文整理）、`reading.commentary`（独立编辑解读）。不需访问 X、镜像或外部文章即可读懂新闻。正文不折叠，搜索也覆盖这三部分；RSS description 含同样的全部文字。

新增期数请使用 `contentFormat: "inline-reading-v1"`，并为每条提供上述三个非空段落数组与带时区的 `reading.updatedAt`。解释必要术语、事情经过、数字口径、证据边界和实际影响，避免只重复导语或给一句泛泛点评。来源段用 `[1]` 等编号对应本条 `sources`；背景中的假设例子和评论须明确与来源事实区分。未能读取来源时如实披露，不补写猜测。

不得把未经授权的受版权保护全文直接转载或逐段翻译；采用适量短摘录及原创整理，保留作者、机构与原文链接。旧期、独立专题文章与 RSS GUID 保持不变。本次仅补充 11 月 7 日三条新闻，不声称旧期已经全部补写。站内可读不等于已验证中国大陆所有网络都能访问 GitHub Pages。

## 高管简报同步与同日日报合并

每日高管简报在同日期 issue.items 中使用固定 `id: "executive-briefing"`、`category: "高管简报"`，正文使用现有 `article.sections`、`visuals`、`tables`，生成 `articles/YYYY-MM-DD-executive-briefing.html` 与 RSS。按日期加 ID 幂等追加或更新，不创建重复日期的 issue。

任何当日 AI 日报或高管简报发布都须先读取最新 main，合并同日 issue.items，不得整期覆盖对方已存在的内容；保持其他条目正文、日期、ID 和 RSS GUID 不变。原简报转换保留来源日期、信息截点、判断、建议及不确定性，不把同步时间称为新增核验；移除 UI 标记与私有链接，使用原创图表并标清金额与期限口径。发布前运行上述全部构建及校验步骤。

## 阅读界面与导航

首页增加本期目录（按编辑顺序、非热度排名）、较新/更早期数按钮和页尾导航。目录跳转会清除筛选，以免跳向被隐藏的新闻；切换期数更新 URL，支持浏览器前进/后退。手机端使用常驻顶部菜单与底部快捷导航，保留安全区，输入字号为 16px，正文 16–17px。独立文章带目录、来源与回到本期的快捷入口。新闻全文仍在首页直接展开，RSS、历史条目 ID 和内容不变。
