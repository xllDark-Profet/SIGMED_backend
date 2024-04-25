import json, os
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from hospitales.models import Hospital

from .models import Solicitud
from .dtos import RespuestasDTO, SolicitudDTO
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
            'emergencia_detectada': solicitud.emergencia_detectada,
            'latitud': solicitud.latitud,
            'longitud': solicitud.longitud,
            'usuario': {
                'id': solicitud.usuario.id,
                'correo': solicitud.usuario.user.email,
                'username': solicitud.usuario.user.username,
            },
            'hospital': {
                'id': solicitud.hospital.id,
                'nombre': solicitud.hospital.nombre
            },
            'triage': solicitud.triage,
            'sintomas_presentes': solicitud.sintomas_presentes
        }
    
    def get(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            id = data.get('id')
            
            if id:
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
        try:
            data = json.loads(request.body)
            solicitud_dto = SolicitudDTO(**data)

            if not all([solicitud_dto.latitud, solicitud_dto.longitud, solicitud_dto.id_usuario, solicitud_dto.emergencia_detectada, solicitud_dto.sintomas_presentes, solicitud_dto.id_hospital, solicitud_dto.triage]):
                parametros_faltantes = []
                if not solicitud_dto.latitud:
                    parametros_faltantes.append('latitud')
                if not solicitud_dto.longitud:
                    parametros_faltantes.append('longitud')
                if not solicitud_dto.id_usuario:
                    parametros_faltantes.append('id_usuario')
                if not solicitud_dto.emergencia_detectada:
                    parametros_faltantes.append('emergencia_detectada')
                if not solicitud_dto.sintomas_presentes:
                    parametros_faltantes.append('sintomas_presentes')
                if not solicitud_dto.id_hospital:
                    parametros_faltantes.append('id_hospital')
                if not solicitud_dto.triage:
                    parametros_faltantes.append('triage')
                    
                mensaje_error = f'Falta el/los siguiente(s) parametro(s): {", ".join(parametros_faltantes)}'
                return JsonResponse({'mensaje': mensaje_error}, status=400)

            try:
                usuario = Usuario.objects.get(id=solicitud_dto.id_usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe un usuario con ese id.'}, status=404)
            
            try:
                hospital = Hospital.objects.get(id=solicitud_dto.id_hospital)
            except Usuario.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe un hospital con ese id.'}, status=404)

            solicitud = Solicitud.objects.create(
                latitud=solicitud_dto.latitud,
                longitud=solicitud_dto.longitud,
                usuario=usuario,
                sintomas_presentes=solicitud_dto.sintomas_presentes,
                emergencia_detectada=solicitud_dto.emergencia_detectada,
                hospital = hospital,
                triage=solicitud_dto.triage
            )

            return JsonResponse({'mensaje': 'Solicitud creada exitosamente', 'id': solicitud.id}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
    
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
            
            if id:
                solicitud = self.buscar_por_id(id)
            else:
                return JsonResponse({'mensaje': 'Debe proporcionar un ID para una solicitud especifica.'}, status=400)
            
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
            solicitud = None
            if id:
                solicitud = self.buscar_por_id(id)
            else:
                return JsonResponse({'mensaje': 'Parametros invalidos de busqueda.'}, status=400)
            
            if solicitud:
                solicitud.delete()
                return JsonResponse({'mensaje': 'Solicitud eliminada exitosamente.'}, status=200)
            else:
                return JsonResponse({'mensaje': 'No se encontro una solicitud con el parametro de busqueda enviado.'}, status=400)
        else:
            return JsonResponse({'mensaje': 'Debe proporcionar un id para detectar la solicitud a eliminar.'}, status=400)

class IdentificadorView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        respuestasDTO = RespuestasDTO(**data)
        
        if not respuestasDTO.sintomas_presentes:
            respuestasDTO.sintomas_presentes = ""
        
        dir_actual = os.path.dirname(__file__)
        ruta_emergencias_json = os.path.join(dir_actual, 'emergencias.json')
        with open(ruta_emergencias_json) as f:
            emergencias = json.load(f)['emergencias']
        sintoma, emergencia_identificada = identificar_emergencia(emergencias, respuestasDTO.sintomas_presentes)
        if not emergencia_identificada and sintoma:
            return JsonResponse({'sintoma': sintoma['sintoma']}, status=200)
        elif emergencia_identificada:
            sintomas = [sintoma for sintoma, respuesta in respuestasDTO.sintomas_presentes.items() if respuesta == "si"]
            puntaje = sum(sintoma['valor'] for sintoma in emergencia_identificada['sintomas'] if sintoma['sintoma'] in sintomas)
            triage = 0
            if puntaje < 3:
                triage = 1
            elif puntaje < 7:
                triage = 2
            else:
                triage = 3
            return JsonResponse({'emergencia_detectada': emergencia_identificada['nombre'], 'especialidad': emergencia_identificada['especialidad'], 'sintomas_presentes':sintomas, 'recomendaciones': emergencia_identificada['recomendaciones'], 'triage': triage}, status=200)
        else:
            return JsonResponse({'mensaje': 'No se pudo detectar la emergencia'}, status=200)

def obtener_respuesta(sintoma, sintomas_respuestas):
    if sintoma['sintoma'] in sintomas_respuestas:
        return sintomas_respuestas[sintoma['sintoma']]
    else:
        return None

def identificar_emergencia(emergencias, sintomas_respuestas):
    respuestas_anteriores = {}
    emergencia_identificada = None

    for emergencia in emergencias:
        sintomas_presentes = []
        continuar = True
        for sintoma in emergencia['sintomas']:
            if sintoma['sintoma'] in respuestas_anteriores:
                respuesta = respuestas_anteriores[sintoma['sintoma']]
            else:
                respuesta = obtener_respuesta(sintoma, sintomas_respuestas)
                if not respuesta:
                    return sintoma, None
                else:
                    respuestas_anteriores[sintoma['sintoma']] = respuesta

            if respuesta == 'no' and sintoma['severidad'] == 'alta':
                continuar = False
                break

            if respuesta == 'si':
                sintomas_presentes.append(sintoma['sintoma'])

        if continuar:
            if emergencia_identificada is None:
                if emergencia != None:
                    emergencia_identificada = emergencia
                break

    if emergencia_identificada:
        return None, emergencia_identificada
    else:
        return None, None