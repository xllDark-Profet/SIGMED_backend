from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_usuario')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_sangre = models.CharField(max_length=10, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    tipo_identificacion = models.CharField(max_length=10, null=True, blank=True)
    identificacion = models.CharField(max_length=15, null=True, blank=True)
    eps = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tipo_identificacion', 'identificacion'], name='unique_identification')
        ]

    def __str__(self):
        return self.user.username