#!/usr/bin/env python3
"""
Launcher script for gallerydl-beyond GUI with custom gallery-dl fork.
This script ensures your forked gallery-dl at /workspace/gallery_dl is used.
"""

import sys
import os

# Add your forked gallery-dl to the Python path
FORKED_GALLERY_DL_PATH = '/workspace/gallery_dl'
if FORKED_GALLERY_DL_PATH not in sys.path:
    sys.path.insert(0, FORKED_GALLERY_DL_PATH)

# Set PYTHONPATH environment variable for subprocess calls
os.environ['PYTHONPATH'] = FORKED_GALLERY_DL_PATH + ':' + os.environ.get('PYTHONPATH', '')

print(f"🚀 Launching gallerydl-beyond GUI...")
print(f"   Using gallery-dl from: {FORKED_GALLERY_DL_PATH}")
print(f"   Python version: {sys.version.split()[0]}")

try:
    # Import and run the GUI
    from gallerydl_beyond import __main__
    
    # Run the main entry point
    __main__.main()
    
except ImportError as e:
    print(f"\n❌ Error: Could not import gallerydl_beyond")
    print(f"   Details: {e}")
    print(f"\n💡 Solution:")
    print(f"   Make sure gallerydl-beyond is installed:")
    print(f"   cd /workspace/gallerydl-beyond && pip install -e .")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
