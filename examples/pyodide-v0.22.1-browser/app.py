#!/usr/bin/env python3
"""
Flask server for testing Pyodide in the browser.
Serves an HTML page that loads Pyodide and the built wheel.
"""

from flask import Flask, send_from_directory, render_template
from pathlib import Path
import os
import sys
import qlacref_postcodes

# Note: __version__ is set by _version_resolver.get_version() which retrieves
# the raw version string from pyproject.toml (e.g., "2025.11.1-alpha.1").
# Wheel filenames use PEP 440 normalized versions (e.g., "2025.11.1a1"),
# so we scan for the actual wheel file rather than constructing the filename.
print(f"qlacref_postcodes version: {qlacref_postcodes.__version__}")

# Get the project root directory (three levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist"


def find_wheel_file():
    """Find the actual wheel file in dist directory.

    Poetry normalizes versions according to PEP 440 when building wheels.
    For example, "2025.11.1-alpha.1" in pyproject.toml becomes "2025.11.1a1"
    in the wheel filename. Since __version__ contains the raw version string
    from pyproject.toml, we scan for the actual wheel file rather than
    constructing the filename from __version__.
    """
    package_name = "quality_lac_data_ref_postcodes"
    if not DIST_DIR.exists():
        return None

    # Look for wheel files matching the package name
    wheel_files = list(DIST_DIR.glob(f"{package_name}-*.whl"))
    if wheel_files:
        # Return the most recently modified wheel (in case of multiple builds)
        return max(wheel_files, key=lambda p: p.stat().st_mtime)
    return None


# Find the actual wheel file (handles PEP 440 normalization)
WHEEL_PATH = find_wheel_file()
if WHEEL_PATH:
    WHEEL_FILENAME = WHEEL_PATH.name
else:
    # Fallback: construct expected filename (may not match due to normalization)
    WHEEL_FILENAME = f"quality_lac_data_ref_postcodes-{qlacref_postcodes.__version__}-py3-none-any.whl"
    WHEEL_PATH = DIST_DIR / WHEEL_FILENAME

# Configure Flask to use the current directory for templates
app = Flask(__name__, template_folder=Path(__file__).parent)


@app.route("/")
def index():
    """Serve the main HTML page with dynamic wheel version."""
    return render_template("index.html", wheel_filename=WHEEL_FILENAME)


@app.route("/dist/<path:filename>")
def serve_dist(filename):
    """Serve files from the dist directory."""
    return send_from_directory(DIST_DIR, filename)


@app.route("/health")
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
    print(f"Open http://localhost:{port} in your browser")
    # Run on all interfaces so it's accessible
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
