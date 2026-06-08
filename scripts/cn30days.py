#!/usr/bin/env python3
"""
cn30days — 中国互联网全网热搜聚合引擎
=========================================
采集国内多个平台的热度数据，按社区参与度评分排序，输出结构化结果供 AI 合成。

数据源（零配置可用）:
  - 微博热搜（公开移动端 API，无需登录）
  - 百度热搜（公开页面，无需登录）
  - Bilibili 热门（公开 API，无需登录）
  - GitHub 趋势（需 GITHUB_TOKEN 环境变量，可选）

用法:
  python3 cn30days.py [--topic KEYWORD] [--days 7] [--sources weibo,baidu,bilibili,github]
  python3 cn30days.py --emit compact    # 输出 AI-ready 紧凑格式
  python3 cn30days.py --help
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from typing import Optional

# Lazy import for topic expansion (same directory)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from topic_expansions import expand_topic
except ImportError:
    def expand_topic(t):
        return [t.strip().lower()]

VERSION = "0.1.0"
BEIJING_TZ = timezone(timedelta(hours=8))

UA = "cn30days/0.1 (cross-platform social heat aggregator; https://github.com/BlueBridge-E/cn30days-skill)"

# ============================================================
# Data source: 微博热搜 (public mobile API)
# ============================================================
def fetch_weibo_hot() -> list[dict]:
    """Fetch Weibo hot search list. Public API, no auth needed."""
    url = "https://weibo.com/ajax/side/hotSearch"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://weibo.com/"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return [{"error": f"weibo: {e}"}]

    items = data.get("data", {}).get("realtime", [])
    results = []
    for idx, item in enumerate(items[:30]):
        # Filter ads and sponsored
        if item.get("flag", 0) == 1 or item.get("promotion", {}):
            continue
        results.append({
            "rank": idx + 1,
            "title": item.get("word", item.get("note", "")),
            "heat": item.get("raw_hot", item.get("num", 0)),
            "url": f"https://s.weibo.com/weibo?q={urllib.parse.quote(item.get('word_scheme', item.get('word', '')))}",
            "source": "weibo",
        })
    return results


# ============================================================
# Data source: 百度热搜
# ============================================================
def fetch_baidu_hot() -> list[dict]:
    """Fetch Baidu realtime hot search."""
    url = "https://top.baidu.com/board?tab=realtime"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [{"error": f"baidu: {e}"}]

    # Extract embedded JSON data from HTML comment
    match = re.search(r"<!--s-data:(.*?)-->", html, re.DOTALL)
    if not match:
        return [{"error": "baidu: data block not found"}]

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return [{"error": "baidu: json parse error"}]

    results = []
    for card in data.get("data", {}).get("cards", []):
        for item in card.get("content", []):
            query = item.get("query", item.get("word", ""))
            if not query or query == "查看更多":
                continue
            try:
                heat_val = int(item.get("hotScore", 0))
            except (ValueError, TypeError):
                heat_val = 0
            results.append({
                "title": query,
                "heat": heat_val,
                "desc": item.get("desc", ""),
                "url": item.get("url", item.get("appUrl", "")),
                "source": "baidu",
            })
    return results


# ============================================================
# Data source: Bilibili 热门视频
# ============================================================
def fetch_bilibili_popular(page: int = 1, page_size: int = 20) -> list[dict]:
    """Fetch Bilibili popular videos."""
    url = f"https://api.bilibili.com/x/web-interface/popular?pn={page}&ps={page_size}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return [{"error": f"bilibili: {e}"}]

    if data.get("code") != 0:
        return [{"error": f"bilibili: code={data.get('code')}"}]

    results = []
    for video in data.get("data", {}).get("list", []):
        stat = video.get("stat", {})
        owner = video.get("owner", {})
        results.append({
            "title": video.get("title", ""),
            "desc": video.get("desc", ""),
            "url": f"https://www.bilibili.com/video/{video.get('bvid', '')}",
            "play": stat.get("view", 0),
            "danmaku": stat.get("danmaku", 0),
            "reply": stat.get("reply", 0),
            "favorite": stat.get("favorite", 0),
            "coin": stat.get("coin", 0),
            "share": stat.get("share", 0),
            "like": stat.get("like", 0),
            "author": owner.get("name", ""),
            "source": "bilibili",
        })
    return results


# ============================================================
# Data source: GitHub 趋势仓库 (via REST API)
# ============================================================
def fetch_github_trending(
    days: int = 7, limit: int = 20, token: Optional[str] = None
) -> list[dict]:
    """Fetch trending GitHub repos in the last N days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    query = f"created:>{since}"
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={limit}"

    headers = {
        "User-Agent": UA,
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return [{"error": f"github: {e}"}]

    results = []
    for repo in data.get("items", []):
        results.append({
            "full_name": repo.get("full_name", ""),
            "description": (repo.get("description") or "")[:200],
            "url": repo.get("html_url", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language", ""),
            "topics": repo.get("topics", [])[:5],
            "created": repo.get("created_at", ""),
            "pushed": repo.get("pushed_at", ""),
            "source": "github",
        })
    return results


# ============================================================
# Data source: 权威媒体 RSS (人民日报、新华社)
# ============================================================
RSS_FEEDS = [
    ("people", "人民日报", "http://www.people.com.cn/rss/politics.xml"),
    ("xinhua", "新华社", "http://www.news.cn/politics/xhll.xml"),
]

def fetch_rss_news() -> list[dict]:
    """Fetch top news from authoritative Chinese media RSS feeds."""
    results = []
    for sid, name, url in RSS_FEEDS:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_text = resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            results.append({"error": f"RSS {sid}: {e}", "source": sid})
            continue

        # Simple regex-based RSS parse
        items = re.findall(r"<item>(.*?)</item>", xml_text, re.DOTALL)
        for item in items[:15]:
            # Handle both CDATA and plain text titles
            title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", item, re.DOTALL)
            link_m = re.search(r"<link>(.*?)</link>", item)
            desc_m = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", item, re.DOTALL)
            pubdate_m = re.search(r"<pubDate>(.*?)</pubDate>", item)
            if title_m:
                title = title_m.group(1).strip()
                results.append({
                    "title": title,
                    "url": link_m.group(1) if link_m else "",
                    "desc": (desc_m.group(1)[:200].strip() if desc_m else ""),
                    "pubdate": pubdate_m.group(1) if pubdate_m else "",
                    "source": sid,
                    "source_name": name,
                })
    return results


# ============================================================
# Heat scoring & ranking
# ============================================================
def compute_cross_source_heat(results: dict[str, list[dict]]) -> list[dict]:
    """
    Normalize heat across sources and produce a unified ranked list.
    Each source has its own engagement metric:
      - weibo: raw_hot (already a heat index)
      - baidu: hotScore
      - bilibili: play + danmaku*10 + like*3 + coin*5
      - github: stars
      - news (people/xinhua): no heat (editorial, by pubdate)
    """
    unified = []

    # Weibo
    for item in results.get("weibo", []):
        if "error" in item:
            continue
        unified.append({
            "title": item["title"],
            "url": item["url"],
            "source": "微博",
            "source_icon": "🧣",
            "heat_raw": item.get("heat", 0),
            "heat_normalized": 0,  # computed below
            "rank": item.get("rank", 0),
        })

    # Baidu
    for item in results.get("baidu", []):
        if "error" in item:
            continue
        unified.append({
            "title": item["title"],
            "url": item["url"],
            "source": "百度",
            "source_icon": "🔍",
            "heat_raw": item.get("heat", 0),
            "heat_normalized": 0,
            "desc": item.get("desc", ""),
        })

    # Bilibili
    for item in results.get("bilibili", []):
        if "error" in item:
            continue
        # Composite engagement score
        score = (
            item.get("play", 0)
            + item.get("danmaku", 0) * 10
            + item.get("like", 0) * 3
            + item.get("coin", 0) * 5
        )
        unified.append({
            "title": item["title"],
            "url": item["url"],
            "source": "B站",
            "source_icon": "📺",
            "heat_raw": score,
            "heat_normalized": 0,
            "sub_text": f"{item.get('author', '')} | ▶️{item.get('play',0)} 💬{item.get('danmaku',0)}",
        })

    # GitHub
    for item in results.get("github", []):
        if "error" in item:
            continue
        unified.append({
            "title": item["full_name"],
            "url": item["url"],
            "source": "GitHub",
            "source_icon": "⭐",
            "heat_raw": item.get("stars", 0),
            "heat_normalized": 0,
            "sub_text": f"⭐{item.get('stars',0)} {item.get('language','')}",
            "desc": item.get("description", ""),
        })

    # News RSS (no heat signal, informational)
    for item in results.get("news", []):
        if "error" in item:
            continue
        unified.append({
            "title": item["title"],
            "url": item["url"],
            "source": item.get("source_name", "官媒"),
            "source_icon": "📰",
            "heat_raw": 0,  # no community heat
            "heat_normalized": 0,
            "desc": item.get("desc", ""),
        })

    # Normalize: z-score per-source then merge
    if unified:
        # Only normalize for items with >0 heat
        heats = [h["heat_raw"] for h in unified if h["heat_raw"] > 0]
        if heats:
            max_h = max(heats)
            min_h = min(heats)
            rng = max_h - min_h or 1
            for item in unified:
                if item["heat_raw"] > 0:
                    item["heat_normalized"] = round((item["heat_raw"] - min_h) / rng * 100, 1)
                else:
                    item["heat_normalized"] = 0

        unified.sort(key=lambda x: x["heat_normalized"], reverse=True)

    return unified


# ============================================================
# Output formatters
# ============================================================
def format_compact(results: dict[str, list[dict]], unified: list[dict]) -> str:
    """Compact AI-ready output format."""
    now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    lines = [f"🌐 cn30days v{VERSION} · synced {now}", ""]

    # Summary counts
    total = len(unified)
    sources = set(item["source"] for item in unified)
    error_sources = [k for k, v in results.items() if v and "error" in v[0]]
    ok_sources = [k for k in results if k not in error_sources and results[k] and "error" not in results[k][0]]

    lines.append(f"## 数据采集报告")
    lines.append(f"**已采集 {total} 条**，来自 {', '.join(ok_sources)}")
    if error_sources:
        lines.append(f"**失败**: {', '.join(error_sources)}")
    lines.append("")

    # Top 20 unified
    lines.append("## 🔥 综合热度 Top 20")
    lines.append("")
    for i, item in enumerate(unified[:20], 1):
        icon = item["source_icon"]
        src = item["source"]
        heat = item["heat_normalized"]
        sub = item.get("sub_text", "")
        desc = item.get("desc", "")
        line = f"{i:2d}. {icon} [{src}] {item['title']}"
        if sub:
            line += f" — {sub}"
        if heat > 0:
            line += f" [热度:{heat:.0f}]"
        lines.append(line)
        if desc:
            lines.append(f"    {desc[:100]}")

    lines.append("")

    # Per-source details
    for source_key in ["weibo", "baidu", "bilibili", "github", "news"]:
        items = results.get(source_key, [])
        if not items or "error" in items[0]:
            lines.append(f"## {source_key}: ❌ 数据源不可用")
            if items and "error" in items[0]:
                lines.append(f"  {items[0]['error']}")
            lines.append("")
            continue

        labels = {
            "weibo": "🧣 微博热搜",
            "baidu": "🔍 百度热搜",
            "bilibili": "📺 B站热门",
            "github": "⭐ GitHub 趋势",
            "news": "📰 权威媒体",
        }
        lines.append(f"## {labels.get(source_key, source_key)} ({len(items)} items)")
        lines.append("")
        for item in items[:10]:
            if source_key == "weibo":
                lines.append(f"  [{item.get('rank',0)}] {item['title']} 🔥{item.get('heat',0)}")
            elif source_key == "baidu":
                lines.append(f"  {item['title']} 🔥{item.get('heat',0)}")
            elif source_key == "bilibili":
                lines.append(f"  {item['title'][:60]}")
                lines.append(f"  ▶️{item.get('play',0)} 💬{item.get('danmaku',0)} 👍{item.get('like',0)} — {item.get('author','')}")
            elif source_key == "github":
                desc = item.get("description", "")[:80]
                lines.append(f"  {item['full_name']} ⭐{item.get('stars',0)}")
                if desc:
                    lines.append(f"  {desc}")
            elif source_key == "news":
                lines.append(f"  [{item.get('source_name','')}] {item['title'][:60]}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"✅ cn30days engine v{VERSION} | {total} results | {datetime.now(BEIJING_TZ).strftime('%H:%M:%S')} CST")
    source_tree = []
    for s in ok_sources:
        item_count = len([x for x in unified if x["source_icon"] == ({"weibo":"🧣","baidu":"🔍","bilibili":"📺","github":"⭐","news":"📰"}.get(s, "?"))]) or len(results.get(s, []))
        source_tree.append(f"├── {s} ({item_count} items)")
    source_tree_final = "\n".join(source_tree).replace("├──", "└──", -1).replace("\n└──", "\n├──", 1) if len(source_tree) == 1 else "\n".join(source_tree)
    lines.append(f"├── Sources:\n{source_tree_final}")
    lines.append("")

    return "\n".join(lines)


def format_json(results: dict[str, list[dict]], unified: list[dict]) -> str:
    """Full JSON output."""
    return json.dumps({
        "version": VERSION,
        "timestamp": datetime.now(BEIJING_TZ).isoformat(),
        "total": len(unified),
        "sources": {k: len(v) for k, v in results.items()},
        "unified": unified,
        "raw": results,
    }, ensure_ascii=False, indent=2)


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="cn30days — Chinese internet cross-source heat aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cn30days.py                          # fetch all sources, compact output
  python3 cn30days.py --emit json              # full JSON output
  python3 cn30days.py --sources weibo,baidu    # specific sources only
  python3 cn30days.py --days 14                 # wider time window for GitHub
        """,
    )
    parser.add_argument("--emit", choices=["compact", "json"], default="compact",
                        help="Output format (default: compact for AI synthesis)")
    parser.add_argument("--sources", default="weibo,baidu,bilibili,github,news",
                        help="Comma-separated source list")
    parser.add_argument("--topic", default="",
                        help="Filter results by keyword/topic (e.g. 'AI', '高考', '考研')")
    parser.add_argument("--days", type=int, default=7,
                        help="Days to look back for time-based sources (default: 7)")
    parser.add_argument("--version", action="version", version=f"cn30days v{VERSION}")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",")]
    token = os.environ.get("GITHUB_TOKEN", os.environ.get("GITHUB_STARYFALL_TOKEN"))

    fetchers = {
        "weibo": fetch_weibo_hot,
        "baidu": fetch_baidu_hot,
        "bilibili": fetch_bilibili_popular,
        "github": lambda: fetch_github_trending(days=args.days, token=token),
        "news": fetch_rss_news,
    }

    results: dict[str, list[dict]] = {}

    # Concurrent fetch
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for src in sources:
            if src in fetchers:
                futures[executor.submit(fetchers[src])] = src

        for future in as_completed(futures):
            src = futures[future]
            try:
                results[src] = future.result()
            except Exception as e:
                results[src] = [{"error": f"{src}: {e}"}]

    unified = compute_cross_source_heat(results)

    # Topic filter: multi-strategy keyword match with topic expansion
    topic = (args.topic or "").strip()
    if topic:
        # Expand topic to related keywords (AI → AI, 人工智能, 大模型, ChatGPT, etc.)
        keywords = expand_topic(topic)
        # Also include single-word components of the original query
        extra = [w.strip().lower() for w in topic.split() if w.strip()]
        keywords = list(set(keywords + extra))

        filtered = []
        for item in unified:
            title = item.get("title", "").lower()
            desc = item.get("desc", "").lower()
            sub = item.get("sub_text", "").lower()
            text = f"{title} {desc} {sub}"

            if any(kw in text for kw in keywords):
                filtered.append(item)

        unified = filtered

    if args.emit == "json":
        print(format_json(results, unified))
    else:
        print(format_compact(results, unified))


if __name__ == "__main__":
    main()
