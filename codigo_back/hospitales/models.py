from django.db import models

class Especialidad(models.Model):
    nombre = models.CharField(max_length=50)

class EPS(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)

class Hospital(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    especialidades = models.ManyToManyField(Especialidad, related_name='hospitales')
    listaeps = models.ManyToManyField(EPS, related_name= 'listaeps')