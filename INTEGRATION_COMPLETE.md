# 🎨 GalleryDL-Beyond GUI - Integrated Edition

## Overview
This is the modern PyQt6-based GUI for **gallery-dl v1.32.6** (your forked version), integrated with the **gallerydl-beyond** project originally by asomoza. This integration brings the powerful gallery-dl command-line tool to life with a beautiful, feature-rich graphical interface.

## ✅ Integration Status

### What Has Been Done:
1. **Forked gallery-dl**: Your fork at `/workspace/gallery_dl/` (v1.32.6) is now the core engine
2. **Integrated gallerydl-beyond**: The GUI code from `/workspace/gallerydl-beyond/` is installed and configured
3. **Verified Compatibility**: All modules import successfully with no API conflicts
4. **CLI Bridge Confirmed**: The GUI uses subprocess calls to gallery-dl CLI, ensuring maximum compatibility

### Architecture:
```
┌─────────────────────────────────────┐
│     gallerydl-beyond GUI (PyQt6)    │
│  - Modern Interface                 │
│  - Download Queue Management        │
│  - Database-backed History          │
│  - Advanced Configuration           │
└──────────────┬──────────────────────┘
               │ Subprocess Calls
               ▼
┌─────────────────────────────────────┐
│   Your Forked gallery-dl v1.32.6    │
│  - 258+ Extractors                  │
│  - Latest Features & Fixes          │
│  - Full CLI Support                 │
└─────────────────────────────────────┘
```

## 🚀 How to Launch

### Method 1: Direct Python Module (Recommended for Development)
```bash
cd /workspace
PYTHONPATH=/workspace/gallery_dl python -m gallerydl_beyond
```

### Method 2: Create a Launcher Script
Create `run_gui.py` in `/workspace`:
```python
#!/usr/bin/env python3
import sys
import os

# Add your forked gallery-dl to the path
sys.path.insert(0, '/workspace/gallery_dl')

# Launch the GUI
from gallerydl_beyond import __main__
__main__.main()
```

Then run:
```bash
python /workspace/run_gui.py
```

### Method 3: Install gallery-dl System-wide (Optional)
```bash
cd /workspace/gallery_dl
pip install -e .
# Then simply run:
gallerydl-beyond
```

## 📋 Key Features

### From gallerydl-beyond:
- **Modern PyQt6 Interface**: Clean, responsive UI with dark/light theme support
- **Download Queue System**: Manage multiple download jobs efficiently
- **Database-Backed History**: SQLite database tracks all downloads
- **Advanced Filtering**: Filter by date, size, tags, and custom expressions
- **Post-Processing**: Built-in support for metadata, archives, and conversions
- **Authentication Manager**: Easy cookie, OAuth, and credential management
- **Real-time Logging**: Color-coded output with filtering options
- **Extractor Browser**: Searchable list of all 258+ supported sites

### From Your Forked gallery-dl v1.32.6:
- **Latest Extractor Updates**: Support for newest site changes
- **Custom Modifications**: Any changes you've made to your fork
- **Bleeding Edge Features**: Access to latest gallery-dl developments
- **Full Control**: You maintain the core engine

## 🔧 Configuration

### First Run Setup:
1. Launch the GUI
2. Go to **Settings → gallery-dl Path**
3. Select **"Python env (python -m gallery_dl)"** mode
4. Ensure PYTHONPATH includes `/workspace/gallery_dl`

### Config File Locations:
- **GUI Settings**: `~/.config/gallerydl-beyond/settings.json`
- **gallery-dl Config**: `~/.config/gallery-dl/config.json`
- **Download Archive**: Configure in GUI or edit config manually

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution**: Ensure PYTHONPATH is set correctly:
```bash
export PYTHONPATH=/workspace/gallery_dl:$PYTHONPATH
```

### Issue: GUI doesn't start
**Solution**: Check PyQt6 installation:
```bash
pip install PyQt6
```

### Issue: gallery-dl commands fail
**Solution**: Verify gallery-dl is accessible:
```bash
PYTHONPATH=/workspace/gallery_dl python -m gallery_dl --version
# Should output: 1.32.6
```

### Issue: Missing extractors
**Solution**: Your fork should have all extractors. Verify:
```bash
PYTHONPATH=/workspace/gallery_dl python -c "from gallery_dl import extractor; print(len(extractor._module_map))"
```

## 📊 Comparison: Old tkinter GUI vs New PyQt6 GUI

| Feature | Old tkinter GUI | New gallerydl-beyond |
|---------|----------------|----------------------|
| **Framework** | tkinter (basic) | PyQt6 (modern) |
| **Theme Support** | None | Dark/Light modes |
| **Download Queue** | Basic | Advanced with DB |
| **History Tracking** | None | SQLite database |
| **Filtering** | Limited | Advanced expressions |
| **Post-Processing** | Manual config | Integrated UI |
| **Authentication** | Basic fields | Full manager |
| **Site Browser** | Simple list | Searchable grid |
| **Active Development** | Stalled (2023) | Active community |
| **Core Engine** | Any version | Your fork v1.32.6 |

## 🔄 Updating Your Fork

When you update your gallery-dl fork:
1. Pull changes to `/workspace/gallery_dl/`
2. Restart the GUI (it uses subprocess, so no recompile needed)
3. Test with `PYTHONPATH=/workspace/gallery_dl python -m gallery_dl --version`

## 📝 Development Notes

### Why This Integration Works:
- **Loose Coupling**: gallerydl-beyond calls gallery-dl via CLI subprocess, not direct API
- **Stable CLI**: gallery-dl's command-line interface is highly stable across versions
- **No Breaking Changes**: v1.32.6 CLI is compatible with gallerydl-beyond expectations

### Future Enhancements:
You can now:
1. Add custom features to your gallery-dl fork
2. Modify the GUI in `/workspace/gallerydl-beyond/src/gallerydl_beyond/`
3. Contribute back to either project
4. Create custom extractors without waiting for upstream

## 🎯 Next Steps

1. **Test the GUI**: Launch it and try downloading from a supported site
2. **Configure Preferences**: Set up your download directories and authentication
3. **Explore Features**: Check out the queue system, filters, and post-processors
4. **Customize**: Modify the GUI or core engine to fit your needs

## 📞 Support

- **gallery-dl Issues**: Check your fork's issues or upstream at https://github.com/mikf/gallery-dl
- **GUI Issues**: Check https://github.com/asomoza/gallerydl-beyond
- **Integration Help**: Review this document or check logs in the GUI

---

**Enjoy your upgraded gallery-dl experience!** 🎉
