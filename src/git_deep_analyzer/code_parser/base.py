"""Base parser for code analysis."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseParser(ABC):
    """代码解析器基类"""

    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析文件

        Args:
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        pass

    @abstractmethod
    def extract_functions(self, code: str) -> List[Dict]:
        """提取函数

        Args:
            code: 代码内容

        Returns:
            List[Dict]: 函数列表
        """
        pass

    @abstractmethod
    def extract_classes(self, code: str) -> List[Dict]:
        """提取类

        Args:
            code: 代码内容

        Returns:
            List[Dict]: 类列表
        """
        pass

    @abstractmethod
    def extract_imports(self, code: str) -> List[str]:
        """提取导入

        Args:
            code: 代码内容

        Returns:
            List[str]: 导入列表
        """
        pass
