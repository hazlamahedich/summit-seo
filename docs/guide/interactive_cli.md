# Interactive CLI Mode Guide

## Overview

The Interactive CLI Mode provides a real-time, keyboard-controlled interface for Summit SEO analysis. This feature allows users to monitor and control the analysis process with command keys, view detailed progress information, and interact with the running analysis.

## Usage

To start an analysis in interactive mode, use the `--interactive` or `-i` flag:

```bash
summit-seo analyze example.com --interactive
```

This will launch the analysis with a full-screen terminal interface that displays progress information and accepts keyboard commands.

## Interface

The interactive interface consists of several sections:

1. **Header**: Shows the title and current status
2. **Progress Bar**: Visual representation of overall progress
3. **Details**: Information about the current step and timing
4. **Help**: Available commands (toggle with `h` key)
5. **Status Bar**: Current analyzer and last key pressed

Example interface:

```
Summit SEO Interactive Analysis
Status: RUNNING                                             Stage: ANALYSIS

 85.25% [███████████████████████████████████░░░░░░░]

Time: 12s elapsed, 5s remaining                 Step: 4/6
Current: Running SecurityAnalyzer (2/4)

Commands:
  p - Pause analysis
  r - Resume analysis
  c - Cancel analysis
  d - Toggle detail level
  h - Show/hide help
  q - Quit interactive mode

Press h for help | Last key: h                                                
```

## Commands

| Key | Command | Description |
| --- | ------- | ----------- |
| `p` | Pause   | Pause the analysis (can be resumed) |
| `r` | Resume  | Resume a paused analysis |
| `c` | Cancel  | Cancel the analysis |
| `d` | Detail  | Toggle detail level (Minimal, Normal, Detailed) |
| `h` | Help    | Show/hide help screen |
| `q` | Quit    | Quit interactive mode |

## Detail Levels

The interface supports three detail levels that can be toggled with the `d` key:

1. **Minimal**: Shows only essential information
2. **Normal**: Shows timing, step count, and current operation
3. **Detailed**: Adds stage-by-stage progress breakdown

## Architecture

The interactive CLI mode is implemented with the following components:

1. **InteractiveMode**: Main controller class that coordinates between analysis runner and display
2. **InteractiveModeDisplay**: Curses-based interface for keyboard input and display
3. **InteractiveCommand**: Enum for available keyboard commands
4. **ProgressTracker Integration**: Shows real-time progress information

### Asynchronous Operation

The interactive mode uses Python's asyncio to handle concurrent operations:

- The analysis runs in one asynchronous task
- The display updates occur in another asynchronous task
- Keyboard input is handled in the event loop

### State Management

The interactive mode integrates with the ProgressTracker's state system:

- **RUNNING**: Analysis is actively running
- **PAUSED**: Analysis is temporarily paused
- **CANCELLED**: Analysis has been manually cancelled
- **COMPLETED**: Analysis finished successfully
- **FAILED**: Analysis encountered an error

## Examples

### Basic Usage

```bash
# Run analysis in interactive mode
summit-seo analyze example.com --interactive

# Run specific analyzers in interactive mode
summit-seo analyze example.com --analyzers=security,performance --interactive

# Run in interactive mode with a specific output format
summit-seo analyze example.com --interactive --format=json --output=results/
```

### Programmatic Usage

```python
from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.interactive_mode import run_interactive_analysis
from summit_seo.cli.progress_display import DisplayStyle

# Create the runner
runner = AnalysisRunner(
    url="https://example.com",
    analyzers=["security", "performance"],
    display_style=DisplayStyle.ANIMATED,
    output_format="html",
    output_path="./results"
)

# Run in interactive mode
run_interactive_analysis(runner)
```

## Integration with Other Components

The interactive mode integrates with other Summit SEO components:

- **Progress Tracking**: Shows real-time progress via the ProgressTracker
- **Analysis Runner**: Controls the analysis process
- **Output Formatter**: Formats final results
- **Logging System**: Captures events for later review

## Best Practices

1. **Terminal Size**: Use a terminal with at least 80x24 characters for best display
2. **Color Support**: Use a terminal that supports colors for best experience
3. **Cancel vs Quit**: Use 'c' to cancel the analysis, 'q' to exit after completion
4. **Detail Levels**: Start with Normal detail and switch to Detailed for more information
5. **Error Handling**: If the analysis fails, check the status bar for error details

## Troubleshooting

### Common Issues

- **Display Issues**: If the display appears corrupted, try resizing your terminal window
- **Color Problems**: If colors appear wrong, check your terminal's color support
- **Keyboard Not Responding**: Ensure terminal focus is on the interactive window

### Terminal Compatibility

The interactive mode works best with the following terminals:

- Linux: GNOME Terminal, Konsole, xterm
- macOS: Terminal.app, iTerm2
- Windows: Windows Terminal, ConEmu

## Customization

Advanced users can customize the interactive mode by extending the following classes:

- **InteractiveModeDisplay**: To customize the display layout
- **InteractiveMode**: To add custom commands or modify behavior

## Limitations

- **Screen Size**: Requires a minimum terminal size of 80x24 characters
- **Non-TTY**: Cannot be used when stdout is not a TTY (e.g., in pipes)
- **Redirected Output**: Does not work with output redirection 