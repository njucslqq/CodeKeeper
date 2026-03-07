"""Tests for code parsers."""

from pathlib import Path
from git_deep_analyzer.code_parser import PythonParser
import pytest


@pytest.mark.unit
class TestPythonParser:
    """测试PythonParser"""

    def test_parse_simple_file(self, temp_dir):
        """测试解析简单Python文件"""
        # Given
        parser = PythonParser()
        test_file = temp_dir / "test.py"
        test_file.write_text("""
def hello():
    print('hello')

class MyClass:
    pass
""")

        # When
        result = parser.parse_file(str(test_file))

        # Then
        assert result["language"] == "python"
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "hello"
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "MyClass"

    def test_extract_functions(self):
        """测试提取函数"""
        # Given
        parser = PythonParser()
        code = """
def func1(x):
    return x + 1

async def async_func():
    await something()

@decorator
def decorated_func():
    pass
"""

        # When
        functions = parser.extract_functions(code)

        # Then
        assert len(functions) == 3
        assert functions[0]["name"] == "func1"
        assert functions[1]["is_async"] is True
        assert functions[2]["decorators"] == ["decorator"]

    def test_extract_classes(self):
        """测试提取类"""
        # Given
        parser = PythonParser()
        code = """
class BaseClass:
    pass

class DerivedClass(BaseClass):
    def method1(self):
        pass
"""

        # When
        classes = parser.extract_classes(code)

        # Then
        assert len(classes) == 2
        assert classes[0]["name"] == "BaseClass"
        assert classes[1]["name"] == "DerivedClass"
        assert "BaseClass" in classes[1]["bases"]

    def test_extract_imports(self):
        """测试提取导入"""
        # Given
        parser = PythonParser()
        code = """
import os
import sys
from pathlib import Path
import json
from collections import defaultdict
"""

        # When
        imports = parser.extract_imports(code)

        # Then
        assert "os" in imports
        assert "sys" in imports
        assert "Path" in imports
        assert "json" in imports
        assert "defaultdict" in imports
