"""Tests for the OSV query client."""

from __future__ import annotations

import json
import socket
from urllib.error import HTTPError, URLError

import pytest

import dependency_scanner.osv_client as osv_client
from dependency_scanner.osv_client import (
    OsvQueryClient,
    OsvQueryError,
)


class FakeResponse:
    """Provide a controlled HTTP response for tests."""

    def __init__(
        self,
        body: object = b"{}",
        status: object = 200,
        read_error: OSError | None = None,
    ) -> None:
        self.body = body
        self.status = status
        self.read_error = read_error

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None

    def read(self) -> object:
        if self.read_error is not None:
            raise self.read_error

        return self.body


def _install_response(
    monkeypatch: pytest.MonkeyPatch,
    response: object,
) -> list[tuple[object, float]]:
    """Install a fake urlopen implementation."""

    calls: list[tuple[object, float]] = []

    def fake_urlopen(
        request: object,
        timeout: float,
    ) -> object:
        calls.append(
            (request, timeout)
        )
        return response

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        fake_urlopen,
    )

    return calls


def _request_payload(
    request: object,
) -> dict[str, object]:
    """Decode request JSON data."""

    request_data = getattr(
        request,
        "data",
    )

    assert isinstance(
        request_data,
        bytes,
    )

    return json.loads(
        request_data.decode("utf-8")
    )


def test_client_uses_default_timeout() -> None:
    client = OsvQueryClient()

    assert client.timeout == 10.0


def test_client_accepts_custom_timeout() -> None:
    client = OsvQueryClient(
        timeout=2.5
    )

    assert client.timeout == 2.5


@pytest.mark.parametrize(
    "timeout",
    [
        0,
        -1,
        "10",
        True,
        float("inf"),
        float("nan"),
    ],
)
def test_client_rejects_invalid_timeout(
    timeout: object,
) -> None:
    with pytest.raises(
        OsvQueryError,
        match="timeout",
    ):
        OsvQueryClient(
            timeout=timeout,  # type: ignore[arg-type]
        )


def test_query_uses_correct_endpoint_and_post_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    request, _ = calls[0]

    assert getattr(
        request,
        "full_url",
    ) == "https://api.osv.dev/v1/query"

    assert request.get_method() == "POST"


def test_query_uses_json_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    request, _ = calls[0]

    assert (
        request.get_header(
            "Content-type"
        )
        == "application/json"
    )


def test_query_uses_configured_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient(
        timeout=4.5
    ).query_package(
        "jinja2",
        "3.1.4",
    )

    _, timeout = calls[0]

    assert timeout == 4.5


def test_query_normalizes_package_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "Sample_Package",
        "1.2.3",
    )

    request, _ = calls[0]
    payload = _request_payload(
        request
    )

    assert payload["package"] == {
        "name": "sample-package",
        "ecosystem": "PyPI",
    }


def test_query_adds_version_to_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    request, _ = calls[0]
    payload = _request_payload(
        request
    )

    assert payload["version"] == "3.1.4"


def test_query_omits_missing_page_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    request, _ = calls[0]
    payload = _request_payload(
        request
    )

    assert "page_token" not in payload


def test_query_adds_page_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_response(
        monkeypatch,
        FakeResponse(),
    )

    OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
        page_token="next-token",
    )

    request, _ = calls[0]
    payload = _request_payload(
        request
    )

    assert (
        payload["page_token"]
        == "next-token"
    )


def test_query_parses_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(
        monkeypatch,
        FakeResponse(
            body=b"{}"
        ),
    )

    result = OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    assert result.vulnerabilities == ()
    assert result.next_page_token is None


def test_query_parses_vulnerability_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "vulns": [
            {
                "id": "OSV-TEST-1",
                "summary": "Example vulnerability",
            },
        ],
    }

    _install_response(
        monkeypatch,
        FakeResponse(
            body=json.dumps(
                payload
            ).encode("utf-8")
        ),
    )

    result = OsvQueryClient().query_package(
        "example-package",
        "1.0.0",
    )

    assert len(
        result.vulnerabilities
    ) == 1

    assert (
        result.vulnerabilities[
            0
        ].advisory_id
        == "OSV-TEST-1"
    )


def test_query_preserves_next_page_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "next_page_token": "page-two",
    }

    _install_response(
        monkeypatch,
        FakeResponse(
            body=json.dumps(
                payload
            ).encode("utf-8")
        ),
    )

    result = OsvQueryClient().query_package(
        "example-package",
        "1.0.0",
    )

    assert (
        result.next_page_token
        == "page-two"
    )


