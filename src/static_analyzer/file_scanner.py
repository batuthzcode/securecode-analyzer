"""Utilities for discovering Python files in a target directory."""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path


DEFAULT_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
    }
)


class FileScanner:
    """Discover Python files while skipping excluded directories."""

    def __init__(
        self,
        excluded_directories: Iterable[str] | None = None,
    ) -> None:
        """Initialize the scanner with default and custom exclusions."""

        custom_exclusions = frozenset(excluded_directories or ())
        self.excluded_directories = (
            DEFAULT_EXCLUDED_DIRECTORIES | custom_exclusions
        )

    def scan(self, target: str | Path) -> list[Path]:
        """Return sorted Python files discovered under the target directory."""

        target_path = Path(target)

        if not target_path.exists():
            raise FileNotFoundError(
                f"Target path does not exist: {target_path}"
            )

        if not target_path.is_dir():
            raise NotADirectoryError(
                f"Target path is not a directory: {target_path}"
            )

        python_files: list[Path] = []

        for current_root, directory_names, file_names in os.walk(
            target_path,
            followlinks=False,
        ):
            current_directory = Path(current_root)

            directory_names[:] = sorted(
                directory_name
                for directory_name in directory_names
                if directory_name not in self.excluded_directories
                and not (
                    current_directory / directory_name
                ).is_symlink()
            )

            for file_name in file_names:
                file_path = current_directory / file_name

                if file_path.suffix == ".py":
                    python_files.append(file_path)

        return sorted(python_files)