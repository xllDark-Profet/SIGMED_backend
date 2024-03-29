from django.urls import path
from hospitales.views import HospitalView

urlpatterns = [
    path('hospitales/', HospitalView.as_view(), name='hospital-list'),
    path('hospitales/agregar/', HospitalView.as_view(), name='hospital-create'),
    path('hospitales/modificar/', HospitalView.as_view(), name='hospital-update'),
    path('hospitales/eliminar/', HospitalView.as_view(), name='hospital-delete')
]