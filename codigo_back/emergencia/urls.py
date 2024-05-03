from django.urls import path
from emergencia.views import SolicitudesView, IdentificadorView, ObtenerHospitalesView, SolicitudView


urlpatterns = [
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes-list'),
    path('identificador/', IdentificadorView.as_view(), name='enviar-respuestas'),
    path('hospitales/identificar/', ObtenerHospitalesView.as_view(), name='obtener-hospitales'),
    path('solicitud/', SolicitudView.as_view(), name='obtener-hospital')
]