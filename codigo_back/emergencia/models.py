from django.db import models
from usuarios.models import Usuario

class Solicitud(models.Model):
    latitud = models.CharField(max_length=30, null=True, blank=True)
    longitud = models.CharField(max_length=30, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, related_name='solicitudes', on_delete=models.CASCADE)
    emergencia = models.OneToOneField('Emergencia', related_name='solicitud', null=True, blank=True, on_delete=models.CASCADE)

class Sintoma(models.Model):
    nombre = models.CharField(max_length=100)
    severidad = models.CharField(max_length=50)
    valor = models.CharField(max_length=50)

class Recomendacion(models.Model):
    descripcion = models.TextField()

class Emergencia(models.Model):
    triage = models.IntegerField(null=True, blank=True)
    sintomas = models.ManyToManyField(Sintoma, related_name='emergencias')
    recomendaciones = models.ManyToManyField(Recomendacion, related_name='emergencias')