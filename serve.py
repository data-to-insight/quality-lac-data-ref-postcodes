#!/usr/bin/env python3
"""
Entry point for Poetry script to serve the Flask app for browser testing.
"""
import sys
import importlib.util
from pathlib import Path

def main():
    """Main entry point for Poetry script."""
    # Load app.py from the examples directory
    examples_dir = Path(__file__).parent / "examples" / "pyodide-v0.22.1-browser"
    app_path = examples_dir / "app.py"

    spec = importlib.util.spec_from_file_location("app", app_path)
    app_module = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app_module
    spec.loader.exec_module(app_module)

    # Call the main function from app.py
    app_module.main()

if __name__ == '__main__':
    main()

