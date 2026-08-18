"""Public dependency scan formatter interfaces."""

from dependency_scanner.formatters.json import (
    format_dependency_scan_json,
)
from dependency_scanner.formatters.text import (
    format_dependency_scan_text,
)

__all__ = [
    "format_dependency_scan_json",
    "format_dependency_scan_text",
]
