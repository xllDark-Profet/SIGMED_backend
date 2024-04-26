from functools import wraps
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views import View
from django.db import transaction
from django.contrib.auth.hashers import make_password

from sigmed.constants import TIPOS_USUARIO
from hospitales.models import EPS, Hospital
from usuarios.models import Usuario

class UsuarioView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_por_id(self, id_usuario):
        try:
            return Usuario.objects.get(user__id=id_usuario)
        except Usuario.DoesNotExist:
            return None
    
    def buscar_por_username(self, nombre_usuario):
        try:
            return Usuario.objects.get(user__username=nombre_usuario)
        except Usuario.DoesNotExist:
            return None
        
    def buscar_por_correo(self, correo):
        try:
            return Usuario.objects.get(user__email=correo)
        except Usuario.DoesNotExist:
            return None
        
    def buscar_por_telefono(self, telefono):
        try:
            return Usuario.objects.get(telefono=telefono)
        except Usuario.DoesNotExist:
            return None

    def buscar_por_identificacion(self, tipo_identificacion, identificacion):
        try:
            return Usuario.objects.get(tipo_identificacion=tipo_identificacion, identificacion=identificacion)
        except Usuario.DoesNotExist:
            return None
        
    def mostrar_admin(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario
        }
        
    def mostrar_moderador(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario,
            'hospital': u.hospital.id
        }
    
    def mostrar_usuario(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario,
            'tipo_sangre': u.tipo_sangre,
            'fecha_nacimiento': u.fecha_nacimiento,
            'eps': u.eps.id
        }
    
    def get(self, request):
        
        usuarios = Usuario.objects.all()
        usuarios_list = []
        
        for usuario in usuarios:
            if usuario.tipo_usuario.lower() == "administrador":
                usuario_info = self.mostrar_admin(usuario)
            elif usuario.tipo_usuario.lower() == "moderador":
                usuario_info = self.mostrar_moderador(usuario)
            elif usuario.tipo_usuario.lower() == "usuario":
                usuario_info = self.mostrar_usuario(usuario)
            usuarios_list.append(usuario_info)
        
        if not usuarios_list:
            return JsonResponse({'mensaje': 'No hay usuarios en el sistema'})
        else:
            return JsonResponse(usuarios_list, safe=False, status=200)

        
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)

        if not isinstance(data, list):
            required_fields = ['tipo_identificacion', 'identificacion', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_usuario', 'clave', 'tipo_usuario']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'mensaje': f'El campo {field} es requerido'}, status=400)
                
            usuario = Usuario()

            usuario.tipo_identificacion = data.get('tipo_identificacion')
            usuario.identificacion = data.get('identificacion')
            nombre = data.get('nombre')
            apellido = data.get('apellido')
            correo = data.get('correo')
            usuario.telefono = data.get('telefono')
            nombre_usuario = data.get('nombre_usuario')
            clave = data.get('clave')
            clave = make_password(clave)
            tipo_usuario = data.get('tipo_usuario').lower()
            if User.objects.filter(username=nombre_usuario).exists():
                return JsonResponse({'mensaje': 'Ya hay un usuario con ese nombre de usuario en la base de datos.'}, status=400)
            user = User(username=nombre_usuario, email=correo, password=clave, first_name=nombre, last_name=apellido)
            usuario.user = user
                
            if tipo_usuario not in [tipo.lower() for tipo in TIPOS_USUARIO]:
                return JsonResponse({'mensaje': 'No existe ese tipo de usuario.'}, status=400)
            
            usuario.tipo_usuario = tipo_usuario
            if tipo_usuario == "moderador":
                nombre_hospital = data.get('nombre_hospital')
                if nombre_hospital:
                    try:
                        hospital = Hospital.objects.get(nombre=nombre_hospital)
                        if hospital:
                            usuario.hospital = hospital
                    except Hospital.DoesNotExist:
                        return JsonResponse({'mensaje': 'No existe un hospital con ese nombre.'}, status=400)
                else:
                    return JsonResponse({'mensaje': 'Para un moderador es necesario un id de hospital'}, status=400)
            elif tipo_usuario == "usuario":
                fecha_nacimiento = data.get('fecha_nacimiento')
                tipo_sangre = data.get('tipo_sangre')
                nombre_eps = data.get('nombre_eps')
                required_fields = ['tipo_sangre', 'fecha_nacimiento', 'nombre_eps']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return JsonResponse({'mensaje': f'El campo {field} es requerido para un usuario'}, status=400)
                else:
                    try:
                        eps = EPS.objects.get(nombre=nombre_eps)
                        if eps:
                            usuario.eps = eps
                    except EPS.DoesNotExist:
                        return JsonResponse({'mensaje': 'No existe esa EPS en el sistema con ese nombre.'}, status=400)
                usuario.fecha_nacimiento = fecha_nacimiento
                usuario.tipo_sangre = tipo_sangre

            user.save()
            usuario.save()

            return JsonResponse({'mensaje': 'Usuario registrado exitosamente.'}, status=200)

        users_created = []
        users_failed = []

        for user_data in data:
            required_fields = ['tipo_identificacion', 'identificacion', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_usuario', 'clave', 'tipo_usuario']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    users_failed.append({'mensaje': f"El campo '{field}' es requerido en uno de los usuarios."})
                    break
            else:
                usuario = Usuario()

                usuario.tipo_identificacion = user_data.get('tipo_identificacion')
                usuario.identificacion = user_data.get('identificacion')
                nombre = user_data.get('nombre')
                apellido = user_data.get('apellido')
                correo = user_data.get('correo')
                usuario.telefono = user_data.get('telefono')
                nombre_usuario = user_data.get('nombre_usuario')
                clave = user_data.get('clave')
                clave = make_password(clave)
                tipo_usuario = user_data.get('tipo_usuario').lower()
                if User.objects.filter(username=nombre_usuario).exists():
                    users_failed.append({'mensaje': f"Nombre de usuario '{nombre_usuario}' ya existe en la base de datos."})
                    continue
                user = User(username=nombre_usuario, email=correo, password=clave, first_name=nombre, last_name=apellido)
                usuario.user = user
                
                if tipo_usuario not in [tipo.lower() for tipo in TIPOS_USUARIO]:
                    users_failed.append({'mensaje': 'No existe ese tipo de usuario.'})
                    continue
                
                usuario.tipo_usuario = tipo_usuario
                
                if tipo_usuario == "moderador":
                    nombre_hospital = user_data.get('nombre_hospital')
                    if nombre_hospital:
                        try:
                            hospital = Hospital.objects.get(nombre=nombre_hospital)
                            if hospital:
                                usuario.hospital = hospital
                        except Hospital.DoesNotExist:
                            users_failed.append({'mensaje':  f"No existe un hospital con el nombre '{nombre_hospital}'."})
                            continue
                    else:
                        users_failed.append({'mensaje': 'Para un moderador es necesario un id de hospital.'})
                        continue
                elif tipo_usuario == "usuario":
                    fecha_nacimiento = user_data.get('fecha_nacimiento')
                    tipo_sangre = user_data.get('tipo_sangre')
                    nombre_eps = user_data.get('nombre_eps')
                    required_fields = ['tipo_sangre', 'fecha_nacimiento', 'nombre_eps']
                    for field in required_fields:
                        if field not in user_data or not user_data[field]:
                            users_failed.append({'mensaje': f"El campo '{field}' es requerido para un usuario."})
                            break
                    else:
                        try:
                            eps = EPS.objects.get(nombre=nombre_eps)
                            if eps:
                                usuario.eps = eps
                        except EPS.DoesNotExist:
                            users_failed.append({'mensaje':  f"No existe una eps con el nombre '{nombre_eps}'."})
                            continue
                    usuario.fecha_nacimiento = fecha_nacimiento
                    usuario.tipo_sangre = tipo_sangre

                user.save()
                usuario.save()

                users_created.append({'mensaje': f"Usuario '{nombre_usuario}' registrado exitosamente."})

        response_data = {
            'usuarios_creados': users_created,
            'usuarios_fallidos': users_failed
        }

        return JsonResponse(response_data, status=200)
    
    def put(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        cambios = False

        tipo_identificacion = data.get('tipo_identificacion')
        identificacion = data.get('identificacion')
        id = data.get('id')
        
        if id:
            usuario = self.buscar_por_id(id)
        elif tipo_identificacion and identificacion:
            usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
        
        if not usuario:
            return JsonResponse({'mensaje': 'Debe ingresar un id de usuario o un tipo y numero de documento validos'}, status=404)

        nombre_usuario = data.get('nombre_usuario')
        clave = data.get('clave')
        nueva_clave = data.get('nueva_clave')
        nueva_clave = make_password(nueva_clave)
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        telefono = data.get('telefono')
        fecha_nacimiento = data.get('fecha_nacimiento')
        tipo_sangre = data.get('tipo_sangre')
        hospital_id = data.get('hospital_id')
        eps_id = data.get('eps_id')

        if nombre and nombre != usuario.user.first_name:
            usuario.user.first_name = nombre
            cambios = True
        if apellido and apellido != usuario.user.last_name:
            usuario.user.last_name = apellido
            cambios = True
        if correo and correo != usuario.user.email:
            if correo != usuario.user.email:
                if self.buscar_por_correo(correo):
                    return JsonResponse({'mensaje': 'Ya existe ese correo.'}, status=400)
                else:
                    cambios=True
                    usuario.user.email = correo
        if nombre_usuario:
            if nombre_usuario != usuario.user.username:
                if self.buscar_por_username(nombre_usuario):
                    return JsonResponse({'mensaje': 'Ya existe ese nombre de usuario.'}, status=400)
                else:
                    cambios=True
                    usuario.user.username = nombre_usuario
        
        if clave:            
            if usuario.user.check_password(clave):
                if nueva_clave:
                    cambios = True
                    usuario.user.set_password(nueva_clave)
                else:
                    return JsonResponse({'mensaje': 'La clave actual del usuario es incorrecta.'}, status=400)
            else:
                return JsonResponse({'mensaje': 'La clave actual del usuario es incorrecta.'}, status=400)

        if telefono:
            if telefono != usuario.telefono:
                if self.buscar_por_username(nombre_usuario):
                    return JsonResponse({'mensaje': 'Ya existe ese nombre de usuario.'}, status=400)
                else:
                    usuario.telefono = telefono
                    cambios = True
                    
        if fecha_nacimiento and fecha_nacimiento != usuario.fecha_nacimiento:
            usuario.fecha_nacimiento = fecha_nacimiento
            cambios = True
        if tipo_sangre and tipo_sangre != usuario.tipo_sangre:
            usuario.tipo_sangre = tipo_sangre
            cambios = True
        
        if hospital_id:
            try:
                hospital = Hospital.objects.get(id=hospital_id)
                if hospital != usuario.hospital:
                    usuario.hospital = hospital
                    cambios = True
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe un hospital con ese codigo de registro.'}, status=400)
        
        if eps:
            try:
                eps = EPS.objects.get(id = eps_id)
                if eps != usuario.eps:
                    usuario.eps = eps
                    cambios = True
            except EPS.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe una EPS con ese codigo de registro.'}, status=400)

        if cambios:
            usuario.save()
            return JsonResponse({'mensaje': 'Usuario actualizado exitosamente.'}, status=200)
        else:
            return JsonResponse({'mensaje': 'No se realizaron cambios en el usuario.'}, status=400)
        
    def delete(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        id = data.get('id')
        nombre_usuario = data.get('nombre_usuario')
        tipo_identificacion = data.get('tipo_identificacion')
        identificacion = data.get('identificacion')

        usuario = None
        
        if id:
            usuario = self.buscar_por_id(id)
        elif nombre_usuario:
            usuario = self.buscar_por_username(nombre_usuario)   
        elif tipo_identificacion and identificacion:
            usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
            
        if usuario:
            with transaction.atomic():
                usuario.user.delete()
            return JsonResponse({'mensaje': 'Usuario eliminado exitosamente de la base de datos.'}, status=200)
        else:
            return JsonResponse({'mensaje': 'No se especifico un nombre de usuario, documento valido o id para eliminar un usuario.'}, status=400)
        
class BuscarUsuarioView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_por_id(self, id_usuario):
        try:
            return Usuario.objects.get(user__id=id_usuario)
        except Usuario.DoesNotExist:
            return None
    
    def buscar_por_username(self, nombre_usuario):
        try:
            return Usuario.objects.get(user__username=nombre_usuario)
        except Usuario.DoesNotExist:
            return None
        
    def buscar_por_correo(self, correo):
        try:
            return Usuario.objects.get(user__email=correo)
        except Usuario.DoesNotExist:
            return None
        
    def buscar_por_telefono(self, telefono):
        try:
            return Usuario.objects.get(telefono=telefono)
        except Usuario.DoesNotExist:
            return None

    def buscar_por_identificacion(self, tipo_identificacion, identificacion):
        try:
            return Usuario.objects.get(tipo_identificacion=tipo_identificacion, identificacion=identificacion)
        except Usuario.DoesNotExist:
            return None
    
    def mostrar_admin(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario
        }
        
    def mostrar_moderador(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario,
            'hospital': u.hospital.id
        }
    
    def mostrar_usuario(self, u):
        return {
            'id': u.id,
            'tipo_identificacion': u.tipo_identificacion,
            'identificacion': u.identificacion,
            'nombre': u.user.first_name,
            'apellido': u.user.last_name,
            'correo': u.user.email,
            'telefono': u.telefono,
            'nombre_usuario': u.user.username,
            'tipo_usuario': u.tipo_usuario,
            'tipo_sangre': u.tipo_sangre,
            'fecha_nacimiento': u.fecha_nacimiento,
            'eps': u.eps.id
        }
        
    def post(self, request):
        data = {}
        especifica = True
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            especifica = False
        
        if especifica:
            tipo_identificacion = data.get('tipo_identificacion')
            identificacion = data.get('identificacion')
            username = data.get('username')
            id = data.get('id')

            if id:
                usuario = self.buscar_por_id(id)
                if not usuario:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese id en el sistema'}, status=404)
                if usuario.tipo_usuario.lower() == "administrador":
                    return JsonResponse(self.mostrar_admin(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "moderador":
                    return JsonResponse(self.mostrar_moderador(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "usuario":
                    return JsonResponse(self.mostrar_usuario(usuario), status=200)
            
            if username:
                usuario = self.buscar_por_username(username)
                if not usuario:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese nombre de usuario'}, status=404)
                if usuario.tipo_usuario.lower() == "administrador":
                    return JsonResponse(self.mostrar_admin(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "moderador":
                    return JsonResponse(self.mostrar_moderador(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "usuario":
                    return JsonResponse(self.mostrar_usuario(usuario), status=200)
            
            elif tipo_identificacion and identificacion:
                usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
                if not usuario:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese nombre de usuario'}, status=404)
                if usuario.tipo_usuario.lower() == "administrador":
                    return JsonResponse(self.mostrar_admin(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "moderador":
                    return JsonResponse(self.mostrar_moderador(usuario), status=200)
                elif usuario.tipo_usuario.lower() == "usuario":
                    return JsonResponse(self.mostrar_usuario(usuario), status=200)
                
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de un usuario dentro de la peticion"}, status=400)
        
class UsuarioLoginView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def buscar_por_id(self, usuario_id):
        try:
            return Usuario.objects.get(user__id=usuario_id)
        except Usuario.DoesNotExist:
            return None
    
    def buscar_por_username(self, nombre_usuario):
        try:
            return Usuario.objects.get(user__username=nombre_usuario)
        except Usuario.DoesNotExist:
            return None
        
    def buscar_por_correo(self, correo):
        try:
            return Usuario.objects.get(user__email=correo)
        except Usuario.DoesNotExist:
            return None
    
    def buscar_por_telefono(self, telefono):
        try:
            return Usuario.objects.get(telefono=telefono)
        except Usuario.DoesNotExist:
            return None        
    
    def post(self, request):
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        acceso = data.get('acceso')
        clave = data.get('clave')
        usuario = None
        
        if not acceso or acceso == "":
            return JsonResponse({'mensaje': 'Debe ingresar un usuario o correo.'}, status=400)
        
        if not clave or clave == "":
            return JsonResponse({'mensaje': 'Debe ingresar una clave'}, status=400)
        
        usuario = self.buscar_por_correo(acceso)
        if usuario is None:
            usuario = self.buscar_por_username(acceso)
                    
        if usuario is None:
            return JsonResponse({'mensaje': 'Usuario o correo incorrecto'}, status=400)
        
        if not usuario.user.check_password(clave):
            return JsonResponse({'mensaje': 'Acceso incorrecto, clave incorrecta.'}, status=400)
        
        tipo_usuario = usuario.tipo_usuario.lower()
        response = {'mensaje': 'Acceso exitoso, contraseña correcta.', 'tipo_usuario': tipo_usuario}
        
        if tipo_usuario == 'moderador':
            response['nombre_hospital'] = usuario.hospital.nombre
        
        return JsonResponse(response)