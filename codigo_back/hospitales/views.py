
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from hospitales.models import Hospital
from especialidades.models import Especialidad
from django.db.models import Q

class HospitalView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_hospital_by_id(self, id):
        return Hospital.objects.get(id=id)
    
    def get_hospital_by_latlong(self, latitud, longitud):
        return Hospital.objects.get(latitud=latitud, longitud=longitud)
    
    def get_hospital_by_nombre(self, nombre):
        return Hospital.objects.get(nombre=nombre)
    
    def get(self, request):
        id = request.GET.get('id')
        latitud = request.GET.get('latitud')
        longitud = request.GET.get('longitud')
        nombre = request.GET.get('nombre')
            
        if id:
            try:
                hospital = self.get_hospital_by_id(id)
                return JsonResponse({
                    'hospital': {
                        'id': hospital.id,
                        'nombre': hospital.nombre,
                        'codigo_registro': hospital.codigo_registro,
                        'latitud': hospital.latitud,
                        'longitud': hospital.longitud,
                        'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()]
                    }
                })
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "No se encontro ningun hospital con el ID proporcionado."}, status=404)
        elif latitud:
            if longitud:
                try:
                    hospital = self.get_hospital_by_latlong(latitud, longitud)
                    return JsonResponse({
                        'hospital': {
                            'id': hospital.id,
                            'nombre': hospital.nombre,
                            'codigo_registro': hospital.codigo_registro,
                            'latitud': hospital.latitud,
                            'longitud': hospital.longitud,
                            'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()]
                        }
                    })
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun hospital con la latitud y longitud proporcionadas."}, status=404)
            else:
                return JsonResponse({'mensaje': "Hace falta la longitud"}, status=400)
        
        elif longitud:
            if latitud:
                try:
                    hospital = self.get_hospital_by_latlong(latitud, longitud)
                    return JsonResponse({
                        'hospital': {
                            'id': hospital.id,
                            'nombre': hospital.nombre,
                            'codigo_registro': hospital.codigo_registro,
                            'latitud': hospital.latitud,
                            'longitud': hospital.longitud,
                            'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()]
                        }
                    })
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun hospital con la latitud y longitud proporcionadas."}, status=404)
            else:
                return JsonResponse({'mensaje': "Hace falta la latitud"}, status=400)
            
        elif nombre:
            try:
                hospital = self.get_hospital_by_nombre(nombre)
                return JsonResponse({
                    'hospital': {
                        'id': hospital.id,
                        'nombre': hospital.nombre,
                        'codigo_registro': hospital.codigo_registro,
                        'latitud': hospital.latitud,
                        'longitud': hospital.longitud,
                        'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()]
                    }
                })
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "No se encontro ningun hospital con nombre proporcionado."}, status=404)
        else:
            hospitales = Hospital.objects.all()

        hospitales_con_especialidades = []

        for hospital in hospitales:
            especialidades = hospital.especialidades.values_list('nombre', flat=True)
            hospitales_con_especialidades.append({
                'id': hospital.id,
                'nombre': hospital.nombre,
                'codigo_registro': hospital.codigo_registro,
                'latitud': hospital.latitud,
                'longitud': hospital.longitud,
                'especialidades': list(especialidades)
            })

        if hospitales_con_especialidades:
            datos = {'mensaje': "Peticion exitosa!", 'hospitales': hospitales_con_especialidades}
        else:
            datos = {'mensaje': "No hay hospitales"}

        return JsonResponse(datos)


    
    def post(self, request):
        rp = json.loads(request.body)
        
        required_fields = ['codigo_registro', 'nombre', 'latitud', 'longitud', 'especialidades']
    
        for field in required_fields:
            if field not in rp:
                datos = {'mensaje': f"El campo '{field}' es requerido."}
                return JsonResponse(datos, status=400)
        
        codigo_registro = rp['codigo_registro']
        nombre = rp['nombre']
        latitud = rp['latitud']
        longitud = rp['longitud']
        especialidades_ids = rp['especialidades']

        if Hospital.objects.filter(codigo_registro=codigo_registro).exists():
            datos = {'mensaje': "Ya existe un hospital con este codigo de registro."}
            return JsonResponse(datos, status=400)
        
        if Hospital.objects.filter(Q(latitud=latitud) & Q(longitud=longitud)).exists():
            datos = {'mensaje': "Ya existe un hospital con la misma latitud y longitud."}
            return JsonResponse(datos, status=400)

        especialidades_existentes = Especialidad.objects.filter(id__in=especialidades_ids)
        if len(especialidades_existentes) != len(especialidades_ids):
            datos = {'mensaje': "Los ID de las especialidades no coinciden con la base de datos."}
            return JsonResponse(datos, status=400)

        nuevo_hospital = Hospital.objects.create(
            nombre=nombre,
            codigo_registro=codigo_registro,
            latitud=latitud,
            longitud=longitud
        )

        nuevo_hospital.especialidades.set(especialidades_existentes)

        datos = {'mensaje': "Hospital creado de manera exitosa!"}
        return JsonResponse(datos, status=200)

    
    def put(self, request):
        rp = json.loads(request.body)
        nombre = rp.get('nombre')
        nuevo_nombre = rp.get('nombre_nuevo')
        codigo_registro = rp.get('codigo_registro')
        latitud = rp.get('latitud')
        longitud = rp.get('longitud')
        especialidades_ids = rp.get('especialidades')
        cambios = False

        try:
            hospital = self.get_hospital_by_nombre(nombre)
        except Hospital.DoesNotExist:
            return JsonResponse({'mensaje': "El hospital no existe."}, status=404)

        if nuevo_nombre and nuevo_nombre != hospital.nombre:
            if Hospital.objects.filter(nombre=nuevo_nombre).exists():
                return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otro hospital."}, status=400)
            hospital.nombre = nuevo_nombre
            cambios = True
        if codigo_registro and codigo_registro != hospital.codigo_registro:
            if Hospital.objects.filter(codigo_registro=codigo_registro).exists():
                return JsonResponse({'mensaje': "El nuevo codigo de registro ya esta en uso por otro hospital."}, status=400)
            hospital.codigo_registro = codigo_registro
            cambios = True
        if latitud and latitud != hospital.latitud:
            hospital.latitud = latitud
            cambios = True
        if longitud and longitud != hospital.longitud:
            hospital.longitud = longitud
            cambios = True
        if especialidades_ids:
            especialidades_existentes = Especialidad.objects.filter(id__in=especialidades_ids)
            if len(especialidades_existentes) != len(especialidades_ids):
                return JsonResponse({'mensaje': "Los ID de las especialidades no coinciden con la base de datos."}, status=400)
            especialidades_actuales = set(hospital.especialidades.all())
            especialidades_nuevas = set(especialidades_existentes)
            if especialidades_actuales != especialidades_nuevas:
                hospital.especialidades.set(especialidades_existentes)
                cambios = True

        if cambios:
            hospital.save()
            return JsonResponse({'mensaje': "Hospital actualizado de manera exitosa!!"})
        else:
            return JsonResponse({'mensaje': "No hay cambios por realizar"}, status = 400)
    
    def delete(self, request):
        id = request.GET.get('id')
        nombre = request.GET.get('nombre')
        if not id and not nombre:
            return JsonResponse({'mensaje': "Se requiere proporcionar la ID o el nombre del hospital para eliminarlo."}, status=400)
        
        if id:
            try:
                hospital = self.get_hospital_by_id(id)
                hospital.delete()
                return JsonResponse({'mensaje': "Hospital eliminado correctamente."})
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital con la ID proporcionada no existe."}, status=404)
        
        if nombre:
            try:
                hospital = self.get_hospital_by_nombre(nombre)
                hospital.delete()
                return JsonResponse({'mensaje': "Hospital eliminado correctamente."})
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital con el nombre proporcionado no existe."}, status=404)