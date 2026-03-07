"""Design pattern matcher - simplified version."""

from typing import List, Dict


class PatternMatcher:
    """设计模式匹配器 - 启发式"""

    PATTERNS = {
        "cpp": {
            "singleton": [
                "private.*constructor",
                "static.*instance",
                "getInstance"
            ],
            "factory": [
                "create.*method",
                "factory.*method",
                "virtual"
            ],
            "observer": [
                "notify",
                "subscribe",
                "observer",
                "listener"
            ]
        },
        "python": {
            "singleton": [
                "__new__",
                "_instance",
                "classmethod"
            ],
            "factory": [
                "create",
                "factory",
                "@classmethod"
            ],
            "decorator": [
                "@",
                "wrapper",
                "enhance"
            ]
        }
    }

    def __init__(self, language: str):
        self.language = language

    def match(self, code: str, language: str = None) -> List[Dict]:
        """匹配设计模式（启发式）"""
        lang = language or self.language
        matched = []

        patterns = self.PATTERNS.get(lang, {})

        for pattern_name, keywords in patterns.items():
            if self._matches_any(code, keywords):
                matched.append({
                    "name": pattern_name,
                    "type": "unknown",
                    "confidence": 0.7  # 启发式匹配置信度
                })

        return matched

    def _matches_any(self, code: str, keywords: List[str]) -> bool:
        """检查是否匹配任意关键词"""
        code_lower = code.lower()
        return any(kw.lower() in code_lower for kw in keywords)
