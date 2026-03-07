"""Tests for LanguageDetector."""

from pathlib import Path
from git_deep_analyzer.language.detector import LanguageDetector
import pytest


@pytest.mark.unit
class TestLanguageDetector:
    """测试LanguageDetector"""

    def test_detect_cpp_file(self):
        """测试检测C++文件"""
        # Given
        detector = LanguageDetector()
        file_path = Path("test.cpp")

        # When
        lang = detector.detect(file_path)

        # Then
        assert lang == "cpp"

    def test_detect_python_file(self):
        """测试检测Python文件"""
        # Given
        detector = LanguageDetector()
        file_path = Path("test.py")

        # When
        lang = detector.detect(file_path)

        # Then
        assert lang == "python"

    def test_detect_python_with_content(self):
        """测试使用shebang检测Python"""
        # Given
        detector = LanguageDetector()
        content = "#!/usr/bin/env python3\nprint('hello')"
        file_path = Path("script")

        # When
        lang = detector.detect(file_path, content)

        # Then
        assert lang == "python"

    def test_detect_unknown_file(self):
        """测试检测未知语言"""
        # Given
        detector = LanguageDetector()
        file_path = Path("test.unknown")

        # When
        lang = detector.detect(file_path)

        # Then
        assert lang == "unknown"

    @pytest.mark.parametrize("filename,expected", [
        ("test.cpp", "cpp"),
        ("test.py", "python"),
        ("test.ts", "typescript"),
        ("test.go", "go"),
        ("test.rs", "rust"),
        ("test.java", "java"),
        ("test.js", "javascript"),
        ("test.html", "html"),
        ("test.css", "css"),
        ("test.sql", "sql"),
        ("test.sh", "shell"),
    ])
    def test_detect_various_languages(self, filename, expected):
        """测试检测各种语言"""
        # Given
        detector = LanguageDetector()
        file_path = Path(filename)

        # When
        lang = detector.detect(file_path)

        # Then
        assert lang == expected

    def test_detect_project_languages(self, temp_dir):
        """测试检测项目语言"""
        # Given
        detector = LanguageDetector()
        (temp_dir / "test.py").write_text("print('hello')")
        (temp_dir / "test.cpp").write_text("int main() {}")
        (temp_dir / "test2.py").write_text("# another python file")
        # 创建.git目录以跳过
        (temp_dir / ".git").mkdir()

        # When
        languages = detector.detect_project_languages(temp_dir)

        # Then
        assert isinstance(languages, dict)
        assert "python" in languages
        assert "cpp" in languages
        assert languages["python"] == 2  # 2个python文件
        assert languages["cpp"] == 1

    def test_detect_empty_content(self, temp_dir):
        """测试检测空内容文件"""
        # Given
        detector = LanguageDetector()
        file_path = temp_dir / "test.unknown"
        content = ""

        # When
        lang = detector.detect(file_path, content)

        # Then
        assert lang == "unknown"

    def test_detect_case_insensitive_extension(self):
        """测试扩展名检测不区分大小写"""
        # Given
        detector = LanguageDetector()
        file_path = Path("TEST.PY")

        # When
        lang = detector.detect(file_path)

        # Then
        assert lang == "python"

    @pytest.mark.parametrize("shebang,expected", [
        ("#!/usr/bin/env python", "python"),
        ("#!/usr/bin/python", "python"),
        ("#!/usr/bin/env python3", "python"),
        ("#!/bin/bash", "shell"),
        ("#!/usr/bin/env bash", "shell"),
        ("#!/bin/sh", "shell"),
    ])
    def test_detect_by_shebang(self, shebang, expected):
        """测试通过shebang检测语言"""
        # Given
        detector = LanguageDetector()
        content = f"{shebang}\nprint('hello')"
        file_path = Path("script")

        # When
        lang = detector.detect(file_path, content)

        # Then
        assert lang == expected

    def test_detect_without_content(self, temp_dir):
        """测试没有content时仅使用扩展名"""
        # Given
        detector = LanguageDetector()
        file_path = temp_dir / "test.cpp"

        # When
        lang = detector.detect(file_path, content=None)

        # Then
        assert lang == "cpp"

    def test_detect_project_with_single_file(self, temp_dir):
        """测试检测单个文件的项目"""
        # Given
        detector = LanguageDetector()
        (temp_dir / "main.py").write_text("print('main')")

        # When
        languages = detector.detect_project_languages(temp_dir)

        # Then
        assert isinstance(languages, dict)
        assert "python" in languages
        assert languages["python"] == 1
        assert len([k for k, v in languages.items() if v > 0]) == 1
