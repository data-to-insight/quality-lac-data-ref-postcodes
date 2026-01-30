"""Version resolution module for quality-lac-data-ref-postcodes package.

This module provides robust version detection that works across different Python
environments, including Pyodide/WASM. It uses multiple fallback strategies to
reliably retrieve the package version string from pyproject.toml or installed
package metadata.

PEP 440 Version Format Support:
    This module supports all PEP 440 version formats including:
    - Pre-releases: 2025.11.1-alpha.1, 2025.11.1-beta.2, 2025.11.1-rc.1
    - Post-releases: 2025.11.1-post.1
    - Dev releases: 2025.11.1+dev
    - Local versions: 2025.11.1+local

    Note: The version string returned is the raw version from pyproject.toml,
    not the PEP 440 normalized version used in wheel filenames. For example,
    "2025.11.1-alpha.1" in pyproject.toml becomes "2025.11.1a1" in wheel
    filenames, but this function returns "2025.11.1-alpha.1".

Pyodide Compatibility:
    This module is designed to work in Pyodide/WASM environments where
    importlib.metadata may have limitations. It uses only Python standard
    library features (Python 3.10+) and does not require external dependencies
    like tomllib or tomli, ensuring compatibility with Pyodide's constraints.

Strategy Order:
    The version resolution uses the following strategies in order:
    1. Parse pyproject.toml directly (most reliable for pre-releases)
    2. Use importlib.metadata.version() (standard Python environments)
    3. Iterate distributions (works better in Pyodide)
    4. Fallback to "unknown" if all strategies fail
"""

from importlib.metadata import version, PackageNotFoundError, distributions
from pathlib import Path
from typing import Optional

# Package name as it appears in pyproject.toml
PACKAGE_NAME = "quality-lac-data-ref-postcodes"

# Fallback version string when all resolution strategies fail
FALLBACK_VERSION = "unknown"


def _strip_toml_quotes(version_str: str) -> str:
    """Remove quotes from a TOML version string.

    Handles single quotes ('), double quotes ("), and triple quotes
    (three double quotes or three single quotes).
    This is a helper function for parsing version strings from pyproject.toml.

    Args:
        version_str: The version string that may be quoted.

    Returns:
        The version string with quotes removed.

    Examples:
        >>> _strip_toml_quotes('"2025.11.1-alpha.1"')
        '2025.11.1-alpha.1'
        >>> _strip_toml_quotes("'2025.11.1'")
        '2025.11.1'
        >>> _strip_toml_quotes('2025.11.1')
        '2025.11.1'
    """
    version_str = version_str.strip()

    # Handle triple quotes (three double quotes or three single quotes)
    triple_double = '"' * 3
    triple_single = "'" * 3
    if version_str.startswith(triple_double) or version_str.startswith(triple_single):
        quote_char = version_str[0:3]
        end_idx = version_str.find(quote_char, 3)
        if end_idx != -1:
            return version_str[3:end_idx]
        else:
            return version_str[3:].strip()

    # Handle single or double quotes
    if (version_str.startswith('"') and version_str.endswith('"')) or (
        version_str.startswith("'") and version_str.endswith("'")
    ):
        return version_str[1:-1]

    # No quotes, return as-is
    return version_str


