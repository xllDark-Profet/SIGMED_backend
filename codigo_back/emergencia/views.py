import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Solicitud, Emergencia, Sintoma, Recomendacion
from .dtos import SolicitudDTO
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
        
class EmergenciasListView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        emergencias = Emergencia.objects.all()
        emergencias_list = []
        
        if not emergencias:
            return JsonResponse({'mensaje': 'No hay emergencias en la base de datos'}, status=404)
        for e in emergencias:
            emergencia = {
                'id': e.id,
                'nombre': e.nombre,
                'triage': e.triage
            }
            emergencias_list.append(emergencia)

        return JsonResponse(emergencias_list, safe=False)

class EmergenciaDetailView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        id = data.get('id')
        
        if id == "":
            return JsonResponse({'mensaje': 'Id se recibio vacio'}, status=400)
        elif not id:
            return JsonResponse({'mensaje': 'Debe ingresar un id'}, status=400)
        
        try:
            emergencia = Emergencia.objects.get(id=id)

            emergencia = {
                'id': emergencia.id,
                'nombre': emergencia.nombre,
                'triage': emergencia.triage,
            }

            return JsonResponse(emergencia, status=200)
        except Emergencia.DoesNotExist:
            return JsonResponse({'mensaje': 'La emergencia con ese id no existe'}, status=404)
        
def cargar_base_conocimiento(archivo):
    with open(archivo) as f:
        return json.load(f)['emergencias']

def generar_pregunta(sintoma):
    return f"¿Tienes {sintoma}? (sí/no): "

def obtener_respuesta(sintoma):
    return input(generar_pregunta(sintoma['sintoma'])).lower()

def mostrar_emergencia_identificada(emergencia_identificada):
    if emergencia_identificada:
        print("\nLa emergencia identificada es:", emergencia_identificada['nombre'])
    else:
        print("No se pudo identificar la emergencia.")

def mostrar_puntaje(emergencia, sintomas_acertados):
    puntaje = sum(sintoma['valor'] for sintoma in emergencia['sintomas'] if sintoma['sintoma'] in sintomas_acertados)
    print("Puntaje de la emergencia", emergencia['nombre'], ":", puntaje)

def mostrar_sintomas_acertados(sintomas_acertados):
    print("Síntomas Identificados:", sintomas_acertados)

def mostrar_recomendaciones(emergencia):
    if 'recomendaciones' in emergencia:
        print("Recomendaciones para la emergencia:", emergencia['nombre'])
        recomendaciones = emergencia['recomendaciones']
        for key, value in recomendaciones.items():
            print(f"- {key.capitalize()}: {value}")
    else:
        print("No hay recomendaciones disponibles para esta emergencia.")

def identificar_emergencia(emergencias, respuestas_usuario):
    emergencia_identificada = None
    puntaje_maximo = 0
    sintomas_acertados = []

    for emergencia in emergencias:
        sintomas_presentes = []
        continuar = True
        for sintoma in emergencia['sintomas']:
            respuesta = respuestas_usuario.get(sintoma['sintoma'], None)

            if respuesta is None:
                continuar = False
                break

            if respuesta == 'no' and sintoma['severidad'] == 'alta':
                puntaje = sum(sintoma['valor'] for sintoma in emergencia['sintomas'] if sintoma['sintoma'] in sintomas_presentes)
                continuar = False
                break

            if respuesta == 'si':
                sintomas_presentes.append(sintoma['sintoma'])

        if continuar:
            puntaje = sum(sintoma['valor'] for sintoma in emergencia['sintomas'] if sintoma['sintoma'] in sintomas_presentes)
            if puntaje > puntaje_maximo:
                puntaje_maximo = puntaje
                emergencia_identificada = emergencia
                sintomas_acertados = sintomas_presentes

    return emergencia_identificada, sintomas_acertados


class EnviarRespuestasView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON válido'}, status=400)
        
        solicitud_dto = SolicitudDTO(**data)

        if not solicitud_dto.usuario or not solicitud_dto.sintomas_respuestas:
            return JsonResponse({'mensaje': 'Se requieren el usuario y las respuestas'}, status=400)

        solicitud = Solicitud.objects.create(
            latitud=solicitud_dto.latitud,
            longitud=solicitud_dto.longitud,
            usuario=solicitud_dto.usuario,
            sintomas_respuestas=solicitud_dto.sintomas_respuestas
        )

        emergencia_identificada = None
        sintomas_acertados = []

        for emergencia in Emergencia.objects.all():
            sintomas_emergencia = emergencia.sintomas.values_list('nombre', flat=True)
            respuestas_usuario = solicitud_dto.sintomas_respuestas.keys()
            
            if set(sintomas_emergencia).issubset(set(respuestas_usuario)):
                emergencia_identificada = emergencia
                sintomas_acertados = list(sintomas_emergencia)
                break
        
        if emergencia_identificada:
            return JsonResponse({
                'mensaje': 'Respuestas procesadas exitosamente',
                'emergencia_identificada': {
                    'nombre': emergencia_identificada.nombre,
                    'triage': emergencia_identificada.triage,
                    'sintomas_acertados': sintomas_acertados
                }
            }, status=200)
        else:
            return JsonResponse({'mensaje': 'No se identificó ninguna emergencia'}, status=404)