def test_query_rejects_http_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(
        monkeypatch,
        FakeResponse(
            status=503
        ),
    )

    with pytest.raises(
        OsvQueryError,
        match="503",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_http_error(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise HTTPError(
            url="https://api.osv.dev/v1/query",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        raise_http_error,
    )

    with pytest.raises(
        OsvQueryError,
        match="429",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_network_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_network_error(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise URLError(
            "network unavailable"
        )

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        raise_network_error,
    )

    with pytest.raises(
        OsvQueryError,
        match="network",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_direct_os_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Socket-level OS errors should use the public query error."""

    def raise_os_error(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise OSError("connection reset")

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        raise_os_error,
    )

    with pytest.raises(
        OsvQueryError,
        match="connection reset",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_timeout(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise socket.timeout(
            "timed out"
        )

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        raise_timeout,
    )

    with pytest.raises(
        OsvQueryError,
        match="timed out",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_url_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_timeout(
        request: object,
        timeout: float,
    ) -> FakeResponse:
        raise URLError(
            socket.timeout(
                "timed out"
            )
        )

    monkeypatch.setattr(
        osv_client,
        "urlopen",
        raise_timeout,
    )

    with pytest.raises(
        OsvQueryError,
        match="timed out",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_response_read_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(
        monkeypatch,
        FakeResponse(
            read_error=OSError(
                "read failed"
            )
        ),
    )

    with pytest.raises(
        OsvQueryError,
        match="could not be read",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_accepts_response_without_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Responses without an explicit status retain urllib compatibility."""

    _install_response(
        monkeypatch,
        FakeResponse(status=None),
    )

    result = OsvQueryClient().query_package(
        "jinja2",
        "3.1.4",
    )

    assert result.vulnerabilities == ()


def test_query_rejects_non_integer_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed response status values should fail closed."""

    _install_response(
        monkeypatch,
        FakeResponse(status="200"),
    )

    with pytest.raises(OsvQueryError, match="status 200"):
        OsvQueryClient().query_package("jinja2", "3.1.4")


def test_query_rejects_response_without_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A response without a callable read method is invalid."""

    class UnreadableResponse:
        status = 200

        def __enter__(self) -> UnreadableResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    _install_response(monkeypatch, UnreadableResponse())

    with pytest.raises(OsvQueryError, match="could not be read"):
        OsvQueryClient().query_package("jinja2", "3.1.4")


def test_query_rejects_non_bytes_response_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """urllib response bodies must remain byte strings."""

    _install_response(
        monkeypatch,
        FakeResponse(body="{}"),
    )

    with pytest.raises(OsvQueryError, match="must contain bytes"):
        OsvQueryClient().query_package("jinja2", "3.1.4")


def test_query_rejects_invalid_utf8(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(
        monkeypatch,
        FakeResponse(
            body=b"\xff"
        ),
    )

    with pytest.raises(
        OsvQueryError,
        match="UTF-8",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_rejects_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(
        monkeypatch,
        FakeResponse(
            body=b"{"
        ),
    )

    with pytest.raises(
        OsvQueryError,
        match="JSON",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


def test_query_translates_invalid_osv_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "vulns": [
            {
                "summary": "Missing ID",
            },
        ],
    }

    _install_response(
        monkeypatch,
        FakeResponse(
            body=json.dumps(
                payload
            ).encode("utf-8")
        ),
    )

    with pytest.raises(
        OsvQueryError,
        match="OSV response is invalid",
    ):
        OsvQueryClient().query_package(
            "jinja2",
            "3.1.4",
        )


@pytest.mark.parametrize(
    "package_name",
    [
        "",
        "   ",
        "invalid/package",
        object(),
    ],
)
def test_query_rejects_invalid_package_name(
    package_name: object,
) -> None:
    with pytest.raises(
        OsvQueryError,
        match="package_name",
    ):
        OsvQueryClient().query_package(
            package_name,  # type: ignore[arg-type]
            "1.0.0",
        )


@pytest.mark.parametrize(
    "version",
    [
        "",
        "   ",
        object(),
    ],
)
def test_query_rejects_invalid_version(
    version: object,
) -> None:
    with pytest.raises(
        OsvQueryError,
        match="version",
    ):
        OsvQueryClient().query_package(
            "example-package",
            version,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "page_token",
    [
        "",
        "   ",
        object(),
    ],
)
def test_query_rejects_invalid_page_token(
    page_token: object,
) -> None:
    with pytest.raises(
        OsvQueryError,
        match="page_token",
    ):
        OsvQueryClient().query_package(
            "example-package",
            "1.0.0",
            page_token=page_token,  # type: ignore[arg-type]
        )
