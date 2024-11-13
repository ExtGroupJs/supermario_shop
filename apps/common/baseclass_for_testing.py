from unittest import TestCase

from django.utils import timezone
from model_bakery import baker
# from oauth2_provider.models import AccessToken, Application
from rest_framework.test import APIClient
from django.core.management import call_command
from faker import Faker


from django.contrib.auth.models import User


class BaseTestClass(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.faker = Faker(0)
        if hasattr(self, "fixtures"):
            call_command(
                "loaddata",
                *self.fixtures,
                **{"verbosity": 0},
            )

        self.user = baker.make(User, _fill_optional=True)  # User.objects.create_user(

        # This code is for oauth, i.e. if the FE were in a separated application with a Js framework
        # self.oauth2_app = baker.make(
        #     Application,
        #     redirect_uris="redirect_uri.com",
        #     client_type=Application.CLIENT_CONFIDENTIAL,
        #     authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        #     name="Test App",
        # )
        # self.oauth2_token = baker.make(
        #     AccessToken,
        #     user_id=self.user.id,
        #     token="test_gen_token",
        #     application_id=self.oauth2_app.id,
        #     expires=timezone.now() + timezone.timedelta(days=1),
        #     scope="read,write",
        # )
