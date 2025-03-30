"""Integration tests for analyzer performance and resource usage."""

import pytest
import time
import psutil
import os
from typing import Dict, Any
from summit_seo.analyzer.factory import AnalyzerFactory

@pytest.mark.integration
@pytest.mark.performance
class TestAnalyzerPerformance:
    """Test suite for analyzer performance and resource usage."""

    def get_process_memory(self) -> float:
        """Get current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def test_analyzer_memory_usage(self, complete_webpage, integration_configs):
        """Test memory usage of analyzers."""
        initial_memory = self.get_process_memory()
        memory_usage = {}
        
        for name, config in integration_configs.items():
            # Measure memory before analyzer creation
            before_memory = self.get_process_memory()
            
            # Create and use analyzer
            analyzer = AnalyzerFactory.get(name)(config)
            analyzer.analyze(complete_webpage)
            
            # Measure memory after analysis
            after_memory = self.get_process_memory()
            
            # Calculate memory impact
            memory_impact = after_memory - before_memory
            memory_usage[name] = memory_impact
            
            # Memory impact should be reasonable (less than 50MB per analyzer)
            assert memory_impact < 50, f"Memory usage for {name} analyzer is too high"
        
        # Total memory impact should be reasonable
        total_memory_impact = self.get_process_memory() - initial_memory
        assert total_memory_impact < 200, "Total memory usage is too high"

    def test_analyzer_execution_time(self, complete_webpage, integration_configs):
        """Test execution time of analyzers."""
        timing_results = {}
        
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            
            # Measure execution time over multiple runs
            times = []
            for _ in range(5):
                start_time = time.time()
                analyzer.analyze(complete_webpage)
                execution_time = time.time() - start_time
                times.append(execution_time)
            
            # Calculate average execution time
            avg_time = sum(times) / len(times)
            timing_results[name] = avg_time
            
            # Individual analyzer should complete within reasonable time (1 second)
            assert avg_time < 1.0, f"{name} analyzer is too slow"
        
        # Log timing results for analysis
        print("\nAnalyzer Timing Results:")
        for name, avg_time in timing_results.items():
            print(f"{name}: {avg_time:.3f} seconds")

    def test_analyzer_scalability(self, integration_configs):
        """Test analyzer performance with increasing content size."""
        content_sizes = [1000, 5000, 10000, 50000]  # Characters
        
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            execution_times = []
            
            for size in content_sizes:
                # Generate HTML content of specified size
                content = f"<html><body>{'Test content. ' * (size // 13)}</body></html>"
                
                # Measure execution time
                start_time = time.time()
                analyzer.analyze(content)
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
            
            # Verify linear or near-linear scaling
            # Time increase should be roughly proportional to content size increase
            for i in range(1, len(content_sizes)):
                size_ratio = content_sizes[i] / content_sizes[i-1]
                time_ratio = execution_times[i] / execution_times[i-1]
                
                # Allow for some overhead in scaling (2x the size ratio)
                assert time_ratio < size_ratio * 2, \
                    f"{name} analyzer shows poor scaling with content size"

    def test_concurrent_resource_usage(self, complete_webpage, integration_configs):
        """Test resource usage under concurrent execution."""
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        def run_analysis(name: str, config: Dict[str, Any]) -> float:
            analyzer = AnalyzerFactory.get(name)(config)
            start_memory = self.get_process_memory()
            
            # Run analysis multiple times
            for _ in range(3):
                analyzer.analyze(complete_webpage)
            
            end_memory = self.get_process_memory()
            return end_memory - start_memory
        
        initial_memory = self.get_process_memory()
        memory_impacts = []
        
        # Run analyzers concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(run_analysis, name, config)
                for name, config in integration_configs.items()
            ]
            
            # Collect memory impacts
            for future in futures:
                memory_impacts.append(future.result())
        
        # Verify reasonable memory usage under concurrent execution
        total_impact = sum(memory_impacts)
        assert total_impact < 400, "Excessive memory usage under concurrent execution"

    def test_resource_cleanup(self, complete_webpage, integration_configs):
        """Test proper resource cleanup after analyzer usage."""
        initial_memory = self.get_process_memory()
        
        for _ in range(5):  # Run multiple cycles
            for name, config in integration_configs.items():
                # Create and use analyzer
                analyzer = AnalyzerFactory.get(name)(config)
                analyzer.analyze(complete_webpage)
                
                # Force cleanup
                del analyzer
            
            # Check memory after each cycle
            current_memory = self.get_process_memory()
            memory_increase = current_memory - initial_memory
            
            # Memory should not grow significantly over cycles
            assert memory_increase < 100, "Memory leak detected in analyzer usage" 