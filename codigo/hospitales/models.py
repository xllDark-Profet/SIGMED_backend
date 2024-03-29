from django.db import models
from especialidades.models import Especialidad

class Hospital(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_registro = models.CharField(max_length=50)
    latitud = models.CharField(max_length=100)
    longitud = models.CharField(max_length=100)
    especialidades = models.ManyToManyField(Especialidad, related_name='hospitales')

    def __str__(self):
        return self.nombre