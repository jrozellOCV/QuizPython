# Python Requirements

[← Back to Documentation Index](index.md)

## Python Version

**Minimum**: Python 3.8+  
**Recommended**: Python 3.10 or higher

Check version:
```bash
python --version
# or
python3 --version
```

### Required Packages

**requirements.txt:**
```
PyQt6>=6.4.0
PyQt6-Qt6>=6.4.0
PyQt6-sip>=13.4.0
```

**Package Details:**

1. **PyQt6** (>=6.4.0): GUI framework and Qt6 bindings
2. **PyQt6-Qt6** (>=6.4.0): Qt6 runtime libraries
3. **PyQt6-sip** (>=13.4.0): SIP bindings for PyQt6

### Installation

**Step 1: Create Virtual Environment**
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Verify Installation**
```bash
python -c "import PyQt6; print(PyQt6.__version__)"
```

### System Dependencies

**macOS (Homebrew):**
```bash
brew install pyqt@6
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyqt6
```

**Windows**: No additional packages needed (wheels available)

### Troubleshooting

**PyQt6 Installation Fails:**
```bash
pip install --upgrade pip
pip install PyQt6 --no-cache-dir
```

**Application Won't Start:**
- Verify Python version (3.8+)
- Check PyQt6 installation: `python -c "import PyQt6"`
- Ensure exam files exist in `exams/` directory

**Display Issues:**
- Linux: `export QT_QPA_PLATFORM=xcb`
- macOS: Update graphics drivers

---
