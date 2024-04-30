import json, os
from datetime import datetime
from datetime import date
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
        fecha_hora = solicitud.fecha_hora.strftime('%d/%m/%Y %H:%M')
        return {
        'id': solicitud.id,
        'emergencia_detectada': solicitud.emergencia_detectada,
        'direccion': solicitud.direccion,
        'nombre_usuario': solicitud.usuario.user.first_name,
        'apellido_usuario': solicitud.usuario.user.last_name,
        'correo_usuario': solicitud.usuario.user.email,
        'fecha_nacimiento_usuario': solicitud.usuario.fecha_nacimiento,
        'telefono_usuario': solicitud.usuario.telefono,
        'triage': solicitud.triage,
        'sintomas_presentes': solicitud.sintomas_presentes,
        'nombre_hospital': solicitud.hospital.nombre,
        'fecha_hora': fecha_hora
    }
        
    def solicitud_simplificada(self, solicitud):
        return {
        'emergencia_detectada': solicitud.emergencia_detectada,
        'triage': solicitud.triage,
        'nombre_usuario': solicitud.usuario.user.first_name,
        'apellido_usuario': solicitud.usuario.user.last_name,
        'edad_usuario': (date.today() - solicitud.usuario.fecha_nacimiento).days // 365 if solicitud.usuario.fecha_nacimiento else None,
    }
    
    def get(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        simplificada = data.get('simplificada')
        
        if especifica and not simplificada:
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
            if simplificada == "si":
                s = self.solicitud_simplificada(solicitud)
            else:
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

            if not all([solicitud_dto.direccion, solicitud_dto.id_usuario, solicitud_dto.emergencia_detectada, solicitud_dto.sintomas_presentes, solicitud_dto.id_hospital, solicitud_dto.triage]):
                parametros_faltantes = []
                if not solicitud_dto.direccion:
                    parametros_faltantes.append('direccion')
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
            
            if usuario.tipo_usuario.lower() != "usuario":
                return JsonResponse({'mensaje': 'No es un usuario valido para una solicitud (solo tipo usuario).'}, status=400)
            
            if solicitud_dto.triage < 1 or solicitud_dto.triage > 5:
                return JsonResponse({'mensaje': "Nivel de triage invalido"}, status=400)
            
            try:
                hospital = Hospital.objects.get(id=solicitud_dto.id_hospital)
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe un hospital con ese id.'}, status=404)
            
            fecha_hora = datetime.now()

            solicitud = Solicitud.objects.create(
                direccion=solicitud_dto.direccion,
                usuario=usuario,
                sintomas_presentes=solicitud_dto.sintomas_presentes,
                emergencia_detectada=solicitud_dto.emergencia_detectada,
                hospital = hospital,
                triage= solicitud_dto.triage,
                fecha_hora= fecha_hora
            )

            return JsonResponse({'mensaje': 'Solicitud creada exitosamente', 'id': solicitud.id}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
    
    def put(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)

        cambios = False
        id = data.get('id')

        if id:
            solicitud = self.buscar_por_id(id)
            if solicitud:
                direccion = data.get('direccion')
                sintomas_presentes = data.get('sintomas_presentes')
                emergencia_detectada = data.get('emergencia_detectada')
                triage = data.get('triage')
                id_usuario = data.get('id_usuario')
                id_hospital = data.get('id_hospital')

                if direccion is not None and solicitud.direccion != direccion:
                    solicitud.direccion = direccion
                    cambios = True

                if sintomas_presentes is not None:
                    solicitud.sintomas_presentes = sintomas_presentes
                    cambios = True

                if emergencia_detectada is not None and solicitud.emergencia_detectada != emergencia_detectada:
                    solicitud.emergencia_detectada = emergencia_detectada
                    cambios = True

                if triage is not None and solicitud.triage != triage:
                    solicitud.triage = triage
                    cambios = True

                if id_usuario is not None:
                    try:
                        usuario = Usuario.objects.get(id=id_usuario)
                        if solicitud.usuario != usuario:
                            if usuario.tipo_usuario.lower() != "usuario":
                                return JsonResponse({'mensaje': 'No es un usuario valido para una solicitud (solo tipo usuario).'}, status=400)
                            solicitud.usuario = usuario
                            cambios = True
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': 'No existe un usuario con ese id en la base de datos.'}, status=404)

                if id_hospital is not None:
                    try:
                        hospital = Hospital.objects.get(id=id_hospital)
                        if solicitud.hospital != hospital:
                            solicitud.hospital = hospital
                            cambios = True
                    except Hospital.DoesNotExist:
                        return JsonResponse({'mensaje': 'No existe un usuario con ese id en la base de datos.'}, status=404)

                if cambios:
                    solicitud.save()
                    return JsonResponse({'mensaje': 'Solicitud actualizada exitosamente'}, status=200)
                else:
                    return JsonResponse({'mensaje': 'No se realizaron cambios en la solicitud'}, status=200)
            else:
                return JsonResponse({'mensaje': 'No se encontro una solicitud con el ID proporcionado'}, status=404)
        else:
            return JsonResponse({'mensaje': 'Debe proporcionar un ID para actualizar una solicitud'}, status=400)

    
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
                return JsonResponse({'mensaje': 'No hay una solicitud con ese id.'}, status=400)
            
            if solicitud:
                solicitud.delete()
                return JsonResponse({'mensaje': 'Solicitud eliminada exitosamente.'}, status=200)
            else:
                return JsonResponse({'mensaje': 'No se pudo eliminar la solicitud.'}, status=400)
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
            if puntaje <= 3:
                triage = 5
            elif puntaje <= 5:
                triage = 4
            elif puntaje <=7:
                triage = 3
            elif puntaje < 10:
                triage = 2
            else:
                triage = 1
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