---
name: cn30days
version: "0.1.0"
description: "Research what people are talking about in the Chinese internet - Weibo, Baidu, Bilibili, GitHub trends, and authoritative news. Pulls hot topics and engagement data from platforms accessible inside China, then synthesizes a narrative report."
argument-hint: 'cn30days | cn30days AI | cn30days 高考 | cn30days 华为 vs 小米'
allowed-tools: Bash, Read, Write, WebSearch
homepage: https://github.com/BlueBridge-E/cn30days-skill
repository: https://github.com/BlueBridge-E/cn30days-skill
author: BlueBridge-E
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "🇨🇳"
    requires:
      env: []
      optionalEnv:
        - GITHUB_TOKEN
      bins:
        - python3
    files:
      - "scripts/*"
    tags:
      - research
      - chinese-internet
      - weibo
      - baidu
      - bilibili
      - github
      - hot-search
      - trends
      - news
      - multi-source
      - cn30days
---

# cn30days — 中国互联网全网热搜聚合 Skill

> What's hot in the Chinese internet RIGHT NOW. Weibo hot search. Baidu trending. Bilibili popular. GitHub stars. Authoritative news. All collected by the engine, then AI reads it all and writes you a narrative synthesis with patterns and conclusions.

**核心思路:** Python engine 负责多源并行采集 → AI 负责读取数据、提炼模式、写成叙事段落。

---

# SKILL CONTRACT — 启动流程（每次调用必须遵循）

## Step 1: 运行 Engine

**如果用户指定了话题**（如 `cn30days AI`、`cn30days 考研`），加 `--topic`：

```bash
source ~/.openclaw/workspace/.secure/github-tokens.sh 2>/dev/null || true
python3 "$SKILL_DIR/scripts/cn30days.py" --topic "{话题}" --emit compact
```

**如果没有指定话题**（如 `cn30days`），不加 `--topic`：

```bash
source ~/.openclaw/workspace/.secure/github-tokens.sh 2>/dev/null || true
python3 "$SKILL_DIR/scripts/cn30days.py" --emit compact
```

不要跳过这一步。Engine 是 skill 的骨架。没有 engine 输出就是瞎编。

## Step 2: （可选）WebSearch 补充

**当用户指定了话题时**，在 engine 数据采集完成后，用 WebSearch 补充 2-3 条外部信息以丰富报告深度。

```
web_search: "{话题} 最新 2026"（中文，count=5）
```

WebSearch 的作用：
- 补充不在热搜上但值得关注的行业动态
- 提供更详细的背景和分析
- 标注为"外部信源"，区别于 engine 的实时热度数据

在合成时，将 WebSearch 结果与 engine 数据融合，标注各自来源。

Engine 输出结构：
- **## 数据采集报告**: 来源、条数、可用/失败
- **## 🔥 综合热度 Top 20**: 跨平台归一化排序
- **## 🧣 微博热搜**: Top 10 微博话题
- **## 🔍 百度热搜**: Top 10 百度搜索
- **## 📺 B站热门**: Top 10 B站视频
- **## ⭐ GitHub 趋势**: Top 10 仓库
- **## 📰 权威媒体**: Top 10 官媒稿件
- **Engine footer**: 统计摘要

## Step 4: AI 合成 → 叙事化输出

你必须阅读 engine 的完整输出，然后自己写出以下结构的叙事报告。不允许直接复制 engine 的列表。

---

# OUTPUT CONTRACT — 输出协议

## BADGE（必须第一行）

```
🇨🇳 cn30days v{VERSION} · synced {YYYY-MM-DD}
```

从 SKILL.md 头部取 version，从今天取日期。空一行后开始正文。

## QUERY_TYPE 判断

根据用户输入自动判断类型：
- `GENERAL` — 没有特殊关键词，就是"看看今天有什么"或概括性话题
- `TOPIC` — 用户指定了特定话题，如 "cn30days AI"、"cn30days 高考"
- `COMPARISON` — 包含"vs"或"对比"，如 "cn30days 华为 vs 小米"
- `RECOMMENDATIONS` — 包含"最好"、"推荐"、"Top"、"最佳"、"有什么好的"

## 输出格式（按类型）

### GENERAL（无指定话题）— 默认就是这种

```
🇨🇳 cn30days v{VERSION} · synced {YYYY-MM-DD}

今日全网速览：

{bold-lead-in 段落1: 今天最大的新闻是什么，覆盖 3-4 句话}
{bold-lead-in 段落2: 次大焦点，覆盖 3-4 句话}
{bold-lead-in 段落3: 值得关注的社会情绪/文化趋势}
{bold-lead-in 段落4: 技术/GitHub 动态}

关键词分析：

1. {关键词1} — {这个方向为什么热，数据支撑，来源}
2. {关键词2} — ...
3. {关键词3} — ...
...
```

