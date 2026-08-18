"""In-memory storage for the sample Flask application."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from sample_app.models import (
    Task,
    validate_task_id,
)


class InMemoryTaskStore:
    """Store tasks in insertion order for one app instance."""

    def __init__(
        self,
        tasks: Iterable[Task] = (),
    ) -> None:
        """Initialize the store from validated unique tasks."""

        self._tasks: dict[int, Task] = {}

        for task in tasks:
            self._add_initial_task(task)

        self._next_id = max(
            self._tasks,
            default=0,
        ) + 1

    def list_tasks(self) -> tuple[Task, ...]:
        """Return an immutable task snapshot."""

        return tuple(self._tasks.values())

    def get_task(self, task_id: int) -> Task | None:
        """Return one task by ID when it exists."""

        validate_task_id(task_id)
        return self._tasks.get(task_id)

    def create_task(
        self,
        title: str,
        description: str = "",
    ) -> Task:
        """Create, store, and return a new incomplete task."""

        task = Task(
            id=self._next_id,
            title=title,
            description=description,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ) -> Task | None:
        """Replace one task while preserving ID and order."""

        validate_task_id(task_id)
        current_task = self._tasks.get(task_id)

        if current_task is None:
            return None

        updated_task = replace(
            current_task,
            title=(
                current_task.title
                if title is None
                else title
            ),
            description=(
                current_task.description
                if description is None
                else description
            ),
            completed=(
                current_task.completed
                if completed is None
                else completed
            ),
        )
        self._tasks[task_id] = updated_task
        return updated_task

    def delete_task(
        self,
        task_id: int,
    ) -> Task | None:
        """Remove and return one task when it exists."""

        validate_task_id(task_id)
        return self._tasks.pop(task_id, None)

    def _add_initial_task(self, task: Task) -> None:
        """Add one validated task during initialization."""

        if not isinstance(task, Task):
            raise ValueError(
                "tasks must contain Task instances."
            )

        if task.id in self._tasks:
            raise ValueError(
                f"Duplicate task id: {task.id}"
            )

        self._tasks[task.id] = task


def create_demo_tasks() -> tuple[Task, ...]:
    """Create safe deterministic tasks for a new app instance."""

    return (
        Task(
            id=1,
            title="Review analyzer report",
            description=(
                "Inspect the latest static analysis "
                "findings."
            ),
        ),
        Task(
            id=2,
            title="Prepare security demo",
            description=(
                "Verify the dependency scan example."
            ),
            completed=True,
        ),
    )
