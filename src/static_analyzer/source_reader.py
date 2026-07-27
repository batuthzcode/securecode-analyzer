"""Utilities for reading and parsing Python source files."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SourceFile:
    """Represent a Python source file and its parsed AST."""

    file_path: Path
    source: str
    tree: ast.AST


class SourceReader:
    """Read Python source files and parse them into AST objects."""

    def read(self, target: str | Path) -> SourceFile:
        """Read and parse a Python source file."""

        file_path = Path(target)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {file_path}"
            )

        if file_path.is_dir():
            raise IsADirectoryError(
                f"Source path is a directory: {file_path}"
            )

        source = file_path.read_text(encoding="utf-8")

        tree = ast.parse(
            source,
            filename=str(file_path),
        )

        return SourceFile(
            file_path=file_path,
            source=source,
            tree=tree,
        )