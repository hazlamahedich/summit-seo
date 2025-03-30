#!/usr/bin/env python3
"""Run the Summit SEO CLI with batch mode enabled.

This is a simple wrapper that calls the CLI with the batch mode flag.
"""

import sys
import subprocess

def main():
    """Run the CLI with batch mode."""
    # Construct the command with batch mode flag
    cmd = ["python", "-m", "summit_seo.cli.main", "analyze"]
    
    # Add the batch mode flag
    cmd.append("--batch")
    
    # Add any other arguments
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default URL if none provided
        cmd.append("https://example.com")
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Execute the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 