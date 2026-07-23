"""Shared interface for static analysis rules."""

from __future__ import annotations

import ast
from abc import ABC, abstractmethod

from static_analyzer.models import Finding


class BaseRule(ABC):
    """Define the common contract implemented by every analysis rule."""

    rule_id: str
    name: str
    description: str

    @abstractmethod
    def check(self, tree: ast.AST, file_path: str) -> list[Finding]:
        """Analyze an AST and return detected findings."""
        raise NotImplementedError