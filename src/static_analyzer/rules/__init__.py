"""Public interfaces and implementations for static analysis rules."""

from static_analyzer.rules.base import BaseRule
from static_analyzer.rules.long_function import LongFunctionRule

__all__ = ["BaseRule", "LongFunctionRule"]