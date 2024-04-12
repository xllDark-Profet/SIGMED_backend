from django.db import models
from usuarios.models import Usuario

class Solicitud(models.Model):
    emergencia = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()
    usuario = models.ForeignKey(Usuario, related_name='solicitudes', on_delete=models.CASCADE)