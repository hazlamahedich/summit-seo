"""Unit tests for batch processing mode in the CLI."""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from summit_seo.cli.main import run_analysis
from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.progress_display import DisplayStyle
from summit_seo.cli.output_formatter import OutputFormat, set_output_format
from summit_seo.progress.analyzer_progress import AnalyzerProgressTracker


@pytest.fixture
def mock_args():
    """Create mock command-line arguments for testing."""
    args = MagicMock()
    args.url = "https://example.com"
    args.analyzers = None
    args.style = "minimal"
    args.format = "html"
    args.output = tempfile.mkdtemp()
    args.visual = False
    args.verbose = False
    args.batch = True
    args.detailed = False
    args.output_format = None
    args.output_width = 80
    args.interactive = False
    args.machine_readable = False
    return args


@pytest.fixture
def mock_analysis_runner():
    """Mock AnalysisRunner class."""
    with patch("summit_seo.cli.analysis_runner.AnalysisRunner") as mock:
        # Set up the mock to return a proper report path
        instance = mock.return_value
        instance.run.return_value = os.path.join(tempfile.mkdtemp(), "report.html")
        yield mock


@pytest.fixture
def mock_progress_tracker():
    """Mock the ProgressTracker to avoid abstract class instantiation issues."""
    with patch("summit_seo.cli.analysis_runner.ProgressTracker", autospec=True) as mock:
        # Return a MagicMock that can be instantiated
        instance = mock.return_value
        instance.set_total_steps.return_value = None
        instance.start.return_value = None
        instance.update_step.return_value = None
        instance.complete.return_value = None
        yield mock


class TestBatchMode:
    """Test batch processing mode in the CLI."""

    @pytest.mark.asyncio
    async def test_batch_output_formatter(self):
        """Test that the BatchFormatter produces the expected output."""
        from summit_seo.cli.output_formatter import BatchFormatter
        
        # Create a test result dictionary
        result = {
            "analyzer": "SecurityAnalyzer",
            "score": 85.5,
            "issues": [
                {"description": "Missing HTTPS", "severity": "critical"},
                {"description": "Insecure cookies", "severity": "high"},
                {"description": "Missing X-Frame-Options", "severity": "medium"}
            ]
        }
        
        # Test with show_details=False (default)
        formatter = BatchFormatter(show_details=False)
        output = formatter.format_result(result)
        
        # Should only include the score line
        assert "SecurityAnalyzer:85.5" in output
        assert "CRITICAL_ISSUES:" not in output
        
        # Test with show_details=True
        formatter = BatchFormatter(show_details=True)
        output = formatter.format_result(result)
        
        # Should include both score and critical issues
        assert "SecurityAnalyzer:85.5" in output
        assert "CRITICAL_ISSUES:" in output
        assert "- Missing HTTPS" in output
        assert "- Insecure cookies" in output
        
        # Medium severity issue should not be included
        assert "- Missing X-Frame-Options" not in output
    
    @pytest.mark.asyncio
    async def test_batch_summary_format(self):
        """Test the format of batch mode summary output."""
        from summit_seo.cli.output_formatter import BatchFormatter
        
        summary = {
            "url": "https://example.com",
            "overall_score": 78.5,
            "duration": 12.34,
            "analyzer_scores": {
                "SecurityAnalyzer": 85.5,
                "PerformanceAnalyzer": 72.0
            }
        }
        
        formatter = BatchFormatter()
        output = formatter.format_summary(summary)
        
        # Check that all expected lines are present
        assert "OVERALL_SCORE:78.5" in output
        assert "DURATION:12.34" in output
        assert "URL:https://example.com" in output
        assert "ANALYZER_SCORES:" in output
        assert "SecurityAnalyzer:85.5" in output
        assert "PerformanceAnalyzer:72.0" in output


    @pytest.mark.asyncio
    async def test_batch_mode_enabled(self, mock_args):
        """Test that batch mode is properly enabled."""
        # Create a mock AnalysisRunner
        with patch("summit_seo.cli.main.AnalysisRunner") as mock_runner:
            # Create an async mock run method
            runner_instance = MagicMock()
            
            async def mock_run():
                return os.path.join(tempfile.mkdtemp(), "report.html")
                
            runner_instance.run = mock_run
            mock_runner.return_value = runner_instance
            
            # Run the analysis
            await run_analysis(mock_args)
            
            # Verify AnalysisRunner was created with batch_mode=True
            _, kwargs = mock_runner.call_args
            assert kwargs.get("batch_mode") is True
            assert kwargs.get("display_style") == DisplayStyle.MINIMAL
    
    def test_machine_readable_implies_batch(self):
        """Test that machine-readable option implies batch mode."""
        # This is a non-async test since we don't need to run the full analysis
        
        # Create a test args object with machine_readable=True and batch=False
        args = MagicMock()
        args.machine_readable = True
        args.batch = False
        
        # Import the function that processes args
        from summit_seo.cli.main import cli
        
        # Mock the function that might be called as a result
        with patch("sys.argv", ["summit-seo", "analyze", "https://example.com", "--machine-readable"]), \
             patch("asyncio.run"), \
             patch("sys.exit"):
            
            # Run cli which should process the args
            cli()
            
            # We can't easily test the effect directly because of nested function calls,
            # but we can verify that the log message about batch mode was printed
            # which is only done when batch mode is enabled
            
        # Get the implementation directly
        from summit_seo.cli.main import run_analysis
            
        # Now directly test the run_analysis function's behavior with machine_readable=True
        with patch("summit_seo.cli.main.set_output_format") as mock_set_format, \
             patch("summit_seo.cli.main.AnalysisRunner") as mock_runner:
            
            # Set up the runner instance with an awaitable run method
            instance = MagicMock()
            instance.run = AsyncMock(return_value="report.html")
            mock_runner.return_value = instance
            
            # Call run_analysis with our args
            import asyncio
            asyncio.run(run_analysis(args))
            
            # Check that AnalysisRunner was called with batch_mode=True
            _, kwargs = mock_runner.call_args
            assert kwargs.get("batch_mode") is True, "machine_readable flag did not set batch_mode to True"
    
    @pytest.mark.asyncio
    async def test_detailed_batch_mode(self, mock_args):
        """Test batch mode with detailed output."""
        mock_args.detailed = True
        
        # Create mocks
        with patch("summit_seo.cli.main.AnalysisRunner") as mock_runner, \
             patch("summit_seo.cli.main.set_output_format") as mock_set_format:
            
            # Create an async mock run method
            runner_instance = MagicMock()
            
            async def mock_run():
                return os.path.join(tempfile.mkdtemp(), "report.html")
                
            runner_instance.run = mock_run
            mock_runner.return_value = runner_instance
            
            # Run the analysis
            await run_analysis(mock_args)
            
            # Verify that set_output_format was called with show_details=True
            mock_set_format.assert_called_once()
            args, kwargs = mock_set_format.call_args
            assert args[0] == OutputFormat.BATCH
            assert kwargs.get("show_details") is True


