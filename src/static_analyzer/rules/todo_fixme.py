"""Detect TODO and FIXME markers in Python comments."""

from __future__ import annotations

import io
import re
import tokenize

from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base_text import BaseTextRule


_MARKER_PATTERN = re.compile(
    r"\b(?:TODO|FIXME)\b",
    re.IGNORECASE,
)


class TodoFixmeRule(BaseTextRule):
    """Detect TODO and FIXME markers in Python comment tokens."""

    rule_id = "SA003"
    name = "TODO/FIXME Comment"
    description = "Detect TODO and FIXME markers in Python comments."

    def check(
        self,
        source: str,
        file_path: str,
    ) -> list[Finding]:
        """Return findings for TODO and FIXME markers in comments."""

        findings: list[Finding] = []

        tokens = tokenize.generate_tokens(
            io.StringIO(source).readline
        )

        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue

            for match in _MARKER_PATTERN.finditer(token.string):
                marker = match.group().upper()

                if marker == "TODO":
                    message = "TODO comment found."
                    severity = Severity.INFO
                else:
                    message = "FIXME comment found."
                    severity = Severity.WARNING

                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        message=message,
                        file_path=file_path,
                        line_number=token.start[0],
                        severity=severity,
                        column_number=(
                            token.start[1]
                            + match.start()
                            + 1
                        ),
                    )
                )

        return findings