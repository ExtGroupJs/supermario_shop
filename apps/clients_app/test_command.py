import pytest


from django.core.management.base import CommandError

from model_bakery import baker
from django.core.management import call_command
from model_bakery.exceptions import InvalidQuantityException

from apps.business_app.models.shop import Shop
from apps.clients_app.models.client import Client


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quantity, response",
    [
        ("", CommandError),
        (baker.random_gen.gen_string(5), CommandError),
        (-2, InvalidQuantityException),
    ],
)
def test_errors_in_create_test_clients_command(quantity, response):
    with pytest.raises(response):
        call_command("create_test_clients", quantity)


@pytest.mark.django_db
def test_create_test_clients_command():
    quantity = baker.random_gen.gen_integer(1, 10)
    baker.make(Shop)
    call_command("create_test_clients", str(quantity))

    client_quantity = Client.objects.count()
    assert client_quantity == quantity
