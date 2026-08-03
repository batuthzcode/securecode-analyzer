"""Parse exact-pinned dependencies from requirements files."""

from __future__ import annotations

import re
from pathlib import Path

from dependency_scanner.models import Dependency


_REQUIREMENT_PATTERN = re.compile(
    r"^(?P<name>"
    r"[A-Za-z0-9]"
    r"(?:[A-Za-z0-9._-]*[A-Za-z0-9])?"
    r")"
    r"\s*==\s*"
    r"(?P<version>[^\s#;=]+)"
    r"$"
)


class RequirementsParseError(ValueError):
    """Represent an invalid active requirements line."""

    __slots__ = (
        "source_file",
        "line_number",
        "line",
        "reason",
    )

    def __init__(
        self,
        *,
        source_file: str,
        line_number: int,
        line: str,
        reason: str,
    ) -> None:
        """Initialize a requirements parsing error."""

        self.source_file = source_file
        self.line_number = line_number
        self.line = line
        self.reason = reason

        super().__init__(
            f"{source_file}:{line_number}: {reason}"
        )


def parse_requirement_line(
    line: str,
    *,
    source_file: str,
    line_number: int,
) -> Dependency | None:
    """Parse one supported requirement line."""

    stripped_line = line.strip()

    if not stripped_line:
        return None

    if stripped_line.startswith("#"):
        return None

    match = _REQUIREMENT_PATTERN.fullmatch(
        stripped_line
    )

    if match is None:
        raise RequirementsParseError(
            source_file=source_file,
            line_number=line_number,
            line=line,
            reason="Unsupported requirement format.",
        )

    return Dependency(
        name=match.group("name"),
        version=match.group("version"),
        operator="==",
        source_file=source_file,
        line_number=line_number,
    )


def parse_requirements_text(
    text: str,
    *,
    source_file: str,
) -> tuple[Dependency, ...]:
    """Parse dependencies from requirements text."""

    dependencies: list[Dependency] = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        dependency = parse_requirement_line(
            line,
            source_file=source_file,
            line_number=line_number,
        )

        if dependency is not None:
            dependencies.append(dependency)

    return tuple(dependencies)


def parse_requirements_file(
    file_path: str | Path,
) -> tuple[Dependency, ...]:
    """Read and parse a UTF-8 requirements file."""

    path = Path(file_path)
    text = path.read_text(encoding="utf-8")

    return parse_requirements_text(
        text,
        source_file=str(path),
    )