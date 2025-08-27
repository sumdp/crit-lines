#!/usr/bin/env python3
"""
Simple script to run Crit Lines without Poetry
"""
import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from crit_lines.interfaces.cli.main import main

if __name__ == "__main__":
    main()