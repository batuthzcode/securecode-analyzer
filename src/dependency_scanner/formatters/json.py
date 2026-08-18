"""Format dependency scan results as machine-readable JSON."""

from __future__ import annotations

import json

from dependency_scanner.scanner import (
    DependencyScanError,
    DependencyScanResult,
)


def format_dependency_scan_json(
    result: DependencyScanResult,
) -> str:
    """Return one dependency scan result as a JSON document."""

    _validate_result(result)

    payload = {
        "dependencies": [
            dependency.to_dict()
            for dependency in result.dependencies
        ],
        "findings": [
            finding.to_dict()
            for finding in result.findings
        ],
        "errors": [
            _serialize_error(error)
            for error in result.errors
        ],
        "summary": {
            "dependencies": len(result.dependencies),
            "findings": len(result.findings),
            "errors": len(result.errors),
            "succeeded": result.succeeded,
        },
    }

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )


def _validate_result(result: object) -> None:
    """Require a complete dependency scan result."""

    if not isinstance(result, DependencyScanResult):
        raise ValueError(
            "result must be a DependencyScanResult instance."
        )


def _serialize_error(
    error: DependencyScanError,
) -> dict[str, object]:
    """Convert one scan error into JSON-compatible data."""

    return {
        "dependency": error.dependency.to_dict(),
        "source": error.source.to_dict(),
        "message": error.message,
    }
