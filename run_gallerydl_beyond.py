#!/usr/bin/env python3
"""
Launcher for GalleryDL Beyond GUI.
This script starts the PyQt6-based GUI for gallery-dl.

Requirements:
- Python 3.12+
- PyQt6
- gallery-dl (already installed in this environment)

Usage:
    python run_gallerydl_beyond.py
    
Or simply run:
    gallerydl_beyond
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gallerydl_beyond_gui', 'src'))

from gallerydl_beyond.__main__ import main

if __name__ == "__main__":
    main()
