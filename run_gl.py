"""Top-level executable script for India vs West Indies Grand League Engine."""
import sys
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from gl_engine.cli import run_cli

if __name__ == "__main__":
    run_cli()
