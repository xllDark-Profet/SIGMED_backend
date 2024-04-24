from django.urls import path
from emergencia.views import SolicitudesView, EmergenciaDetailView, EmergenciasListView, EnviarRespuestasView


urlpatterns = [
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes-list'),
    path('enviar-respuestas/', EnviarRespuestasView.as_view(), name='enviar-respuestas'),
    path('emergencias/', EmergenciasListView.as_view(), name='emergencias-list'),
    path('emergencia/', EmergenciaDetailView.as_view(), name='emergencia-detail'),
]