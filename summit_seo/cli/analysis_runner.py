"""Command-line interface for running Summit SEO analysis with progress display."""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from summit_seo.analyzer import AnalyzerFactory
from summit_seo.collector import CollectorFactory
from summit_seo.processor import ProcessorFactory
from summit_seo.reporter import ReporterFactory
from summit_seo.progress import AnalyzerProgressTracker, ProgressStage
from summit_seo.cli.progress_display import CLIProgressDisplay, DisplayStyle
from summit_seo.progress.base import ProgressTracker, ProgressState
from summit_seo.visualization import VisualizationFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class AnalysisRunner:
    """Runner for executing SEO analysis from the CLI."""
    
    def __init__(
        self,
        url: str,
        analyzers: Optional[List[str]] = None,
        display_style: DisplayStyle = DisplayStyle.ANIMATED,
        output_format: str = "html",
        output_path: str = ".",
        visual_report: bool = False,
        verbose: bool = False,
        batch_mode: bool = False
    ):
        """Initialize the analysis runner.
        
        Args:
            url: URL to analyze.
            analyzers: List of analyzer names to run (None for all).
            display_style: Progress display style.
            output_format: Report output format.
            output_path: Directory for saving reports.
            visual_report: Whether to generate visual report.
            verbose: Whether to enable verbose output.
            batch_mode: Whether to run in batch mode with minimal output.
        """
        self.url = url
        self.analyzer_names = analyzers
        self.display_style = display_style
        self.output_format = output_format
        self.output_path = output_path
        self.visual_report = visual_report
        self.verbose = verbose
        self.batch_mode = batch_mode
        
        # Create the progress tracker
        self.progress_tracker = ProgressTracker(
            name=f"SEO Analysis: {url}",
            total_steps=0  # Will be set later
        )
        
        # Initialize other attributes
        self._display = None
        self._analyzers = []
        self._collector = None
        self._processor = None
        self._reporter = None
        self._visualization = None
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially
        self._start_time = None
    
    async def pause(self) -> None:
        """Pause the analysis."""
        if not self._paused:
            self._paused = True
            self._pause_event.clear()
            self.progress_tracker.pause()
            logger.info("Analysis paused")
    
    async def resume(self) -> None:
        """Resume the analysis."""
        if self._paused:
            self._paused = False
            self._pause_event.set()
            self.progress_tracker.resume()
            logger.info("Analysis resumed")
    
    async def cancel(self) -> None:
        """Cancel the analysis."""
        self.progress_tracker.cancel()
        logger.info("Analysis cancelled")
    
    async def _setup_components(self) -> None:
        """Set up required analysis components."""
        # Create collector
        self._collector = CollectorFactory.create("html", url=self.url)
        
        # Create processor
        self._processor = ProcessorFactory.create("html")
        
        # Create analyzers
        if self.analyzer_names:
            self._analyzers = [
                AnalyzerFactory.create(name) 
                for name in self.analyzer_names
                if name in AnalyzerFactory.get_registered_analyzers()
            ]
        else:
            # Create all registered analyzers if none specified
            self._analyzers = [
                AnalyzerFactory.create(name)
                for name in AnalyzerFactory.get_registered_analyzers()
            ]
        
        # Create reporter
        self._reporter = ReporterFactory.create(
            self.output_format,
            output_path=self.output_path
        )
        
        # Create visualization if requested
        if self.visual_report:
            self._visualization = VisualizationFactory.create("matplotlib")
            
        # Calculate total steps for progress tracking
        # 1 for collection, 1 for processing, 1 for each analyzer, 1 for reporting
        total_steps = 3 + len(self._analyzers)
        self.progress_tracker.set_total_steps(total_steps)
        
        # Initialize progress display
        if not self.batch_mode:
            self._display = CLIProgressDisplay(
                tracker=self.progress_tracker,
                style=self.display_style,
                refresh_rate=0.2
            )
    
    async def _run_with_pause_check(self, coro):
        """Run a coroutine with pause check."""
        while True:
            # Wait if paused
            await self._pause_event.wait()
            
            # Check if cancelled
            if self.progress_tracker.state == ProgressState.CANCELLED:
                raise asyncio.CancelledError("Analysis cancelled")
                
            try:
                return await coro
            except asyncio.CancelledError:
                # Propagate cancellation
                raise
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                if self.verbose:
                    logger.exception("Detailed error information")
                raise
    
    async def _collect_data(self) -> Dict[str, Any]:
        """Collect data using the configured collector."""
        self.progress_tracker.set_current_stage(ProgressStage.COLLECTION)
        self.progress_tracker.update_step(1, f"Collecting data from {self.url}")
        
        return await self._run_with_pause_check(self._collector.collect())
    
    async def _process_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process collected data."""
        self.progress_tracker.set_current_stage(ProgressStage.PROCESSING)
        self.progress_tracker.update_step(2, "Processing collected data")
        
        return await self._run_with_pause_check(self._processor.process(collected_data))
    
    async def _analyze_data(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run analyzers on processed data."""
        self.progress_tracker.set_current_stage(ProgressStage.ANALYSIS)
        
        results = []
        current_step = 3  # After collection and processing
        
        for i, analyzer in enumerate(self._analyzers, 1):
            analyzer_name = analyzer.__class__.__name__
            self.progress_tracker.update_step(
                current_step, 
                f"Running {analyzer_name} ({i}/{len(self._analyzers)})"
            )
            
            # Store current analyzer name for display
            self.progress_tracker.analyzer_name = analyzer_name
            
            # Run the analyzer
            try:
                result = await self._run_with_pause_check(analyzer.analyze(processed_data))
                results.append(result)
            except Exception as e:
                logger.error(f"Error in {analyzer_name}: {str(e)}")
                if self.verbose:
                    logger.exception(f"Detailed error in {analyzer_name}")
            
            current_step += 1
        
        return results
    
    async def _generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a report from analysis results."""
        self.progress_tracker.set_current_stage(ProgressStage.REPORTING)
        self.progress_tracker.update_step(
            self.progress_tracker.total_steps, 
            "Generating report"
        )
        
        # Generate visualizations if enabled
        visualizations = None
        if self.visual_report and self._visualization:
            visualizations = self._visualization.create_visualizations(results)
        
        # Generate the report
        report_path = await self._run_with_pause_check(
            self._reporter.generate_report(
                url=self.url,
                results=results,
                visualizations=visualizations
            )
        )
        
        return report_path
    
    def _print_batch_summary(self, start_time: float, report_path: str) -> None:
        """Print a summary when running in batch mode."""
        duration = time.time() - start_time
        
        # Calculate success status based on progress tracker state
        success = self.progress_tracker.state == ProgressState.COMPLETED
        status = "SUCCESS" if success else "FAILED"
        
        # Format summary in a compact way suitable for automated processing
        print("\n─────────────────────────────────────────────")
        print(f"BATCH ANALYSIS {status}")
        print("─────────────────────────────────────────────")
        print(f"URL: {self.url}")
        print(f"Analyzers: {len(self._analyzers)}")
        print(f"Duration: {duration:.2f}s")
        
        # Only print the report path if it was successfully generated
        if report_path:
            print(f"Report: {Path(report_path).absolute()}")
        
        # Print exit code for potential shell script integration
        if not success:
            print(f"Exit Code: 1 (Analysis failed)")
        else:
            print(f"Exit Code: 0 (Analysis completed successfully)")
        print("─────────────────────────────────────────────")

    async def _run_batch_mode(self) -> str:
        """Run analysis in batch mode with minimal output.
        
        Returns:
            Path to the generated report.
        """
        report_path = ""
        
        try:
            # Set up components
            await self._setup_components()
            
            # Print minimal start message
            print(f"Summit SEO Batch Analysis: {self.url}")
            print("─────────────────────────────────────────────")
            
            # Start the analysis
            self.progress_tracker.start()
            
            # Collect data
            sys.stdout.write("Collecting data... ")
            sys.stdout.flush()
            collected_data = await self._collect_data()
            print("Done")
                
            # Process data
            sys.stdout.write("Processing data... ")
            sys.stdout.flush()
            processed_data = await self._process_data(collected_data)
            print("Done")
                
            # Analyze data
            print(f"Running {len(self._analyzers)} analyzers...")
            results = await self._analyze_data(processed_data)
            
            # Generate report
            sys.stdout.write("Generating report... ")
            sys.stdout.flush()
            report_path = await self._generate_report(results)
            print("Done")
                
            # Mark as completed
            self.progress_tracker.complete()
            
        except asyncio.CancelledError:
            print("Analysis cancelled")
            self.progress_tracker.cancel()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            if self.verbose:
                logger.exception("Detailed error information")
            self.progress_tracker.fail()
        
        return report_path

    async def run(self) -> str:
        """Run the complete analysis process.
        
        Returns:
            Path to the generated report.
        """
        self._start_time = time.time()
        report_path = ""
        
        try:
            # Run in appropriate mode
            if self.batch_mode:
                report_path = await self._run_batch_mode()
            else:
                # Set up components
                await self._setup_components()
                
                # Start the progress display
                await self._display.start()
                
                # Start the analysis
                self.progress_tracker.start()
                
                # Collect data
                collected_data = await self._collect_data()
                    
                # Process data
                processed_data = await self._process_data(collected_data)
                    
                # Analyze data
                results = await self._analyze_data(processed_data)
                    
                # Generate report
                report_path = await self._generate_report(results)
                    
                # Mark as completed
                self.progress_tracker.complete()
            
        except asyncio.CancelledError:
            if not self.batch_mode:
                logger.info("Analysis cancelled")
            self.progress_tracker.cancel()
            
        except Exception as e:
            if not self.batch_mode:
                logger.error(f"Analysis failed: {str(e)}")
                if self.verbose:
                    logger.exception("Detailed error information")
            self.progress_tracker.fail()
            
        finally:
            # Stop the progress display if not in batch mode
            if self._display and not self.batch_mode:
                await self._display.stop()
                
            # Print batch mode summary if enabled
            if self.batch_mode:
                self._print_batch_summary(self._start_time, report_path)
        
        return report_path


async def main():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description="Summit SEO Analysis Tool")
    
    # Required arguments
    parser.add_argument("url", help="URL to analyze")
    
    # Optional arguments
    parser.add_argument(
        "-a", "--analyzers",
        help="Comma-separated list of analyzers to run (default: all)",
        type=str
    )
    
    parser.add_argument(
        "-s", "--style",
        help="Progress display style (default: animated)",
        choices=["minimal", "detailed", "animated", "compact"],
        default="animated"
    )
    
    parser.add_argument(
        "-f", "--format",
        help="Output format (default: html)",
        choices=["html", "json", "csv", "xml", "pdf"],
        default="html"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: current directory)",
        default="."
    )
    
    parser.add_argument(
        "--visual",
        help="Generate a visual report with charts (HTML format only)",
        action="store_true"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    
    parser.add_argument(
        "--batch",
        help="Run in batch mode with minimal output",
        action="store_true"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert analyzers string to list if provided
    analyzers = None
    if args.analyzers:
        analyzers = [a.strip() for a in args.analyzers.split(",")]
    
    # Convert style string to DisplayStyle enum
    style_map = {
        "minimal": DisplayStyle.MINIMAL,
        "detailed": DisplayStyle.DETAILED,
        "animated": DisplayStyle.ANIMATED,
        "compact": DisplayStyle.COMPACT
    }
    display_style = style_map.get(args.style, DisplayStyle.ANIMATED)
    
    # Check if visual report is requested but format is not HTML
    if args.visual and args.format.lower() != "html":
        logger.warning("Visual reports are only available for HTML format. Ignoring --visual flag.")
        args.visual = False
    
    # Create and run the analysis
    runner = AnalysisRunner(
        url=args.url,
        analyzers=analyzers,
        display_style=display_style,
        output_format=args.format,
        output_path=args.output,
        visual_report=args.visual,
        verbose=args.verbose,
        batch_mode=args.batch
    )
    
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main()) 