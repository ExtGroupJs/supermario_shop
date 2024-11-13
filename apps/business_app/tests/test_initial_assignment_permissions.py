import pytest
from django.urls import reverse
from rest_framework import status

from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups


@pytest.mark.django_db
class TestInitialAssignmentViewSet(BaseTestClass):
    fixtures = ["auth.group.json"]

    def test_ep_permissions(self):
        """
        Este test comprueba que solo un superadmin o un Gestor de asignaciones del CUPET puede acceder al EP
        """
        self.client.force_authenticate(self.user, self.oauth2_token)

        url = reverse("incoming_assignment-list")
        # User has no role, so has no permissions to access the endpoint.
        self.assertEqual(
            self.client.post(url, format="json").status_code, status.HTTP_403_FORBIDDEN
        )

        # user with FUEL_ASIGNATION_GESTOR_CUPET role is allowed
        self.user.groups.add(Groups.FUEL_ASIGNATION_GESTOR_CUPET.value)
        self.assertNotEqual(
            self.client.post(url, format="json").status_code, status.HTTP_403_FORBIDDEN
        )

        # user with SUPER_ADMIN role is allowed
        self.user.groups.clear()  # Remove the group to avoid side effects in other tests.
        self.user.groups.add(Groups.SUPER_ADMIN.value)
        self.assertNotEqual(
            self.client.post(url, format="json").status_code, status.HTTP_403_FORBIDDEN
        )

        remaining_groups = [
            group
            for group in Groups
            if group != Groups.SUPER_ADMIN
            and group != Groups.FUEL_ASIGNATION_GESTOR_CUPET
        ]
        # *for each of them the ep is forbidden
        for group in remaining_groups:
            self.user.groups.clear()  # Remove the group to avoid side effects in other tests.
            self.user.groups.add(group.value)
            self.assertEqual(
                self.client.post(url, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
