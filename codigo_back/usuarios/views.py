from functools import wraps
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views import View

from hospitales.models import EPS, Hospital
from sigmed.constants import TIPOS_USUARIO
from usuarios.models import Usuario

class UsuarioView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
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
            'codigo_registro': u.codigo_registro
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
            'eps': u.eps.nombre
        }
    
    def get(self, request):
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

            if username:
                try:
                    usuario = self.buscar_por_username(username)
                    if not usuario:
                        return JsonResponse({'mensaje': 'No hay un usuario con ese nombre de usuario'}, status=404)
                    if usuario.user.is_active:
                        if usuario.tipo_usuario.lower() == "administrador":
                            return JsonResponse(self.mostrar_admin(usuario), status=200)
                        elif usuario.tipo_usuario.lower() == "moderador":
                            return JsonResponse(self.mostrar_moderador(usuario), status=200)
                        elif usuario.tipo_usuario.lower() == "administrador":
                            return JsonResponse(self.mostrar_usuario(usuario), status=200)
                except Usuario.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun usuario con el username proporcionado."}, status=404)
            
            elif tipo_identificacion:
                if identificacion:
                    try:
                        usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
                        if not usuario:
                            return JsonResponse({'mensaje': 'No hay un usuario con ese tipo y numero de identificacion'}, status=404)
                        if usuario.user.is_active:
                            if usuario.tipo_usuario.lower() == "administrador":
                                return JsonResponse(self.mostrar_admin(usuario), status=200)
                            elif usuario.tipo_usuario.lower() == "moderador":
                                return JsonResponse(self.mostrar_moderador(usuario), status=200)
                            elif usuario.tipo_usuario.lower() == "administrador":
                                return JsonResponse(self.mostrar_usuario(usuario), status=200)
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun usuario con el tipo y numero de documento proporcionados."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta el numero de identificacion."}, status=400)
                
            elif identificacion:
                if tipo_identificacion:
                    try:
                        usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
                        if usuario.user.is_active:
                            if usuario.tipo_usuario.lower() == "administrador":
                                return JsonResponse(self.mostrar_admin(usuario), status=200)
                            elif usuario.tipo_usuario.lower() == "moderador":
                                return JsonResponse(self.mostrar_moderador(usuario), status=200)
                            elif usuario.tipo_usuario.lower() == "administrador":
                                return JsonResponse(self.mostrar_usuario(usuario), status=200)
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun usuario con el tipo y numero de documento proporcionados."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta el tipo de identificacion."}, status=400)
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de usuario dentro de la peticion"}, status=400)
        
        usuarios = Usuario.objects.all()
        usuarios_list = []
        
        for usuario in usuarios:
            if usuario.user.is_active:
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
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON válido'}, status=400)

        if not isinstance(data, list):
            required_fields = ['tipo_identificacion', 'identificacion', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_usuario', 'clave', 'tipo_usuario']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'mensaje': f'El campo {field} es requerido'}, status=400)

            tipo_identificacion = data.get('tipo_identificacion')
            identificacion = data.get('identificacion')
            nombre = data.get('nombre')
            apellido = data.get('apellido')
            correo = data.get('correo')
            telefono = data.get('telefono')
            nombre_usuario = data.get('nombre_usuario')
            clave = data.get('clave')
            fecha_nacimiento = data.get('fecha_nacimiento')
            tipo_sangre = data.get('tipo_sangre')
            tipo_usuario = data.get('tipo_usuario')
            codigo_registro = data.get('codigo_registro')
            eps = data.get('eps')
            
            if tipo_usuario.lower() == "moderador":
                if codigo_registro:
                    try:
                        hospital = Hospital.objects.get(codigo_registro=codigo_registro)
                    except Hospital.DoesNotExist:
                        return JsonResponse({'mensaje': 'No existe un hospital con ese codigo de registro.'}, status=400)
                else:
                    return JsonResponse({'mensaje': 'Para un moderador es necesario un codigo de registro'}, status=400)
            elif tipo_usuario.lower() == "usuario":
                required_fields = ['tipo_sangre', 'fecha_nacimiento', 'eps']
                for field in required_fields:
                    if field not in data or not data[field]:
                        return JsonResponse({'mensaje': f'El campo {field} es requerido para un usuario'}, status=400)
                try:
                    eps = EPS.objects.get(nombre=eps)
                except EPS.DoesNotExist:
                    return JsonResponse({'mensaje': 'No existe esa EPS en el sistema.'}, status=400)

            if Usuario.objects.filter(tipo_identificacion=tipo_identificacion, identificacion=identificacion).exists():
                return JsonResponse({'mensaje': 'Ya hay un usuario con este tipo y numero de identificacion en la base de datos'}, status=400)

            if Usuario.objects.filter(user__username=nombre_usuario).exists():
                return JsonResponse({'mensaje': 'Ya hay un usuario con ese nombre de usuario en la base de datos'}, status=400)
            
            if Usuario.objects.filter(telefono=telefono).exists():
                return JsonResponse({'mensaje': 'Ya hay un usuario con ese telefono en la base de datos'}, status=400)
            
            user = User.objects.create_user(username=nombre_usuario, email=correo, password=clave, first_name=nombre, last_name=apellido)

            usuario = Usuario(
                user=user,
                tipo_identificacion=tipo_identificacion,
                identificacion=identificacion,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento,
                tipo_sangre=tipo_sangre,
                tipo_usuario=tipo_usuario,
                codigo_registro=codigo_registro,
                eps=eps
            )

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
                tipo_identificacion = user_data.get('tipo_identificacion')
                identificacion = user_data.get('identificacion')
                nombre = user_data.get('nombre')
                apellido = user_data.get('apellido')
                correo = user_data.get('correo')
                telefono = user_data.get('telefono')
                nombre_usuario = user_data.get('nombre_usuario')
                clave = user_data.get('clave')
                fecha_nacimiento = user_data.get('fecha_nacimiento')
                tipo_sangre = user_data.get('tipo_sangre')
                tipo_usuario = user_data.get('tipo_usuario')
                codigo_registro = user_data.get('codigo_registro')
                eps = user_data.get('eps')
                
                if tipo_usuario.lower() == "moderador":
                    if codigo_registro:
                        try:
                            hospital = Hospital.objects.get(codigo_registro=codigo_registro)
                        except Hospital.DoesNotExist:
                            users_failed.append({'mensaje': 'No existe un hospital con ese código de registro.'})
                            continue
                    else:
                        users_failed.append({'mensaje': 'Para un moderador es necesario un código de registro.'})
                        continue
                elif tipo_usuario.lower() == "usuario":
                    required_fields = ['tipo_sangre', 'fecha_nacimiento', 'eps']
                    for field in required_fields:
                        if field not in user_data or not user_data[field]:
                            users_failed.append({'mensaje': f"El campo '{field}' es requerido para un usuario."})
                            break
                    else:
                        try:
                            eps = EPS.objects.get(nombre=eps)
                        except EPS.DoesNotExist:
                            users_failed.append({'mensaje': 'No existe esa EPS en el sistema.'})
                            continue

                if Usuario.objects.filter(tipo_identificacion=tipo_identificacion, identificacion=identificacion).exists():
                    users_failed.append({'mensaje': 'Ya hay un usuario con este tipo y número de identificación en la base de datos.'})
                    continue

                if Usuario.objects.filter(user__username=nombre_usuario).exists():
                    users_failed.append({'mensaje': 'Ya hay un usuario con ese nombre de usuario en la base de datos.'})
                    continue
                
                if Usuario.objects.filter(telefono=telefono).exists():
                    users_failed.append({'mensaje': 'Ya hay un usuario con ese teléfono en la base de datos.'})
                    continue
                
                user = User.objects.create_user(username=nombre_usuario, email=correo, password=clave, first_name=nombre, last_name=apellido)

                usuario = Usuario(
                    user=user,
                    tipo_identificacion=tipo_identificacion,
                    identificacion=identificacion,
                    telefono=telefono,
                    fecha_nacimiento=fecha_nacimiento,
                    tipo_sangre=tipo_sangre,
                    tipo_usuario=tipo_usuario,
                    codigo_registro=codigo_registro,
                    eps=eps
                )

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
        usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
        
        if not usuario:
            return JsonResponse({'mensaje': 'El usuario no existe en el sistema'}, status=404)

        nombre_usuario = data.get('nombre_usuario')
        clave = data.get('clave')
        nueva_clave = data.get('nueva_clave')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        telefono = data.get('telefono')
        fecha_nacimiento = data.get('fecha_nacimiento')
        tipo_sangre = data.get('tipo_sangre')
        tipo_usuario = data.get('tipo_usuario')
        codigo_registro = data.get('codigo_registro')
        eps = data.get('eps')

        user = usuario.user
        if nombre:
            user.first_name = nombre
            cambios = True
        if apellido:
            user.last_name = apellido
            cambios = True
        if correo:
            if correo != usuario.user.email:
                if self.buscar_por_correo(correo):
                    return JsonResponse({'mensaje': 'Ya existe ese correo.'}, status=400)
                else:
                    cambios=True
                    user.email = correo
        if nombre_usuario:
            if nombre_usuario != usuario.user.username:
                if self.buscar_por_username(nombre_usuario):
                    return JsonResponse({'mensaje': 'Ya existe ese nombre de usuario.'}, status=400)
                else:
                    cambios=True
                    user.username = nombre_usuario
        
        if clave:            
            if user.check_password(clave):
                if nueva_clave:
                    cambios = True
                    user.set_password(nueva_clave)
                else:
                    return JsonResponse({'mensaje': 'La clave actual del usuario es incorrecta.'}, status=400)
            else:
                return JsonResponse({'mensaje': 'La clave actual del usuario es incorrecta.'}, status=400)
            
        user.save()

        if telefono:
            if telefono != usuario.telefono:
                if self.buscar_por_username(nombre_usuario):
                    return JsonResponse({'mensaje': 'Ya existe ese nombre de usuario.'}, status=400)
                else:
                    usuario.telefono = telefono
                    cambios = True
                    
        if fecha_nacimiento:
            usuario.fecha_nacimiento = fecha_nacimiento
            cambios = True
        if tipo_sangre:
            usuario.tipo_sangre = tipo_sangre
            cambios = True
        if tipo_usuario:
            usuario.tipo_usuario = tipo_usuario
            cambios = True
        
        if codigo_registro:
            try:
                hospital = Hospital.objects.get(codigo_registro=codigo_registro)
            except Hospital.DoesNotExist:
                return JsonResponse({'mensaje': 'No existe un hospital con ese codigo de registro.'}, status=400)
        
        if eps:
            try:
                eps = EPS.objects.get(nombre=eps)
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
        nombre_usuario = data.get('nombre_usuario')
        tipo_identificacion = data.get('tipo_identificacion')
        identificacion = data.get('identificacion')

        usuario = None

        if nombre_usuario:
            try:
                usuario = self.buscar_por_username(nombre_usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({'mensaje': 'No se encontro ningun usuario por ese nombre de usuario'}, status=404)
            
        if tipo_identificacion and identificacion:
            try:
                usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
            except Usuario.DoesNotExist:
                return JsonResponse({'mensaje': 'No se encontro ningun usuario con ese tipo y numero de identificiacion'}, status=404)
        
        if usuario:
            if usuario.user.is_active:
                usuario.user.is_active = False
                usuario.user.save()
                return JsonResponse({'mensaje': 'Usuario inactivado exitosamente.'}, status=200)
            else:
                return JsonResponse({'mensaje': 'Usuario ya se encontraba inactivo.'}, status=400)
        else:
            return JsonResponse({'mensaje': 'No se especifico un nombre de usuario o documento valido para inactivar.'}, status=400)
        
class UsuarioLoginView(View):
    
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
        
        tipo_usuario = data.get('tipo_usuario')
        
        if tipo_usuario and tipo_usuario.lower() in TIPOS_USUARIO:
            username = data.get('username')
            telefono = data.get('telefono')
            email = data.get('email')
            clave = data.get('clave')
            usuario = None
            
            if not clave:
                return JsonResponse({'mensaje': 'Falta la clave'}, status=400)
            
            if username:
                usuario = self.buscar_por_username(username)
                if usuario is None:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese nombre de usuario'}, status=400)                             
            elif email:
                usuario = self.buscar_por_correo(email)
                if usuario is None:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese correo'}, status=400)
            elif telefono:
                usuario = self.buscar_por_telefono(telefono)
                if usuario is None:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese telefono'}, status=400)
            else:
                return JsonResponse({'mensaje': 'Debe proporcionar un telefono, nombre de usuario o un correo electronico'}, status=400)
            
            if usuario.tipo_usuario.lower() != tipo_usuario.lower():
                return JsonResponse({'mensaje': 'El tipo de usuario para ese usuario es incorrecto'}, status=400)
            
            if not usuario.user.is_active:
                return JsonResponse({'mensaje': 'El usuario se encuentra inactivo'}, status=401)
            
            if tipo_usuario.lower() == "moderador":
                codigo_registro = data.get('codigo_registro')
                if not codigo_registro:
                    return JsonResponse({'mensaje': 'Hace falta un codigo de registro para el acceso de un moderador'}, status=400)
                
                try:
                    hospital = Hospital.objects.get(codigo_registro=codigo_registro)
                except Hospital.DoesNotExist:
                    return JsonResponse({'mensaje': 'No existe un hospital con ese codigo de registro.'}, status=400)
                
                if usuario.codigo_registro != codigo_registro:
                    return JsonResponse({'mensaje': 'El codigo de registro del usuario es incorrecto'}, status=400)
            
            if not usuario.user.check_password(clave):
                return JsonResponse({'mensaje': 'Acceso incorrecto, clave erronea.'}, status=400)
            
            # Aqui el resto
            response = JsonResponse({"mensaje": "Si"})
            
            return response
        else:
            return JsonResponse({'mensaje': 'No hay un tipo de usuario o el tipo de usuario es incorrecto'}, status=400)