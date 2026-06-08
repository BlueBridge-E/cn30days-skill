# cn30days-skill

> 🇨🇳 中国互联网全网热搜聚合引擎 — AI agent skill that researches what's hot across the Chinese internet.

**Weibo hot search. Baidu trending. Bilibili popular. GitHub stars. Authoritative news.** All scored and ranked by real engagement, not editors.

## Why

`last30days-skill` is brilliant — Reddit upvotes, X likes, YouTube transcripts, Polymarket odds. But it doesn't work inside China. Reddit/X/YouTube are blocked. That's millions of Chinese internet users and their conversations that go unseen.

**cn30days does for the Chinese internet what last30days does for the English internet** — multi-source aggregation with community-driven heat scoring.

## Zero Config

```bash
python3 scripts/cn30days.py
```

Weibo, Baidu, Bilibili work immediately. No API keys needed. Set `GITHUB_TOKEN` for GitHub trends.

## Data Sources

| Source | Signal | Auth | Description |
|---|---|---|---|
| 🧣 Weibo 微博 | raw_hot heat index | None | Real-time public opinion pulse |
| 🔍 Baidu 百度 | hotScore | None | Mass search intent |
| 📺 Bilibili B站 | views + danmaku + likes | None | Youth culture & gaming |
| ⭐ GitHub | stars (7-day) | Token (optional) | Developer consensus |
| 📰 PeopleDaily/Xinhua | editorial | None | Authoritative news |

## Install

```bash
# Via npx skills
npx skills add BlueBridge-E/cn30days-skill -g

# Or clone manually
git clone https://github.com/BlueBridge-E/cn30days-skill.git ~/.agents/skills/cn30days
```

## Usage

```bash
# Full scan — compact AI-ready output
python3 scripts/cn30days.py

# JSON for your own processing
python3 scripts/cn30days.py --emit json

# Weibo + Baidu only
python3 scripts/cn30days.py --sources weibo,baidu

# Wider GitHub window
python3 scripts/cn30days.py --days 14

# With GitHub token (5000 req/h vs 60)
GITHUB_TOKEN=ghp_xxx python3 scripts/cn30days.py
```

### Example Output

```
🇨🇳 cn30days v0.1.0 · synced 2026-06-08

## 数据采集报告
**已采集 113 条**，来自 weibo, baidu, bilibili, github

## 🔥 综合热度 Top 20
1. 📺 [B站] 信 |《归唐》19分钟完整实机演示 [热度:100]
2. 🔍 [百度] 习近平在朝鲜媒体发表署名文章 [热度:90]
3. 🔍 [百度] 考生直呼物理太难了 [热度:88]
...
```

## Roadmap

- [ ] Keyword-based filtering (--topic)
- [ ] Zhihu hot topics (anti-crawl)
- [ ] Douyin trending
- [ ] WeChat articles 搜一搜
- [ ] HTML brief export (like last30days --emit=html)
- [ ] Time range filter
- [ ] Sentiment analysis overlay

## License

MIT — use it, fork it, ship it.