def _parse_version_from_toml_line(line: str) -> Optional[str]:
    """Extract version string from a TOML line.

    Parses a line that may contain "version = ..." and extracts the version
    value. Handles comments, various quote styles, and whitespace.

    Args:
        line: A line from a TOML file that may contain a version declaration.

    Returns:
        The version string if found, None otherwise.

    Examples:
        >>> _parse_version_from_toml_line('version = "2025.11.1-alpha.1"')
        '2025.11.1-alpha.1'
        >>> _parse_version_from_toml_line("version = '2025.11.1'  # comment")
        '2025.11.1'
        >>> _parse_version_from_toml_line('name = "package"')
        None
    """
    # Strip the line and remove comments (everything after #)
    stripped = line.strip()
    if "#" in stripped:
        # Remove comment, but be careful not to remove # inside quotes
        # Simple approach: find first # that's not inside quotes
        in_quotes = False
        quote_char = None
        for i, char in enumerate(stripped):
            if char in ('"', "'") and (i == 0 or stripped[i - 1] != "\\"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            elif char == "#" and not in_quotes:
                stripped = stripped[:i].strip()
                break

    # Check if this line contains a version declaration
    if not stripped.startswith("version"):
        return None

    # Check for "version =" or "version="
    if "=" not in stripped:
        return None

    # Extract everything after the = sign
    version_part = stripped.split("=", 1)[1].strip()
    if not version_part:
        return None

    # Remove quotes
    version_str = _strip_toml_quotes(version_part)
    return version_str if version_str else None


def _get_version_from_pyproject_toml() -> Optional[str]:
    """Get version from pyproject.toml file.

    This strategy reads the pyproject.toml file directly and parses the version
    from the [tool.poetry] section. This is the most reliable method for
    pre-releases because it returns the exact version string as written in
    pyproject.toml, before any PEP 440 normalization that occurs during
    package building.

    This strategy works even when:
    - The package is not installed
    - importlib.metadata has issues (common in Pyodide)
    - The package is in development mode

    Returns:
        The version string from pyproject.toml if found, None otherwise.

    Examples:
        If pyproject.toml contains: version = "2025.11.1-alpha.1"
        Returns: "2025.11.1-alpha.1"
    """
    try:
        # Locate pyproject.toml (two levels up from this file)
        package_dir = Path(__file__).parent.parent
        pyproject_file = package_dir / "pyproject.toml"

        if not pyproject_file.exists():
            return None

        # Read and parse the file
        content = pyproject_file.read_text(encoding="utf-8")

        # Track whether we're in the [tool.poetry] section
        in_poetry_section = False

        for line in content.splitlines():
            stripped = line.strip()

            # Check for section headers
            if stripped.startswith("[") and stripped.endswith("]"):
                section_name = stripped[1:-1].strip()
                in_poetry_section = section_name == "tool.poetry"
                continue

            # Only parse version lines when we're in the [tool.poetry] section
            if in_poetry_section:
                version_str = _parse_version_from_toml_line(line)
                if version_str:
                    return version_str

        return None
    except (OSError, IOError, UnicodeDecodeError):
        # File doesn't exist, can't be read, or encoding issue
        return None
    except Exception:
        # Other unexpected errors (keep broad for Pyodide compatibility)
        return None


def _get_version_from_importlib_metadata() -> Optional[str]:
    """Get version using importlib.metadata.version().

    This strategy uses the standard library's importlib.metadata.version()
    function, which reads version information from installed package metadata.
    This works well in standard Python environments where the package is
    properly installed.

    Limitations:
    - May not work in Pyodide/WASM environments
    - Requires the package to be installed
    - May have issues with pre-release versions in some environments

    Returns:
        The version string from package metadata if found, None otherwise.
    """
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return None
    except Exception:
        # Other exceptions (keep broad for compatibility)
        return None


def _get_version_from_distributions() -> Optional[str]:
    """Get version by iterating through installed distributions.

    This strategy iterates through all installed distributions and matches
    by package name. This approach works better in Pyodide environments
    where importlib.metadata.version() may have limitations.

    The matching handles package name normalization (hyphens vs underscores),
    as package names in metadata may differ from the canonical name.

    Returns:
        The version string from distribution metadata if found, None otherwise.
    """
    try:
        for dist in distributions():
            dist_name = dist.metadata.get("Name", "")
            if not dist_name:
                continue

            # Normalize names for comparison (handle hyphens/underscores)
            dist_name_normalized = dist_name.lower().replace("_", "-")
            package_name_normalized = PACKAGE_NAME.lower()

            if dist_name_normalized == package_name_normalized:
                version_str = dist.version
                if version_str:
                    return version_str

        return None
    except Exception:
        # Keep broad exception handling for Pyodide compatibility
        return None


def get_version() -> str:
    """Get package version using multiple fallback strategies.

    This function attempts to retrieve the package version using a series of
    fallback strategies, ensuring reliability across different Python
    environments including Pyodide/WASM.

    Strategy Order:
        1. Parse pyproject.toml directly (most reliable for pre-releases)
           - Returns the exact version string as written in pyproject.toml
           - Works even when package is not installed
           - Best for development and pre-release versions

        2. Use importlib.metadata.version() (standard Python)
           - Uses standard library metadata
           - Works when package is properly installed
           - May fail in Pyodide environments

        3. Iterate distributions (Pyodide-friendly)
           - Scans all installed distributions
           - Handles package name normalization
           - More reliable in Pyodide/WASM environments

        4. Fallback to "unknown"
           - Returns "unknown" if all strategies fail

    Return Value:
        The version string from pyproject.toml or package metadata. This is
        the raw version string (e.g., "2025.11.1-alpha.1"), not the PEP 440
        normalized version used in wheel filenames (e.g., "2025.11.1a1").

        If all strategies fail, returns "unknown".

    PEP 440 Support:
        Supports all PEP 440 version formats:
        - Pre-releases: 2025.11.1-alpha.1, 2025.11.1-beta.2, 2025.11.1-rc.1
        - Post-releases: 2025.11.1-post.1
        - Dev releases: 2025.11.1+dev
        - Local versions: 2025.11.1+local

    Pyodide Compatibility:
        This function is designed to work in Pyodide/WASM environments where
        importlib.metadata may have limitations. It uses only Python standard
        library features and does not require external dependencies.

    Examples:
        >>> get_version()  # Returns version from pyproject.toml or metadata
        '2025.11.1-alpha.1'

        In a standard Python environment with installed package:
        >>> get_version()
        '2025.11.1-alpha.1'

        In Pyodide/WASM environment:
        >>> get_version()
        '2025.11.1-alpha.1'

        If version cannot be determined:
        >>> get_version()
        'unknown'

    Returns:
        The package version string, or "unknown" if version cannot be determined.
    """
    # Strategy 1: Try reading from pyproject.toml first
    # This ensures we get the exact version string including pre-release suffixes
    # even if importlib.metadata has issues or the package isn't fully installed
    version_str = _get_version_from_pyproject_toml()
    if version_str:
        return version_str

    # Strategy 2: Try importlib.metadata.version() (works in regular Python)
    # Note: This should support pre-releases, but may fail in Pyodide or if
    # package metadata isn't properly registered
    version_str = _get_version_from_importlib_metadata()
    if version_str:
        return version_str

    # Strategy 3: Try to find distribution by iterating (works better in Pyodide)
    version_str = _get_version_from_distributions()
    if version_str:
        return version_str

    # Strategy 4: Fallback to unknown
    return FALLBACK_VERSION
