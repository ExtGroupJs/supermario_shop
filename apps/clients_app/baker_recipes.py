from faker import Faker
from model_bakery.recipe import Recipe

from apps.business_app.models.shop import Shop
from apps.clients_app.models.client import Client

faker = Faker(0)

client = Recipe(
    Client,
    name=faker.name,
    phone=faker.phone_number,
    shop=Shop.objects.first,
)
