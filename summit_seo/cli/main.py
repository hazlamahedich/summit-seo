"""Command-line interface for Summit SEO tool."""

import asyncio
import click
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..collector import CollectorFactory
from ..processor import ProcessorFactory
from ..analyzer import AnalyzerFactory
from ..reporter import ReporterFactory, ReportGenerationError

@click.group()
def cli():
    """Summit SEO - A comprehensive SEO analysis tool."""
    pass

@cli.command()
@click.argument('url', type=str)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file path for analysis results.'
)
@click.option(
    '--format',
    '-f',
    type=click.Choice(['json', 'html', 'console'], case_sensitive=False),
    default='console',
    help='Output format for analysis results.'
)
@click.option(
    '--analyzers',
    '-a',
    multiple=True,
    help='Specific analyzers to use (default: all).'
)
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True),
    help='Path to configuration file.'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output.'
)
@click.option(
    '--output-format',
    type=click.Choice(['console', 'json', 'html', 'csv']),
    default='console',
    help='Output format for analysis results'
)
@click.option(
    '--output-file',
    type=click.Path(),
    help='File to write output to (required for html/json/csv formats)'
)
@click.option(
    '--config-file',
    type=click.Path(exists=True),
    help='Path to configuration file'
)
def analyze(
    url: str,
    output: Optional[str],
    format: str,
    analyzers: List[str],
    config: Optional[str],
    verbose: bool,
    output_format: str,
    output_file: Optional[str],
    config_file: Optional[str]
):
    """Analyze a URL for SEO optimization."""
    try:
        # Load configuration
        config_data = _load_config(config_file) if config_file else {}
        
        # Run analysis
        results = asyncio.run(_analyze_url(
            url=url,
            analyzers=analyzers,
            config=config_data,
            verbose=verbose
        ))
        
        # Output results
        _output_results(results, output_format, output_file)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('urls', type=click.Path(exists=True))
@click.option(
    '--output-dir',
    '-o',
    type=click.Path(),
    help='Output directory for analysis results.'
)
@click.option(
    '--format',
    '-f',
    type=click.Choice(['json', 'html', 'console'], case_sensitive=False),
    default='json',
    help='Output format for analysis results.'
)
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True),
    help='Path to configuration file.'
)
@click.option(
    '--parallel',
    '-p',
    type=int,
    default=5,
    help='Number of parallel analyses to run.'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output.'
)
def batch(
    urls: str,
    output_dir: Optional[str],
    format: str,
    config: Optional[str],
    parallel: int,
    verbose: bool
):
    """Analyze multiple URLs from a file."""
    try:
        # Load URLs
        with open(urls, 'r') as f:
            url_list = [line.strip() for line in f if line.strip()]
        
        # Load configuration
        config_data = _load_config(config) if config else {}
        
        # Create output directory if needed
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Run batch analysis
        results = asyncio.run(_analyze_batch(
            urls=url_list,
            config=config_data,
            parallel=parallel,
            verbose=verbose
        ))
        
        # Output results
        _output_batch_results(results, output_dir, format)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
def list_analyzers():
    """List available analyzers."""
    analyzers = AnalyzerFactory.get_registered_analyzers()
    click.echo("\nAvailable Analyzers:")
    for name in analyzers:
        click.echo(f"  - {name}")

async def _analyze_url(
    url: str,
    analyzers: List[str],
    config: Dict[str, Any],
    verbose: bool
) -> Dict[str, Any]:
    """Run SEO analysis on a single URL."""
    try:
        # Create collector
        collector = CollectorFactory.create('webpage', config.get('collector', {}))
        
        # Collect data
        if verbose:
            click.echo(f"Collecting data from {url}...")
        collection_result = await collector.collect(url)
        
        # Create processor
        processor = ProcessorFactory.create('html', config.get('processor', {}))
        
        # Process data
        if verbose:
            click.echo("Processing collected data...")
        processing_result = await processor.process(
            {'html_content': collection_result.content},
            url
        )
        
        # Run analyzers
        if verbose:
            click.echo("Running analysis...")
        
        results = {}
        available_analyzers = AnalyzerFactory.get_registered_analyzers()
        selected_analyzers = analyzers or available_analyzers.keys()
        
        for name in selected_analyzers:
            if name not in available_analyzers:
                click.echo(f"Warning: Analyzer '{name}' not found.", err=True)
                continue
            
            analyzer = AnalyzerFactory.create(name, config.get('analyzers', {}).get(name, {}))
            analysis_result = await analyzer.analyze(processing_result.processed_data)
            results[name] = analysis_result.to_dict()
        
        return {
            'url': url,
            'timestamp': collection_result.timestamp.isoformat(),
            'results': results
        }
        
    except Exception as e:
        if verbose:
            click.echo(f"Error analyzing {url}: {str(e)}", err=True)
        raise

