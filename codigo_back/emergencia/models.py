from django.db import models
from usuarios.models import Usuario

class Solicitud(models.Model):
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, related_name='solicitudes', on_delete=models.CASCADE)
    sintomas_respuestas = models.JSONField()

class Sintoma(models.Model):
    nombre = models.CharField(max_length=100)
    severidad = models.CharField(max_length=50)
    valor = models.CharField(max_length=50)

class Recomendacion(models.Model):
    descripcion = models.TextField()

class Emergencia(models.Model):
    nombre = models.CharField(max_length=100)
    triage = models.IntegerField(null=True, blank=True)
    sintomas = models.ManyToManyField(Sintoma, related_name='emergencias')
    recomendaciones = models.ManyToManyField(Recomendacion, related_name='emergencias')