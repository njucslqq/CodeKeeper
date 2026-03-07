"""Concurrency detector - simplified version."""

from typing import Dict, List


class ConcurrencyDetector:
    """并发代码检测器"""

    KEYWORDS = {
        "cpp": {
            "threads": ["thread", "pthread", "std::thread"],
            "locks": ["mutex", "lock", "unique_lock", "shared_lock", "rwlock"],
            "async": ["future", "promise", "async", "await"],
            "atomic": ["atomic", "memory_order"],
            "memory_barriers": ["std::atomic_thread_fence", "memory_order_acq_rel"],
            "volatile": ["volatile"],
            "thread_local": ["thread_local", "__thread"],
            "condition_variables": ["condition_variable", "cv", "notify", "wait"]
        },
        "python": {
            "threads": ["Thread", "threading"],
            "locks": ["Lock", "RLock", "Semaphore"],
            "async": ["async", "await", "asyncio", "coroutine"],
            "atomic": [],  # Python没有原生atomic
            "memory_barriers": [],
            "volatile": [],
            "thread_local": ["threading.local"],
            "condition_variables": ["Condition", "threading.Condition", "notify", "wait"]
        }
    }

    def __init__(self, language: str):
        self.language = language

    def detect(self, code: str, language: str = None) -> Dict:
        """检测并发特征"""
        lang = language or self.language
        keywords = self.KEYWORDS.get(lang, {})
        
        return {
            "threads": self._find_keywords(code, keywords.get("threads", [])),
            "locks": self._find_keywords(code, keywords.get("locks", [])),
            "async": self._find_keywords(code, keywords.get("async", [])),
            "atomic": self._find_keywords(code, keywords.get("atomic", [])),
            "memory_barriers": self._find_keywords(code, keywords.get("memory_barriers", [])),
            "volatile": self._find_keywords(code, keywords.get("volatile", [])),
            "thread_local": self._find_keywords(code, keywords.get("thread_local", [])),
            "condition_variables": self._find_keywords(code, keywords.get("condition_variables", []))
        }

    def _find_keywords(self, code: str, keywords: List[str]) -> List[str]:
        """查找关键词"""
        found = []
        code_lower = code.lower()
        
        for kw in keywords:
            if kw.lower() in code_lower:
                found.append(kw)
        
        return found
