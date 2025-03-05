from rest_framework import routers
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api import (
    CompletoViewSet, PersonajesViewSet, MascotasViewSet,
    EdicionesViewSet, SkullectorViewSet, RegisterView, LogoutView, LoginView, UsuarioViewSet
)

router = routers.DefaultRouter()

router.register('todos', CompletoViewSet, basename='completo')
router.register('personajes', PersonajesViewSet, basename='personajes')
router.register('mascotas', MascotasViewSet, basename='mascotas')
router.register('ediciones', EdicionesViewSet, basename='ediciones')
router.register('skullectors', SkullectorViewSet, basename='skullectors')
router.register('usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls