BLOOM_KEYWORDS: dict[str, list[str]] = {
    "remember": ["define", "list", "recall", "name", "identify", "state"],
    "understand": ["explain", "summarise", "summarize", "describe", "discuss", "interpret"],
    "apply": ["solve", "use", "calculate", "apply", "demonstrate", "compute"],
    "analyse": ["compare", "contrast", "examine", "analyse", "analyze", "differentiate"],
    "evaluate": ["judge", "argue", "defend", "evaluate", "justify", "critique"],
    "create": ["design", "build", "create", "construct", "formulate", "devise"],
}

DEFAULT_LEVEL = "understand"


def tag_bloom_level(text: str) -> str:
    lower_text = text.lower()

    for level, keywords in BLOOM_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            return level

    return DEFAULT_LEVEL
