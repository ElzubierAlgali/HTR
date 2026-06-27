#!/usr/bin/env python3
"""Legacy entry point — delegates to unified Gradio app."""

import subprocess
import sys
from pathlib import Path

app = Path(__file__).resolve().parents[1] / "app" / "gradio_app.py"
raise SystemExit(subprocess.call([sys.executable, str(app)] + sys.argv[1:]))
