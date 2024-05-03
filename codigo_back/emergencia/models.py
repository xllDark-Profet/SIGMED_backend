from django.db import models
from hospitales.models import Hospital
from usuarios.models import Usuario

class Solicitud(models.Model):
    direccion = models.CharField(max_length=50, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, related_name='solicitudes', on_delete=models.CASCADE)
    sintomas_presentes = models.JSONField()
    emergencia_detectada = models.CharField(max_length=100)
    triage = models.IntegerField(null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_hora = models.DateTimeField()