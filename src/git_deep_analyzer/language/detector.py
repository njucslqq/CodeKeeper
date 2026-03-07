"""Language detector for identifying programming languages."""

from pathlib import Path
from typing import Optional


class LanguageDetector:
    """语言检测器"""

    EXTENSIONS = {
        "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".c"],
        "python": [".py", ".pyw", ".pyi"],
        "java": [".java", ".class"],
        "javascript": [".js", ".jsx", ".mjs", ".cjs"],
        "typescript": [".ts", ".tsx"],
        "go": [".go"],
        "rust": [".rs"],
        "c": [".c", ".h"],
        "csharp": [".cs"],
        "ruby": [".rb"],
        "php": [".php"],
        "swift": [".swift"],
        "kotlin": [".kt", ".kts"],
        "scala": [".scala"],
        "r": [".r", ".R"],
        "shell": [".sh", ".bash", ".zsh", ".fish"],
        "sql": [".sql"],
        "html": [".html", ".htm", ".xhtml"],
        "css": [".css", ".scss", ".sass", ".less"],
        "json": [".json"],
        "yaml": [".yaml", ".yml"],
        "xml": [".xml"],
        "markdown": [".md", ".markdown"],
    }

    SHEBANG_PATTERNS = {
        "python": [
            ("#!/usr/bin/env python", "#!/usr/bin/python"),
            ("#!/usr/bin/env python3", "#!/usr/bin/python3"),
        ],
        "shell": [
            ("#!/bin/bash", "#!/usr/bin/env bash"),
            ("#!/bin/sh", "#!/usr/bin/env sh"),
            ("#!/bin/zsh", "#!/usr/bin/env zsh"),
        ],
    }

    def __init__(self):
        """初始化语言检测器"""
        pass

    def detect(self, file_path: Path, content: Optional[str] = None) -> str:
        """检测文件语言

        Args:
            file_path: 文件路径
            content: 文件内容（可选）

        Returns:
            str: 语言名称（"unknown"如果无法识别）
        """
        # 方法1: 扩展名检测
        lang = self._detect_by_extension(file_path)
        if lang != "unknown":
            return lang

        # 方法2: Shebang检测（需要content）
        if content:
            lang = self._detect_by_shebang(content)
            if lang != "unknown":
                return lang

        return "unknown"

    def _detect_by_extension(self, file_path: Path) -> str:
        """根据扩展名检测语言"""
        ext = file_path.suffix.lower()

        for lang, extensions in self.EXTENSIONS.items():
            if ext in extensions:
                return lang

        return "unknown"

    def _detect_by_shebang(self, content: str) -> str:
        """根据shebang检测语言"""
        # 获取第一行
        first_line = content.split("\n")[0] if content else ""

        for lang, patterns in self.SHEBANG_PATTERNS.items():
            for pattern_pair in patterns:
                if first_line.startswith(pattern_pair[0]) or first_line.startswith(pattern_pair[1]):
                    return lang

        return "unknown"

    def detect_project_languages(self, repo_path: Path) -> dict:
        """检测项目的主要语言

        Args:
            repo_path: Git仓库路径

        Returns:
            dict: 语言统计字典 {语言名称: 文件数量}
        """
        languages = {}

        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                # 跳过git目录
                if ".git" in str(file_path):
                    continue

                lang = self.detect(file_path)
                languages[lang] = languages.get(lang, 0) + 1

        # 按文件数量降序排序
        sorted_languages = {
            k: v for k, v in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        }

        return sorted_languages
