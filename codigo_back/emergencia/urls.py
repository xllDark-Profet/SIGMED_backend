from django.urls import path
from emergencia.views import SolicitudesView


urlpatterns = [
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes-list'),
]