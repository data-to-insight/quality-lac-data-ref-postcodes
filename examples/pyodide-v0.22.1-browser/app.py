#!/usr/bin/env python3
"""
Flask server for testing Pyodide in the browser.
Serves an HTML page that loads Pyodide and the built wheel.
"""

from flask import Flask, send_from_directory, send_file
from pathlib import Path
import os
import sys

app = Flask(__name__)

# Get the project root directory (three levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist"

# Expected wheel filename based on pyproject.toml
WHEEL_FILENAME = "quality_lac_data_ref_postcodes-2021.8.1-py3-none-any.whl"
WHEEL_PATH = DIST_DIR / WHEEL_FILENAME

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_file(Path(__file__).parent / "index.html")

@app.route('/dist/<path:filename>')
def serve_dist(filename):
    """Serve files from the dist directory."""
    return send_from_directory(DIST_DIR, filename)

@app.route('/health')
def health():
    """Health check endpoint."""
    return {"status": "ok"}

def check_wheel_exists():
    """Check if the wheel file exists and provide helpful error message if not."""
    if not WHEEL_PATH.exists():
        print("=" * 70, file=sys.stderr)
        print("ERROR: Wheel file not found!", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"\nExpected wheel file: {WHEEL_PATH}", file=sys.stderr)
        print(f"Dist directory: {DIST_DIR}", file=sys.stderr)
        print("\nTo build the wheel, run:", file=sys.stderr)
        print("  poetry build", file=sys.stderr)
        print("\nOr if using pip:", file=sys.stderr)
        print("  python -m build", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the Flask server."""
    check_wheel_exists()
    port = os.getenv("PORT", 8123)
    print(f"✓ Wheel found: {WHEEL_PATH}")
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    print(f"Open http://localhost:5000 in your browser")
    # Run on all interfaces so it's accessible
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()

