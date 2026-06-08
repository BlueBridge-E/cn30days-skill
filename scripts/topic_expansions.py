#!/usr/bin/env python3
"""
Semantic keyword expansion for cn30days topic search.
Maps short topics to expanded keyword sets for Chinese internet coverage.
"""

# Each topic maps to a list of related keywords
# Order: primary first, then synonyms, then related terms
TOPIC_EXPANSIONS: dict[str, list[str]] = {
    # AI & Tech
    "ai": ["ai", "人工智能", "大模型", "chatgpt", "claude", "gpt", "深度学习",
           "机器学习", "agent", "智能", "openai", "gemini", "llm", "推理",
           "cursor", "copilot", "skill", "prompt", "token"],
    "大模型": ["大模型", "llm", "ai", "人工智能", "gpt", "claude", "deepseek",
              "千问", "文心", "混元", "token", "开源模型"],
    "deepseek": ["deepseek", "深度求索", "ds", "deep seek"],
    "gpt": ["gpt", "chatgpt", "openai", "claude", "大模型", "ai"],
    "agent": ["agent", "智能体", "ai agent", "skill", "mcp", "function call",
              "tool use", "自主", "多模态agent", "浏览器agent"],

    # Exams
    "考研": ["考研", "研究生", "硕士", "22408", "408", "调剂", "国家线",
             "复试", "初试", "二战", "上岸", "备考", "自习"],
    "高考": ["高考", "高考加油", "高考物理", "高考历史", "高考数学", "考生",
             "2026高考", "估分", "志愿", "分数线", "录取"],
    "考公": ["考公", "公务员", "国考", "省考", "申论", "行测", "编制"],

    # Jobs & economy
    "就业": ["就业", "失业", "裁员", "招聘", "找工作", "应届", "校招",
             "社招", "外包", "降薪", "跳槽", "offer", "大厂"],
    "经济": ["经济", "gdp", "通胀", "cpi", "ppi", "制造业", "消费",
             "出口", "贸易", "关税", "制裁", "产业"],

    # Sectors
    "房价": ["房价", "房地产", "楼市", "买房", "房贷", "首付", "利率",
             "限购", "二手房", "新房", "开发商", "恒大", "碧桂园",
             "土地", "库存"],
    "股市": ["股市", "a股", "上证", "深证", "创业板", "牛市", "熊市",
             "ipo", "量化", "etf", "基金"],
    "新能源": ["新能源", "电动车", "电池", "光伏", "风电", "储能",
              "锂电池", "钠电池", "宁德时代", "比亚迪", "充电"],

    # Tech Stack
    "rust": ["rust", "rust语言", "cargo", "wasm", "系统编程"],
    "python": ["python", "pandas", "django", "fastapi", "pytorch", "tensorflow"],
    "前端": ["前端", "react", "vue", "typescript", "javascript", "css", "html",
             "nextjs", "astro", "tailwind", "组件"],
    "区块链": ["区块链", "bitcoin", "ethereum", "eth", "btc", "加密", "web3",
              "defi", "nft", "solana", "跨链", "layer2"],
}


def expand_topic(topic: str) -> list[str]:
    """Expand a topic string into a list of search keywords.
    Returns the original topic as the only keyword if no expansion exists.
    """
    key = topic.strip().lower()
    if key in TOPIC_EXPANSIONS:
        return TOPIC_EXPANSIONS[key]
    # Also check partial matches (e.g. "AI agent" → "agent")
    words = key.split()
    expanded = set(words)
    for w in words:
        if w in TOPIC_EXPANSIONS:
            expanded.update(TOPIC_EXPANSIONS[w])
    return list(expanded)
