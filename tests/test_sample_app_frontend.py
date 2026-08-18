"""Browser integration tests for the sample application frontend."""

from __future__ import annotations

from flask.testing import FlaskClient

from sample_app import (
    InMemoryTaskStore,
    Task,
    create_app,
)


_HTML_HEADERS = {"Accept": "text/html"}


def create_client(
    tasks: tuple[Task, ...] = (),
) -> tuple[FlaskClient, InMemoryTaskStore]:
    """Create an isolated browser client and store."""

    store = InMemoryTaskStore(tasks)
    app = create_app(
        {"TESTING": True},
        task_store=store,
    )
    return app.test_client(), store


def create_task(
    task_id: int,
    title: str,
    *,
    description: str = "Review the findings.",
    completed: bool = False,
) -> Task:
    """Create one task for browser rendering tests."""

    return Task(
        id=task_id,
        title=title,
        description=description,
        completed=completed,
    )


def test_home_page_renders_workspace_and_task_summary() -> None:
    """The root page presents tasks and explicit status counts."""

    client, _ = create_client(
        (
            create_task(1, "Pending review"),
            create_task(
                2,
                "Completed review",
                completed=True,
            ),
        )
    )

    response = client.get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "Security work, kept in motion." in page
    assert "SecureCode Analyzer Sample App home" in page
    assert "Pending review" in page
    assert "Completed review" in page
    assert "Pending" in page
    assert "Completed" in page
    assert "<dd>2</dd>" in page


def test_home_page_renders_empty_state() -> None:
    """An empty store remains a successful browser state."""

    client, _ = create_client()

    response = client.get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Your review queue is clear." in page
    assert "Create the first task" in page


def test_home_page_escapes_task_text() -> None:
    """Jinja autoescape prevents task text from becoming markup."""

    task = create_task(
        1,
        "<script>alert('title')</script>",
        description='<img src="x" onerror="alert(1)">',
    )
    client, _ = create_client((task,))

    page = client.get("/").get_data(as_text=True)

    assert "<script>" not in page
    assert "<img src=" not in page
    assert "&lt;script&gt;" in page
    assert "&lt;img src=&#34;x&#34;" in page


def test_frontend_stylesheet_is_served() -> None:
    """Flask serves the responsive stylesheet from static."""

    client, _ = create_client()

    response = client.get("/static/style.css")
    stylesheet = response.get_data(as_text=True)

    assert response.status_code == 200
    assert response.mimetype == "text/css"
    assert ":focus-visible" in stylesheet
    assert "@media (max-width: 620px)" in stylesheet
    assert "prefers-reduced-motion" in stylesheet


def test_home_page_exposes_create_edit_and_delete_forms() -> None:
    """The browser page links every supported task action."""

    client, _ = create_client(
        (create_task(7, "Review release"),)
    )

    page = client.get("/").get_data(as_text=True)

    assert 'action="/tasks"' in page
    assert 'href="/tasks/7/edit"' in page
    assert 'action="/tasks/7/delete"' in page
    assert 'for="new-title"' in page
    assert 'for="new-description"' in page


def test_browser_create_redirects_to_home() -> None:
    """A successful browser create follows Post/Redirect/Get."""

    client, store = create_client()

    response = client.post(
        "/tasks",
        data={
            "title": "  Review release  ",
            "description": "  Inspect results.  ",
        },
        headers=_HTML_HEADERS,
    )

    created = store.get_task(1)
    assert response.status_code == 303
    assert response.headers["Location"] == "/"
    assert created.title == "Review release"
    assert created.description == "Inspect results."


def test_browser_create_redirect_renders_new_task() -> None:
    """Following the create redirect displays the stored task."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data={"title": "Publish report"},
        headers=_HTML_HEADERS,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/"
    assert "Publish report" in response.get_data(
        as_text=True
    )


def test_browser_create_error_renders_safe_form_values() -> None:
    """Invalid browser input returns HTML without mutating state."""

    client, store = create_client()

    response = client.post(
        "/tasks",
        data={
            "title": "<b>Unsafe title</b>",
            "description": "Keep this context.",
            "unexpected": "value",
        },
        headers=_HTML_HEADERS,
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 400
    assert response.mimetype == "text/html"
    assert "Unexpected fields: unexpected." in page
    assert "&lt;b&gt;Unsafe title&lt;/b&gt;" in page
    assert "Keep this context." in page
    assert store.list_tasks() == ()


def test_wildcard_accept_preserves_form_json_contract() -> None:
    """Wildcard programmatic form clients still receive JSON."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        data={"title": "API form task"},
        headers={"Accept": "*/*"},
    )

    assert response.status_code == 201
    assert response.is_json
    assert response.get_json()["task"][
        "title"
    ] == "API form task"