async def _analyze_batch(
    urls: List[str],
    config: Dict[str, Any],
    parallel: int,
    verbose: bool
) -> List[Dict[str, Any]]:
    """Run SEO analysis on multiple URLs."""
    semaphore = asyncio.Semaphore(parallel)
    
    async def analyze_with_semaphore(url: str) -> Dict[str, Any]:
        async with semaphore:
            return await _analyze_url(url, [], config, verbose)
    
    if verbose:
        click.echo(f"Analyzing {len(urls)} URLs with {parallel} parallel workers...")
    
    tasks = [analyze_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)

def _load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def _output_results(results: Dict[str, Any], output_format: str, output_file: Optional[str] = None) -> None:
    """Output analysis results in the specified format.
    
    Args:
        results: Analysis results to output.
        output_format: Format to output results in ('console', 'json', 'html', 'csv').
        output_file: Optional file to write output to.
    """
    try:
        if output_format == 'console':
            _print_console_output(results)
        else:
            if not output_file:
                click.echo("Error: --output-file is required for non-console output formats", err=True)
                sys.exit(1)
                
            reporter_config = {}
            if output_format == 'json':
                reporter_config = {
                    'indent': 2,
                    'sort_keys': True
                }
            elif output_format == 'csv':
                reporter_config = {
                    'include_headers': True,
                    'flatten_lists': True
                }
            elif output_format == 'html':
                reporter_config = {
                    'template_dir': str(Path(__file__).parent.parent / 'templates'),
                    'minify': True
                }
            
            reporter = ReporterFactory.create(output_format, reporter_config)
            report_result = asyncio.run(reporter.generate_report(results))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_result.content)
            
            click.echo(f"Report saved to {output_file}")
            
    except ReportGenerationError as e:
        click.echo(f"Error generating report: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)

def _print_console_output(results: Dict[str, Any]) -> None:
    """Print analysis results to console in a readable format.
    
    Args:
        results: Analysis results to print.
    """
    click.echo(f"\nAnalysis Results for {results['url']}")
    click.echo(f"Timestamp: {results['timestamp']}\n")
    
    for analyzer, result in results['results'].items():
        click.echo(f"{analyzer} Score: {result['score']}")
        
        if result.get('issues'):
            click.echo("\nIssues:")
            for issue in result['issues']:
                click.echo(f"  - {issue}")
        
        if result.get('warnings'):
            click.echo("\nWarnings:")
            for warning in result['warnings']:
                click.echo(f"  - {warning}")
        
        if result.get('suggestions'):
            click.echo("\nSuggestions:")
            for suggestion in result['suggestions']:
                click.echo(f"  - {suggestion}")
        
        click.echo("")

def _output_batch_results(
    results: List[Dict[str, Any]],
    output_dir: Optional[str],
    format: str
):
    """Output batch analysis results."""
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            click.echo(f"Error in batch item {i}: {str(result)}", err=True)
            continue
        
        if output_dir:
            filename = f"analysis_{i}_{Path(result['url']).name}"
            if format == 'json':
                filename = f"{filename}.json"
            elif format == 'html':
                filename = f"{filename}.html"
            
            output_path = str(Path(output_dir) / filename)
            _output_results(result, format, output_path)
        else:
            _output_results(result, format, None)

if __name__ == '__main__':
    cli() 