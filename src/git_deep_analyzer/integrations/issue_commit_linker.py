"""Issue and Commit linker."""

import re
from typing import List, Dict
from datetime import datetime


class IssueCommitLinker:
    """Issue与Commit关联器"""

    def __init__(self, config: dict):
        self.config = config
        self.patterns = self._build_patterns(config)

    def link(self, issues: List, commits: List) -> Dict[str, List]:
        """关联Issue和Commit（基于提交消息）- 策略A"""
        # 构建Issue key映射
        issue_map = {issue.key: issue for issue in issues}
        links = {issue.key: [] for issue in issues}

        # 遍历提交，匹配Issue
        for commit in commits:
            issue_keys = self._extract_issue_keys(commit.message)
            for issue_key in issue_keys:
                if issue_key in issue_map:
                    links[issue_key].append(commit)

        return links

    def _build_patterns(self, config: dict) -> List[str]:
        """构建Issue匹配模式"""
        # 默认模式
        default_patterns = [
            r'(?:fixes?|closes?|resolves?|references?|refs?|related to)\s+([A-Z]+-\d+)',
            r'([A-Z]+-\d+)',
            r'\[([A-Za-z]+-\d+)\]',
        ]

        # 自定义模式
        custom_patterns = config.get("issue_patterns", [])

        return default_patterns + custom_patterns

    def _extract_issue_keys(self, message: str) -> List[str]:
        """从提交消息中提取Issue key"""
        issue_keys = set()

        for pattern in self.patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # 处理不同capture组
                if isinstance(match, tuple):
                    for m in match:
                        if m and '-' in m:
                            issue_keys.add(m)
                elif isinstance(match, str):
                    if '-' in match:
                        issue_keys.add(match)

        return list(issue_keys)
