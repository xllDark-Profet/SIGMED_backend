
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
    
    def buscar_hospital_por_id(self, id):
        return Hospital.objects.get(id=id)
    
    def buscar_hospital_por_latlong(self, latitud, longitud):
        return Hospital.objects.get(latitud=latitud, longitud=longitud)
    
    def buscar_hospital_por_nombre(self, nombre):
        return Hospital.objects.get(nombre=nombre)
    
    def mostrar_hospital(self, hospital):
        return {
            'id': hospital.id,
            'nombre': hospital.nombre,
            'latitud': hospital.latitud,
            'longitud': hospital.longitud,
            'especialidades': [especialidad.nombre for especialidad in hospital.especialidades.all()],
            'listaeps': [eps.nombre for eps in hospital.listaeps.all()]
        }
    
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
                    hospital = self.buscar_hospital_por_id(id)
                    return JsonResponse(self.mostrar_hospital(hospital))
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun hospital con el ID proporcionado."}, status=404)
            elif latitud:
                if longitud:
                    try:
                        hospital = self.buscar_hospital_por_latlong(latitud, longitud)
                        return JsonResponse(self.mostrar_hospital(hospital))
                    except Hospital.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun hospital con la latitud y longitud proporcionadas."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta la longitud"}, status=400)
            
            elif longitud:
                if latitud:
                    try:
                        hospital = self.buscar_hospital_por_latlong(latitud, longitud)
                        return JsonResponse(self.mostrar_hospital(hospital))
                    except Hospital.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun hospital con la latitud y longitud proporcionadas."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta la latitud"}, status=400)
                
            elif nombre:
                try:
                    hospital = self.buscar_hospital_por_nombre(nombre)
                    return JsonResponse(self.mostrar_hospital(hospital))
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun hospital con nombre proporcionado."}, status=404)
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de hospital dentro de la peticion"}, status=400)
        
        hospitales = Hospital.objects.all()

        hospitales_con_especialidades = []

        for hospital in hospitales:
            especialidades = hospital.especialidades.values_list('nombre', flat=True)
            hospitales_con_especialidades.append(self.mostrar_hospital(hospital))

        if hospitales_con_especialidades:
            return JsonResponse(hospitales_con_especialidades, safe=False, status=200)
        else:
            return JsonResponse({'mensaje': "No hay hospitales en la base de datos"})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON válido'}, status=400)

        if not isinstance(data, list):
            required_fields = ['nombre', 'latitud', 'longitud', 'especialidades', 'listaeps']
    
            for field in required_fields:
                if field not in data:
                    datos = {'mensaje': f"El campo '{field}' es requerido."}
                    return JsonResponse(datos, status=400)
            
            nombre = data['nombre']
            latitud = data['latitud']
            longitud = data['longitud']
            especialidades = data['especialidades']
            listaeps = data['listaeps']
            
            if Hospital.objects.filter(Q(latitud=latitud) & Q(longitud=longitud)).exists():
                datos = {'mensaje': "Ya existe un hospital con la misma latitud y longitud."}
                return JsonResponse(datos, status=400)

            especialidades_existentes = Especialidad.objects.filter(nombre__in=especialidades)
            if len(especialidades_existentes) != len(especialidades):
                datos = {'mensaje': "Los nombres de las especialidades no coinciden con la base de datos."}
                return JsonResponse(datos, status=400)
            
            eps_existentes = EPS.objects.filter(nombre__in=listaeps)
            if len(eps_existentes) != len(listaeps):
                datos = {'mensaje': "Los nombres de las EPS no coinciden con la base de datos."}
                return JsonResponse(datos, status=400)

            nuevo_hospital = Hospital.objects.create(
                nombre=nombre,
                latitud=latitud,
                longitud=longitud
            )

            nuevo_hospital.especialidades.set(especialidades_existentes)
            nuevo_hospital.listaeps.set(eps_existentes)

            return JsonResponse({'mensaje': "Hospital creado con exito"}, status=200)

        hospitals_created = []
        hospitals_failed = []

        for hospital_data in data:
            required_fields = ['nombre', 'latitud', 'longitud', 'especialidades', 'listaeps']
            for field in required_fields:
                if field not in hospital_data:
                    hospitals_failed.append({'mensaje': f"El campo '{field}' es requerido en uno de los hospitales."})
                    break
            else:
                nombre = hospital_data['nombre']
                latitud = hospital_data['latitud']
                longitud = hospital_data['longitud']
                especialidades = hospital_data['especialidades']
                listaeps = hospital_data['listaeps']
                
                if Hospital.objects.filter(Q(latitud=latitud) & Q(longitud=longitud)).exists():
                    hospitals_failed.append({'mensaje': f"Ya existe otro hospital con esa misma latitud y longitud que se ingreso del hospital '{nombre}'."})
                    continue

                especialidades_existentes = Especialidad.objects.filter(nombre__in=especialidades)
                if len(especialidades_existentes) != len(especialidades):
                    hospitals_failed.append({'mensaje': f"Los nombres de las especialidades del hospital '{nombre}' no coinciden con la base de datos."})
                    continue
                
                eps_existentes = EPS.objects.filter(nombre__in=listaeps)
                if len(eps_existentes) != len(listaeps):
                    hospitals_failed.append({'mensaje': f"Los nombres de las EPS del hospital '{nombre}' no coinciden con la base de datos."})
                    continue

                nuevo_hospital = Hospital.objects.create(
                    nombre=nombre,
                    latitud=latitud,
                    longitud=longitud
                )

                nuevo_hospital.especialidades.set(especialidades_existentes)
                nuevo_hospital.listaeps.set(eps_existentes)

                hospitals_created.append({'mensaje': f"Hospital '{nombre}' creado con exito"})

        response_data = {
            'hospitales_creados': hospitals_created,
            'hospitales_fallidos': hospitals_failed
        }

        return JsonResponse(response_data, status=200)
    
    def put(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        especialidades = data.get('especialidades')
        listaeps = data.get('listaeps')
        cambios = False
        
        if id:
            try:
                hospital = self.buscar_hospital_por_id(id)
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital no existe con ese id."}, status=404)

        if nombre and nombre != hospital.nombre:
            if Hospital.objects.filter(nombre=nombre).exists():
                return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otro hospital."}, status=400)
            hospital.nombre = nombre
            cambios = True
        if latitud and latitud != hospital.latitud:
            hospital.latitud = latitud
            cambios = True
        if longitud and longitud != hospital.longitud:
            hospital.longitud = longitud
            cambios = True
        if especialidades is not None:
            if not especialidades:
                hospital.especialidades.set([])
                cambios = True
            else:
                especialidades_existentes = Especialidad.objects.filter(nombre__in=especialidades)
                if len(especialidades_existentes) != len(especialidades):
                    return JsonResponse({'mensaje': "Los nombres de las especialidades no coinciden con la base de datos."}, status=400)
                especialidades_actuales = set(hospital.especialidades.all())
                especialidades_nuevas = set(especialidades_existentes)
                if especialidades_actuales != especialidades_nuevas:
                    hospital.especialidades.set(especialidades_existentes)
                    cambios = True
        else:
            hospital.especialidades.set([])
            cambios = True
        if listaeps is not None:
            if not listaeps:
                hospital.listaeps.set([])
                cambios = True
            else:
                eps_existentes = EPS.objects.filter(nombre__in=listaeps)
                if len(eps_existentes) != len(listaeps):
                    return JsonResponse({'mensaje': "Los nombres de las EPS no coinciden con la base de datos."}, status=400)
                eps_actuales = set(hospital.listaeps.all())
                eps_nuevas = set(eps_existentes)
                if eps_actuales != eps_nuevas:
                    hospital.listaeps.set(eps_nuevas)
                    cambios = True
        else:
            hospital.listaeps.set([])
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
                hospital = self.buscar_hospital_por_id(id)
                hospital.delete()
                return JsonResponse({'mensaje': "Hospital eliminado correctamente."})
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital con la ID proporcionada no existe."}, status=404)
        
        if nombre:
            try:
                hospital = self.buscar_hospital_por_nombre(nombre)
                hospital.delete()
                return JsonResponse({'mensaje': "Hospital eliminado correctamente."})
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': "El hospital con el nombre proporcionado no existe."}, status=404)
            
class EpsView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_eps_por_id(self, id):
        return EPS.objects.get(id=id)
    
    def buscar_eps_por_nombre(self, nombre):
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
                    eps = self.buscar_eps_por_id(id)
                    return JsonResponse({
                        'id': eps.id,
                        'nombre': eps.nombre
                    })
                except EPS.DoesNotExist:
                    return JsonResponse({'mensaje': "La eps con ese ID no existe en la base de datos"}, status=404)
            
            if nombre:
                try:
                    eps = self.buscar_eps_por_nombre(nombre)
                    return JsonResponse({
                        'id': eps.id,
                        'nombre': eps.nombre
                    })
                except EPS.DoesNotExist:
                    datos = {'mensaje': "Eps no encontrada con ese nombre en la base de datos"}
                    return JsonResponse(datos, status=404)
            
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de eps dentro de la peticion"}, status=404)

        listaeps = EPS.objects.all()
        eps_list = []
        
        for eps in listaeps:
            eps_info = {
                'id': eps.id,
                "nombre": eps.nombre
            }
            eps_list.append(eps_info)
            
        if eps_list:
            return JsonResponse(eps_list, safe=False, status=200)
        else:
            return JsonResponse({'mensaje': "No se encontraron eps en la base de datos"})

    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)

        if not isinstance(data, list):
            nombre = data.get('nombre')
            if nombre:
                if EPS.objects.filter(nombre=nombre).exists():
                    return JsonResponse({'mensaje': "Ya existe una EPS con este nombre en la base de datos"}, status=400)
                EPS.objects.create(nombre=nombre)
                return JsonResponse({'mensaje': "EPS creada con exito"}, status=200)
            else:
                return JsonResponse({'mensaje': "Se esperaba el nombre de la EPS"}, status=400)
        else:
            for eps_data in data:
                nombre = eps_data.get('nombre')
                if nombre:
                    if EPS.objects.filter(nombre=nombre).exists():
                        return JsonResponse({'mensaje': f"Ya existe una EPS con el nombre '{nombre}' en la base de datos"}, status=400)
                    EPS.objects.create(nombre=nombre)
                else:
                    return JsonResponse({'mensaje': "Se esperaba el nombre para cada EPS"}, status=400)
            return JsonResponse({'mensaje': "EPS creadas con exito"}, status=200)
        
    def put(self,request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        cambios = False

        if id:
            eps = self.buscar_eps_por_id(id)
            if eps is None:
                return JsonResponse({'mensaje': "La eps con ese id no existe."}, status=404)
            if nombre and nombre != eps.nombre:
                if EPS.objects.filter(nombre=nombre).exists():
                    return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra EPS."}, status=400)
                eps.nombre = nombre
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
                eps = self.buscar_eps_por_id(id)
                eps.delete()
                return JsonResponse({'mensaje': "Eps eliminada correctamente."})
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': "La Eps con la ID proporcionada no existe."}, status=404)
        
        if nombre:
            try:
                eps = self.buscar_eps_por_nombre(nombre)
                eps.delete()
                return JsonResponse({'mensaje': "Eps eliminada correctamente."})
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': "La Eps con el nombre proporcionado no existe."}, status=404)

class EspecialidadView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_especialidad_por_id(self, id):
        return Especialidad.objects.get(id=id)
    
    def buscar_especialidad_por_nombre(self, nombre):
        return Especialidad.objects.get(nombre=nombre)

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
                especialidad = self.buscar_especialidad_por_id(id)
                if especialidad:
                    return JsonResponse({
                        'id': especialidad.id,
                        'nombre': especialidad.nombre
                    })
                else:
                    return JsonResponse({'mensaje': "La especialidad con ese ID no existe en la base de datos"}, status=404)
            
            if nombre:
                especialidad = self.buscar_especialidad_por_nombre(nombre)
                if especialidad:
                    return JsonResponse({
                        'id': especialidad.id,
                        'nombre': especialidad.nombre
                    })
                else:
                    datos = {'mensaje': "Especialidad no encontrada con ese nombre en la base de datos"}
                    return JsonResponse(datos, status=404)
                
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de especialidad dentro de la peticion"}, status=404)

        especialidades = Especialidad.objects.all()
        listaesp = []
        for e in especialidades:
            especialidad = {
                "id": e.id,
                "nombre": e.nombre
            }
            listaesp.append(especialidad)
        if listaesp:
            return JsonResponse(listaesp, safe=False, status=200)
        else:
            return JsonResponse({'mensaje': "No se encontraron especialidades en la base de datos"})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)

        if not isinstance(data, list):
            nombre = data.get('nombre')
            if nombre:
                if Especialidad.objects.filter(nombre=nombre).exists():
                    return JsonResponse({'mensaje': "Ya existe una especialidad con este nombre en la base de datos"}, status=400)
                Especialidad.objects.create(nombre=nombre)
                return JsonResponse({'mensaje': "Especialidad creada con exito"}, status=200)
            else:
                return JsonResponse({'mensaje': "Se esperaba el nombre para la especialidad"}, status=400)
        else:
            for especialidad_data in data:
                nombre = especialidad_data.get('nombre')
                if nombre:
                    if Especialidad.objects.filter(nombre=nombre).exists():
                        return JsonResponse({'mensaje': f"Ya existe una especialidad con el nombre '{nombre}' en la base de datos"}, status=400)
                    Especialidad.objects.create(nombre=nombre)
                else:
                    return JsonResponse({'mensaje': "Se esperaba el nombre para cada especialidad"}, status=400)
            return JsonResponse({'mensaje': "Especialidades creadas con exito"}, status=200)
    
    def put(self,request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        id = data.get('id')
        nombre = data.get('nombre')
        cambios = False

        if id:
            try:
                especialidad = self.buscar_especialidad_por_id(id)
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con ese ID no existe."}, status=404)
            
            if nombre:
                if nombre != especialidad.nombre:
                    if Especialidad.objects.filter(nombre=nombre).exists():
                        return JsonResponse({'mensaje': "El nuevo nombre ya esta en uso por otra especialidad."}, status=400)
                    especialidad.nombre = nombre
                    cambios = True

        if cambios:
            especialidad.save()
            return JsonResponse({'mensaje': "Especialidad actualizada de manera exitosa!"})
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
            return JsonResponse({'mensaje': "Se requiere proporcionar la ID o el nombre de la especialidad para eliminarla."}, status=400)
        
        if id:
            try:
                especialidad = self.buscar_especialidad_por_id(id)
                especialidad.delete()
                return JsonResponse({'mensaje': "Especialidad eliminada correctamente."})
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con la ID proporcionada no existe."}, status=404)
        elif nombre:
            try:
                especialidad = self.buscar_especialidad_por_nombre(nombre)
                especialidad.delete()
                return JsonResponse({'mensaje': "Especialidad eliminada correctamente."})
            except Especialidad.DoesNotExist:
                return JsonResponse({'mensaje': "La especialidad con el nombre proporcionado no existe."}, status=404)