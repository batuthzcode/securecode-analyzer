"""Format static analysis findings as machine-readable JSON."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from static_analyzer.models import Finding


def format_findings_json(
    findings: Iterable[Finding],
) -> str:
    """Return findings formatted as a machine-readable JSON document."""

    finding_items = tuple(findings)

    payload: dict[str, Any] = {
        "findings": [
            finding.to_dict()
            for finding in finding_items
        ],
        "summary": {
            "total": len(finding_items),
        },
    }

    return json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )