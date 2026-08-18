"""Tests for sample application in-memory storage."""

import pytest

from sample_app import (
    InMemoryTaskStore,
    Task,
    create_demo_tasks,
)


def create_task(
    task_id: int,
    title: str = "Review report",
) -> Task:
    """Create a valid task used by store tests."""

    return Task(
        id=task_id,
        title=title,
    )


def test_empty_store_returns_empty_tuple() -> None:
    """A store without seed data exposes an empty snapshot."""

    store = InMemoryTaskStore()

    assert store.list_tasks() == ()


def test_store_preserves_initial_task_order() -> None:
    """Seed tasks remain in their insertion order."""

    second = create_task(2, "Second")
    first = create_task(1, "First")
    store = InMemoryTaskStore((second, first))

    assert store.list_tasks() == (second, first)


def test_store_rejects_duplicate_task_id() -> None:
    """Seed data cannot contain duplicate identifiers."""

    with pytest.raises(
        ValueError,
        match="Duplicate task id: 1",
    ):
        InMemoryTaskStore(
            (
                create_task(1, "First"),
                create_task(1, "Duplicate"),
            )
        )


def test_store_rejects_non_task_seed_value() -> None:
    """Every seed value must be a Task instance."""

    with pytest.raises(
        ValueError,
        match="must contain Task instances",
    ):
        InMemoryTaskStore(
            (object(),)  # type: ignore[arg-type]
        )


def test_store_gets_existing_and_missing_tasks() -> None:
    """Lookup returns one task or None."""

    task = create_task(3)
    store = InMemoryTaskStore((task,))

    assert store.get_task(3) is task
    assert store.get_task(4) is None


@pytest.mark.parametrize(
    "task_id",
    [
        0,
        -1,
        True,
    ],
)
def test_store_rejects_invalid_lookup_id(
    task_id: object,
) -> None:
    """Lookup uses the same positive ID contract as Task."""

    store = InMemoryTaskStore()

    with pytest.raises(ValueError):
        store.get_task(
            task_id  # type: ignore[arg-type]
        )


def test_store_creates_tasks_after_largest_seed_id() -> None:
    """New task IDs continue after the largest seed ID."""

    store = InMemoryTaskStore(
        (
            create_task(2),
            create_task(7),
        )
    )

    first_created = store.create_task(
        "  Prepare demo  ",
        "  Verify the report.  ",
    )
    second_created = store.create_task("Present demo")

    assert first_created == Task(
        id=8,
        title="Prepare demo",
        description="Verify the report.",
    )
    assert second_created.id == 9
    assert store.list_tasks()[-2:] == (
        first_created,
        second_created,
    )


def test_task_snapshot_is_not_changed_by_later_create() -> None:
    """Existing tuple snapshots remain immutable values."""

    store = InMemoryTaskStore((create_task(1),))
    snapshot = store.list_tasks()

    store.create_task("Prepare demo")

    assert len(snapshot) == 1
    assert len(store.list_tasks()) == 2


def test_demo_tasks_are_safe_and_deterministic() -> None:
    """Each app starts with the same two non-sensitive tasks."""

    first = create_demo_tasks()
    second = create_demo_tasks()

    assert first == second
    assert first is not second
    assert tuple(task.id for task in first) == (1, 2)
    assert first[0].completed is False
    assert first[1].completed is True


def test_store_instances_do_not_share_created_tasks() -> None:
    """Mutating one store does not affect another store."""

    first = InMemoryTaskStore(create_demo_tasks())
    second = InMemoryTaskStore(create_demo_tasks())

    first.create_task("Only in first")

    assert len(first.list_tasks()) == 3
    assert len(second.list_tasks()) == 2
