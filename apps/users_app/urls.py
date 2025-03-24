from rest_framework import routers

from apps.users_app.views import UserViewSet
from apps.users_app.views.group import GroupViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"groups", GroupViewSet, basename="groups")

urlpatterns = []

urlpatterns += router.urls
