import pytest
from model_bakery import baker

from apps.users_app.views import pages

CATALOG_TEMPLATE = "catalogo_por_mayor/catalogo_por_mayor.html"


@pytest.fixture
def anonymous_country(monkeypatch, client):
    """Force the geo-IP answer for anonymous requests."""

    def set_country(country):
        monkeypatch.setattr(pages, "get_country_code", lambda request: country)
        return client

    return set_country


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,url,expected_template",
    [
        ("root", "/", CATALOG_TEMPLATE),
        ("catalog", "/catalog/", "catalogo/catalogo.html"),
        ("wholesale", "/wholesale_catalog/", CATALOG_TEMPLATE),
    ],
)
def test_foreign_visitor_sees_catalog(anonymous_country, url_name, url, expected_template):
    client = anonymous_country("US")
    response = client.get(url)
    assert response.status_code == 200
    assert expected_template in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.parametrize("country", ["CU", ""])
@pytest.mark.parametrize(
    "url",
    ["/", "/catalog/", "/wholesale_catalog/"],
)
def test_blocked_visitor_is_redirected_to_login(anonymous_country, country, url):
    client = anonymous_country(country)
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == "/login/"


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/", "/catalog/", "/wholesale_catalog/"])
def test_authenticated_user_sees_catalog_from_cuba(client, url):
    client.force_login(baker.make("users_app.SystemUser", _fill_optional=True))
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_skips_geo_lookup(monkeypatch, client):
    """A logged user must not pay the geo-IP latency on every page load."""
    calls = []
    monkeypatch.setattr(pages, "get_country_code", lambda request: calls.append(1))
    client.force_login(baker.make("users_app.SystemUser", _fill_optional=True))
    assert client.get("/").status_code == 200
    assert calls == []


@pytest.mark.django_db
def test_catalog_by_shop_stays_public(anonymous_country):
    client = anonymous_country("CU")
    response = client.get("/catalogo/tienda/test-shop/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_real_helper_drives_the_decision(monkeypatch, client):
    """The view must call the real geo helper, not a patched copy of it."""
    monkeypatch.setattr(
        "apps.common.utils.geo.requests.get",
        lambda *args, **kwargs: type(
            "R", (), {"ok": True, "json": lambda self: {"country": "US"}}
        )(),
    )
    assert client.get("/").status_code == 200