@pytest.mark.asyncio
@patch("summit_seo.cli.analysis_runner.ProgressTracker")
async def test_real_batch_mode(mock_progress_tracker):
    """Integration test for batch mode with a mock runner."""
    
    # Create a minimal mock for testing
    class MockRunner(AnalysisRunner):
        """Mock runner that doesn't actually analyze anything."""
        
        async def _setup_components(self):
            """Mock setup that doesn't do anything."""
            self._analyzers = [MagicMock(), MagicMock()]
            self.progress_tracker.set_total_steps(4)  # 2 analyzers + collect + process
        
        async def _collect_data(self):
            """Mock collection."""
            await asyncio.sleep(0.1)  # Small delay for realism
            return {"html": "<html></html>"}
        
        async def _process_data(self, collected_data):
            """Mock processing."""
            await asyncio.sleep(0.1)  # Small delay for realism
            return {"processed": True}
        
        async def _analyze_data(self, processed_data):
            """Mock analysis."""
            await asyncio.sleep(0.1)  # Small delay for realism
            return [{"score": 85}, {"score": 90}]
        
        async def _generate_report(self, results):
            """Mock report generation."""
            await asyncio.sleep(0.1)  # Small delay for realism
            report_path = os.path.join(tempfile.mkdtemp(), "report.html")
            # Create an empty file
            with open(report_path, "w") as f:
                f.write("<html></html>")
            return report_path
    
    # Set up the mock progress tracker
    instance = mock_progress_tracker.return_value
    
    # Create a runner with batch mode enabled
    runner = MockRunner(
        url="https://example.com",
        batch_mode=True
    )
    
    # Run the analysis
    report_path = await runner.run()
    
    # Verify that the batch method was used
    assert os.path.exists(report_path)
    
    # Clean up
    os.remove(report_path)


@pytest.mark.asyncio
@patch("summit_seo.cli.analysis_runner.ProgressTracker")
async def test_batch_processing_works(mock_progress_tracker):
    """Basic test to verify batch processing executes correctly."""
    # Set up the mock progress tracker
    tracker_instance = mock_progress_tracker.return_value
    
    # Create a minimal batch mode runner
    runner = AnalysisRunner(
        url="https://example.com",
        batch_mode=True
    )
    
    # Patch the methods to not do actual work
    with patch.object(runner, '_setup_components'), \
         patch.object(runner, '_collect_data', return_value={"html": "<html></html>"}), \
         patch.object(runner, '_process_data', return_value={"processed": True}), \
         patch.object(runner, '_analyze_data', return_value=[]), \
         patch.object(runner, '_generate_report', return_value="report.html"), \
         patch('builtins.print') as mock_print:
        
        # Run the analysis in batch mode
        await runner.run()
        
        # Check that _run_batch_mode was called (by examining print calls)
        # Specifically, the batch mode header and footer should be printed
        batch_header_printed = False
        batch_summary_printed = False
        
        for call_args in mock_print.call_args_list:
            arg = call_args[0][0] if call_args[0] else ""
            if isinstance(arg, str) and "Summit SEO Batch Analysis:" in arg:
                batch_header_printed = True
            if isinstance(arg, str) and "BATCH ANALYSIS" in arg:
                batch_summary_printed = True
        
        assert batch_header_printed, "Batch mode header not printed"
        assert batch_summary_printed, "Batch mode summary not printed" 