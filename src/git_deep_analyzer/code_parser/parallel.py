"""Parallel processor - simplified version."""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Callable, Any


class ParallelProcessor:
    """并行处理器"""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or os.cpu_count()

    def parse_files_parallel(
        self,
        files: List[str],
        parser: Callable[[str], Any]
    ) -> List[Any]:
        """并行解析文件"""
        results = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(parser, f): f
                for f in files
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Warning: Failed to parse {futures[future]}: {e}")

        return results

    def process_parallel(
        self,
        items: List[Any],
        processor: Callable[[Any], Any]
    ) -> List[Any]:
        """并行处理任意项"""
        results = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processor, item): item
                for item in items
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Warning: Failed to process item: {e}")

        return results
