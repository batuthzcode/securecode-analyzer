"""Data models used by the sample Flask application."""

from __future__ import annotations

from dataclasses import dataclass


def validate_task_id(task_id: object) -> None:
    """Validate a positive integer task identifier."""

    if type(task_id) is not int or task_id <= 0:
        raise ValueError(
            "id must be a positive integer."
        )


def _clean_title(title: object) -> str:
    """Return a stripped, non-empty task title."""

    if not isinstance(title, str):
        raise ValueError("title must be a string.")

    cleaned_title = title.strip()

    if not cleaned_title:
        raise ValueError("title must not be empty.")

    return cleaned_title


def _clean_description(description: object) -> str:
    """Return a stripped task description."""

    if not isinstance(description, str):
        raise ValueError(
            "description must be a string."
        )

    return description.strip()


def _validate_completed(completed: object) -> None:
    """Validate the task completion flag."""

    if type(completed) is not bool:
        raise ValueError(
            "completed must be a boolean."
        )


@dataclass(frozen=True, slots=True)
class Task:
    """Represent one in-memory sample application task."""

    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate and normalize task fields."""

        validate_task_id(self.id)
        _validate_completed(self.completed)

        object.__setattr__(
            self,
            "title",
            _clean_title(self.title),
        )
        object.__setattr__(
            self,
            "description",
            _clean_description(self.description),
        )

    def to_dict(self) -> dict[str, object]:
        """Convert the task to JSON-compatible data."""

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
        }
