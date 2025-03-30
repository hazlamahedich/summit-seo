#!/usr/bin/env python
"""
Sample logo generator for testing PDF Reporter.

This script generates a simple logo file that can be used for testing 
the PDF Reporter's logo inclusion functionality without requiring 
external dependencies.
"""

import os
import sys
from pathlib import Path
import base64
from io import BytesIO

def generate_sample_logo(output_path=None):
    """
    Generate a simple PNG logo for testing.
    
    Args:
        output_path: Path where to save the logo file.
                     If None, will be saved as sample_logo.png in the same directory.
    
    Returns:
        Path to the generated logo file.
    """
    # Sample PNG data (a basic 100x100 PNG with a blue square)
    # This is a base64 encoded minimal PNG image
    base64_png = """
    iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAA
    CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5QwSDCwxcSuFpAAAAB1pVFh0Q29tbWVudAAA
    AAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAACaklEQVR42u3dMU/bQBjG8b+TBCkdIkWCgbVS
    pA7s7Sy98AP0G/Bb8gWqLl26dM3QpRtbp3ZkYqlUJAQDB+KoSo6DgZiFCO49z9D3bYmUJYvl
    59m9YCGcc+TM3PtHsrq86NWuc3We3t6TKLnGqA4i1yZBABEEEEEAEQQQQQARBJA8IDKrWbPU
    T4Sc6Z3L6z+HhCCACAKIIIAIAogggAgCiCCACAKIIIAIAogggMwZRGZ1QBAE1Ot1qtUqpVKJ
    KIrot/tcnHe5vPjBcBy+vKZnZ/+cRyNvf80myGiHi9u73gE2VtdZaW9RKBS4urxgEA8BiMcx
    9/0HAH4e/+DsJPnzeb2xztbOx7n1Xypv+7EO0m63AXj8/Yu78ADgcdDnXx/a2WnC4/1d5nq9
    3R3sxw/3dzPXr62vM0mS3PaoI1O79PWry8RxnHl9GIZ526NeWSCCACIIIH4/yNtnC2kak6Yx
    adL48zZK07zuz2+Qm+urzOvj0TBzPUmS3PaoI0O9MIzo9XpMJhOmecrNzTXtVgvnHGdnpzjn
    MOfodtOZ9WEYzqyvVCp526MgpVIZawz1ep1Go0GSJNzf3TLs97m9ucE5x9HhIavtNmEYcnR4
    mFlfLlfy1n3/D+LcbOjD0ZDBwz2DwYCDz/ssLbVYX99Ar91mafEDC4uL7O59mrueNh7JCWJm
    6mEYsry8zObmFs45Pn3+QhRFVKurAOzufaRWq82tj+MRxpq89XxHpiTOzZZ8weICjUaT/f0D
    VldWaLVaOOdotVozw56WfNHC1KeW5K3Lz4PANEYpFKMUCsZijMVaw8LiIg5HkkzzVahVYzV7
    FiT/fgMm03WoGZiH4gAAAABJRU5ErkJggg==
    """
    
    # Decode the base64 PNG
    png_data = base64.b64decode(base64_png.replace("\n", "").strip())
    
    # Determine output path
    if output_path is None:
        script_dir = Path(__file__).parent.absolute()
        output_path = script_dir / "sample_logo.png"
    else:
        output_path = Path(output_path)
    
    # Write the PNG data to the file
    with open(output_path, "wb") as f:
        f.write(png_data)
    
    print(f"Generated sample logo at: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    # If output path is provided as command line argument, use it
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    generate_sample_logo(output_path) 