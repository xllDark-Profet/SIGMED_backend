from django.urls import path
from usuarios.views import UsuarioLoginView, UsuarioView, BuscarUsuarioView

urlpatterns = [
    path('usuarios/', UsuarioView.as_view(), name='usuarios-list'),
    path('usuarios/agregar/', UsuarioView.as_view(), name='usuarios-create'),
    path('usuarios/modificar/', UsuarioView.as_view(), name='usuarios-update'),
    path('usuarios/eliminar/', UsuarioView.as_view(), name='usuarios-delete'),
    path('usuarios/login/', UsuarioLoginView.as_view(), name='usuarios-login'),
    path('usuarios/buscar/', BuscarUsuarioView.as_view(), name='usuarios-search'),
]