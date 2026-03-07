"""C++ code parser - simplified version using libclang."""

import subprocess
import json
from typing import Dict
from pathlib import Path
from .base import BaseParser


class CppParser(BaseParser):
    """C++代码解析器 - 使用libclang"""

    def __init__(self, config: dict = None):
        """初始化C++解析器"""
        self.clang_path = config.get("clang_path", "clang") if config else "clang"
        self.cpp_std = config.get("cpp_std", "17") if config else "17"

    def parse_file(self, file_path: str) -> Dict:
        """解析C++文件"""
        result = {
            "language": "cpp",
            "functions": [],
            "classes": [],
            "imports": []
        }

        try:
            ast_json = self._get_clang_ast(file_path)
            if ast_json:
                result["functions"] = self._extract_functions(ast_json)
                result["classes"] = self._extract_classes(ast_json)
                result["imports"] = self._extract_includes(ast_json)
        except Exception as e:
            raise RuntimeError(f"Failed to parse C++ file: {e}") from e

        return result

    def _get_clang_ast(self, file_path: str) -> dict:
        """使用clang获取JSON AST"""
        cmd = [
            self.clang_path,
            "-Xclang", "-ast-dump=json",
            f"-std=c++{self.cpp_std}",
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"Clang failed: {result.stderr}")
        
        return json.loads(result.stdout)

    def extract_functions(self, ast_json: dict) -> list:
        """从AST提取函数（简化版）"""
        # 简化实现：扫描kind为FunctionDecl的节点
        functions = []
        
        def traverse(node):
            if isinstance(node, dict):
                kind = node.get("kind")
                if kind == "FunctionDecl" and node.get("name"):
                    functions.append({
                        "name": node["name"],
                        "lineno": node.get("loc", {}).get("offsetLine", 0),
                        "return_type": self._get_type_name(node.get("type", {}))
                    })
                for child in node.get("inner", []):
                    traverse(child)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(ast_json)
        return functions

    def extract_classes(self, ast_json: dict) -> list:
        """从AST提取类（简化版）"""
        classes = []
        
        def traverse(node):
            if isinstance(node, dict):
                kind = node.get("kind")
                if kind == "CXXRecordDecl" and node.get("name"):
                    classes.append({
                        "name": node["name"],
                        "lineno": node.get("loc", {}).get("offsetLine", 0),
                        "bases": [self._get_type_name(b) for b in node.get("bases", [])]
                    })
                for child in node.get("inner", []):
                    traverse(child)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(ast_json)
        return classes

    def extract_imports(self, ast_json: dict) -> list:
        """从AST提取导入（简化版）"""
        # 简化实现：扫描InclusionDirective
        imports = []
        
        def traverse(node):
            if isinstance(node, dict):
                kind = node.get("kind")
                if kind == "InclusionDirective":
                    included_file = node.get("includedFile", "")
                    if included_file and "<" not in included_file:
                        imports.append(included_file)
                for child in node.get("inner", []):
                    traverse(child)
            elif isinstance(node, list):
                for item in node:
                    traverse(item)
        
        traverse(ast_json)
        return imports

    def _get_type_name(self, type_node: dict) -> str:
        """获取类型名称"""
        if not isinstance(type_node, dict):
            return str(type_node)
        return type_node.get("qualType", type_node.get("name", "unknown"))

    # BaseParser abstract methods
    def extract_functions(self, code: str) -> list:
        return self.extract_functions(json.loads(code))

    def extract_classes(self, code: str) -> list:
        return self.extract_classes(json.loads(code))

    def extract_imports(self, code: str) -> list:
        return self.extract_imports(json.loads(code))
