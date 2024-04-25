from django.urls import path
from emergencia.views import SolicitudesView, IdentificadorView


urlpatterns = [
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes-list'),
    path('identificador/', IdentificadorView.as_view(), name='enviar-respuestas')
]