"""Python code parser using AST."""

import ast
from typing import List, Dict, Any
from pathlib import Path
from .base import BaseParser


class PythonParser(BaseParser):
    """Python代码解析器 - 使用ast模块"""

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)

        return {
            "language": "python",
            "functions": self.extract_functions(code, tree),
            "classes": self.extract_classes(code, tree),
            "imports": self.extract_imports(code, tree)
        }

    def extract_functions(self, code: str, tree=None) -> List[Dict]:
        """提取函数"""
        if tree is None:
            tree = ast.parse(code)

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    "args": [a.arg for a in node.args.args],
                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                })
        return functions

    def extract_classes(self, code: str, tree=None) -> List[Dict]:
        """提取类"""
        if tree is None:
            tree = ast.parse(code)

        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "bases": [self._get_base_name(b) for b in node.bases],
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
        return classes

    def extract_imports(self, code: str, tree=None) -> List[str]:
        """提取导入"""
        if tree is None:
            tree = ast.parse(code)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _get_base_name(self, base):
        """获取基类名称"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return str(base)
