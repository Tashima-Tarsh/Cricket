"""Top-level executable script for STRIKE//OS Pro Grand League Engine."""
import sys
import os

# Ensure repo root is always in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from gl_engine.cli import run_cli

if __name__ == "__main__":
    run_cli()
