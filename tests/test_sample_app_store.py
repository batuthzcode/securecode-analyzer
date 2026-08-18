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


def test_store_updates_task_with_immutable_replacement() -> None:
    """Update returns a new Task and preserves omitted fields."""

    original = Task(
        id=1,
        title="Original title",
        description="Original description",
        completed=False,
    )
    store = InMemoryTaskStore((original,))

    updated = store.update_task(
        1,
        title="  Updated title  ",
    )

    assert updated == Task(
        id=1,
        title="Updated title",
        description="Original description",
        completed=False,
    )
    assert updated is not original
    assert original.title == "Original title"
    assert store.get_task(1) is updated


def test_store_updates_multiple_fields() -> None:
    """Update can replace description and completion together."""

    store = InMemoryTaskStore(
        (create_task(1),)
    )

    updated = store.update_task(
        1,
        description="Complete review.",
        completed=True,
    )

    assert updated.description == "Complete review."
    assert updated.completed is True


def test_store_update_preserves_task_order() -> None:
    """Replacing an existing dictionary value keeps order."""

    first = create_task(1, "First")
    second = create_task(2, "Second")
    store = InMemoryTaskStore((first, second))

    updated = store.update_task(
        1,
        title="Updated first",
    )

    assert store.list_tasks() == (
        updated,
        second,
    )


def test_store_update_returns_none_for_missing_task() -> None:
    """Updating an unknown ID does not create a task."""

    store = InMemoryTaskStore((create_task(1),))

    updated = store.update_task(
        99,
        title="Missing",
    )

    assert updated is None
    assert store.list_tasks() == (create_task(1),)


def test_store_invalid_update_preserves_state() -> None:
    """Validation completes before the stored value changes."""

    original = create_task(1)
    store = InMemoryTaskStore((original,))

    with pytest.raises(
        ValueError,
        match="title must not be empty",
    ):
        store.update_task(
            1,
            title="   ",
        )

    assert store.get_task(1) is original


def test_store_deletes_and_returns_existing_task() -> None:
    """Delete removes exactly one task and returns it."""

    first = create_task(1, "First")
    second = create_task(2, "Second")
    store = InMemoryTaskStore((first, second))

    deleted = store.delete_task(1)

    assert deleted is first
    assert store.list_tasks() == (second,)


def test_store_delete_returns_none_for_missing_task() -> None:
    """Deleting an unknown ID leaves state unchanged."""

    task = create_task(1)
    store = InMemoryTaskStore((task,))

    deleted = store.delete_task(99)

    assert deleted is None
    assert store.list_tasks() == (task,)


def test_store_does_not_reuse_deleted_task_id() -> None:
    """Create continues from the monotonic ID sequence."""

    store = InMemoryTaskStore(
        (
            create_task(1),
            create_task(2),
        )
    )

    store.delete_task(2)
    created = store.create_task("Third")

    assert created.id == 3


@pytest.mark.parametrize(
    "operation",
    [
        "update",
        "delete",
    ],
)
def test_store_write_rejects_invalid_task_id(
    operation: str,
) -> None:
    """Update and delete preserve the positive ID contract."""

    store = InMemoryTaskStore()

    with pytest.raises(ValueError):
        if operation == "update":
            store.update_task(
                0,
                title="Invalid",
            )
        else:
            store.delete_task(0)
