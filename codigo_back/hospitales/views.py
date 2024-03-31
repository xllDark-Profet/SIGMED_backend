
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from hospitales.models import EPS, Hospital, Especialidad
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
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
            
        id = data.get('id')
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        nombre = data.get('nombre')
        
        if especifica:     
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
                            'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()],
                            'listaeps': [eps.nombre for eps in hospital.listaeps.all()]
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
                                'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()],
                                'listaeps': [eps.nombre for eps in hospital.listaeps.all()]
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
                                'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()],
                                'listaeps': [eps.nombre for eps in hospital.eps.all()]
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
                            'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()],
                            'listaeps': [eps.nombre for eps in hospital.listaeps.all()]
                        }
                    })
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun hospital con nombre proporcionado."}, status=404)
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de hospital dentro de la peticion"}, status=400)
        
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
                'especialidades': list(especialidades),
                'listaeps': [eps.nombre for eps in hospital.listaeps.all()]
            })

        if hospitales_con_especialidades:
            datos = {'mensaje': "Peticion exitosa!", 'hospitales': hospitales_con_especialidades}
        else:
            datos = {'mensaje': "No hay hospitales"}

        return JsonResponse(datos)


    
    def post(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        required_fields = ['codigo_registro', 'nombre', 'latitud', 'longitud', 'especialidades', 'listaeps']
    
        for field in required_fields:
            if field not in data:
                datos = {'mensaje': f"El campo '{field}' es requerido."}
                return JsonResponse(datos, status=400)
        
        codigo_registro = data['codigo_registro']
        nombre = data['nombre']
        latitud = data['latitud']
        longitud = data['longitud']
        especialidades_ids = data['especialidades']
        listaeps_ids = data['listaeps']

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
        
        eps_existentes = EPS.objects.filter(id__in=listaeps_ids)
        if len(eps_existentes) != len(listaeps_ids):
            datos = {'mensaje': "Los ID de las eps no coinciden con la base de datos."}
            return JsonResponse(datos, status=400)

        nuevo_hospital = Hospital.objects.create(
            nombre=nombre,
            codigo_registro=codigo_registro,
            latitud=latitud,
            longitud=longitud
        )

        nuevo_hospital.especialidades.set(especialidades_existentes)
        nuevo_hospital.listaeps.set(eps_existentes)

        datos = {'mensaje': "Hospital creado de manera exitosa!"}
        return JsonResponse(datos, status=200)

    
    def put(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        nuevo_nombre = data.get('nombre_nuevo')
        codigo_registro = data.get('codigo_registro')
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        especialidades_ids = data.get('especialidades')
        listaeps_ids = data.get('listaeps')
        cambios = False
        
        if nombre:
            try:
                hospital = self.get_hospital_by_nombre(nombre)
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital no existe con ese nombre."}, status=404)
        elif id:
            try:
                hospital = self.get_hospital_by_id(id)
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital no existe con ese id."}, status=404)

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
        if listaeps_ids:
            eps_existentes = EPS.objects.filter(id__in=listaeps_ids)
            if len(eps_existentes) != len(listaeps_ids):
                return JsonResponse({'mensaje': "Los ID de las eps no coinciden con la base de datos."}, status=400)
            eps_actuales = set(hospital.listaeps.all())
            eps_nuevas = set(eps_existentes)
            if eps_actuales != eps_nuevas:
                hospital.listaeps.set(eps_nuevas)
                cambios = True
        
        if cambios:
            hospital.save()
            return JsonResponse({'mensaje': "Hospital actualizado de manera exitosa!!"}, status = 200)
        else:
            return JsonResponse({'mensaje': "No hay cambios por realizar"}, status = 400)
    
    def delete(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        id = data.get('id')
        nombre = data.get('nombre')
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
            
class EpsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_eps_by_id(self, id):
        return EPS.objects.get(id=id)
    
    def get_eps_by_nombre(self, nombre):
        return EPS.objects.get(nombre=nombre)

    def get(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            id = data.get('id')
            nombre = data.get('nombre')
            if id:
                try:
                    eps = self.get_eps_by_id(id)
                    return JsonResponse({
                        'Eps': {
                            'id': eps.id,
                            'nombre': eps.nombre
                        }
                    })
                except EPS.DoesNotExist:
                    return JsonResponse({'mensaje': "La eps con ese ID no existe en la base de datos"}, status=404)
            
            if nombre:
                try:
                    eps = self.get_eps_by_nombre(nombre)
                    return JsonResponse({
                        'Eps': {
                            'id': eps.id,
                            'nombre': eps.nombre
                        }
                    })
                except EPS.DoesNotExist:
                    datos = {'mensaje': "Eps no encontrada con ese nombre en la base de datos"}
                    return JsonResponse(datos, status=404)
            
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de eps dentro de la peticion"}, status=404)

        especialidades = EPS.objects.all()
        if especialidades:
            datos = {'mensaje': "Peticion exitosa!", 'eps': list(especialidades.values())}
        else:
            datos = {'mensaje': "No se encontraron eps en la base de datos"}

        return JsonResponse(datos)
    
    def post(self,request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        nombre = data.get('nombre')
        
        if EPS.objects.filter(nombre=nombre).exists():
            datos = {'mensaje': "Ya existe una eps con este nombre en la base de datos"}
            return JsonResponse(datos, status=400)
        
        if EPS.objects.create(nombre=nombre):
            return JsonResponse ({'mensaje': "Eps creada de manera exitosa!"}, status= 200)
        else:
            return JsonResponse ({'mensaje': "Error al crear la eps"}, status= 400)
        
    def put(self,request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        nombre_nuevo = data.get('nombre_nuevo')
        cambios = False

        if id:
            try:
                eps = self.get_eps_by_id(id)
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La eps con ese ID no existe."}, status=404)
            if nombre_nuevo and nombre_nuevo != eps.nombre:
                if EPS.objects.filter(nombre=nombre_nuevo).exists():
                    return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra EPS."}, status=400)
                eps.nombre = nombre_nuevo
                cambios = True
            
        elif nombre:
            try:
                eps = self.get_eps_by_nombre(nombre)
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': "La eps con ese nombre no existe."}, status=404)
            
            if nombre_nuevo and nombre_nuevo != eps.nombre:
                if EPS.objects.filter(nombre=nombre_nuevo).exists():
                    return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra eps."}, status=400)
                eps.nombre = nombre_nuevo
                cambios = True

        if cambios:
            eps.save()
            return JsonResponse({'mensaje': "Eps actualizada de manera exitosa!"})
        else:
            return JsonResponse({'mensaje': "No hay cambios por realizar"},status=400)        
    
    def delete(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        if not id and not nombre:
            return JsonResponse({'mensaje': "Se requiere proporcionar la ID o el nombre de la eps para eliminarla."}, status=400)
        
        if id:
            try:
                eps = self.get_eps_by_id(id)
                eps.delete()
                return JsonResponse({'mensaje': "Eps eliminada correctamente."})
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': "La Eps con la ID proporcionada no existe."}, status=404)
        
        if nombre:
            try:
                eps = self.get_eps_by_nombre(nombre)
                eps.delete()
                return JsonResponse({'mensaje': "Eps eliminada correctamente."})
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': "La Eps con el nombre proporcionado no existe."}, status=404)

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