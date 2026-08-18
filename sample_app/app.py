"""Create and configure the sample Flask application."""

from __future__ import annotations

from collections.abc import Mapping

from flask import Flask, current_app

from sample_app.store import (
    InMemoryTaskStore,
    create_demo_tasks,
)


_APPLICATION_NAME = "SecureCode Analyzer Sample App"
_STORE_EXTENSION_KEY = "sample_app.task_store"


def create_app(
    test_config: Mapping[str, object] | None = None,
    *,
    task_store: InMemoryTaskStore | None = None,
) -> Flask:
    """Create one isolated sample application instance."""

    app = Flask(__name__)

    if test_config is not None:
        app.config.from_mapping(test_config)

    app.extensions[_STORE_EXTENSION_KEY] = (
        _select_task_store(task_store)
    )

    _register_routes(app)
    return app


def _select_task_store(
    task_store: InMemoryTaskStore | None,
) -> InMemoryTaskStore:
    """Return an injected store or a fresh demo store."""

    if task_store is None:
        return InMemoryTaskStore(
            create_demo_tasks()
        )

    if not isinstance(
        task_store,
        InMemoryTaskStore,
    ):
        raise ValueError(
            "task_store must be an "
            "InMemoryTaskStore instance."
        )

    return task_store


def _get_task_store() -> InMemoryTaskStore:
    """Return the store bound to the current application."""

    task_store = current_app.extensions.get(
        _STORE_EXTENSION_KEY
    )

    if not isinstance(
        task_store,
        InMemoryTaskStore,
    ):
        raise RuntimeError(
            "Sample app task store is not configured."
        )

    return task_store


def _register_routes(app: Flask) -> None:
    """Register foundation routes on one application."""

    @app.get("/")
    def index() -> dict[str, object]:
        """Return application details and current tasks."""

        task_store = _get_task_store()

        return {
            "application": _APPLICATION_NAME,
            "tasks": [
                task.to_dict()
                for task in task_store.list_tasks()
            ],
        }