def test_json_create_preserves_json_with_html_accept() -> None:
    """JSON request semantics take priority over HTML preference."""

    client, _ = create_client()

    response = client.post(
        "/tasks",
        json={"title": "JSON task"},
        headers=_HTML_HEADERS,
    )

    assert response.status_code == 201
    assert response.is_json
    assert response.get_json()["task"][
        "title"
    ] == "JSON task"


def test_edit_page_prefills_current_task() -> None:
    """The edit form displays current values and status."""

    task = create_task(
        3,
        "Review report",
        description="Inspect the final report.",
        completed=True,
    )
    client, _ = create_client((task,))

    response = client.get("/tasks/3/edit")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'value="Review report"' in page
    assert "Inspect the final report." in page
    assert 'value="true"' in page
    assert "selected" in page
    assert 'for="edit-completed"' in page


def test_edit_page_escapes_current_task_text() -> None:
    """Edit form values remain escaped in attribute and text contexts."""

    task = create_task(
        1,
        '"><script>alert(1)</script>',
        description="<strong>description</strong>",
    )
    client, _ = create_client((task,))

    page = client.get(
        "/tasks/1/edit"
    ).get_data(as_text=True)

    assert "<script>" not in page
    assert "<strong>description</strong>" not in page
    assert "&lt;script&gt;" in page
    assert "&lt;strong&gt;description&lt;/strong&gt;" in page


def test_browser_edit_updates_task_and_redirects() -> None:
    """A valid edit replaces every submitted field then redirects."""

    original = create_task(1, "Initial task")
    client, store = create_client((original,))

    response = client.post(
        "/tasks/1/edit",
        data={
            "title": "Updated task",
            "description": "Ready to publish.",
            "completed": "true",
        },
        headers=_HTML_HEADERS,
    )

    updated = store.get_task(1)
    assert response.status_code == 303
    assert response.headers["Location"] == "/"
    assert updated is not original
    assert updated == Task(
        id=1,
        title="Updated task",
        description="Ready to publish.",
        completed=True,
    )


def test_browser_edit_error_preserves_store_and_form() -> None:
    """Invalid edits render inline while keeping stored state."""

    original = create_task(
        1,
        "Original task",
        description="Original description.",
    )
    client, store = create_client((original,))

    response = client.post(
        "/tasks/1/edit",
        data={
            "title": "   ",
            "description": "Unsaved description.",
            "completed": "true",
        },
        headers=_HTML_HEADERS,
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "title must not be empty." in page
    assert "Unsaved description." in page
    assert store.get_task(1) is original


def test_missing_edit_renders_html_404() -> None:
    """Unknown edit IDs produce a controlled workspace error."""

    client, _ = create_client()

    response = client.get("/tasks/99/edit")
    page = response.get_data(as_text=True)

    assert response.status_code == 404
    assert response.mimetype == "text/html"
    assert "Task 99 was not found." in page


def test_browser_delete_removes_task_and_redirects() -> None:
    """The delete form removes one task then redirects home."""

    task = create_task(1, "Remove task")
    client, store = create_client((task,))

    response = client.post(
        "/tasks/1/delete",
        headers=_HTML_HEADERS,
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/"
    assert store.get_task(1) is None


def test_missing_browser_delete_renders_html_404() -> None:
    """Unknown delete IDs produce a controlled workspace error."""

    existing = create_task(1, "Existing task")
    client, store = create_client((existing,))

    response = client.post(
        "/tasks/99/delete",
        headers=_HTML_HEADERS,
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 404
    assert "Task 99 was not found." in page
    assert store.list_tasks() == (existing,)


def test_delete_form_route_rejects_get() -> None:
    """A GET request cannot mutate state through the delete route."""

    task = create_task(1, "Keep task")
    client, store = create_client((task,))

    response = client.get("/tasks/1/delete")

    assert response.status_code == 405
    assert store.list_tasks() == (task,)
