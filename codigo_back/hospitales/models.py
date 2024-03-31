from django.db import models

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

class EPS(models.Model):
    nombre = models.CharField(max_length=100)

class Hospital(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_registro = models.CharField(max_length=50)
    latitud = models.CharField(max_length=100)
    longitud = models.CharField(max_length=100)
    especialidades = models.ManyToManyField(Especialidad, related_name='hospitales')
    listaeps = models.ManyToManyField(EPS, related_name= 'listaeps')