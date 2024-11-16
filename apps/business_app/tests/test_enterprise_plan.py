import datetime
import json

from apps.common.baseclass_for_incoming_file_testing import (
    BaseTestClassForIncomingFileTesting,
)
import pytest
from django.urls import reverse
from apps.fuel_app.models.notification import Notification
from apps.users_app.models.groups import Groups
from model_bakery import baker

from apps.enterprises_app.models.enterprise import Enterprise

from apps.fuel_app.models.enterprise_assignment import EnterpriseAssignment
from apps.fuel_app.models.enterprise_plan import EnterprisePlan
from apps.fuel_app.models.incoming_assignment import IncomingAssignment
from rest_framework import status

from apps.users_app.models.system_user import SystemUser


@pytest.mark.django_db
class TestEnterprisePlanViewSet(BaseTestClassForIncomingFileTesting):
    fixtures = ["auth.group.json"]

    def test_create_enterprise_plan_plan_by_planner_and_notificate_cupet_gestor(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=baker.make(Enterprise, name="AZCUBA - GE AZCUBA"),
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
        )
        self.assertIs(enterprise_assignment.status, EnterpriseAssignment.Status.INITIAL)
        url = reverse("enterprise_plan-list")

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        fuel_gestor = baker.make(
            SystemUser,
        )
        fuel_gestor.groups.add(Groups.FUEL_ASIGNATION_GESTOR_CUPET.value)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        created_plans = EnterprisePlan.objects.count()
        self.assertEqual(created_plans, qty)
        enterprise_assignment.refresh_from_db()
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.PROPOSAL.value
        )

        self.assertEqual(
            created_plans,
            EnterprisePlan.objects.filter(
                updated_at__isnull=False, created_at__isnull=False, updated_by=self.user
            ).count(),
        )
        self.assertTrue(Notification.objects.count(), 1)
        self.assertTrue(Notification.objects.count(), fuel_gestor.notifications.count())

    def test_update_enterprise_plan_by_planner_and_notificate_cupet_gestor(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=baker.make(Enterprise, name="AZCUBA - GE AZCUBA"),
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
            status=EnterpriseAssignment.Status.PROPOSAL.value,
        )
        for i in range(qty):
            baker.make(
                EnterprisePlan,
                enterprise_assignment=enterprise_assignment,
                for_date=today + datetime.timedelta(days=i),
                assignation=0.0,  # setted on 0.0 to be able to update it later.
            )

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        url = reverse("enterprise_plan-update-plans")
        fuel_gestor = baker.make(
            SystemUser,
        )
        fuel_gestor.groups.add(Groups.FUEL_ASIGNATION_GESTOR_CUPET.value)

        response = self.client.put(url, data=json_data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        created_plans = EnterprisePlan.objects.count()
        self.assertEqual(created_plans, qty)
        enterprise_assignment.refresh_from_db()
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.PROPOSAL.value
        )
        self.assertEqual(
            created_plans,
            EnterprisePlan.objects.filter(
                updated_at__isnull=False,
                created_at__isnull=False,
                updated_by=self.user,
            )
            .exclude(assignation=0.0)
            .count(),
        )
        self.assertTrue(Notification.objects.count(), 1)
        self.assertTrue(Notification.objects.count(), fuel_gestor.notifications.count())

    def test_update_enterprise_plan_by_cupet_gestor_fails_if_not_correct_role(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=baker.make(Enterprise, name="AZCUBA - GE AZCUBA"),
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
            status=EnterpriseAssignment.Status.PROPOSAL.value,
        )
        for i in range(qty):
            baker.make(
                EnterprisePlan,
                enterprise_assignment=enterprise_assignment,
                for_date=today + datetime.timedelta(days=i),
                assignation=0.0,  # setted on 0.0 to be able to update it later.
            )

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
        }

        json_data = json.dumps(payload)
        # FUEL_ASIGNATION_GESTOR_CUPET required to do this action
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)

        url = reverse("enterprise_plan-update-plans-by-gestor-cupet")
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_update_enterprise_plan_by_cupet_gestor_with_notification_to_planner(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=enterprise,
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
            status=EnterpriseAssignment.Status.PROPOSAL.value,
        )
        for i in range(qty):
            baker.make(
                EnterprisePlan,
                enterprise_assignment=enterprise_assignment,
                for_date=today + datetime.timedelta(days=i),
                assignation=0.0,  # setted on 0.0 to be able to update it later.
            )

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
            # "message": "ommited now to cause a provoqued 400 error on the call. It is required"
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ASIGNATION_GESTOR_CUPET.value)
        url = reverse("enterprise_plan-update-plans-by-gestor-cupet")
        response = self.client.put(url, data=json_data, content_type="application/json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )  # because of provoqued 400 error
        payload["message"] = baker.random_gen.gen_string(max_length=20)
        json_data = json.dumps(payload)
        enterprise_planner = baker.make(
            SystemUser,
            enterprise=enterprise,
        )
        enterprise_planner.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        response = self.client.put(url, data=json_data, content_type="application/json")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        created_plans = EnterprisePlan.objects.count()
        self.assertEqual(created_plans, qty)
        enterprise_assignment.refresh_from_db()
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.PROPOSAL.value
        )
        self.assertEqual(
            created_plans,
            EnterprisePlan.objects.filter(
                updated_at__isnull=False,
                created_at__isnull=False,
                updated_by=self.user,
            )
            .exclude(assignation=0.0)
            .count(),
        )
        self.assertTrue(Notification.objects.count(), 1)
        self.assertTrue(
            Notification.objects.count(), enterprise_planner.notifications.count()
        )
        created_notification = Notification.objects.first()
        self.assertEqual(
            created_notification.message,
            payload["message"],
        )
        self.assertEqual(
            created_notification.title,
            f"Su planificación del {enterprise_assignment.initial_date} al {enterprise_assignment.final_date} fue aprobada con cambios",
        )
        self.assertEqual(
            created_notification.origin_user,
            self.user,
        )
        self.assertEqual(
            created_notification.target_user.id,
            enterprise_planner.id,
        )

    def test_create_enterprise_plan_fails_if_try_to_insert_existing_date(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=baker.make(Enterprise, name="AZCUBA - GE AZCUBA"),
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
        )
        self.assertIs(enterprise_assignment.status, EnterpriseAssignment.Status.INITIAL)
        url = reverse("enterprise_plan-list")

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(EnterprisePlan.objects.count(), qty)
        enterprise_assignment.refresh_from_db()
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.PROPOSAL.value
        )
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(EnterprisePlan.objects.count(), qty)

    def test_create_enterprise_plan_fails_with_incorrect_dates(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=baker.make(Enterprise, name="AZCUBA - GE AZCUBA"),
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
        )
        self.assertIs(enterprise_assignment.status, EnterpriseAssignment.Status.INITIAL)
        url = reverse("enterprise_plan-list")

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=qty + 1)),
                }
            ],
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today - datetime.timedelta(days=1)),
                }
            ],
        }

        json_data = json.dumps(payload)

        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [],
        }

        json_data = json.dumps(payload)

        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Nothing new created
        self.assertEqual(EnterprisePlan.objects.count(), 0)
        enterprise_assignment.refresh_from_db()
        # No change in the status
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.INITIAL.value
        )

    def test_retreive_enterprise_plan_happy_path(self):
        # self.client.force_authenticate(self.user, self.oauth2_token)
        self.client.force_authenticate(self.user)
        qty = baker.random_gen.gen_integer(
            min_int=2, max_int=10
        )  # Random number between 2 and 10

        today = datetime.date.today()
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        enterprise_assignment = baker.make(
            EnterpriseAssignment,
            incoming_assignment=baker.make(
                IncomingAssignment, incoming_file="incoming_plan_for_test.xlsx"
            ),
            enterprise=enterprise,
            initial_date=today,
            final_date=today + datetime.timedelta(days=qty),
        )
        self.assertIs(enterprise_assignment.status, EnterpriseAssignment.Status.INITIAL)
        url = reverse("enterprise_plan-list")

        payload = {
            "enterprise_assignment": enterprise_assignment.id,
            "data": [
                {
                    "assignation": baker.random_gen.gen_integer(
                        min_int=10, max_int=1000
                    ),
                    "for_date": str(today + datetime.timedelta(days=i)),
                }
                for i in range(qty)
            ],
        }

        json_data = json.dumps(payload)
        self.user.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(EnterprisePlan.objects.count(), qty)
        enterprise_assignment.refresh_from_db()
        self.assertIs(
            enterprise_assignment.status, EnterpriseAssignment.Status.PROPOSAL.value
        )

        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.json().get("count"),
            qty,
        )
