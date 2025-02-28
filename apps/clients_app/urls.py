from rest_framework import routers

from apps.clients_app.views.client import ClientViewSet

router = routers.DefaultRouter()
router.register(r"clients", ClientViewSet, basename="users")

urlpatterns = []

urlpatterns += router.urls
