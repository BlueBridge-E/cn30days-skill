# cn30days — Project Rules

## Architecture

```
cn30days-skill/
├── scripts/
│   └── cn30days.py         # Python engine — multi-source data fetcher
├── skills/
│   └── cn30days/
│       └── SKILL.md         # AI agent skill spec
├── README.md
├── AGENTS.md                # This file
└── LICENSE
```

## Development Rules

1. **Python only, no external deps.** The engine uses only stdlib (`urllib`, `json`, `argparse`, `concurrent.futures`, `re`). No `pip install` needed.
2. **Zero-config first.** Default sources must work without any API keys or auth.
3. **Concurrent fetch.** All sources fetched in parallel via `ThreadPoolExecutor`.
4. **Graceful degradation.** If a source fails, mark it as error and continue with others.
5. **Output formats.** `compact` (AI synthesis) and `json` (programmatic) only.

## Adding a New Source

1. Add a `fetch_<source>()` function in `cn30days.py`
2. Register it in the `fetchers` dict in `main()`
3. Add heat normalization logic in `compute_cross_source_heat()`
4. Add compact output formatting in `format_compact()`
5. Update SKILL.md source table
6. Update README.md source table

## Source Criteria

- ✅ Public API or scrapeable with no auth
- ✅ Accessible from mainland China
- ✅ Has community engagement signal (likes, views, stars, etc.)
- ❌ Requires complex anti-bot bypass
- ❌ Blocked by GFW

## Testing

```bash
# Full test
source ~/.openclaw/workspace/.secure/github-tokens.sh
python3 scripts/cn30days.py

# Single source test
python3 scripts/cn30days.py --sources weibo

# JSON output test
python3 scripts/cn30days.py --emit json | python3 -m json.tool > /dev/null && echo "OK"
```
