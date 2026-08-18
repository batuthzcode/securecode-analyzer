"""Parse task creation data at the HTTP boundary."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from flask import Request


_ALLOWED_FIELDS = frozenset(
    {
        "description",
        "title",
    }
)
_FORM_MIMETYPES = frozenset(
    {
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    }
)


@dataclass(frozen=True, slots=True)
class CreateTaskRequest:
    """Represent validated fields for one task creation."""

    title: str
    description: str = ""


class TaskRequestError(ValueError):
    """Represent one expected client request failure."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        """Initialize a serializable request error."""

        super().__init__(message)
        self.code = code
        self.status_code = status_code


def parse_create_task_request(
    http_request: Request,
) -> CreateTaskRequest:
    """Parse and validate one JSON or form task request."""

    payload = _load_payload(http_request)
    _reject_unexpected_fields(payload)

    if "title" not in payload:
        raise TaskRequestError(
            code="invalid_task",
            message="title is required.",
        )

    title = payload["title"]
    description = payload.get("description", "")

    if not isinstance(title, str):
        raise TaskRequestError(
            code="invalid_task",
            message="title must be a string.",
        )

    if not isinstance(description, str):
        raise TaskRequestError(
            code="invalid_task",
            message="description must be a string.",
        )

    return CreateTaskRequest(
        title=title,
        description=description,
    )


def _load_payload(
    http_request: Request,
) -> Mapping[str, object]:
    """Load one supported request body as a mapping."""

    if http_request.is_json:
        payload = http_request.get_json(
            silent=True
        )

        if not isinstance(payload, dict):
            raise TaskRequestError(
                code="invalid_request",
                message=(
                    "Request body must contain a valid "
                    "JSON object."
                ),
            )

        return payload

    if http_request.mimetype in _FORM_MIMETYPES:
        return http_request.form.to_dict(
            flat=True
        )

    raise TaskRequestError(
        code="unsupported_media_type",
        message=(
            "Content-Type must be application/json "
            "or form data."
        ),
        status_code=415,
    )


def _reject_unexpected_fields(
    payload: Mapping[str, object],
) -> None:
    """Reject fields that are not part of task creation."""

    unexpected_fields = sorted(
        set(payload) - _ALLOWED_FIELDS
    )

    if not unexpected_fields:
        return

    field_list = ", ".join(unexpected_fields)
    raise TaskRequestError(
        code="invalid_request",
        message=f"Unexpected fields: {field_list}.",
    )
