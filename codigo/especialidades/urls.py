from django.urls import path
from especialidades.views import EspecialidadView

urlpatterns = [
    path('especialidades/', EspecialidadView.as_view(), name='especialidades_list'),
    path('especialidades/agregar/', EspecialidadView.as_view(), name='especialidades-create'),
    path('especialidades/modificar/', EspecialidadView.as_view(), name='especialidades-update'),
    path('especialidades/eliminar/', EspecialidadView.as_view(), name='especialidades-delete')
]