**bold-lead-in 段落写法：**
- 每一段用 `**粗体开头几句**` 作为引子，然后展开
- 包含具体数据（多少播放、多少赞、哪个排名）
- 标注来源平台（微博/B站/百度/GitHub/人民日报）
- 有 URL 的用 `[标题](URL)` 做 inline 链接
- 禁止 `##` 小节标题
- 禁止单独列 `Sources:` 块
- 禁止 em-dash（—），用 ` - ` 替代

### TOPIC（指定话题）

```
🇨🇳 cn30days v{VERSION} · synced {YYYY-MM-DD}

关于「{话题}」，我从全网采集了以下发现：

{bold-lead-in 段落1: 核心发现 - 来自 engine 数据}
{bold-lead-in 段落2: 行业背景 - 来自 WebSearch 补充}
{bold-lead-in 段落3: 社区反应/讨论方向 - 来自 engine 数据}
...

关键结论：

1. {结论} — {证据 + 来源标注：engine数据 / WebSearch / 两者交叉验证}
2. ...
```

**WebSearch 与 engine 数据的融合规则：**
- engine 数据标注为"来自全网热搜"，提供实时热度
- WebSearch 数据标注为"来自行业报道"，提供深度背景
- 两者一致 → 标记为"交叉验证"
- 两者不一致 → 列出各自说法，优先采信 engine（实时数据）

### COMPARISON（对比）

```
🇨🇳 cn30days v{VERSION} · synced {YYYY-MM-DD}

# {A} vs {B}: 今日全网对比

## 一言蔽之
{一句话总结}

## {A}
{3-5 句关于 A 的发现，来源数据}

## {B}
{3-5 句关于 B 的发现，来源数据}

## 对比分析

| 维度 | {A} | {B} |
|---|---|---|
| 热度 | {数据} | {数据} |
| 舆情方向 | {正面/负面/中性} | {正面/负面/中性} |
| 代表事件 | {事件} | {事件} |

## 结论
{2-3 句总结}
```

### RECOMMENDATIONS（推荐类）

```
🇨🇳 cn30days v{VERSION} · synced {YYYY-MM-DD}

关于「{话题}」的推荐清单：

1. {推荐项} — {为什么推荐，热度/数据}
2. ...
```

---

## 输出铁律（LAWS）

**LAW 1: BADGE 必须第一行，不能少。** 这是防止 AI 写 blog-post 风格标题的锚点。

**LAW 2: 禁止 `##` 小节标题（COMPARISON 除外）。** 用粗体段落开头替代。

**LAW 3: 禁止 em-dash。** 用 ` - ` 替代 `—` 和 `–`。

**LAW 4: 禁止末尾 Sources 块。** 用 inline `[平台](URL)` 链接替代。Engine footer 就是来源列表。

**LAW 5: Engine footer 必须存在于输出末尾。** 直接通过 engine 的 `---` 分割线 + `✅ cn30days engine` 行。

**LAW 6: Inline 链接必须。** 提到具体话题词条、视频、仓库、新闻时，有能力就用 `[名字](URL)`。

**LAW 7: 有数据才说话。** 每条结论必须有 engine 数据支撑，不编造。

**LAW 8: 中文输出。** 整篇报告用中文撰写。

---

## 合成后自检清单

在发送之前，检查：

1. □ 第一行是 BADGE 吗？
2. □ 没有 `##` 小节标题吗（COMPARISON 除外）？
3. □ 没有 em-dash 吗？
4. □ 末尾没有裸露的 `Sources:` 块吗？
5. □ 有 inline `[链接](URL)` 吗？
6. □ 有 engine footer 吗？
7. □ 全是中文吗？

全部通过再发送。

---

## 数据源参考

| Source | Signal | Auth | Icon |
|---|---|---|---|
| 微博热搜 | raw_hot heat index | None | 🧣 |
| 百度热搜 | hotScore | None | 🔍 |
| Bilibili 热门 | views + danmaku + likes | None | 📺 |
| GitHub 趋势 | stars (7-day) | Token (optional) | ⭐ |
| 权威媒体 (人民网/新华社) | editorial | None | 📰 |

## 独立 CLI 使用

```bash
# 采集数据（不合成）
python3 scripts/cn30days.py --emit compact

# JSON 输出
python3 scripts/cn30days.py --emit json

# 特定来源
python3 scripts/cn30days.py --sources weibo,baidu

# GitHub 更多天
python3 scripts/cn30days.py --days 14
```
