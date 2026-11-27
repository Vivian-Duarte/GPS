from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import AgendamentoViewSet, QuadraViewSet

router = DefaultRouter()
router.register("quadras", QuadraViewSet, basename="quadra")
router.register("agendamentos", AgendamentoViewSet, basename="agendamento")

urlpatterns = [
    path("auth/login/", obtain_auth_token, name="api-login"),
    path("", include(router.urls)),
]