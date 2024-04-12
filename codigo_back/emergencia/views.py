import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from emergencia.models import Solicitud
from usuarios.models import Usuario

class SolicitudesView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_por_emergencia(self, emergencia):
        try:
            return Solicitud.objects.get(emergencia=emergencia)
        except Solicitud.DoesNotExist:
            return None
        
    def buscar_por_id(self, id):
        try:
            return Solicitud.objects.get(id=id)
        except Solicitud.DoesNotExist:
            return None
        
    def mostrar_solicitud(self, solicitud):
        return {
            'id': solicitud.id,
            'emergencia': solicitud.emergencia,
            'latitud': solicitud.latitud,
            'longitud': solicitud.longitud,
            'usuario': {
                'id': solicitud.usuario.id,
                'correo': solicitud.usuario.user.email,
                'username': solicitud.usuario.user.username,
            }
        }
    
    def get(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            emergencia = data.get('emergencia')
            id = data.get('id')
            
            if emergencia:
                solicitud = self.buscar_por_emergencia(emergencia)
                if not solicitud:
                    return JsonResponse({'mensaje': 'No se encontro ninguna solicitud con el numero de emergencia proporcionado.'}, status=404)
                else:
                    self.mostrar_solicitud(solicitud)
            elif id:
                solicitud = self.buscar_por_id(id)
                if not solicitud:
                    return JsonResponse({'mensaje': 'No se encontro ninguna solicitud con el id proporcionado.'}, status=404)
                else:
                    self.mostrar_solicitud(solicitud)
            else:
                return JsonResponse({'mensaje': 'Los parametros ingresados no son validos para una solicitud'}, status=404)
        
        
        solicitudes = Solicitud.objects.all()
        solicitudes_list = []
        
        for solicitud in solicitudes:
            s = self.mostrar_solicitud(solicitud)
            solicitudes_list.append(s)
        
        if not solicitudes_list:
            return JsonResponse({'mensaje': 'No hay solicitudes registradas en el sistema'})
        else:
            return JsonResponse(solicitudes_list, safe=False, status=200)
        
    def post(self, request):
        data = json.loads(request.body)
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        usuario = data.get('usuario')
        emergencia = data.get('emergencia')
        
        if not all([latitud, longitud, usuario, emergencia]):
            return JsonResponse({'mensaje': 'Todos los campos son requeridos'}, status=400)
        
        try:
            usuario = Usuario.objects.get(id=usuario)
        except Usuario.DoesNotExist:
            return JsonResponse({'mensaje': 'El usuario proporcionado no existe'}, status=404)
        
        solicitud = Solicitud.objects.create(
            latitud=latitud,
            longitud=longitud,
            usuario=usuario,
            emergencia=emergencia
        )
        
        return JsonResponse({'mensaje': 'Solicitud creada exitosamente', 'id': solicitud.id}, status=201)
    
    def put(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            cambios = False
            id = data.get('id')
            emergencia = data.get('emergencia')
            
            if id:
                solicitud = self.buscar_por_id(id)
            elif emergencia:
                solicitud = self.buscar_por_emergencia(emergencia)
            else:
                return JsonResponse({'mensaje': 'Debe proporcionar un ID o una emergencia para una solicitud especifica.'}, status=400)
            
            if solicitud:
                latitud = data.get('latitud')
                longitud = data.get('longitud')
                usuario = data.get('usuario')
                
                
                if latitud and solicitud.latitud != latitud:
                    solicitud.latitud = latitud
                    cambios = True
                elif longitud and solicitud.longitud != longitud:
                    solicitud.longitud = longitud
                    cambios = True
                elif usuario:
                    try:
                        usuario = Usuario.objects.get(id=usuario)
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': 'El usuario proporcionado no existe'}, status=404)
                    if solicitud.usuario != usuario:
                        solicitud.usuario = usuario
                        cambios = True
                if cambios:
                    solicitud.save()
                    return JsonResponse({'mensaje': 'Solicitud actualizada exitosamente'}, status=200)
                else:
                    return JsonResponse({'mensaje': 'No hubo cambios por realizar'}, status=400)
            else:
                return JsonResponse({'mensaje': 'No se encontro una solicitud especifica.'}, status=400)
    
    def delete(self, request):
        
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            id = data.get('id')
            emergencia = data.get('emergencia')
            solicitud = None
            if id:
                solicitud = self.buscar_por_id(id)
            elif emergencia:
                solicitud = self.buscar_por_emergencia(emergencia)
            else:
                return JsonResponse({'mensaje': 'Parametros invalidos de busqueda.'}, status=400)
            
            if solicitud:
                solicitud.delete()
                return JsonResponse({'mensaje': 'Solicitud eliminada exitosamente.'}, status=200)
            else:
                return JsonResponse({'mensaje': 'No se encontro una solicitud con el parametro de busqueda enviado.'}, status=400)
        else:
            return JsonResponse({'mensaje': 'Debe proporcionar un id o un numero de emergencia para detectar la solicitud a eliminar.'}, status=400)