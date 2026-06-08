---
name: cn30days
version: "0.1.0"
description: "Research what people are talking about in the Chinese internet - Weibo, Baidu, Bilibili, GitHub trends, and authoritative news. Pulls hot topics and engagement data from platforms accessible inside China."
argument-hint: 'cn30days | cn30days AI | cn30days 高考 | cn30days --emit json'
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

> What's hot in the Chinese internet RIGHT NOW. Weibo hot search. Baidu trending. Bilibili popular. GitHub stars. All scored and ranked by real engagement.

## What It Does

```bash
python3 $SKILL_DIR/scripts/cn30days.py
```

Zero config. Weibo, Baidu, Bilibili work immediately. Set `GITHUB_TOKEN` for GitHub trends.

## When To Use

- "最近微博上在讨论什么？"
- "B站最近有什么火的视频？"
- "AI 圈最近有什么新项目？" (GitHub trends)
- "帮我查查今天的热搜"
- "最近一周有什么值得关注的事？"
- "cn30days AI agent" — topic-focused query

## Data Sources

| Source | Signal | No Auth | Signal Type |
|---|---|---|---|
| 🧣 **Weibo** 热搜 | raw_hot heat index | ✅ | Public opinion pulse |
| 🔍 **Baidu** 热搜 | hotScore | ✅ | Mass search intent |
| 📺 **Bilibili** 热门 | views + danmaku + likes | ✅ | Youth culture signal |
| ⭐ **GitHub** 趋势 | stars (7-day window) | ⚠️ token | Developer consensus |
| 📰 **PeopleDaily/Xinhua** RSS | editorial coverage | ✅ | Authoritative news |

## Usage

### Quick scan — compact AI synthesis format

```bash
python3 $SKILL_DIR/scripts/cn30days.py --emit compact
```

### Full JSON for custom processing

```bash
python3 $SKILL_DIR/scripts/cn30days.py --emit json
```

### Specific sources only

```bash
python3 $SKILL_DIR/scripts/cn30days.py --sources weibo,baidu
```

### Extended GitHub window

```bash
python3 $SKILL_DIR/scripts/cn30days.py --days 14
```

### With GitHub token

```bash
GITHUB_TOKEN=ghp_xxx python3 $SKILL_DIR/scripts/cn30days.py
```

---

# SKILL CONTRACT — 输出协议

When the user invokes `cn30days` or asks about Chinese internet trends, follow these rules:

## 输出格式

### BADGE (第一行)

```
🇨🇳 cn30days v0.1.0 · synced YYYY-MM-DD
```

### 结构

1. **数据采集概览** — 几个数据源，多少条，哪些可用/失败
2. **🔥 综合热度 Top 15** — 跨平台统一的卷标列表，附热度评分和来源
3. **按来源详列** — 每个来源的 Top 10
4. **Engine footer** — 统计摘要

### 规则

- **LAW 1**: 综合热度排序，不是简单罗列。B站视频+微博热搜+百度热搜混排，按归一化热度从高到低
- **LAW 2**: 每个条目标注来源平台和 emoji icon
- **LAW 3**: 百度热搜的 `desc` 字段提供上下文，包含在输出中
- **LAW 4**: GitHub 结果展示 repo 名 + stars + 描述
- **LAW 5**: Engine footer 必须包含在输出末尾

## Post-Processing Tips

After running the engine, use `WebSearch` to verify or expand on particularly interesting items. The engine provides WHAT people are talking about; web search can add WHY.

## Configuration

Create `~/.cn30days/config.json` (optional):

```json
{
  "github_token": "ghp_xxx",
  "sources": ["weibo", "baidu", "bilibili", "github", "news"],
  "days": 7,
  "max_per_source": 20
}
```

Environment variables override config file:
- `GITHUB_TOKEN` — GitHub API token (increases rate limit from 60/h to 5000/h)
