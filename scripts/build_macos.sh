#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENTRY_FILE="$ROOT_DIR/ICT/test.py"
ICON_FILE="$ROOT_DIR/ICT/azwm0-ubi0j.icns"

python3 -m PyInstaller \
  --windowed \
  --name "加班计算器" \
  --clean \
  --noconfirm \
  --hidden-import=PyQt6.QtCore \
  --hidden-import=PyQt6.QtGui \
  --hidden-import=PyQt6.QtWidgets \
  --hidden-import=PyQt6.QtWebEngineWidgets \
  --hidden-import=PyQt6.QtWebEngineCore \
  --hidden-import=PyQt6.QtWebChannel \
  --collect-data PyQt6.QtWebEngineWidgets \
  --collect-data PyQt6.QtWebEngineCore \
  --icon "$ICON_FILE" \
  "$ENTRY_FILE"
