from ._reader import Postcodes

__all__ = ["Postcodes"]

try:
    from ._version_resolver import get_version

    __version__ = get_version()
except Exception:
    __version__ = "unknown"
