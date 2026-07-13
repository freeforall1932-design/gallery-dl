# GalleryDL Beyond - Modern PyQt6 GUI for gallery-dl

## Overview

This is a modern, feature-rich graphical user interface for [gallery-dl](https://github.com/mikf/gallery-dl), based on the [gallerydl-beyond](https://github.com/asomoza/gallerydl-beyond) project by Alvaro Somoza. It provides a professional PyQt6-based interface with advanced download management, history tracking, and database support.

## Features

### Core Features
- **Modern PyQt6 Interface** - Clean, responsive UI with native look and feel
- **Multi-threaded Downloads** - Concurrent download support with configurable limits
- **Download Queue Management** - Add, pause, resume, and stop individual downloads
- **History Database** - Persistent storage of all download attempts with status tracking
- **Real-time Logging** - Live output from gallery-dl with color-coded messages
- **Smart URL Detection** - Automatic extractor detection and validation

### Advanced Features
- **Download History** - View past downloads, re-download failed items, check for new content
- **Tag Management** - Organize downloads with custom tags
- **Force Redownload** - Re-download previously skipped or completed items
- **Skip Detection** - Automatically detect and report already downloaded files
- **Configurable Concurrency** - Set maximum simultaneous downloads
- **Gallery-dl Options Dialog** - Full access to all gallery-dl CLI options
- **Database Management** - Export, import, and manage download history

### Technical Features
- **Multiple gallery-dl Modes**:
  - Auto-detect system installation
  - Python module mode (`python -m gallery_dl`)
  - External Python interpreter
  - Custom gallery-dl path
- **Environment Discovery** - Automatically finds pipx, uv tools, and venv installations
- **Self-update Support** - Update gallery-dl directly from the GUI (when applicable)
- **Cross-platform** - Works on Windows, Linux, and macOS

## Installation

### Prerequisites
- Python 3.12 or higher
- PyQt6 (`pip install pyqt6`)
- gallery-dl (`pip install gallery-dl` or use your fork)

### Quick Start

The GUI is already installed in editable mode. You can launch it in several ways:

#### Method 1: Command Line Entry Point
```bash
gallerydl_beyond
```

#### Method 2: Python Script
```bash
python run_gallerydl_beyond.py
```

#### Method 3: Direct Module Execution
```bash
python -m gallerydl_beyond
```

## Project Structure

```
/workspace/
├── gallerydl_beyond_gui/       # Main GUI source code
│   ├── src/gallerydl_beyond/
│   │   ├── Application/        # Main window and app logic
│   │   ├── components/         # UI widgets (tabs, inputs)
│   │   ├── dialogs/            # Configuration dialogs
│   │   ├── gallerydl_utils/    # gallery-dl integration
│   │   ├── models/             # Data models
│   │   ├── threads/            # Download workers
│   │   └── common/             # Shared utilities
│   └── pyproject.toml          # Package configuration
├── gallery-dl/                 # Your forked gallery-dl (core engine)
├── run_gallerydl_beyond.py     # Convenience launcher
└── README_BEYOND.md           # This file
```

## Usage Guide

### Basic Download
1. Launch the GUI
2. Enter URLs in the Downloads tab (one per line or comma-separated)
3. Configure destination directory if needed
4. Click "Start" to begin downloading

### Managing Downloads
- **Pause**: Temporarily halt a running download
- **Stop**: Cancel a download (can be requeued)
- **Skip**: Mark as skipped without downloading
- **Requeue**: Add a stopped/failed item back to the queue

### History Tab
- View all past downloads with status indicators
- Filter by status (Completed, Failed, Stopped, Skipped)
- Right-click for context menu actions:
  - Check for new content (for supported extractors)
  - Force redownload
  - Resume stopped downloads
  - Edit tags

### Gallery-dl Options
Click "Gallery-dl Options" button to access:
- Authentication settings (cookies, username/password)
- Network configuration (proxy, retries, timeout)
- File naming and formatting
- Post-processing options
- Rate limiting and sleep delays

## Integration with Your Fork

The GUI uses gallery-dl as a subprocess, so it works seamlessly with:
- The official [mikf/gallery-dl](https://github.com/mikf/gallery-dl)
- Your forked version
- Any compatible gallery-dl installation

To use your fork:
1. Ensure your fork is installed: `pip install -e /path/to/your/fork`
2. Or configure the GUI to use a custom gallery-dl path via Settings

## Troubleshooting

### GUI Won't Start
- Ensure PyQt6 is installed: `pip install pyqt6`
- Check Python version: must be 3.12+
- Verify gallery-dl installation: `gallery-dl --version`

### Downloads Fail Immediately
- Check gallery-dl command resolution in settings
- Verify the selected gallery-dl mode matches your installation
- Review the log output for specific error messages

### No Display/Headless Environment
This GUI requires a display server (X11, Wayland, or Windows desktop). For headless operation, use gallery-dl directly from the command line.

## Comparison with Old Tkinter GUI

| Feature | Old Tkinter GUI | GalleryDL Beyond |
|---------|----------------|------------------|
| Framework | Tkinter | PyQt6 |
| Threading | Basic subprocess | Advanced worker pool |
| History | None | SQLite database |
| Queue Management | Basic | Full-featured |
| Multi-download | Sequential | Concurrent |
| UI Polish | Minimal | Professional |
| Active Development | ❌ (2023) | ✅ (Maintained) |
| Extractor Info | Manual | Integrated |

## Development

### Running from Source
```bash
cd /workspace/gallerydl_beyond_gui
pip install -e .
gallerydl_beyond
```

### Building Executable (Optional)
```bash
pip install pyinstaller
pyinstaller run_gallerydl_beyond.spec
```

## Credits

- **Original GUI**: [Alvaro Somoza](https://github.com/asomoza/gallerydl-beyond)
- **Core Engine**: [mikf/gallery-dl](https://github.com/mikf/gallery-dl)
- **Integration**: Custom setup for your forked environment

## License

Same as gallerydl-beyond: See `gallerydl_beyond_gui/LICENSE` for details.

---

**Note**: This GUI replaces the previous Tkinter-based implementation (`gallery_dl_gui.py`). The old file is kept for reference but is no longer maintained.
