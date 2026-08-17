"""Query the OSV API for Python package vulnerabilities."""

from __future__ import annotations

import json
import math
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dependency_scanner.osv_models import OsvQueryResponse
from dependency_scanner.osv_parser import (
    OsvResponseParseError,
    parse_osv_query_response,
)
from dependency_scanner.package_normalizer import (
    normalize_package_name,
)


_OSV_QUERY_URL = "https://api.osv.dev/v1/query"
_PYPI_ECOSYSTEM = "PyPI"
_DEFAULT_TIMEOUT = 10.0


class OsvQueryError(RuntimeError):
    """Represent an error while querying the OSV service."""


class OsvQueryClient:
    """Query OSV for vulnerabilities affecting Python packages."""

    def __init__(
        self,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        """Create an OSV query client."""

        self._timeout = _validate_timeout(
            timeout
        )

    @property
    def timeout(self) -> float:
        """Return the configured HTTP timeout."""

        return self._timeout

    def query_package(
        self,
        package_name: str,
        version: str,
        page_token: str | None = None,
    ) -> OsvQueryResponse:
        """Query one OSV response page for a package version."""

        payload = _build_query_payload(
            package_name,
            version,
            page_token,
        )
        request = _build_request(payload)
        response_body = _send_request(
            request,
            self._timeout,
        )
        decoded_payload = _decode_response(
            response_body
        )

        try:
            return parse_osv_query_response(
                decoded_payload
            )
        except OsvResponseParseError as error:
            raise OsvQueryError(
                f"OSV response is invalid: {error}"
            ) from error


def _build_query_payload(
    package_name: str,
    version: str,
    page_token: str | None,
) -> dict[str, object]:
    """Build an OSV package/version query payload."""

    normalized_name = _normalize_package_name(
        package_name
    )
    validated_version = _validate_required_string(
        version,
        "version",
    )

    payload: dict[str, object] = {
        "package": {
            "name": normalized_name,
            "ecosystem": _PYPI_ECOSYSTEM,
        },
        "version": validated_version,
    }

    if page_token is not None:
        payload["page_token"] = (
            _validate_required_string(
                page_token,
                "page_token",
            )
        )

    return payload


def _normalize_package_name(
    package_name: str,
) -> str:
    """Normalize a package name and translate validation errors."""

    try:
        return normalize_package_name(
            package_name
        )
    except ValueError as error:
        raise OsvQueryError(
            f"Invalid package_name: {error}"
        ) from error


def _validate_required_string(
    value: object,
    field_name: str,
) -> str:
    """Validate a required non-empty string."""

    if not isinstance(value, str):
        raise OsvQueryError(
            f"{field_name} must be a string."
        )

    cleaned_value = value.strip()

    if not cleaned_value:
        raise OsvQueryError(
            f"{field_name} must not be empty."
        )

    return cleaned_value


def _validate_timeout(
    timeout: object,
) -> float:
    """Validate and normalize an HTTP timeout."""

    if (
        isinstance(timeout, bool)
        or not isinstance(
            timeout,
            (int, float),
        )
    ):
        raise OsvQueryError(
            "timeout must be a positive number."
        )

    normalized_timeout = float(timeout)

    if (
        not math.isfinite(normalized_timeout)
        or normalized_timeout <= 0
    ):
        raise OsvQueryError(
            "timeout must be a positive number."
        )

    return normalized_timeout


def _build_request(
    payload: dict[str, object],
) -> Request:
    """Build the HTTP request sent to OSV."""

    request_body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    return Request(
        _OSV_QUERY_URL,
        data=request_body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )


def _send_request(
    request: Request,
    timeout: float,
) -> bytes:
    """Send an OSV request and return its response body."""

    try:
        with urlopen(
            request,
            timeout=timeout,
        ) as response:
            _validate_http_status(response)
            return _read_response_body(
                response
            )
    except OsvQueryError:
        raise
    except HTTPError as error:
        raise OsvQueryError(
            "OSV request failed with HTTP "
            f"status {error.code}."
        ) from error
    except URLError as error:
        _raise_url_error(error)
    except (TimeoutError, socket.timeout) as error:
        raise OsvQueryError(
            "OSV request timed out."
        ) from error
    except OSError as error:
        raise OsvQueryError(
            f"OSV network request failed: {error}"
        ) from error


def _raise_url_error(
    error: URLError,
) -> None:
    """Translate a urllib URL error."""

    if isinstance(
        error.reason,
        (TimeoutError, socket.timeout),
    ):
        raise OsvQueryError(
            "OSV request timed out."
        ) from error

    raise OsvQueryError(
        f"OSV network request failed: {error.reason}"
    ) from error


def _validate_http_status(
    response: object,
) -> None:
    """Reject explicit non-success HTTP status values."""

    status = getattr(
        response,
        "status",
        None,
    )

    if status is None:
        return

    if (
        not isinstance(status, int)
        or not 200 <= status < 300
    ):
        raise OsvQueryError(
            "OSV request failed with HTTP "
            f"status {status}."
        )


def _read_response_body(
    response: object,
) -> bytes:
    """Read an HTTP response body."""

    read = getattr(
        response,
        "read",
        None,
    )

    if not callable(read):
        raise OsvQueryError(
            "OSV response body could not be read."
        )

    try:
        response_body = read()
    except OSError as error:
        raise OsvQueryError(
            "OSV response body could not be read."
        ) from error

    if not isinstance(response_body, bytes):
        raise OsvQueryError(
            "OSV response body must contain bytes."
        )

    return response_body


def _decode_response(
    response_body: bytes,
) -> object:
    """Decode an OSV JSON response body."""

    try:
        response_text = response_body.decode(
            "utf-8"
        )
        return json.loads(
            response_text
        )
    except UnicodeDecodeError as error:
        raise OsvQueryError(
            "OSV response is not valid UTF-8."
        ) from error
    except json.JSONDecodeError as error:
        raise OsvQueryError(
            "OSV response is not valid JSON."
        ) from error