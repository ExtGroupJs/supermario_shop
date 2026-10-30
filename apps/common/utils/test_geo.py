import pytest
import requests
from django.core.cache import cache
from unittest.mock import MagicMock, patch

from apps.common.utils.geo import get_client_ip, get_country_code

LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@pytest.fixture(autouse=True)
def _locmem_cache(settings):
    """Real cache for these tests; LocMemCache keeps data between tests."""
    settings.CACHES = LOCMEM
    cache.clear()
    yield
    cache.clear()


def _request(ip):
    return MagicMock(META={"REMOTE_ADDR": ip})


def _response(country):
    return MagicMock(ok=True, json=lambda: {"ip": "8.8.8.8", "country": country})


@pytest.mark.parametrize("code", ["US", "us"])
def test_country_code_returned_for_foreign_ip(code):
    with patch("apps.common.utils.geo.requests.get", return_value=_response(code)):
        assert get_country_code(_request("8.8.8.8")) == "US"


def test_country_code_is_cached_per_ip():
    with patch(
        "apps.common.utils.geo.requests.get", return_value=_response("US")
    ) as get:
        get_country_code(_request("8.8.8.8"))
        get_country_code(_request("8.8.8.8"))
    assert get.call_count == 1


def test_timeout_returns_empty_country():
    with patch(
        "apps.common.utils.geo.requests.get",
        side_effect=requests.Timeout("boom"),
    ):
        assert get_country_code(_request("8.8.8.8")) == ""


@pytest.mark.parametrize(
    "response",
    [
        MagicMock(ok=True, json=lambda: {"error": "rate limited"}),
        MagicMock(ok=True, json=lambda: {"country": "N/A"}),
        MagicMock(ok=True, json=lambda: None),
        MagicMock(ok=False, json=lambda: {"country": "US"}),
    ],
)
def test_invalid_response_returns_empty_country(response):
    with patch("apps.common.utils.geo.requests.get", return_value=response):
        assert get_country_code(_request("8.8.8.8")) == ""


def test_first_forwarded_ip_is_used():
    request = MagicMock(META={"HTTP_X_FORWARDED_FOR": "8.8.8.8, 10.0.0.1"})
    assert get_client_ip(request) == "8.8.8.8"


def test_missing_ip_returns_empty_country():
    assert get_country_code(MagicMock(META={})) == ""
