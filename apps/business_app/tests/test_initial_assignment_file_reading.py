import datetime

import pytest
from model_bakery import baker

from apps.common.baseclass_for_incoming_file_testing import (
    BaseTestClassForIncomingFileTesting,
)
from apps.common.utils.months import Months
from apps.enterprises_app.models.enterprise import Enterprise
from apps.fuel_app.models.enterprise_assignment import (
    EnterpriseAssignment,
)
from apps.fuel_app.models.incoming_assignment import IncomingAssignment
from apps.fuel_app.models.notification import Notification
from apps.users_app.models.groups import Groups
from apps.users_app.models.system_user import SystemUser


@pytest.mark.django_db
class TestInitialAssignmentViewSet(BaseTestClassForIncomingFileTesting):
    fixtures = ["auth.group.json"]

    def test_reading_incoming_assignment_file_for_standard_date(self):
        """
        Esta prueba está fuertemente ligada al fichero de ejemplo: incoming_plan_for_test.xlsx
        que es representativo de una carga de un fichero, con una sola empresa: AZCUBA - GE AZCUBA
        Los rangos de fecha a comprobar son: 29 AL 2/3 AL 9/10 al 16/17 AL 23/24 AL 4
        para cada uno de estos períodos se colocó un valor fijo de 10

        """
        # self.client.force_authenticate(self.user, self.oauth2_token)
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        current_year = datetime.datetime.today().year
        current_month = Months.FEB
        incoming_assignment = baker.make(
            IncomingAssignment,
            incoming_file="incoming_plan_for_test.xlsx",
            year=current_year,
            month=current_month,
        )
        self.assertEqual(incoming_assignment.year, current_year)
        self.assertEqual(incoming_assignment.month, current_month)

        created_enterprise_assignments = EnterpriseAssignment.objects.all()
        expected_enterprise_assignments = 5
        self.assertEqual(
            created_enterprise_assignments.count(), expected_enterprise_assignments
        )
        self.assertEqual(
            EnterpriseAssignment.objects.filter(
                enterprise=enterprise,
                incoming_assignment=incoming_assignment,
                assignment=10,
                status=EnterpriseAssignment.Status.INITIAL,
            ).count(),
            created_enterprise_assignments.count(),
        )

        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=3
                ),
                final_date=datetime.date(year=current_year, month=current_month, day=9),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=10
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=16
                ),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=17
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=23
                ),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(year=current_year, month=Months.ENE, day=29),
                final_date=datetime.date(year=current_year, month=current_month, day=2),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=24
                ),
                final_date=datetime.date(year=current_year, month=Months.MAR, day=4),
            ).exists()
        )

    def test_reading_incoming_assignment_file_creates_a_notification_for_every_enterprise_assignment(
        self,
    ):
        """
        Esta prueba está fuertemente ligada al fichero de ejemplo: incoming_plan_for_test.xlsx
        que es representativo de una carga de un fichero, con una sola empresa: AZCUBA - GE AZCUBA
        Los rangos de fecha a comprobar son: 29 AL 2/3 AL 9/10 al 16/17 AL 23/24 AL 4
        para cada uno de estos períodos se colocó un valor fijo de 10

        """
        # self.client.force_authenticate(self.user, self.oauth2_token)
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        enterprise_planner = baker.make(
            SystemUser,
            enterprise=enterprise,
        )
        enterprise_planner.groups.add(Groups.FUEL_ENTITY_REPRESENTANT.value)
        current_year = datetime.datetime.today().year
        current_month = Months.FEB
        incoming_assignment = baker.make(
            IncomingAssignment,
            incoming_file="incoming_plan_for_test.xlsx",
            year=current_year,
            month=current_month,
        )
        self.assertEqual(incoming_assignment.year, current_year)
        self.assertEqual(incoming_assignment.month, current_month)

        created_enterprise_assignments = EnterpriseAssignment.objects.all()
        expected_enterprise_assignments = 5
        self.assertEqual(
            created_enterprise_assignments.count(), expected_enterprise_assignments
        )
        self.assertEqual(
            EnterpriseAssignment.objects.filter(
                enterprise=enterprise,
                incoming_assignment=incoming_assignment,
                assignment=10,
                status=EnterpriseAssignment.Status.INITIAL,
            ).count(),
            created_enterprise_assignments.count(),
        )
        self.assertTrue(Notification.objects.count(), expected_enterprise_assignments)
        self.assertTrue(
            Notification.objects.count(), enterprise_planner.notifications.count()
        )

    def test_reading_incoming_assignment_file_for_edge_under_date(self):
        """
        Esta prueba está fuertemente ligada al fichero de ejemplo: incoming_plan_for_test.xlsx
        que es representativo de una carga de un fichero, con una sola empresa: AZCUBA - GE AZCUBA
        Los rangos de fecha a comprobar son: 29 AL 2/3 AL 9/10 al 16/17 AL 23/24 AL 4
        para cada uno de estos períodos se colocó un valor fijo de 10

        """
        # self.client.force_authenticate(self.user, self.oauth2_token)
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        current_year = datetime.datetime.today().year
        current_month = Months.ENE
        incoming_assignment = baker.make(
            IncomingAssignment,
            incoming_file="incoming_plan_for_test.xlsx",
            year=current_year,
            month=current_month,
        )
        self.assertEqual(incoming_assignment.year, current_year)
        self.assertEqual(incoming_assignment.month, current_month)

        created_enterprise_initial_assignments = EnterpriseAssignment.objects.all()
        self.assertEqual(created_enterprise_initial_assignments.count(), 5)
        self.assertEqual(
            EnterpriseAssignment.objects.filter(
                enterprise=enterprise,
                incoming_assignment=incoming_assignment,
                assignment=10,
                status=EnterpriseAssignment.Status.INITIAL,
            ).count(),
            created_enterprise_initial_assignments.count(),
        )

        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=3
                ),
                final_date=datetime.date(year=current_year, month=current_month, day=9),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=10
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=16
                ),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=17
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=23
                ),
            ).exists()
        )

        # This corresponds to december of the previous year assumming the load was on january
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year - 1, month=Months.DIC, day=29
                ),
                final_date=datetime.date(year=current_year, month=current_month, day=2),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=24
                ),
                final_date=datetime.date(year=current_year, month=Months.FEB, day=4),
            ).exists()
        )

    def test_reading_incoming_assignment_file_for_edge_upper_date(self):
        """
        Esta prueba está fuertemente ligada al fichero de ejemplo: incoming_plan_for_test.xlsx
        que es representativo de una carga de un fichero, con una sola empresa: AZCUBA - GE AZCUBA
        Los rangos de fecha a comprobar son: 29 AL 2/3 AL 9/10 al 16/17 AL 23/24 AL 4
        para cada uno de estos períodos se colocó un valor fijo de 10

        """
        # self.client.force_authenticate(self.user, self.oauth2_token)
        enterprise = baker.make(Enterprise, name="AZCUBA - GE AZCUBA")
        current_year = datetime.datetime.today().year
        current_month = Months.DIC
        incoming_assignment = baker.make(
            IncomingAssignment,
            incoming_file="incoming_plan_for_test.xlsx",
            year=current_year,
            month=current_month,
        )
        self.assertEqual(incoming_assignment.year, current_year)
        self.assertEqual(incoming_assignment.month, current_month)

        created_enterprise_assignments = EnterpriseAssignment.objects.all()
        self.assertEqual(created_enterprise_assignments.count(), 5)
        self.assertEqual(
            EnterpriseAssignment.objects.filter(
                enterprise=enterprise,
                incoming_assignment=incoming_assignment,
                assignment=10,
                status=EnterpriseAssignment.Status.INITIAL,
            ).count(),
            created_enterprise_assignments.count(),
        )

        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=3
                ),
                final_date=datetime.date(year=current_year, month=current_month, day=9),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=10
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=16
                ),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=17
                ),
                final_date=datetime.date(
                    year=current_year, month=current_month, day=23
                ),
            ).exists()
        )
        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(year=current_year, month=Months.NOV, day=29),
                final_date=datetime.date(year=current_year, month=current_month, day=2),
            ).exists()
        )

        # This corresponds to january of the next year assumming the load was on december

        self.assertTrue(
            EnterpriseAssignment.objects.filter(
                initial_date=datetime.date(
                    year=current_year, month=current_month, day=24
                ),
                final_date=datetime.date(
                    year=current_year + 1, month=Months.ENE, day=4
                ),
            ).exists()
        )
