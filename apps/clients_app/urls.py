from rest_framework import routers

from apps.clients_app.views.client import ClientViewSet
from apps.users_app.views.group import GroupViewSet

router = routers.DefaultRouter()
router.register(r"clients", ClientViewSet, basename="users")

urlpatterns = []

urlpatterns += router.urls
