import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from especialidades.models import Especialidad
from hospitales.models import Hospital

class EspecialidadView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_especialidad_by_id(self, id):
        return Especialidad.objects.get(id=id)
    
    def get_especialidad_by_nombre(self, nombre):
        return Especialidad.objects.get(nombre=nombre)

    def get(self, request):
        id = request.GET.get('id')
        nombre = request.GET.get('nombre')
        if id:
            try:
                especialidad = self.get_especialidad_by_id(id)
                return JsonResponse({
                    'Especialidad': {
                        'id': especialidad.id,
                        'nombre': especialidad.nombre
                    }
                })
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con ese ID no existe en la base de datos"}, status=404)
        
        if nombre:
            try:
                especialidad = self.get_especialidad_by_nombre(nombre)
                return JsonResponse({
                    'Especialidad': {
                        'id': especialidad.id,
                        'nombre': especialidad.nombre
                    }
                })
            except Especialidad.DoesNotExist:
                datos = {'mensaje': "Especialidad no encontrada con ese nombre en la base de datos"}
                return JsonResponse(datos, status=404)

        especialidades = Especialidad.objects.all()
        if especialidades:
            datos = {'mensaje': "Peticion exitosa!", 'especialidades': list(especialidades.values())}
        else:
            datos = {'mensaje': "No se encontraron especialidades en la base de datos"}

        return JsonResponse(datos)


    
    def post(self,request):
        rp = json.loads(request.body)
        nombre = rp.get('nombre')
        
        if Especialidad.objects.filter(nombre=nombre).exists():
            datos = {'mensaje': "Ya existe una especialidad con este nombre en la base de datos"}
            return JsonResponse(datos, status=400)

        nueva_especialidad = Especialidad.objects.create(nombre=nombre)
        datos = {'mensaje': "Especialidad creada de manera exitosa!"}
        return JsonResponse(datos, status=200)

    
    def put(self,request):
        rp = json.loads(request.body)
        id = request.GET.get('id')
        nombre = rp.get('nombre')
        nombre_nuevo = rp.get('nombre_nuevo')
        cambios = False

        if id:
            try:
                especialidad = self.get_especialidad_by_id(id)
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con ese ID no existe."}, status=404)
            if nombre_nuevo and nombre_nuevo != especialidad.nombre:
                if Especialidad.objects.filter(nombre=nombre_nuevo).exists():
                    return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra especialidad."}, status=400)
                especialidad.nombre = nombre_nuevo
                cambios = True
            
        elif nombre:
            try:
                especialidad = self.get_especialidad_by_nombre(nombre)
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con ese nombre no existe."}, status=404)
            
            if nombre_nuevo and nombre_nuevo != especialidad.nombre:
                if Especialidad.objects.filter(nombre=nombre_nuevo).exists():
                    return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra especialidad."}, status=400)
                especialidad.nombre = nombre_nuevo
                cambios = True

        if cambios:
            especialidad.save()
            return JsonResponse({'mensaje': "Especialidad actualizada de manera exitosa!"})
        else:
            return JsonResponse({'mensaje': "No hay cambios por realizar"},status=400)        
    
    def delete(self, request):
        id = request.GET.get('id')
        nombre = request.GET.get('nombre')
        if not id and not nombre:
            return JsonResponse({'mensaje': "Se requiere proporcionar la ID o el nombre de la especialidad para eliminarla."}, status=400)
        
        if id:
            try:
                especialidad = self.get_especialidad_by_id(id)
                especialidad.delete()
                return JsonResponse({'mensaje': "Especialidad eliminada correctamente."})
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con la ID proporcionada no existe."}, status=404)
        
        if nombre:
            try:
                especialidad = self.get_especialidad_by_nombre(nombre)
                especialidad.delete()
                return JsonResponse({'mensaje': "Especialidad eliminada correctamente."})
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con el nombre proporcionado no existe."}, status=404)
