"""Tests for sample application data models."""

from dataclasses import FrozenInstanceError

import pytest
import sample_app

from sample_app import Task


def create_task() -> Task:
    """Create a valid task used by model tests."""

    return Task(
        id=1,
        title="Review report",
        description="Inspect findings.",
    )


def test_task_normalizes_text_fields() -> None:
    """Task strips surrounding text whitespace."""

    task = Task(
        id=1,
        title="  Review report  ",
        description="  Inspect findings.  ",
    )

    assert task.title == "Review report"
    assert task.description == "Inspect findings."


def test_task_accepts_empty_description() -> None:
    """A task description may be blank."""

    task = Task(
        id=1,
        title="Review report",
        description="   ",
    )

    assert task.description == ""


def test_task_to_dict_returns_serializable_data() -> None:
    """Task converts all fields to JSON-compatible data."""

    task = Task(
        id=4,
        title="Review report",
        description="Inspect findings.",
        completed=True,
    )

    assert task.to_dict() == {
        "id": 4,
        "title": "Review report",
        "description": "Inspect findings.",
        "completed": True,
    }


def test_task_is_frozen() -> None:
    """Task instances cannot be changed in place."""

    task = create_task()

    with pytest.raises(FrozenInstanceError):
        task.completed = True


def test_task_uses_slots() -> None:
    """Task does not expose a dynamic attribute dictionary."""

    assert not hasattr(create_task(), "__dict__")


@pytest.mark.parametrize(
    "task_id",
    [
        0,
        -1,
        True,
        1.5,
        "1",
    ],
)
def test_task_rejects_invalid_id(
    task_id: object,
) -> None:
    """Task IDs must be positive integers."""

    with pytest.raises(
        ValueError,
        match="id must be a positive integer",
    ):
        Task(
            id=task_id,  # type: ignore[arg-type]
            title="Review report",
        )


@pytest.mark.parametrize(
    "title",
    [
        "",
        "   ",
        None,
        42,
    ],
)
def test_task_rejects_invalid_title(
    title: object,
) -> None:
    """Task titles must be non-empty strings."""

    with pytest.raises(ValueError):
        Task(
            id=1,
            title=title,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "description",
    [
        None,
        42,
    ],
)
def test_task_rejects_invalid_description(
    description: object,
) -> None:
    """Task descriptions must be strings."""

    with pytest.raises(
        ValueError,
        match="description must be a string",
    ):
        Task(
            id=1,
            title="Review report",
            description=description,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "completed",
    [
        0,
        1,
        "yes",
        None,
    ],
)
def test_task_rejects_invalid_completed(
    completed: object,
) -> None:
    """Task completion values must be booleans."""

    with pytest.raises(
        ValueError,
        match="completed must be a boolean",
    ):
        Task(
            id=1,
            title="Review report",
            completed=completed,  # type: ignore[arg-type]
        )


def test_package_exports_task_model() -> None:
    """Task is available through the package interface."""

    assert sample_app.Task is Task
