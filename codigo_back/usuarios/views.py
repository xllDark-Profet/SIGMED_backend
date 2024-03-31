import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views import View

from hospitales.models import Hospital
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
                    usuario_info = {
                        'tipo_identificacion': usuario.tipo_identificacion,
                        'identificacion': usuario.identificacion,
                        'nombre': usuario.user.first_name,
                        'apellido': usuario.user.last_name,
                        'correo': usuario.user.email,
                        'telefono': usuario.telefono,
                        'nombre_usuario': usuario.user.username,
                        'activo': usuario.user.is_active,
                        'fecha_nacimiento': usuario.fecha_nacimiento,
                        'tipo_sangre': usuario.tipo_sangre,
                        'tipo_usuario': usuario.tipo_usuario
                    }
                    return JsonResponse({'usuario': usuario_info})
                except Usuario.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun usuario con el username proporcionado."}, status=404)
            
            elif tipo_identificacion:
                if identificacion:
                    try:
                        usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
                        if not usuario:
                            return JsonResponse({'mensaje': 'No hay un usuario con ese tipo y numero de identificacion'}, status=404)
                        usuario_info = {
                            'tipo_identificacion': usuario.tipo_identificacion,
                            'identificacion': usuario.identificacion,
                            'nombre': usuario.user.first_name,
                            'apellido': usuario.user.last_name,
                            'correo': usuario.user.email,
                            'telefono': usuario.telefono,
                            'nombre_usuario': usuario.user.username,
                            'activo': usuario.user.is_active,
                            'fecha_nacimiento': usuario.fecha_nacimiento,
                            'tipo_sangre': usuario.tipo_sangre,
                            'tipo_usuario': usuario.tipo_usuario
                        }
                        return JsonResponse({'usuario': usuario_info})
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun usuario con el tipo y numero de documento proporcionados."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta el numero de identificacion."}, status=400)
                
            elif identificacion:
                if tipo_identificacion:
                    try:
                        usuario = self.buscar_por_identificacion(tipo_identificacion, identificacion)
                        if not usuario:
                            return JsonResponse({'mensaje': 'No hay un usuario con ese tipo y numero de identificacion'}, status=404)
                        usuario_info = {
                            'tipo_identificacion': usuario.tipo_identificacion,
                            'identificacion': usuario.identificacion,
                            'nombre': usuario.user.first_name,
                            'apellido': usuario.user.last_name,
                            'correo': usuario.user.email,
                            'telefono': usuario.telefono,
                            'nombre_usuario': usuario.user.username,
                            'activo': usuario.user.is_active,
                            'fecha_nacimiento': usuario.fecha_nacimiento,
                            'tipo_sangre': usuario.tipo_sangre,
                            'tipo_usuario': usuario.tipo_usuario
                        }
                        return JsonResponse({'usuario': usuario_info})
                    except Usuario.DoesNotExist:
                        return JsonResponse({'mensaje': "No se encontro ningun usuario con el tipo y numero de documento proporcionados."}, status=404)
                else:
                    return JsonResponse({'mensaje': "Hace falta el tipo de identificacion."}, status=400)
            return JsonResponse({'mensaje': "No hay datos validos de busqueda de usuario dentro de la peticion"}, status=400)
        
        usuarios = Usuario.objects.all()
        usuarios_list = []
        
        for usuario in usuarios:
            usuario_info = {
                'tipo_identificacion': usuario.tipo_identificacion,
                'identificacion': usuario.identificacion,
                'nombre': usuario.user.first_name,
                'apellido': usuario.user.last_name,
                'correo': usuario.user.email,
                'telefono': usuario.telefono,
                'nombre_usuario': usuario.user.username,
                'activo': usuario.user.is_active,
                'fecha_nacimiento': usuario.fecha_nacimiento,
                'tipo_sangre': usuario.tipo_sangre,
                'tipo_usuario': usuario.tipo_usuario
            }
            usuarios_list.append(usuario_info)
        
        if not usuarios_list:
            return JsonResponse({'mensaje': 'No hay usuarios en el sistema'})
        else:
            return JsonResponse({'usuarios': usuarios_list})
        
    def post(self, request):
            
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        required_fields = ['tipo_identificacion', 'identificacion', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_usuario', 'clave', 'fecha_nacimiento', 'tipo_sangre', 'tipo_usuario']
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
            tipo_usuario=tipo_usuario
        )

        usuario.save()

        return JsonResponse({'mensaje': 'Usuario registrado exitosamente.'}, status=200)
    
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
        
    def entrar(self, data):
        username = data.get('username')
        telefono = data.get('telefono')
        email = data.get('email')
        clave = data.get('clave')
        
        if username:
            if clave:
                usuario = self.buscar_por_username(username)
                if usuario is not None:
                    if usuario.user.check_password(clave):
                        return JsonResponse({'mensaje': 'Usuario loggeado exitosamente'}, status=200)
                    else:
                        return JsonResponse({'mensaje': 'Clave incorrecta'}, status=401)
                else:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese nombre de usuario'}, status=400)                
            else:
                return JsonResponse({'mensaje': 'Falta la clave'}, status=400)
        elif email:
            if clave:
                usuario = self.buscar_por_correo(email)
                if usuario is not None:
                    if usuario.user.check_password(clave):
                        return JsonResponse({'mensaje': 'Usuario loggeado exitosamente'}, status=200)
                    else:
                        return JsonResponse({'mensaje': 'Clave incorrecta'}, status=401)
                else:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese correo'}, status=400)
            else:
                return JsonResponse({'mensaje': 'Falta la clave'}, status=400)
        elif telefono:
            if clave:
                usuario = self.buscar_por_telefono(telefono)
                if usuario is not None:
                    if usuario.user.check_password(clave):
                        return JsonResponse({'mensaje': 'Usuario loggeado exitosamente'}, status=200)
                    else:
                        return JsonResponse({'mensaje': 'Clave incorrecta'}, status=401)
                else:
                    return JsonResponse({'mensaje': 'No hay un usuario con ese telefono'}, status=400)
            else:
                return JsonResponse({'mensaje': 'Falta la clave'}, status=400)
        else:
            return JsonResponse({'mensaje': 'Debe proporcionar un telefono, nombre de usuario o un correo electronico'}, status=400)
    
    def post (self, request):
        
        data = {}
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'mensaje': 'El cuerpo de la solicitud no es JSON valido'}, status=400)
        
        tipo_usuario = data.get('tipo_usuario')
        
        if tipo_usuario == "administrador" or tipo_usuario == "usuario":
            return self.entrar(data)
        elif tipo_usuario == "moderador":
            codigo_registro = data.get('codigo_registro')
            if codigo_registro:
                hospitales = Hospital.objects.filter(codigo_registro=codigo_registro)
                if hospitales.exists():
                    return self.entrar(data)
                else:
                    return JsonResponse({'mensaje': 'El codigo de registro no existe en la base de datos'}, status=404)
            else:
                return JsonResponse({'mensaje': 'Se debe ingresar un codigo de registro'}, status=400)
        else:
            return JsonResponse({'mensaje': 'Tipo de usuario invalido'}, status=400)