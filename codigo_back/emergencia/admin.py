from django.contrib import admin
from emergencia.models import Solicitud, Sintoma, Recomendacion, Emergencia

admin.site.register(Solicitud)
admin.site.register(Sintoma)
admin.site.register(Recomendacion)
admin.site.register(Emergencia)