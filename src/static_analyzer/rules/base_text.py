"""Shared interface for text-based static analysis rules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from static_analyzer.models import Finding


class BaseTextRule(ABC):
    """Define the contract implemented by text analysis rules."""

    rule_id: str
    name: str
    description: str

    @abstractmethod
    def check(
        self,
        source: str,
        file_path: str,
    ) -> list[Finding]:
        """Analyze source text and return detected findings."""

        raise NotImplementedError