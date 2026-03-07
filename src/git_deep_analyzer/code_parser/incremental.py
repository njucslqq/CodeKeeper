"""Incremental analyzer - simplified version."""

from pathlib import Path
from typing import Dict, List


class IncrementalAnalyzer:
    """增量分析器 - 基于文件内容哈希"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index = self._load_index()

    def should_analyze(self, file_path: Path) -> bool:
        """判断是否需要分析"""
        current_hash = self._compute_hash(file_path)
        return str(file_path) not in self.index or self.index[str(file_path)] != current_hash

    def get_cached(self, file_path: Path):
        """获取缓存结果"""
        cache_file = self.cache_dir / f"{self._compute_hash(file_path)}.json"
        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def cache_result(self, file_path: Path, result: Dict):
        """缓存结果"""
        cache_file = self.cache_dir / f"{self._compute_hash(file_path)}.json"
        try:
            import json
            with open(cache_file, 'w') as f:
                json.dump(result, f)
            self.index[str(file_path)] = self._compute_hash(file_path)
            self._save_index()
        except Exception as e:
            print(f"Warning: Failed to cache result: {e}")

    def _compute_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        try:
            import hashlib
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return str(file_path)

    def _load_index(self) -> dict:
        """加载索引"""
        if (self.cache_dir / "index.json").exists():
            try:
                import json
                with open(self.cache_dir / "index.json", 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_index(self):
        """保存索引"""
        try:
            import json
            with open(self.cache_dir / "index.json", 'w') as f:
                json.dump(self.index, f)
        except Exception as e:
            print(f"Warning: Failed to save index: {e}")
