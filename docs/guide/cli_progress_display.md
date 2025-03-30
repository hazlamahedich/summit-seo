# CLI Progress Display Guide

The Summit SEO toolkit includes a powerful CLI progress display component that provides real-time feedback during analysis operations. This guide explains how to use and customize the progress display in your applications.

## Available Display Styles

The CLI progress display supports four different styles:

### 1. Minimal Style

A compact single-line progress bar that shows only essential information:

```
[#################               ] 48.3% 00:04/00:08 running
```

The minimal style is ideal for scripts or when you want to minimize screen usage.

### 2. Detailed Style

A multi-line display with comprehensive progress information:

```
Analyzing example.com [running]
[#################               ] 48.3%
Step: 25/50
Stage: processing (60.0% complete)
Time elapsed: 00:04
Time remaining: 00:08

Recent messages:
  [12:34:56] Collected 30% of data
  [12:34:57] Processing HTML content
  [12:34:58] Analyzing metadata
```

The detailed style provides a complete overview of the analysis progress, including recent messages and errors.

### 3. Animated Style

A visually enhanced display with color gradients and mini-bars for stage progress:

```
⠋ Analyzing example.com [running]
[#################               ] 48.3%
➤ initialization [■■■■■■■■■■] 100%
➤ collection     [■■■■■■■■■■] 100%
  processing     [■■■■■■    ] 60%
  analysis       [          ] 0%
  reporting      [          ] 0%
  cleanup        [          ] 0%
⏱ 00:04 (est. 00:08 remaining)
```

The animated style provides a visually appealing representation of the overall progress and individual stages.

### 4. Compact Style

A minimalist display with Unicode block characters to represent progress:

```
running ⠋ [⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀] 50% - processing
```

The compact style is the most space-efficient option, showing progress without taking much screen space.

## Using the CLI Progress Display

### Command-Line Usage

When using the Summit SEO CLI tool, you can select a display style using the `--style` option:

```bash
./summit-seo analyze https://example.com --style animated
```

Available style options:
- `minimal`: Simple one-line progress bar
- `detailed`: Multi-line progress with comprehensive stats
- `animated`: Animated progress bar with gradient effects
- `compact`: Compact single-line status display

### Programmatic Usage

You can also use the CLI progress display programmatically in your own applications:

```python
from summit_seo.progress import SimpleProgressTracker, ProgressStage
from summit_seo.cli import CLIProgressDisplay, DisplayStyle
import asyncio

async def run_with_progress():
    # Create a progress tracker
    tracker = SimpleProgressTracker(name="My Analysis Task")
    
    # Create a CLI progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.ANIMATED,
        refresh_rate=0.1,
        bar_width=40,
        show_spinner=True,
        show_time=True,
        show_percentage=True
    )
    
    # Start the tracker and display
    tracker.start()
    await display.start()
    
    # Update progress as your task runs
    tracker.set_stage(ProgressStage.INITIALIZATION, 0.0)
    # ... your initialization code ...
    tracker.update_stage_progress(1.0)
    
    tracker.set_stage(ProgressStage.COLLECTION, 0.0)
    # ... your data collection code ...
    tracker.update_stage_progress(1.0)
    
    # ... continue with other stages ...
    
    # Complete the tracking
    tracker.complete()
    
    # Stop the display
    await display.stop()

# Run your async function
asyncio.run(run_with_progress())
```

## Customization Options

The `CLIProgressDisplay` class accepts several customization parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `tracker` | The progress tracker to visualize | Required |
| `style` | Display style to use | `DisplayStyle.DETAILED` |
| `refresh_rate` | How often to refresh the display (seconds) | `0.2` |
| `show_spinner` | Whether to show a spinner animation | `True` |
| `show_time` | Whether to show elapsed/remaining time | `True` |
| `show_percentage` | Whether to show percentage complete | `True` |
| `bar_width` | Width of the progress bar in characters | `40` |
| `clear_on_complete` | Whether to clear the display when complete | `False` |

## Integration with Progress Tracking

The CLI progress display works with both `SimpleProgressTracker` and `AnalyzerProgressTracker` from the progress tracking module. When using `AnalyzerProgressTracker`, the display will show the progress of individual analyzers in the detailed and animated styles.

## Error Handling

The display automatically shows error messages from the tracker in the detailed style. You can add error messages to the tracker using the `_add_error()` method:

```python
tracker._add_error("Connection timeout")
```

## Example Code

For a complete example of how to use the CLI progress display, see the example script at `examples/cli_progress_example.py`. 