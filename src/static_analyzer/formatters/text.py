"""Format static analysis findings as human-readable text."""

from __future__ import annotations

from collections.abc import Iterable

from static_analyzer.models import Finding


def format_findings_text(
    findings: Iterable[Finding],
) -> str:
    """Return findings formatted as human-readable terminal text."""

    finding_items = tuple(findings)

    if not finding_items:
        return "No findings found."

    finding_lines = [
        _format_finding(finding)
        for finding in finding_items
    ]

    finding_count = len(finding_items)

    if finding_count == 1:
        summary = "1 finding found."
    else:
        summary = f"{finding_count} findings found."

    return "\n".join(
        [
            *finding_lines,
            "",
            summary,
        ]
    )


def _format_finding(finding: Finding) -> str:
    """Format one finding without modifying it."""

    location = (
        f"{finding.file_path}:"
        f"{finding.line_number}"
    )

    if finding.column_number is not None:
        location += f":{finding.column_number}"

    severity = finding.severity.value.upper()

    return (
        f"[{severity}] "
        f"{finding.rule_id} "
        f"{location} - "
        f"{finding.message}"
    )