"""Detect string literals assigned to sensitive variable names."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Iterator

from static_analyzer.models import Finding, Severity
from static_analyzer.rules.base import BaseRule


_SENSITIVE_NAMES = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "access_token",
        "auth_token",
        "client_secret",
        "private_key",
    }
)


class HardcodedSecretRule(BaseRule):
    """Detect possible secrets stored directly in source code."""

    rule_id = "SA005"
    name = "Hardcoded Secret"
    description = (
        "Detect string literals assigned to sensitive variable names."
    )

    def check(
        self,
        tree: ast.AST,
        file_path: str,
    ) -> list[Finding]:
        """Return findings for possible hardcoded secret assignments."""

        sensitive_targets = self._find_sensitive_targets(tree)
        unique_targets = self._deduplicate_targets(
            sensitive_targets
        )

        return [
            self._create_finding(target, file_path)
            for target in unique_targets
        ]

    @classmethod
    def _find_sensitive_targets(
        cls,
        tree: ast.AST,
    ) -> list[ast.expr]:
        """Return sensitive assignment targets in source order."""

        sensitive_targets = (
            target
            for target in cls._iter_assignment_targets(tree)
            if cls._is_sensitive_target(target)
        )

        return sorted(
            sensitive_targets,
            key=lambda target: (
                target.lineno,
                target.col_offset,
            ),
        )

    @classmethod
    def _iter_assignment_targets(
        cls,
        tree: ast.AST,
    ) -> Iterator[ast.expr]:
        """Yield targets assigned a non-empty string literal."""

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if cls._is_non_empty_string(node.value):
                    yield from node.targets

            elif isinstance(node, ast.AnnAssign):
                if cls._is_non_empty_string(node.value):
                    yield node.target

    @staticmethod
    def _deduplicate_targets(
        targets: Iterable[ast.expr],
    ) -> list[ast.expr]:
        """Remove duplicate target objects while preserving order."""

        unique_targets: list[ast.expr] = []
        seen_targets: set[int] = set()

        for target in targets:
            target_identity = id(target)

            if target_identity in seen_targets:
                continue

            seen_targets.add(target_identity)
            unique_targets.append(target)

        return unique_targets

    def _create_finding(
        self,
        target: ast.expr,
        file_path: str,
    ) -> Finding:
        """Create a hardcoded-secret finding for one target."""

        return Finding(
            rule_id=self.rule_id,
            message="Possible hardcoded secret found.",
            file_path=file_path,
            line_number=target.lineno,
            severity=Severity.WARNING,
            column_number=target.col_offset + 1,
        )

    @staticmethod
    def _is_non_empty_string(
        value: ast.expr | None,
    ) -> bool:
        """Return whether the value is a non-empty string literal."""

        return (
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and bool(value.value.strip())
        )

    @classmethod
    def _is_sensitive_target(
        cls,
        target: ast.expr,
    ) -> bool:
        """Return whether an assignment target has a sensitive name."""

        target_name = cls._get_target_name(target)

        if target_name is None:
            return False

        normalized_name = target_name.casefold()
        padded_name = f"_{normalized_name}_"

        return any(
            f"_{sensitive_name}_" in padded_name
            for sensitive_name in _SENSITIVE_NAMES
        )

    @staticmethod
    def _get_target_name(
        target: ast.expr,
    ) -> str | None:
        """Extract a supported assignment target name."""

        if isinstance(target, ast.Name):
            return target.id

        if isinstance(target, ast.Attribute):
            return target.attr

        return None