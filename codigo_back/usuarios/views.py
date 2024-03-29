import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views import View

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

    def buscar_por_identificacion(self, tipo_identificacion, identificacion):
        try:
            return Usuario.objects.get(tipo_identificacion=tipo_identificacion, identificacion=identificacion)
        except Usuario.DoesNotExist:
            return None
    
    def get(self, request):
        tipo_identificacion = request.GET.get('tipo_identificacion')
        identificacion = request.GET.get('identificacion')
        username = request.GET.get('username')

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
                    'eps': usuario.eps,
                    'tipo_sangre': usuario.tipo_sangre,
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
                        'eps': usuario.eps,
                        'tipo_sangre': usuario.tipo_sangre,
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
                        'eps': usuario.eps,
                        'tipo_sangre': usuario.tipo_sangre,
                    }
                    return JsonResponse({'usuario': usuario_info})
                except Usuario.DoesNotExist:
                    return JsonResponse({'mensaje': "No se encontro ningun usuario con el tipo y numero de documento proporcionados."}, status=404)
            else:
                return JsonResponse({'mensaje': "Hace falta el tipo de identificacion."}, status=400)
        
        else:
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
                    'eps': usuario.eps,
                    'tipo_sangre': usuario.tipo_sangre,
                }
                usuarios_list.append(usuario_info)
            
            if not usuarios_list:
                return JsonResponse({'mensaje': 'No hay usuarios en el sistema'})
            else:
                return JsonResponse({'usuarios': usuarios_list})
        
    def post(self, request):
        data = json.loads(request.body)

        tipo_identificacion = data.get('tipo_identificacion')
        identificacion = data.get('identificacion')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        telefono = data.get('telefono')
        nombre_usuario = data.get('nombre_usuario')
        clave = data.get('clave')
        fecha_nacimiento = data.get('fecha_nacimiento')
        eps = data.get('eps')
        tipo_sangre = data.get('tipo_sangre')

        if Usuario.objects.filter(tipo_identificacion=tipo_identificacion, identificacion=identificacion).exists():
            return JsonResponse({'mensaje': 'Ya hay un usuario con este tipo y numero de identificacion en la base de datos'}, status=400)

        if Usuario.objects.filter().exists():
            return JsonResponse({'mensaje': 'Ya hay un usuario con este tipo y numero de identificacion en la base de datos'}, status=400)
        
        user = User.objects.create_user(username=nombre_usuario, email=correo, password=clave, first_name=nombre, last_name=apellido)

        usuario = Usuario(
            user=user,
            tipo_identificacion=tipo_identificacion,
            identificacion=identificacion,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            eps=eps,
            tipo_sangre=tipo_sangre
        )

        usuario.save()

        return JsonResponse({'mensaje': 'Usuario registrado exitosamente.'}, status=200)
    
    def put(self, request):
        data = json.loads(request.body)
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
        eps = data.get('eps')
        tipo_sangre = data.get('tipo_sangre')

        user = usuario.user
        if nombre:
            user.first_name = nombre
            cambios = True
        if apellido:
            user.last_name = apellido
            cambios = True
        if correo:
            user.email = correo
            cambios = True
        if nombre_usuario:
            if nombre_usuario != user.username:
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
            usuario.telefono = telefono
            cambios = True
        if fecha_nacimiento:
            usuario.fecha_nacimiento = fecha_nacimiento
            cambios = True
        if eps:
            usuario.eps = eps
            cambios = True
        if tipo_sangre:
            usuario.tipo_sangre = tipo_sangre
            cambios = True

        if cambios:
            usuario.save()
            return JsonResponse({'mensaje': 'Usuario actualizado exitosamente.'}, status=200)
        else:
            return JsonResponse({'mensaje': 'No se realizaron cambios en el usuario.'}, status=400)
        
    def delete(self, request):
        data = json.loads(request.body)
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