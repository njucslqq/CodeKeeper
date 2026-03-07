"""Analysis execution strategies."""

from typing import Dict, Any, List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib


class AnalysisStrategy:
    """Base class for analysis strategies."""

    def execute(self, analyzers: List[Callable], **kwargs) -> List[Dict[str, Any]]:
        """
        Execute analyzers using this strategy.

        Args:
            analyzers: List of analyzer functions
            **kwargs: Additional parameters for analyzers

        Returns:
            List of analysis results
        """
        raise NotImplementedError


class SerialStrategy(AnalysisStrategy):
    """Execute analyzers serially (one after another)."""

    def execute(self, analyzers: List[Callable], **kwargs) -> List[Dict[str, Any]]:
        """
        Execute analyzers serially.

        Args:
            analyzers: List of analyzer functions
            **kwargs: Parameters for analyzers

        Returns:
            List of analysis results in order
        """
        results = []
        for analyzer in analyzers:
            try:
                result = analyzer(**kwargs)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        return results


class ParallelStrategy(AnalysisStrategy):
    """Execute analyzers in parallel."""

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel strategy.

        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers

    def execute(self, analyzers: List[Callable], **kwargs) -> List[Dict[str, Any]]:
        """
        Execute analyzers in parallel.

        Args:
            analyzers: List of analyzer functions
            **kwargs: Parameters for analyzers

        Returns:
            List of analysis results (order not guaranteed)
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all analyzer tasks
            future_to_analyzer = {
                executor.submit(analyzer, **kwargs): i
                for i, analyzer in enumerate(analyzers)
            }

            # Collect results as they complete
            future_results = {}
            for future in as_completed(future_to_analyzer):
                index = future_to_analyzer[future]
                try:
                    result = future.result()
                    future_results[index] = result
                except Exception as e:
                    future_results[index] = {"error": str(e)}

            # Sort by original index
            for i in range(len(analyzers)):
                if i in future_results:
                    results.append(future_results[i])
                else:
                    results.append({"error": "Analysis not completed"})

        return results


class LayeredStrategy(AnalysisStrategy):
    """Execute analyzers in layers (higher layers depend on lower layers)."""

    def __init__(self, strategy: str = "serial"):
        """
        Initialize layered strategy.

        Args:
            strategy: Strategy for each layer (serial/parallel)
        """
        self.strategy = strategy

    def execute(self, layers: List[List[Callable]], **kwargs) -> List[Dict[str, Any]]:
        """
        Execute analyzers in layers.

        Args:
            layers: List of layers, each layer is a list of analyzers
            **kwargs: Parameters for analyzers

        Returns:
            List of analysis results from all layers
        """
        all_results = []
        previous_results = {}

        for layer_index, layer_analyzers in enumerate(layers):
            # Pass previous results to current layer
            current_kwargs = {**kwargs, "previous_results": previous_results}

            # Execute layer using configured strategy
            if self.strategy == "parallel":
                layer_results = ParallelStrategy().execute(layer_analyzers, **current_kwargs)
            else:
                layer_results = SerialStrategy().execute(layer_analyzers, **current_kwargs)

            # Merge layer results
            for result in layer_results:
                all_results.append(result)
                previous_results.update(result)

        return all_results


class IncrementalStrategy(AnalysisStrategy):
    """Execute analyzers incrementally based on file changes."""

    def execute(
        self,
        analyzer: Callable,
        file_hash_map: Dict[str, str],
        previous_results: Dict[str, Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute analyzer only on changed files.

        Args:
            analyzer: Analyzer function
            file_hash_map: Current file hash map
            previous_results: Previous analysis results
            **kwargs: Parameters for analyzers

        Returns:
            Analysis results with cached results for unchanged files
        """
        results = {}
        changed_files = []

        # Identify changed files
        for file_path, current_hash in file_hash_map.items():
            if file_path not in previous_results:
                # New file
                changed_files.append(file_path)
            else:
                # Check if hash changed (assuming previous results stored hash)
                # For simplicity, assume any file in previous_results is unchanged
                # In production, compare actual hashes
                pass

        # Re-analyze changed files
        for file_path in changed_files:
            try:
                result = analyzer(file_path=file_path, **kwargs)
                results[file_path] = result
            except Exception as e:
                results[file_path] = {"error": str(e)}

        # Use cached results for unchanged files
        for file_path in file_hash_map:
            if file_path not in results:
                results[file_path] = previous_results.get(file_path, {})

        return results


class AnalysisExecutor:
    """Main executor that manages analysis strategies."""

    def __init__(self, ai_client, logger=None):
        """
        Initialize analysis executor.

        Args:
            ai_client: AI client for analysis
            logger: Optional logger instance
        """
        self.ai_client = ai_client
        self.logger = logger

        # Strategy registry
        self.strategies = {
            "serial": SerialStrategy(),
            "parallel": ParallelStrategy(max_workers=4),
            "layered": LayeredStrategy(),
            "incremental": IncrementalStrategy(),
        }

    def execute(
        self,
        analyzers: List[Callable],
        config: Dict[str, Any],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Execute analyzers using configured strategy.

        Args:
            analyzers: List of analyzer functions
            config: Configuration dict with strategy settings
            **kwargs: Additional parameters for analyzers

        Returns:
            List of analysis results
        """
        strategy_name = config.get("strategy", "serial").lower()

        # Get strategy
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
        else:
            # Fallback to serial
            if self.logger:
                self.logger.log_error(
                    "AnalysisExecutor",
                    ValueError(f"Unknown strategy: {strategy_name}, using serial")
                )
            strategy = self.strategies["serial"]

        # Handle special cases
        if strategy_name == "incremental":
            # Incremental requires different parameters
            return strategy.execute(
                analyzers[0],  # Incremental uses single analyzer
                kwargs.get("file_hash_map", {}),
                kwargs.get("previous_results", {}),
                **kwargs
            )
        elif strategy_name == "layered":
            # Layered expects layers parameter
            layers = kwargs.get("layers", [analyzers])
            return strategy.execute(layers, **kwargs)
        else:
            # Serial and parallel
            return strategy.execute(analyzers, **kwargs)

    def combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple analysis results into one.

        Args:
            results: List of analysis results

        Returns:
            Combined results dictionary
        """
        combined = {}
        for result in results:
            if isinstance(result, dict):
                combined.update(result)
        return combined

    def register_strategy(self, name: str, strategy: AnalysisStrategy):
        """
        Register a custom strategy.

        Args:
            name: Strategy name
            strategy: Strategy instance
        """
        self.strategies[name.lower()] = strategy

    def get_strategy(self, name: str) -> Optional[AnalysisStrategy]:
        """
        Get strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy instance or None
        """
        return self.strategies.get(name.lower())
