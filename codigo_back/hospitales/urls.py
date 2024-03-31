from django.urls import path
from hospitales.views import HospitalView, EpsView, EspecialidadView

urlpatterns = [
    path('hospitales/', HospitalView.as_view(), name='hospital-list'),
    path('hospitales/agregar/', HospitalView.as_view(), name='hospital-create'),
    path('hospitales/modificar/', HospitalView.as_view(), name='hospital-update'),
    path('hospitales/eliminar/', HospitalView.as_view(), name='hospital-delete'),
    path('eps/', EpsView.as_view(), name='eps-list'),
    path('eps/agregar/', EpsView.as_view(), name='eps-create'),
    path('eps/modificar/', EpsView.as_view(), name='eps-update'),
    path('eps/eliminar/', EpsView.as_view(), name='eps-delete'),
    path('especialidades/', EspecialidadView.as_view(), name='especialidades_list'),
    path('especialidades/agregar/', EspecialidadView.as_view(), name='especialidades-create'),
    path('especialidades/modificar/', EspecialidadView.as_view(), name='especialidades-update'),
    path('especialidades/eliminar/', EspecialidadView.as_view(), name='especialidades-delete')
]